"""Versioned trade evidence. Archived judgments never become repaired model inputs."""
import copy,json,math,re
from collections import Counter
from workspace import ROOT
from collection_state import atomic_json
from trade_registry import digest,bootstrap_ids
from build_nba_stats import WEIGHTS
from player_identity import key

GPA={'A+':4.3,'A':4,'B':3,'C':2,'D':1,'F':0}
METHODS={
 'historical':{'version':1,'label':'Historical grade','description':'Original February 2026 archive. Includes missing-data penalties and inferred pick values; not a repaired result.','publication_date':None,'source_snapshot_date':'2026-02-21'},
 'improvement':{'version':1,'label':'Player improvement','minimum_gp':10,'description':'Sum of received players’ following-season minus trade-season YK FP/G. Complete comparable counting totals required. Package size affects the result. Picks excluded; not market value or predicted wins.','thresholds':[[8,'A+'],[4,'A'],[1,'B'],[-1,'C'],[-4,'D']],'gpa':GPA,'comparison_gap':0.5},
 'observed':{'version':1,'label':'Observed production','description':'Final NBA games collected strictly after the deal, through the selected season cutoff. Same-day games excluded. Not fantasy lineup credits or verified tenure.'}}

def points(stats):
    if not stats or not all(type(stats.get(k)) in (int,float) and math.isfinite(stats[k]) for k in WEIGHTS):return None
    return round(sum(stats[k]*w for k,w in WEIGHTS.items()),4)

def grade(delta):
    return next((letter for bound,letter in METHODS['improvement']['thresholds'] if delta>=bound),'F')

def next_season(s):
    if not re.fullmatch(r'20\d\d-\d\d',s) or (int(s[:4])+1)%100!=int(s[5:]):raise ValueError('Invalid season')
    return f'{int(s[:4])+1}-{(int(s[5:])+1)%100:02d}'

def canonical_dashboard(d):
    c=copy.deepcopy(d);c.pop('trade_evaluations',None)
    # Capture dates are preserved. This field is only the offline build invocation.
    c.get('nba_stats',{}).pop('built_at',None)
    return digest(c)

def names(values):
    return sorted(key(re.sub(r'^(?:(?:PG|SG|SF|PF|C|G|F)(?:/(?:PG|SG|SF|PF|C|G|F))*\s+)','',v)) for v in values)

def completed(snapshot,proof):
    return bool(proof and proof.get('complete_regular_season') is True and
                proof.get('snapshot_sha256')==digest(snapshot) and proof.get('evidence'))

def improvement(event,owner,seasons,proofs):
    pre=event['year'];post=next_season(pre)
    incoming=[a for a in event['assets'] if a.get('recipient')==owner]
    players=[a for a in incoming if a['type']=='player'];picks=[a for a in incoming if a['type']=='pick']
    reasons=[];rows=[];indexes={s:{r['player_id']:r for r in seasons.get(s,{}).get('rows',[])} for s in [pre,post]}
    if not all(a.get('sender') and a.get('recipient') for a in event['assets']):reasons.append('Asset recipients are unresolved')
    if not players:reasons.append('No resolved incoming players')
    if len({a.get('player_id') for a in players})!=len(players):reasons.append('Duplicate player assets need review')
    for s in [pre,post]:
        if not completed(seasons.get(s,{}),proofs.get(s)):reasons.append(s+' complete counting totals are not verified')
    for a in players:
        pid=a.get('player_id');before=indexes[pre].get(pid);after=indexes[post].get(pid);why=[]
        if not pid or not pid.startswith('nba:'):why.append('Player identity unresolved')
        vals=[]
        for s,r in [(pre,before),(post,after)]:
            fp=points((r or {}).get('totals'));gp=(r or {}).get('gp')
            if fp is None:why.append(s+' complete scoring inputs unavailable')
            if type(gp) not in (int,float) or gp<METHODS['improvement']['minimum_gp']:why.append(s+' fewer than 10 verified games')
            vals.append(fp/gp if fp is not None and gp and gp>0 else None)
        delta=round(vals[1]-vals[0],4) if not why else None
        rows.append({'player_id':pid,'label':a['label'],'pre_fpg':vals[0],'post_fpg':vals[1],'gp_pre':(before or {}).get('gp'),'gp_post':(after or {}).get('gp'),'delta':delta,'reasons':why})
    if any(r['reasons'] for r in rows):reasons.append('Some received players lack eligible evidence')
    eligible=bool(rows) and not reasons
    delta=round(sum(r['delta'] for r in rows),4) if eligible else None
    letter=grade(delta) if eligible else None
    operators={a.get('recorded_operator') for a in event['assets'] if a.get('sender')==owner and a.get('recorded_operator')}
    return {'franchise':owner,'recorded_operator':next(iter(operators)) if len(operators)==1 else None,
            'method_id':'improvement','method_version':1,'status':'eligible' if eligible else 'incomplete','grade':letter,'gpa':GPA.get(letter),
            'pre_season':pre,'post_season':post,'score':delta,'mean_delta':round(delta/len(rows),4) if eligible else None,
            'players':rows,'included_count':len(rows),'covered_count':sum(not r['reasons'] for r in rows),'excluded_picks':[a['label'] for a in picks],
            'reasons':reasons,'scope':'players_only'}

def verdict(event,sides):
    eligible=len(sides)==2 and len(event['parties'])==2 and all(s['status']=='eligible' for s in sides) and all(a['type']=='player' for a in event['assets'])
    if not eligible:return {'status':'ineligible','favored':None,'gap':None,'label':'Whole-package comparison unavailable'}
    gap=abs(sides[0]['gpa']-sides[1]['gpa']);winner=max(sides,key=lambda s:s['gpa'])['franchise'] if gap>0.5 else None
    return {'status':'eligible','favored':winner,'gap':round(gap,4),'label':'Favored by player-improvement model' if winner else 'Even by player-improvement model'}

def observed(event,snapshot):
    byid={r['player_id']:r for r in snapshot.get('rows',[])};rows=[]
    for a in event['assets']:
        if a['type']!='player':continue
        r=byid.get(a.get('player_id'),{});games=[g for g in r.get('game_stats',[]) if event.get('date_iso') and event['date_iso']<g['date']<=snapshot.get('through','')]
        if len({g['game_id'] for g in games})!=len(games):raise ValueError('Duplicate observed player game')
        vals=[points(g['stats']) for g in games];fp=round(sum(vals),4) if vals and all(v is not None for v in vals) else None
        rows.append({'player_id':a.get('player_id'),'label':a['label'],'recipient':a.get('recipient'),'games':len(games) if fp is not None else None,'points':fp,
                     'reason':None if fp is not None else ('Trade date unavailable' if not event.get('date_iso') else 'No complete collected games after deal')})
    return {'method_id':'observed','method_version':1,'season':snapshot['season'],'through':snapshot.get('through'),'source_url':snapshot.get('url'),
            'captured_at':snapshot.get('captured_at'),'coverage':'Partial collected window','rows':rows,
            'sides':[{'franchise':o,'players':len(rs),'covered':sum(r['points'] is not None for r in rs),'points':round(sum(r['points'] for r in rs if r['points'] is not None),4) if any(r['points'] is not None for r in rs) else None} for o in event['parties'] for rs in [[r for r in rows if r['recipient']==o]]]}

def archive_links(d,archive,registry):
    owners={key(v):o['real_name'] for o in d['teams']['owners'] for v in [o['real_name'],o['owner_id'],*o['aliases']]}
    events={e['event_id']:e for e in d['trades']['trade_events']};aliases={alias:e['event_id'] for e in events.values() for alias in e.get('duplicate_source_entries',[])}
    ids=registry['collections']['legacy']['bootstrap_ids'];out=[]
    for i,t in enumerate(archive['trades']):
        idx=t['trade_index'];candidate=ids[idx] if isinstance(idx,int) and 0<=idx<len(ids) else None
        canonical=aliases.get(candidate,candidate);e=events.get(canonical);why=[]
        if not e:why.append('No canonical event for pinned source row')
        elif e['year']!=t['season'] or names([a['label'] for a in e['assets']])!=names([a for k in ['side_a','side_b'] for a in t.get(k,{}).get('gave',[])]):why.append('Source asset set or season differs')
        sides=[]
        for k in ['side_a','side_b']:
            raw=t.get(k)
            if not raw:continue
            franchise=owners.get(key(raw.get('owner','')))
            route_ok=bool(e and franchise and all(a.get('recipient') for a in e['assets']) and
                 names(raw.get('received',[]))==names([a['label'] for a in e['assets'] if a.get('recipient')==franchise]) and
                 names(raw.get('gave',[]))==names([a['label'] for a in e['assets'] if a.get('sender')==franchise]))
            player_links={}
            for name in raw.get('received',[])+raw.get('gave',[]):
                matches=[a['player_id'] for a in (e or {}).get('assets',[]) if a.get('player_id') and names([a['label']])==names([name])]
                if len(set(matches))==1:player_links[name]=matches[0]
            sides.append({'archive_side':k,'franchise':franchise,'recorded_operator':raw.get('owner'),'route_verified':route_ok,'player_links':player_links,
                          'grade':raw.get('combined_grade',raw.get('grade')),'gpa':raw.get('combined_gpa'),'original':raw})
        status='unmatched' if why else 'duplicate_alias' if candidate in aliases else 'linked'
        out.append({'archive_id':'archive-'+str(i),'source_index':idx,'candidate_event_id':candidate,'event_id':canonical if not why else None,
                    'status':status,'season':t['season'],'source_date':t.get('date'),'date_conflict':bool(e and t.get('date') and e.get('date_iso')!=t['date']),
                    'route_status':'verified' if sides and all(s['route_verified'] for s in sides) else 'unresolved','reasons':why,'sides':sides,
                    'method_id':'historical','method_version':1,'source':'docs/data/legacy/trade_grades.json'})
    return out

def build(d, root=ROOT):
    archive=json.loads((root/'docs/data/legacy/trade_grades.json').read_text())
    registry_path=root/'source/context/trade_event_registry.json';registry=json.loads(registry_path.read_text())
    # Pin the historical archive edition so replacement files cannot reuse positional joins.
    pinned=registry.setdefault('archive_grade_sha256',digest(archive))
    if pinned!=digest(archive):raise ValueError('New archive grade edition needs reviewed mapping')
    atomic_json(registry_path,registry)
    proofs_path=root/'source/context/trade_stat_completeness.json'
    proofs=json.loads(proofs_path.read_text()) if proofs_path.exists() else {}
    seasons=d['nba_stats']['seasons'];links=archive_links(d,archive,registry);events=[]
    for e in d['trades']['trade_events']:
        sides=[improvement(e,o,seasons,proofs) for o in e['parties']]
        events.append({'event_id':e['event_id'],'season':e['year'],'date':e['date_iso'],'parties':e['parties'],'type':e['trade_type_label'],
                       'search':' '.join([*e['parties'],*[a['label'] for a in e['assets']]]),'archive_ids':[a['archive_id'] for a in links if a['event_id']==e['event_id']],
                       'improvement':{'method_id':'improvement','method_version':1,'sides':sides,'verdict':verdict(e,sides)},
                       'observed':{s:observed(e,snap) for s,snap in seasons.items() if snap.get('games')}})
    # Legacy pick chains are associations, not verified final outcomes. Preserve source labels.
    rawpicks=json.loads((root/'source/yk/docs/data/pick_ledger.json').read_text())['picks'];alias={a:e['event_id'] for e in d['trades']['trade_events'] for a in e.get('duplicate_source_entries',[])}
    ids=registry['collections']['legacy']['bootstrap_ids'];valid={e['event_id'] for e in events};paths=[]
    for p in d['picks']['ledger']:
        source=rawpicks.get(p['pick_id'],{});steps=[]
        for step in source.get('trades',[]):
            idx=step['trade_index'];eid=ids[idx] if 0<=idx<len(ids) else None;eid=alias.get(eid,eid)
            steps.append({'event_id':eid if eid in valid else None,'season':step.get('season'),'from_label':step.get('from'),'to_label':step.get('to'),'raw':step.get('raw'),'basis':'Archived pick association; protection and original-pick lineage unverified'})
        paths.append({**p,'transfers':steps,'selected_player':None,'grade':None})
    out={'schema_version':1,'dashboard_sha256':canonical_dashboard(d),'methods':METHODS,'formula':WEIGHTS,'formula_version':'yk-points-v1',
         'source_hashes':{'archive':digest(archive),'registry':digest(registry),'nba':digest(seasons),'completeness':digest(proofs)},
         'source_capture':d['target']['checked_at'],'archive':links,'events':events,'pick_paths':paths,
         'audit':{'archive_records':len(links),'archive_status':dict(Counter(x['status'] for x in links)),'route_unresolved':sum(x['route_status']!='verified' for x in links),
                  'canonical_events':len(events),'eligible_sides':sum(s['status']=='eligible' for e in events for s in e['improvement']['sides']),
                  'eligible_comparisons':sum(e['improvement']['verdict']['status']=='eligible' for e in events)}}
    validate(out,d);return out

def validate(bundle,d):
    def public_only(value):
        if isinstance(value,dict):
            if any(k.lower() in {'cookie','cookies','authorization','password','email','jsessionid','fx_rm'} for k in value):raise ValueError('Sensitive field in evaluation bundle')
            for v in value.values():public_only(v)
        elif isinstance(value,list):
            for v in value:public_only(v)
    public_only(bundle)
    if bundle['dashboard_sha256']!=canonical_dashboard(d):raise ValueError('Evaluation/dashboard mismatch')
    ids=[e['event_id'] for e in bundle['events']]
    if len(set(ids))!=len(ids) or set(ids)!={e['event_id'] for e in d['trades']['trade_events']}:raise ValueError('Event coverage mismatch')
    if sum(bundle['audit']['archive_status'].values())!=len(bundle['archive']):raise ValueError('Archive audit mismatch')
    for e in bundle['events']:
        for s in e['improvement']['sides']:
            if s['status']=='eligible':
                if s['grade'] not in GPA or s['gpa']!=GPA[s['grade']] or s['reasons']:raise ValueError('Invalid eligible side')
            elif s['grade'] is not None or s['gpa'] is not None:raise ValueError('Incomplete side has grade')
    if any(p['selected_player'] or p['grade'] or p['status']!='outcome_unresolved' for p in bundle['pick_paths']):raise ValueError('Unsupported pick outcome')
