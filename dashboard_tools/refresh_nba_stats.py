"""Refresh ESPN final NBA box scores (max seven dates, one request per endpoint).
Failed/incomplete refreshes retain the last successful public snapshot. No credentials.
"""
import argparse,json,hashlib
from datetime import date,datetime,timezone,timedelta
from pathlib import Path
import requests
from collection_state import atomic_json
from build_nba_stats import build,from_game,ROOT

def refresh(start,end):
    start=date.fromisoformat(start);end=date.fromisoformat(end)
    if not 0<=(end-start).days<7 or end>date.today():raise ValueError('Choose one to seven non-future dates')
    p=ROOT/'private/nba_evidence';attempts=[];failed=False;seen=set();pending={}
    for offset in range((end-start).days+1):
        day=start+timedelta(days=offset);u='https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates='+day.strftime('%Y%m%d')+'&limit=100'
        try:
            r=requests.get(u,timeout=20);r.raise_for_status();d=r.json()
            if 'events' not in d:raise ValueError('Missing events')
            pending['scoreboard_'+day.isoformat()+'.json']=d
            attempts.append({'id':'scoreboard_'+day.isoformat(),'url':u,'captured_at':datetime.now(timezone.utc).isoformat(),'status':'success'})
            for e in d['events']:
                if not e['status']['type']['completed'] or e.get('season',{}).get('type',2)!=2 or e['id'] in seen:continue
                seen.add(e['id']);gid=e['id'];u='https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event='+gid
                g=requests.get(u,timeout=20);g.raise_for_status();game=g.json()
                if str(game['header']['id'])!=gid or game['header']['season']['type']!=2 or not from_game(game):raise ValueError('Mismatched or empty completed game')
                pending['game_'+gid+'.json']=game;attempts.append({'id':'game_'+gid,'url':u,'captured_at':datetime.now(timezone.utc).isoformat(),'status':'success'})
        except Exception as e:
            failed=True;attempts.append({'id':str(day),'url':u,'status':'failed','error':type(e).__name__});break
    atomic_json(p/'refresh_attempts.json',attempts)
    if failed:raise RuntimeError('Refresh failed; last public snapshot retained. Inspect private attempt log.')
    for name,payload in pending.items():
        digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        atomic_json(ROOT/'private/nba_raw_snapshots'/(digest+'.json'),payload)
        atomic_json(p/name,payload)
    build()
    from build_dashboard import build as dashboard
    from collection_state import publish_snapshot
    publish_snapshot(ROOT/'docs/data/dashboard.json',dashboard(),ROOT/'private')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--start',required=True);p.add_argument('--end',required=True);a=p.parse_args();refresh(a.start,a.end)
