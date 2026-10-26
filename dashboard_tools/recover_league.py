"""Reconcile explicit CSV transfers and supplied trades without inferring pick outcomes."""
import json,csv,re,hashlib,shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from player_identity import ROOT,Identity,key
from collection_state import atomic_json
INPUT=ROOT.parent/'source_inputs/YK_Dynasty_History/Info' # Optional; normal builds use private/transaction_csv.
def build():
    from build_dashboard import build as core_build
    d=core_build(include_repairs=False); identity=Identity();owners={}; manifest=[]
    for o in d['teams']['owners']:
        for n in [o['real_name'],o['owner_id'],*o['aliases'],*[x['team_name'] for x in o['history']]]:owners[key(n)]=o['real_name']
    owners[key('Pure Sweat Farm')]=owners[key('Moss')];owners[key('Sands')]='Logan Berke'
    private=ROOT/'private/transaction_csv';private.mkdir(exist_ok=True)
    for p in INPUT.glob('Fantrax-Transaction-History-Trades-*.csv'):
        if not (private/p.name).exists():shutil.copy2(p,private/p.name)
    observations={}
    for p in sorted(private.glob('*.csv')):
        manifest.append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        for line,r in enumerate(csv.DictReader(p.open(encoding='utf-8-sig')),2):
            if not r.get('Player') or not r.get('Date (EST)'):continue
            dt=datetime.strptime(r['Date (EST)'],'%a %b %d, %Y, %I:%M%p');season=f'{dt.year if dt.month>=7 else dt.year-1}-{str(dt.year+1 if dt.month>=7 else dt.year)[-2:]}'
            pick=bool(re.search(r'draft pick|round|swap',r['Player'],re.I));from_owner=owners.get(key(r['From']));to_owner=owners.get(key(r['To']))
            pid=None if pick else identity.resolve(r['Player'])
            uid=hashlib.sha256('|'.join([pid or key(r['Player']),from_owner or key(r['From']),to_owner or key(r['To']),dt.isoformat()]).encode()).hexdigest()[:16]
            evidence={'source':p.name,'row':line}
            if uid in observations:
                observations[uid]['source_evidence'].append(evidence);continue
            observations[uid]={'id':'csv-'+uid,'player_id':pid,'player_name':r['Player'],'type':'pick' if pick else 'player','sender':from_owner,'recipient':to_owner,'from_team':r['From'],'to_team':r['To'],'date':dt.isoformat(timespec='minutes'),'timezone':'America/New_York','season':season,'source':p.name,'source_row':line,'source_evidence':[evidence],'period_label':r.get('Period'),'kind':'exported_transfer'}
    groups=defaultdict(list)
    for r in observations.values():groups[(r['date'],tuple(sorted(filter(None,[r['sender'],r['recipient']]))))].append(r)
    events=[];reconciled=[]
    def fingerprint(assets):return sorted(a['player_id'] for a in assets if a.get('player_id'))
    for (dt,parties),rows in groups.items():
        season=rows[0]['season'];assets=[{'raw':r['player_name'],'label':r['player_name'],'player_id':r['player_id'],'type':r['type'],'sender':r['sender'],'recipient':r['recipient'],'side':'give','source':r['source'],'source_row':r['source_row']} for r in rows]
        candidates=[t for t in d['trades']['trade_events'] if t['year']==season and sorted(t['parties'])==list(parties) and fingerprint(t['assets'])==fingerprint(assets) and fingerprint(assets)]
        if candidates and (len(candidates)==1 or all(t['date_iso']==dt[:10] for t in candidates)):
            reconciled.append({'event_id':candidates[0]['event_id'],'duplicate_event_ids':[t['event_id'] for t in candidates[1:]],'date':dt,'observations':[r['id'] for r in rows],'basis':'Exact player set and party pair; pick descriptions retained independently'})
        else:
            events.append({'event_id':'csv-event-'+rows[0]['id'][4:],'source_index':None,'year':season,'date_iso':dt[:10],'parties':list(parties),'assets':assets,'route_status':'explicit_csv_routes','trade_type_label':'Players + picks' if any(a['type']=='pick' for a in assets) else 'Players','source':'Fantrax CSV transfers grouped by timestamp and pair; transaction ID unavailable','fantrax_confirmed':True})
    from trade_registry import assign
    workbook_ids=assign('workbook',d['context']['recent_trades'],'workbook-2026-')
    for i,t in enumerate(d['context']['recent_trades']):
        assets=[];sides=[]
        for side in ['give','get']:
            own=set()
            for text in t[side]:
                prefix,_,label=text.partition(' ');who=owners.get(key(prefix));pick=bool(re.search(r'20\d\d|round|swap',label,re.I));pid=None if pick else identity.resolve(label)
                assets.append({'raw':text,'label':label,'player_id':pid,'type':'pick' if pick else 'player','sender':who,'recipient':None,'side':side});
                if who:own.add(who)
            sides.append(own)
        parties=sorted(set.union(*sides));clear=len(parties)==2 and all(len(s)==1 for s in sides) and not sides[0]&sides[1] and all(a['sender'] for a in assets)
        if clear:
            for a in assets:a['recipient']=next(o for o in parties if o!=a['sender'])
        events.append({'event_id':workbook_ids[i],'source_index':i,'year':'2026-27','date_iso':t['date'],'parties':parties,'assets':assets,'route_status':'two_party_record' if clear else 'recipient_unresolved','trade_type_label':'Players + picks' if any(a['type']=='pick' for a in assets) else 'Players','source':'YK Dynasty Basketball.xlsx · '+t['sheet']+' '+t['source_range'],'fantrax_confirmed':False})
    schedules={}
    for p in sorted((ROOT/'private/saved').glob('*/getLeagueInfo.json'))+sorted((ROOT/'private/target/runs').glob('*/getLeagueInfo.json')):
        info=json.loads(p.read_text());s=f"{info['seasonYear']}-{str(info['seasonYear']+1)[-2:]}";rows=[]
        for period in info.get('matchups',[]):
            for match in period['matchupList']:
                if not all(match.get(side,{}).get('name') for side in ['away','home']):continue
                rows.append({'period':period['period'],'away_team':match['away']['name'],'home_team':match['home']['name'],'away_owner':owners.get(key(match['away']['name'])),'home_owner':owners.get(key(match['home']['name'])),'away_score':None,'home_score':None,'status':'schedule_only'})
        schedules[s]=rows
    result={'observations':list(observations.values()),'additional_events':events,'reconciled':reconciled,'schedules':schedules,'sources':manifest}
    atomic_json(ROOT/'source/context/recovered_league.json',result)
    print('Transfers',len(observations),'matched event groups',len(reconciled),'additional groups/workbook events',len(events),'scheduled periods',{s:len(set(x['period'] for x in rows)) for s,rows in schedules.items()})
if __name__=='__main__':build()
