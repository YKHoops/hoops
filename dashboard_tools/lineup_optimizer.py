"""Points-first, whole-period lineup planning. No network or Fantrax mutations.

Integer assignments include off-day fillers, so the reserve limit remains legal.
Scoring starts, active roster placements and actual credited GP are distinct.
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
import math
from zoneinfo import ZoneInfo

SLOTS = ['PG', 'SG', 'G', 'SF', 'PF', 'F', 'C', 'Flx', 'Flx2', 'Flx3']
MAIN = {'ACTIVE', 'RESERVE'}


def blend(current, history):
    """history contains only prior-season rows with compatible YK scoring."""
    valid = [r for r in history if r.get('gp', 0) > 0 and finite(r.get('fp_pg'))]
    gp = sum(r['gp'] for r in valid)
    past = sum(r['gp'] * r['fp_pg'] for r in valid) / gp if gp else None
    now = current.get('fp_pg') if current.get('gp', 0) > 0 else None
    if not finite(now): now = None
    value = .9 * now + .1 * past if now is not None and past is not None else now if now is not None else past
    return {'fp_pg': round(value, 4) if value is not None else None,
            'current': now, 'current_gp': current.get('gp', 0), 'historical': past,
            'historical_gp': gp, 'historical_seasons': [r['season'] for r in valid],
            'basis': '90/10 blend' if now is not None and past is not None else
                     'Current only · no history' if now is not None else
                     'Historical only · no current games' if past is not None else 'Projection unavailable',
            'small_sample': 0 < current.get('gp', 0) < 10}


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def protection(player, manual=(), ownership_fresh=True):
    if player['id'] in manual: return 'Manually protected'
    pct = player.get('rostered_pct')
    if not finite(pct) or not ownership_fresh: return 'Ownership unavailable or stale'
    if pct > 70: return 'Over 70% rostered'
    return None


def dates(period):
    start, end = date.fromisoformat(period.get('planning_start',period['start'])), date.fromisoformat(period['end'])
    return [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]


def validate(data):
    if data.get('schema_version') != 1: raise ValueError('Unsupported lineup input version')
    period = data['period']; days = dates(period)
    if not 1 <= len(days) <= 31: raise ValueError('Period must contain 1–31 days')
    cap = period.get('cap')
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 0: raise ValueError('Verified or explicit integer cap required')
    if not period.get('cap_basis'): raise ValueError('Cap basis required; do not silently prorate')
    for key in ['credited_gp', 'reserved_gp']:
        if not isinstance(period.get(key), int) or period[key] < 0: raise ValueError('Explicit credited/reserved GP required')
    cutoff = datetime.fromisoformat(data['as_of'])
    if cutoff.tzinfo is None: raise ValueError('Timezone-aware capture required')
    ids = set(); slots = data['rules']['slots']; locked_slots=set(); locked_games=0
    if period.get('planning_start',period['start']) < period['start']: raise ValueError('Planning start precedes period')
    if not slots or len(set(slots)) != len(slots): raise ValueError('Unique slots required')
    for p in data['players']:
        if p['id'] in ids: raise ValueError('Duplicate player')
        ids.add(p['id'])
        if not p['eligible_slots'] or not set(p['eligible_slots']) <= set(slots): raise ValueError('Invalid eligibility')
        if p['status'] not in MAIN | {'IR', 'MINORS'}: raise ValueError('Unknown roster status')
        if p.get('rostered_pct') is not None and (not finite(p['rostered_pct']) or not 0 <= p['rostered_pct'] <= 100): raise ValueError('Invalid ownership')
        seen = set()
        for g in p['games']:
            if g['date'] not in days or g['date'] in seen: raise ValueError('Duplicate or out-of-period player game')
            seen.add(g['date'])
            if g['availability'] not in ['available', 'out', 'conditional']: raise ValueError('Unknown availability')
            start = datetime.fromisoformat(g['start'])
            if start.tzinfo is None: raise ValueError('Game start timezone required')
            if start.astimezone(ZoneInfo('America/New_York')).date().isoformat()!=g['date']: raise ValueError('Game date disagrees with league timezone')
            if g.get('locked_slot') is not None:
                if g['locked_slot'] not in p['eligible_slots']: raise ValueError('Invalid locked slot')
                lock=(g['date'],g['locked_slot'])
                if lock in locked_slots: raise ValueError('Conflicting locked slots')
                locked_slots.add(lock)
                if not g.get('settled') and g['availability']!='out': locked_games+=1
            if start <= cutoff and not g.get('settled') and 'locked_slot' not in g:
                raise ValueError('Past/started game requires settled or explicit locked-slot evidence')
    if locked_games>period['reserved_gp']: raise ValueError('Locked games must be reserved against the cap')
    if sum(p['status'] in MAIN for p in data['players']) > data['rules']['max_main']: raise ValueError('Main roster is over limit')


def solve(data, objective='points', conditional=False, target_games=None, target_points=None, excluded=(), time_limit=15):
    """MILP status 0 proves the optimum for these inputs, never future outcomes."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    validate(data)
    if objective not in ['points', 'games', 'depth']: raise ValueError('Unknown objective')
    period = data['period']; days = dates(period); slots = data['rules']['slots']
    remaining = max(0, period['cap'] - period['credited_gp'] - period['reserved_gp'])
    players = [p for p in data['players'] if p['status'] in MAIN]
    variables = []; by_player_day = defaultdict(list); by_slot = defaultdict(list); by_day = defaultdict(list)
    scoring = {}; scores = {}; locked = []; game_map = {}
    for pi, p in enumerate(players):
        games = {g['date']: g for g in p['games']}; game_map[p['id']] = games
        for day in days:
            g = games.get(day)
            if g and g.get('settled'): continue
            is_locked = g is not None and 'locked_slot' in g
            can_play = bool(g and g['availability'] != 'out')
            selectable = p['id'] not in excluded and (not g or g['availability'] != 'conditional' or conditional)
            quality = p.get('projection', {}).get('fp_pg')
            for slot in p['eligible_slots']:
                # Uncertain/unknown-projection games cannot sneak in as zero-point fillers.
                if can_play and not is_locked and (not selectable or not finite(quality)): continue
                if is_locked and slot != g['locked_slot']: continue
                idx = len(variables); variables.append((pi, day, slot))
                by_player_day[pi, day].append(idx); by_slot[day, slot].append(idx); by_day[day].append(idx)
                if can_play and not is_locked:
                    scoring[idx] = 1; scores[idx] = quality
                if is_locked: locked.append(idx)
    nx = len(variables); n = nx + len(players)
    rows=[]; lower=[]; upper=[]
    def constraint(coeff, lo=-np.inf, hi=np.inf):
        rows.append(coeff); lower.append(lo); upper.append(hi)
    for indices in by_player_day.values(): constraint({i:1 for i in indices}, hi=1)
    for indices in by_slot.values(): constraint({i:1 for i in indices}, hi=1)
    for day, indices in by_day.items():
        # Past settled days are not replanned. Each remaining complete day keeps reserves legal.
        if any(g.get('settled') for gs in game_map.values() for d,g in gs.items() if d == day): continue
        constraint({i:1 for i in indices}, lo=max(0,len(players)-data['rules']['max_reserve']))
    constraint(scoring, hi=remaining)
    if target_games is not None: constraint(scoring, lo=target_games)
    if target_points is not None: constraint(scores, lo=target_points - 1e-6)
    for i in scoring:
        pi = variables[i][0]; constraint({i:1, nx+pi:-1}, hi=0)
    for pi in range(len(players)):
        eligible = [i for i in scoring if variables[i][0] == pi]
        constraint({nx+pi:1, **{i:-1 for i in eligible}}, hi=0)
    if not n: return {'status':'optimal','gap':0,'assignments':[],'active_placements':[], 'games':0,'points':0,'players_used':0,'player_ids':[]}
    def run(cost, extra=()):
        rs=rows+[x[0] for x in extra]; lo=lower+[x[1] for x in extra]; hi=upper+[x[2] for x in extra]
        rr=[];cc=[];vv=[]
        for r, coeff in enumerate(rs):
            for c,v in coeff.items(): rr.append(r);cc.append(c);vv.append(v)
        matrix=coo_matrix((vv,(rr,cc)),shape=(len(rs),n)).tocsc()
        lb=np.zeros(n);ub=np.ones(n)
        for i in locked: lb[i]=1
        return milp(np.array(cost),integrality=np.ones(n),bounds=Bounds(lb,ub),
                    constraints=LinearConstraint(matrix,lo,hi),options={'time_limit':time_limit,'mip_rel_gap':0})
    cost=[0.0]*n
    if objective=='depth':
        for i in range(nx,n): cost[i]=1
    else:
        for i in scoring: cost[i]=-scores[i] if objective=='points' else -1
    result=run(cost)
    if result.x is None:
        return {'status':'infeasible' if result.status==2 else 'unavailable','gap':None,'assignments':[],
                'active_placements':[],'games':None,'points':None,'players_used':None,'player_ids':[]}
    # Lexicographic secondary solve preserves the first optimum exactly.
    proven=result.status==0
    if proven and objective in ['points','games']:
        if objective=='games':
            fixed=sum(result.x[i] for i in scoring); extra=[(scoring,fixed-.001,fixed+.001)]
            second=[-scores.get(i,0) for i in range(n)]
        else:
            fixed=sum(scores[i]*result.x[i] for i in scores);extra=[(scores,fixed-1e-6,np.inf)]
            # Avoid useless zero-point starts; then prefer the existing slot when tied.
            second=[(1 if i in scoring else 0)+(.00001 if i<nx and variables[i][2]!=players[variables[i][0]].get('lineup_slot') else 0) for i in range(n)]
        improved=run(second,extra)
        if improved.x is not None: result=improved
        proven=proven and improved.status==0
    active=[]; assignments=[]
    for i,(pi,day,slot) in enumerate(variables):
        if result.x[i] < .5: continue
        p=players[pi]; row={'player_id':p['id'],'date':day,'slot':slot,'locked':i in locked}
        active.append(row)
        if i in scoring:
            g=game_map[p['id']][day]
            assignments.append({**row,'points':scores[i],'opponent':g['opponent'],'start':g['start'],
                                'conditional':g['availability']=='conditional','game_id':g['id']})
    used=sorted({r['player_id'] for r in assignments})
    return {'status':'optimal' if proven else 'best_found','gap':float(result.mip_gap) if finite(result.get('mip_gap')) else None,
            'assignments':sorted(assignments,key=lambda r:(r['date'],slots.index(r['slot']))),
            'active_placements':active,'games':len(assignments),'points':round(sum(r['points'] for r in assignments),4),
            'players_used':len(used),'player_ids':used}


def analyze(data, conditional=False, excluded=()):
    best=solve(data,conditional=conditional,excluded=excluded)
    reach=solve(data,'games',conditional=conditional,excluded=excluded)
    remaining=max(0,data['period']['cap']-data['period']['credited_gp']-data['period']['reserved_gp'])
    depth=solve(data,'depth',conditional=conditional,target_games=remaining,excluded=excluded) if reach['games'] is not None and reach['games']>=remaining else {'status':'unreachable' if reach['status']=='optimal' else 'unavailable','players_used':None}
    preserve=solve(data,'depth',conditional=conditional,target_points=best['points']*.95,excluded=excluded) if best['points'] is not None else {'status':'unavailable','players_used':None}
    used={(r['player_id'],r['date']) for r in best['assignments']}
    daily=[]
    for day in dates(data['period']):
        starts=[a for a in best['assignments'] if a['date']==day]
        eligible=[]; unavailable=[]; bench=[]
        for p in data['players']:
            g=next((g for g in p['games'] if g['date']==day),None)
            if not g: continue
            if p['status'] not in MAIN: reason='IR/minors · activation required'
            elif p['id'] in excluded: reason='Excluded in this scenario'
            elif g.get('settled'): reason='Completed · not replanned'
            elif 'locked_slot' in g: reason='Locked · counted in reserved GP'
            elif g['availability']=='out': reason='Unavailable'
            elif g['availability']=='conditional' and not conditional: reason='Conditional return excluded'
            elif not finite(p.get('projection',{}).get('fp_pg')): reason='Projection unavailable'
            else:
                eligible.append(p['id'])
                if (p['id'],day) in used: continue
                reason='Bench · weekly points/cap or position fit'
            row={'player_id':p['id'],'reason':reason}
            (bench if p['id'] in eligible else unavailable).append(row)
        daily.append({'date':day,'starts':len(starts),'scheduled':sum(any(g['date']==day for g in p['games']) for p in data['players']),
                      'available':len(eligible),'open_slots':[s for s in data['rules']['slots'] if s not in {a['slot'] for a in starts}],
                      'bench':bench,'unavailable':unavailable})
    return {'best':best,'reach':reach,'minimum_players':depth,'preserve_95':preserve,'daily':daily,
            'shortfall':max(0,remaining-reach['games']) if reach['games'] is not None else None,
            'conditional':conditional,'excluded':list(excluded)}
