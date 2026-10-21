"""Offline import of read-only Fantrax UI captures; never reads browser credentials.

Capture files are private. Only validated basketball fields enter public bundles.
"""
import json,re,hashlib,csv
from datetime import datetime
from collections import defaultdict
from workspace import ROOT
from collection_state import atomic_json
from player_identity import Identity,key
P=ROOT/'private/fantrax_browser'
def read(p):return json.loads(p.read_text())
def number(x):return None if x.strip() in ('','-') else float(x.replace(',','').strip())
def player_id(row,identity):
    match=re.search(r'/hs([a-z0-9]+)_',row.get('image') or '')
    return 'nba:'+match[1] if match else identity.resolve(row['name'])
def stat_rows(kind):
    files=sorted(P.glob(kind+'-[123].json'))
    if len(files)!=3:raise ValueError('Need all three captured player pages: '+kind)
    rows=[r for p in files for r in read(p)['rows']]
    if len(rows)!=1287 or len({(r['name'],r.get('image')) for r in rows})!=1287:raise ValueError('Missing or duplicated player pages')
    return files,rows
def nba_snapshot(identity):
    from build_nba_stats import fantasy,percentages
    files,raw=stat_rows('nba-2025-26-totals');rows=[]
    minutes={player_id(r,identity):number(r['cells'][9]) for p in P.glob('nba-2025-26-standard-*.json') for r in read(p)['rows'] if len(r['cells'])==23}
    for r in raw:
        c=r['cells'];assert len(c)==20
        gp=number(c[8])
        if not gp:continue
        totals=dict(zip(['fgm','fga','fg3m','ftm','fta','pts','reb','ast','stl','blk','tov'],map(number,c[9:])))
        totals['fp']=fantasy(totals)
        if totals['fp']!=number(c[4]):raise ValueError('Fantrax total points mismatch: '+r['name'])
        if totals['pts']!=2*totals['fgm']+totals['fg3m']+totals['ftm']:raise ValueError('Shooting reconciliation: '+r['name'])
        totals.update(min=None,fg3a=None);totals.update(percentages(totals));pid=player_id(r,identity)
        per={k:(v if k.endswith('_pct') else v/gp) if v is not None else None for k,v in totals.items()};per['min']=minutes.get(pid)
        # The NBA team shown in this UI is current, not the team(s) that produced last season's totals.
        rows.append({'player_id':pid,'player_name':r['name'],'position':r['position'].split('\n')[0].replace(',','/'),'nba_team':'','source_player_id':pid.removeprefix('nba:') if pid.startswith('nba:') else None,'gp':int(gp),'totals':totals,'per_game':per,'basis':'fantrax_season_totals'})
    if len({r['player_id'] for r in rows})!=len(rows):raise ValueError('Duplicate Fantrax identity')
    return {'season':'2025-26','source':'Fantrax · NBA regular-season totals','url':read(files[0])['url'],'captured_at':max(read(p)['captured_at'] for p in files),'through':None,'coverage':f'{len(rows)} players with GP > 0 from all 1,287 listed players. Completed 2025–26 regular-season YTD view; no roster filter.','precision':'Exact displayed counting totals; YK points reconciled to Fantrax. Minutes are rounded per game where available. 3PA and 3P% unavailable. Current NBA affiliations are not backdated.','rows':rows,'sha256':hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest()}
def projections(identity):
    from build_nba_stats import fantasy
    from ranking_import import promote
    files,raw=stat_rows('nba-2026-27-projected-season');rows=[]
    for r in raw:
        c=r['cells'];gp=number(c[8])
        if not gp:continue
        total=dict(zip(['fgm','fga','fg3m','ftm','fta','pts','reb','ast','stl','blk','tov'],map(number,c[9:])))
        per={k:v/gp for k,v in total.items()};fp=fantasy(per)
        # Displayed one-decimal projected totals introduce small rounding differences.
        if abs(fantasy(total)-number(c[4]))>1:raise ValueError('Projection formula mismatch: '+r['name'])
        rows.append({'player_id':player_id(r,identity),'player_name':r['name'],'position':r['position'].split('\n')[0].replace(',','/'),'source_original_rank':int(number(c[0])),'projection_inputs':per,'projected_fp_pg':fp,'identity_status':'fantrax_ui_identity'})
    rows.sort(key=lambda r:-r['projected_fp_pg'])
    for r in rows:r['original_rank']=1+sum(x['projected_fp_pg']>r['projected_fp_pg'] for x in rows)
    promote({'id':'fantrax_yk_model','label':'YK scoring · Fantrax full-season projected FP/G','publisher':'fantrax','url':read(files[0])['url'],'published_at':max(read(p)['captured_at'][:10] for p in files),'publication_precision':'capture_only','season':'2026-27','scoring_format':'yk_projection','horizon':'full_season','rank_scope':'overall','coverage':'derived_full_accessible_projection_pool','notes':'574 positive-GP projections from all 1,287 listed players. Publication date is not supplied: displayed date is capture date. Ranked by YK projected points per game from complete rounded shooting/counting inputs; source original rank is Fantrax season-total order. Full-season forecast, not rest-of-season. Single model, isolated from expert consensus. Zero-GP projection rows are unknown, not ranked zero.','points_weights':{'PTS':1,'REB':1,'AST':2,'STL':4,'BLK':4,'FGM':2,'FGA':-1,'FTM':1,'FTA':-1,'3PM':1,'TO':-2},'raw_sha256':hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest(),'rows':rows})
def build():
    from build_dashboard import build as core_build
    d=core_build(include_repairs=False);identity=Identity();owners={}
    for o in d['teams']['owners']:
        for name in [o['real_name'],*o['aliases'],*[h['team_name'] for h in o['history']]]:owners[key(name)]=o['real_name']
    def owner(name):
        result=owners.get(key(name))
        if not result:raise ValueError('Unmapped team: '+name)
        return result
    results={};standings={};sources=[];live=[]
    for p in sorted(P.glob('*-results-blocks.json')):
        raw=read(p);season=raw['season'];period=None;date_label=None;rows=[]
        for b in raw['blocks']:
            if b['tag']=='H4' and re.fullmatch(r'Scoring Period \d+',b['text']):period=int(b['text'].split()[-1])
            elif b['tag']=='H5' and period:date_label=b['text']
            elif b['tag']=='TABLE' and period:
                for r in b['rows']:
                    if len(r)!=4 or not r[0]['links'] or not r[2]['links']:continue
                    a,h=owner(r[0]['text']),owner(r[2]['text']);av,hv=number(r[1]['text']),number(r[3]['text'])
                    if av is None or hv is None:raise ValueError('Missing result')
                    rows.append({'period':period,'away_team':r[0]['text'],'home_team':r[2]['text'],'away_owner':a,'home_owner':h,'away_score':av,'home_score':hv,'winner':a if av>hv else h if hv>av else None,'status':'completed','date_label':date_label})
        periods=sorted({r['period'] for r in rows})
        if periods!=list(range(1,max(periods)+1)) or len(rows)!=5*len(periods):raise ValueError('Incomplete result grid')
        results[season]={'matchups':rows,'periods_available':periods,'source':raw['url'],'captured_at':raw['captured_at'],'complete_regular_season':True,'note':'All displayed completed regular-season results; excludes playoff rounds.'}
    for p in sorted(P.glob('*-regular-blocks.json')):
        raw=read(p);season=raw['season'];blocks=raw['blocks'];names=next(b['text'].splitlines() for b in blocks if b['tag']=='ASIDE' and b['text'].startswith('1\n'));table=next(b['rows'] for b in blocks if b['tag']=='TABLE');rows=[]
        assert len(names)==20 and len(table)==10
        for i,r in enumerate(table):
            c=[x['text'] for x in r];offset=1 if season in ('2022-23','2023-24') else 0 # Verified WW column precedes FPtsF in these two seasons.
            rows.append({'season':season,'owner_real_name':owner(names[2*i+1]),'team_name':names[2*i+1],'rank':int(names[2*i]),'w':number(c[0]),'l':number(c[1]),'t':number(c[2]),'win_pct':number(c[3]),'pts':number(c[5+offset]),'points_against':number(c[6+offset]),'status':'in_progress' if season=='2026-27' else 'completed_regular_season'})
        if season in results:
            for r in rows:
                games=[m for m in results[season]['matchups'] if r['owner_real_name'] in (m['away_owner'],m['home_owner'])]
                pts=sum(m['away_score'] if m['away_owner']==r['owner_real_name'] else m['home_score'] for m in games)
                against=sum(m['home_score'] if m['away_owner']==r['owner_real_name'] else m['away_score'] for m in games)
                wins=sum(m['winner']==r['owner_real_name'] for m in games)
                if pts!=r['pts'] or against!=r['points_against'] or wins!=r['w'] or len(games)!=r['w']+r['l']+r['t']:raise ValueError('Weekly/YTD reconciliation failed: '+season+' '+r['team_name'])
        standings[season]={'rows':rows,'captured_at':raw['captured_at'],'source':raw['url']}
        if season=='2026-27':
            for b in blocks:
                if b['tag']=='TABLE':
                    for r in b['rows']:
                        if len(r)==4 and r[0]['links'] and r[2]['links']:live.append({'period':1,'away_team':r[0]['text'],'home_team':r[2]['text'],'away_owner':owner(r[0]['text']),'home_owner':owner(r[2]['text']),'away_score':number(r[1]['text']),'home_score':number(r[3]['text']),'status':'in_progress'})
    # Explicit player-transfer rows only. A processing timestamp is not assumed to be the negotiated deal date.
    transfers=[]
    for p in sorted(P.glob('*-trades-dom.json')):
        raw=read(p);rows=raw['tables'][0];assert len(rows)==len(raw['players']);stamp=None;remaining=0
        for i,(r,pl) in enumerate(zip(rows,raw['players'])):
            if len(r)==5:
                stamp=r[2]['text'].strip();remaining=int(r[2]['rowspan'] or 1)
            if not remaining or not stamp:raise ValueError('Unresolved merged transfer date')
            remaining-=1
            transfers.append({'Player':pl['name'],'From':r[0]['text'],'To':r[1]['text'],'Date (EST)':stamp,'Period':r[-2]['text'] if len(r)==5 else r[2]['text']})
    out=ROOT/'private/transaction_csv/Fantrax-browser-executed-trades.csv'
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Player','From','To','Date (EST)','Period']);w.writeheader();w.writerows(transfers)
    for p in sorted([*P.glob('*.json'),*P.glob('*.txt')]):sources.append({'path':'private/fantrax_browser/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    payload={'results':results,'standings':standings,'current_matchups':live,'sources':sources,'verified_rules':{'url':'https://www.fantrax.com/fantasy/league/noz9r7uxmphcb74p/rules','checked_at':'2026-10-21','ir_max':4,'minors_max':2,'center_max':5,'main_max':20,'active_max':10,'reserve_max':10,'gp_min':35,'gp_max':55,'gp_enforcement':'Do nothing for either limit; prorated by period length','minors_eligibility':'Any player may occupy a Minors slot under configured rules','standings_tiebreakers':['Season fantasy points for','Head-to-head record among tied teams','Fewest season fantasy points against','Random selection']},'transfer_rows':len(transfers)}
    atomic_json(ROOT/'source/context/fantrax_browser.json',payload)
    atomic_json(ROOT/'source/context/fantrax_nba_2025.json',nba_snapshot(identity));projections(identity)
    print('Authenticated UI import:',{s:len(v['matchups']) for s,v in results.items()},'transfer rows',len(transfers))
if __name__=='__main__':build()
