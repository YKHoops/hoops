"""Offline NBA results build. Retains raw games; never sums aggregate and team-split rows."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
from zoneinfo import ZoneInfo
from player_identity import ROOT,Identity
from collection_state import atomic_json
WEIGHTS={'pts':1,'reb':1,'ast':2,'stl':4,'blk':4,'fgm':2,'fga':-1,'ftm':1,'fta':-1,'fg3m':1,'tov':-2}
FIELDS=['min','pts','reb','ast','stl','blk','tov','fgm','fga','fg3m','fg3a','ftm','fta']
def fantasy(stats):
    return round(sum(stats[k]*v for k,v in WEIGHTS.items()),4) if all(isinstance(stats.get(k),(int,float)) for k in WEIGHTS) else None
def percentages(s):
    return {k:round(100*s[m]/s[a],4) if s.get(a) and s.get(m) is not None else None for k,m,a in [('fg_pct','fgm','fga'),('fg3_pct','fg3m','fg3a'),('ft_pct','ftm','fta')]}
def from_game(d):
    if not d['header']['competitions'][0]['status']['type']['completed']:return []
    rows=[]
    for team in d['boxscore']['players']:
        block=team['statistics'][0]; labels=block['labels']
        for a in block['athletes']:
            if a.get('didNotPlay') or not a.get('stats'):continue
            v=dict(zip(labels,a['stats'])); t={}
            for src,out in [('PTS','pts'),('REB','reb'),('AST','ast'),('STL','stl'),('BLK','blk'),('TO','tov')]: t[out]=float(v[src])
            t['min']=sum(float(x)/60**i for i,x in enumerate(v['MIN'].split(':')))
            for src,m,at in [('FG','fgm','fga'),('3PT','fg3m','fg3a'),('FT','ftm','fta')]:t[m],t[at]=map(float,v[src].split('-'))
            if any(t[m]>t[at] for m,at in [('fgm','fga'),('fg3m','fg3a'),('ftm','fta')]):raise ValueError('Invalid shooting line')
            if t['pts']!=2*t['fgm']+t['fg3m']+t['ftm']:raise ValueError('Box score point reconciliation failed')
            rows.append({'source_player_id':a['athlete']['id'],'player_name':a['athlete']['displayName'],'position':a['athlete'].get('position',{}).get('abbreviation',''),'nba_team':team['team']['abbreviation'],'totals':t})
    return rows

def build():
    settings=json.loads((ROOT/'private/target/runs/2026-10-21T17-04-30.964717+00-00/getLeagueInfo.json').read_text())['scoringSystem']['scoringCategories']['PLAYER']
    aliases={'ST':'stl','TO':'tov','3PTM':'fg3m'}
    verified={aliases.get(k,k.lower()):float(v['Default'].replace('points','')) for k,v in settings.items()}
    if verified!=WEIGHTS:raise ValueError('YK scoring changed; review formula before rebuilding results')
    identity=Identity(); seasons={}; original=ROOT/'source/yk/docs/data/player_stats_historical.json'
    raw=json.loads(original.read_text()); fields={'mpg':'min','ppg':'pts','rpg':'reb','apg':'ast','spg':'stl','bpg':'blk','topg':'tov','fgm_pg':'fgm','fga_pg':'fga','fg3m_pg':'fg3m','ftm_pg':'ftm','fta_pg':'fta'}
    for season,players in raw.items():
        rows=[]
        for r in players.values():
            per={v:r.get(k) for k,v in fields.items()};per['fg3a']=None
            per.update(percentages(per));per['fp']=fantasy(per)
            # Total estimates from rounded per-game inputs are intentionally not represented as exact totals.
            rows.append({'player_id':identity.resolve(r['player_name']),'player_name':r['player_name'],'position':r.get('pos',''),'nba_team':r.get('team',''),'source_player_id':None,'gp':r['gp'],'per_game':per,'totals':None,'basis':'archived_rounded_per_game'})
        assert len({x['player_id'] for x in rows})==len(rows),'Ambiguous archived names require review'
        seasons[season]={'season':season,'source':'Basketball Reference · saved archive','url':f'https://www.basketball-reference.com/leagues/NBA_{int(season[:4])+1}_per_game.html','captured_at':None,'through':None,'coverage':'Partial February snapshot; maximum GP 57, original capture time unavailable' if season=='2025-26' else 'Saved historical snapshot; capture date and completeness unverified','precision':'Rounded per-game inputs; FP/G and FG% / FT% recalculated from available makes and attempts. Exact totals and 3PA unavailable.','sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'rows':rows}
    evidence=ROOT/'private/nba_evidence'; snapshots={}; game_ids=defaultdict(set); totals=defaultdict(dict)
    for p in sorted(evidence.glob('game_*.json')):
        d=json.loads(p.read_text());header=d['header']; season=header['season']['year'];season=f'{int(season)-1}-{str(season)[-2:]}'
        if header['season'].get('type')!=2:continue
        gid=str(header['id']); date=datetime.fromisoformat(header['competitions'][0]['date'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat()
        game_ids[season].add(gid)
        snapshots[gid]={'url':'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event='+gid,'date':date,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for r in from_game(d):
            sid=r['source_player_id']; pid=identity.resolve(r['player_name'],'espn:'+sid)
            if pid not in totals[season]: totals[season][pid]={**r,'player_id':pid,'gp':0,'totals':{k:0 for k in FIELDS},'game_ids':[],'game_stats':[],'teams':set()}
            t=totals[season][pid]
            if gid in t['game_ids']:raise ValueError('Duplicate game/player')
            t['gp']+=1;t['game_ids'].append(gid);t['game_stats'].append({'game_id':gid,'date':date,'stats':r['totals']});t['teams'].add(r['nba_team'])
            for k in FIELDS:t['totals'][k]+=r['totals'][k]
    for s,players in totals.items():
        rows=[]
        for r in players.values():
            r['source_position']=r['position'];r['position']=identity.meta.get(r['player_id'],{}).get('position') or r['position'];r['nba_team']='/'.join(sorted(r.pop('teams')));r['totals']['fp']=fantasy(r['totals']);r['totals'].update(percentages(r['totals']))
            r['per_game']={k:(v if k.endswith('_pct') else v/r['gp']) if v is not None else None for k,v in r['totals'].items()};r['basis']='observed_box_scores';rows.append(r)
        meta_files=[p for p in evidence.glob('*attempts.json')]
        captures=[x.get('captured_at','') for p in meta_files for x in json.loads(p.read_text()) if x.get('id','').startswith('game_')]
        seasons[s]={'season':s,'source':'ESPN final NBA box scores','url':'https://www.espn.com/nba/scoreboard','captured_at':max(captures,default='') or None,'through':max(snapshots[g]['date'] for g in game_ids[s]),'coverage':f'{len(game_ids[s])} completed regular-season games collected. Players without an observed appearance are unknown; not zero.','precision':'Exact box-score counting totals; minutes as reported. YK points calculated from complete inputs; not fantasy lineup credits.','games':sorted(game_ids[s]),'rows':rows}
    full_baseline=ROOT/'source/context/fantrax_nba_2025.json'
    if full_baseline.exists():seasons['2025-26']=json.loads(full_baseline.read_text())
    bundle={'schema_version':1,'built_at':datetime.now(timezone.utc).isoformat(),'default_season':max(seasons),'weights':WEIGHTS,'seasons':seasons,'game_sources':snapshots,'season_status':{'season':'2026-27','opening_date':'2026-10-20','url':'https://pr.nba.com/2026-27-nba-regular-season-schedule','status':f'Regular season has begun; {len(game_ids["2026-27"])} final games collected.'}}
    checksum=hashlib.sha256(json.dumps(bundle,sort_keys=True).encode()).hexdigest();atomic_json(ROOT/'private/nba_snapshots'/(checksum+'.json'),bundle);atomic_json(ROOT/'docs/data/nba_stats.json',bundle)
    print({s:len(d['rows']) for s,d in seasons.items()})
if __name__=='__main__':build()
