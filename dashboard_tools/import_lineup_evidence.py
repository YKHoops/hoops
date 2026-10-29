"""Import a reviewed Fantrax UI capture into a versioned planning contract.

No endpoint probing, credential use, or public publication. Ambiguous identities
and incomplete schedules fail before promotion. See LINEUP_SETTING_README.md.
"""
import argparse
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from collection_state import atomic_json
from player_identity import Identity
from lineup_optimizer import blend, validate, SLOTS
from workspace import ROOT


def normalize(raw, dashboard):
    identity=Identity(); season=raw['season']; start_year=int(season[:4])
    observed_day=datetime.fromisoformat(raw['as_of']).astimezone(ZoneInfo('America/New_York')).date()
    planning_day=date.fromisoformat(raw['period'].get('planning_start',raw['period']['start']))
    observed_week=observed_day-timedelta(days=observed_day.weekday())
    planning_week=planning_day-timedelta(days=planning_day.weekday())
    allowance=raw['claims_remaining_observed'] if planning_week==observed_week else 4 if planning_week>observed_week else None
    roster=dashboard['rosters_by_season'][season]['by_owner'][raw['owner']]
    expected={p['player_id'] for p in roster}; players=[]
    prior=[f'{y}-{str(y+1)[-2:]}' for y in range(start_year-3,start_year)]
    historical={s:{p['player_id']:p for p in dashboard['nba_stats']['seasons'].get(s,{}).get('rows',[])} for s in prior}
    game_ids=[r[0] for r in raw['games']]
    if len(game_ids)!=len(set(game_ids)): raise ValueError('Duplicate game IDs')
    for name,slot,positions,team,fp,gp,pct,injury in raw['rows']:
        pid=identity.resolve(name)
        if pid not in expected: raise ValueError('Unreviewed roster identity: '+name)
        history=[]
        for s in prior:
            h=historical[s].get(pid)
            if h: history.append({'season':s,'gp':h['gp'],'fp_pg':h['per_game'].get('fp')})
        return_date=None
        if injury:
            text=injury.split('Expected return ',1)[1]
            ret=datetime.strptime(text+' '+str(start_year),'%b %d %Y').date()
            if ret.month<7: ret=ret.replace(year=start_year+1)
            return_date=ret.isoformat()
        games=[]
        for gid,day,time,away,home in raw['games']:
            if team not in [away,home]: continue
            availability='available' if not injury else 'out' if day < return_date else 'conditional'
            games.append({'id':gid,'date':day,'start':datetime.fromisoformat(day+'T'+time).replace(tzinfo=ZoneInfo('America/New_York')).isoformat(),
                          'opponent':('@'+home if team==away else away),'availability':availability})
        status={'Res':'RESERVE','IR':'IR','Min':'MINORS'}.get(slot,'ACTIVE')
        players.append({'id':pid,'name':name,'status':status,'lineup_slot':slot,'positions':positions.split(','),
                        'eligible_slots':[s for s in SLOTS if s in positions.split(',') or s.startswith('Flx')],
                        'nba_team':team,'rostered_pct':pct,'injury':injury,'expected_return':return_date,
                        'projection':blend({'fp_pg':fp,'gp':gp},history),'games':sorted(games,key=lambda g:g['start'])})
    if {p['id'] for p in players}!=expected or len(players)!=len(expected): raise ValueError('Roster capture must reconcile completely')
    result={'schema_version':1,'as_of':raw['as_of'],'owner':raw['owner'],'team_name':raw['team_name'],'season':season,
            'period':raw['period'],'period_evidence':raw.get('period_evidence',[]),'rules':{'slots':SLOTS,'max_main':20,'max_reserve':10},'players':players,
            'sources':[{'label':'Fantrax roster, Trends, Schedule – Week','url':raw['source'],'as_of':raw['as_of']},
                       {'label':'Previous three seasons · saved YK production','as_of':dashboard['nba_stats'].get('built_at')}],
            'assumptions':[f"Fantrax Min/Max verifies period {raw['period']['fantrax_period']}, {raw['period']['start']}–{raw['period']['end']}: minimum {raw['period']['minimum']} and maximum {raw['period']['cap']}. Calendar-day prorating is not assumed.",
                           'Flex slots accept all observed basketball positions. Individual eligibility comes from the league roster view.',
                           'No IR/minors activations or acquisitions are assumed. Expected return dates are conditional, not medical clearance.',
                           'Schedule includes all visible games for the captured roster; other NBA teams are not a complete free-agent schedule.',
                           'Historical FP/G uses three prior seasons with available evidence; older rounded/partial snapshots retain that limitation.'],
            'claims':{'weekly_limit':4,'observed_remaining':raw['claims_remaining_observed'],'observed_week_start':observed_week.isoformat(),
                      'planning_week_start':planning_week.isoformat(),'planning_allowance':allowance,'basis':'Allowance for the selected planning week only; Monday resets are separate from matchup boundaries. Recheck successful and pending claims before acting'},
            'waivers':{'status':'unavailable','reason':'Free-agent eligibility, waiver clearance, bid/claim timing and center-limit counting need verified candidate data.'},
            'comparisons':{'status':'unavailable','reason':'Daily historical rosters and credited GP are not captured; Fantrax optimal cap behavior is unverified.'}}
    validate(result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('capture',type=Path);args=parser.parse_args()
    raw=json.loads(args.capture.read_text());d=json.loads((ROOT/'docs/data/dashboard.json').read_text())
    normalized=normalize(raw,d)
    destination=ROOT/'private/lineup_snapshots'/('input-'+normalized['period']['id']+'.json')
    atomic_json(destination,normalized)
    manifest=ROOT/'private/lineup_snapshots/approved.json'
    paths=json.loads(manifest.read_text())['paths'] if manifest.exists() else []
    atomic_json(manifest,{'paths':sorted(set(paths+[destination.name]))})
    print('Validated',len(normalized['players']),'players; reviewed input selected:',destination.name)


if __name__=='__main__':main()
