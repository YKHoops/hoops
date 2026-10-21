"""Extract only names, original ranks and positions from cached public/supplied evidence."""
from pathlib import Path
from collections import defaultdict
import hashlib, json, re, html
import openpyxl
from ranking_import import ROOT, promote, bundle
from build_dashboard import CURRENT, normal
from fetch_ranking_evidence import URLS
P=ROOT/'private/ranking_evidence'
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',s))).strip()
def table_rows(key):
    raw=(P/(key+'.html')).read_text()
    table=re.findall(r'<table\b.*?</table>',raw,re.S)[0]
    return [[clean(c) for c in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',r,re.S)] for r in re.findall(r'<tr\b.*?</tr>',table,re.S)]
D=json.loads((ROOT/'docs/data/dashboard.json').read_text())
directory=json.loads((CURRENT/'getPlayerIds.json').read_text());names=defaultdict(set)
for pid,p in directory.items():
    n=p['name'];n=' '.join(reversed(n.split(', ',1))) if ', ' in n else n
    names[normal(n)].add('nba:'+pid)
# Saved IDs anchor duplicate directory names; no suffix stripping or fuzzy matches.
for p in D['journeys']['player_index'].values():
    if p['identity_status']=='fantrax':names[normal(p['player_name'])]={p['player_id']}
ALIASES={'Nic Claxton':'Nicolas Claxton','Cam Johnson':'Cameron Johnson','Robert Williams':'Robert Williams III','Jaren Jackson':'Jaren Jackson Jr.','Gary Trent':'Gary Trent Jr.','Michael Porter':'Michael Porter Jr.','GG Jackson':'GG Jackson II','Ron Holland':'Ronald Holland II','Alex Sarr':'Alexandre Sarr','Carlton Carrington':'Bub Carrington','A.J. Dybantsa':'AJ Dybantsa','Cameron Boozer':'Cameron Boozer'}
# Explicit suffix variants reviewed against the cached Fantrax directory above, not a general suffix rule.
for full in ['Trey Murphy III','Jaren Jackson Jr.','Michael Porter Jr.','Jabari Smith Jr.','Dereck Lively II','Kevin Porter Jr.','Jimmy Butler III','Walter Clayton Jr.','Wendell Carter Jr.','Jaime Jaquez Jr.','Scotty Pippen Jr.','Robert Williams III','Derrick Jones Jr.','Bobby Portis Jr.','Craig Porter Jr.','Vince Williams Jr.','Bruce Brown Jr.','DaRon Holmes II','Gary Trent Jr.','Terrence Shannon Jr.','Tim Hardaway Jr.','Marvin Bagley III','Xavier Tillman Sr.','Larry Nance Jr.','Andre Jackson Jr.','Lindy Waters III','Nick Smith Jr.','TyTy Washington Jr.','Wendell Moore Jr.','Kevin McCullar Jr.','Tolu Smith III','Ron Harper Jr.','Mikel Brown Jr.','Darius Acuff Jr.','Morez Johnson Jr.','Chris Cenac Jr.','Tarris Reed Jr.','Labaron Philon Jr.','Jaron Pierre Jr.','Kenyon Martin Jr.']:
    ALIASES[full]=full.rsplit(' ',1)[0]
ALIASES.update({'Alexandre Sarr':'Alex Sarr','Alex Sarr':'Alex Sarr','Ronald Holland II':'Ron Holland','Ron Holland II':'Ron Holland','Ron Holland':'Ron Holland','GG Jackson II':'GG Jackson','GG Jackson':'GG Jackson','Cam Thomas':'Cameron Thomas','Herb Jones':'Herbert Jones','Kon Knueppel II':'Kon Knueppel','Ayo Dosumnu':'Ayo Dosunmu','Terrance Shannon Jr.':'Terrence Shannon','Quentin Post':'Quinten Post','Bogoljbub Markovic':'Bogoljub Markovic','Svi Mykhailuk':'Svi Mykhailiuk'})
# Two Jaylin Williams directory records; OKC NBA team disambiguates this list entry.
names[normal('Jaylin Williams')]={'nba:0621x'}
def row(rank,name,pos):
    key=normal(ALIASES.get(name,name));ids=names.get(key,set());pid=next(iter(ids)) if len(ids)==1 else 'unmatched:'+normal(name)
    return {'player_id':pid,'player_name':name,'position':pos,'original_rank':int(rank),
            'identity_status':'fantrax_exact_or_audited_alias' if len(ids)==1 else 'unresolved'}
def source(key,label,publisher,published,horizon,rows,format='nine_category',notes='Overall list; original ranks retained.',coverage='complete_published_list',season='2026-27',url=None,rawfile=None):
    rawfile=rawfile or P/(key+'.html')
    s={'id':key,'label':label,'publisher':publisher,'url':url or URLS[key],'published_at':published,'season':season,
       'scoring_format':format,'horizon':horizon,'rank_scope':'overall','coverage':coverage,'notes':notes,
       'raw_sha256':hashlib.sha256(rawfile.read_bytes()).hexdigest(),'rows':rows}
    if format=='yk_points':s['points_weights']={'PTS':1,'REB':1,'AST':2,'STL':4,'BLK':4,'FGM':2,'FGA':-1,'FTM':1,'FTA':-1,'3PM':1,'TO':-2}
    promote(s);print(key,len(rows),'unresolved',sum(r['identity_status']=='unresolved' for r in rows))

def build():
    raw=(P/'hashtag_dynasty.html').read_text()
    rows=[]
    for card in raw.split('<div class="card dyn-card">')[1:]:
        rank=re.search(r'class="dyn-rank">(\d+)',card)[1]
        name=clean(re.search(r'class="dyn-name">(.*?)</div>',card,re.S)[1])
        pos=clean(re.search(r'class="badge badge-light-secondary">(.*?)</span>',card,re.S)[1])
        rows.append(row(rank,name,pos))
    assert len(rows)==400
    rows=[r for r in rows if not r['player_name'].startswith('2027 Draft (')]
    source('hashtag_dynasty','Hashtag Basketball','hashtag','2026-09-24','dynasty',rows,notes='Category dynasty overall list; keeper ranks excluded. Not the YK points formula. Eight generic pick tiers excluded; original rank gaps preserved.')
    w=openpyxl.load_workbook(P/'dizzle.xlsx',read_only=True,data_only=True)
    rows=[row(r[0],r[1],r[2]) for r in w['October 2026 Dynasty Ranks, 9Ca'].values if isinstance(r[0],(int,float)) and r[1]]
    assert len(rows)==450
    source('dizzle','Dizzle Dynasty','dizzle','2026-10-13','dynasty',rows,notes='October 2026 9Cat tab only. RotoBaller republication is the same publisher. Points and rookie tabs excluded.',rawfile=P/'dizzle.xlsx')
    rows=[row(r[0],r[3],r[5]) for r in table_rows('ninecat') if len(r)>6 and r[0].isdigit()]
    assert len(rows)==200
    source('ninecat','9cat.app','ninecat','2026-10-14','full_season',rows,notes='2026-27 projections, all nine categories, per-game overall rank. No punts; published top 200.',coverage='published_top_200')
    rows=[row(r[0],r[2],r[1]) for r in table_rows('nbc_categories') if len(r)==4 and r[0].isdigit()]
    assert len(rows)==200
    source('nbc_categories','NBC / Rotoworld','rotoworld','2026-10-07','full_season',rows,notes='Preseason overall nine-category draft rankings; availability risk is part of editorial ordering.',coverage='published_top_200')
    rows=[row(r[0],r[1],r[3]) for r in table_rows('smartdraft_points') if len(r)==7 and r[0].isdigit()]
    assert len(rows)==25
    source('smartdraft_points','Smart Draft Board · ESPN','smartdraft','2026-10-21','full_season',rows,format='yk_points',notes='Exact YK/ESPN scoring weights verified. Overall draft rank is VORP-based, not raw projected FP/G. Only the public top 25; severe roster coverage limits.',coverage='partial_public_preview_25')
    path=ROOT/'source/yk/docs/data/rankings.json'
    rows=[row(r['rank'],r['player_name'],r['position']) for r in json.loads(path.read_text())]
    source('all_access_20260218','ALL ACCESS · Feb 2026','all_access','2026-02-18','dynasty',rows,notes='Dated nine-category dynasty import; source URL was not retained. Publication date inferred from supplied filename. Historical season only; not fresh 2026-27 rankings.',season='2025-26',url='file:YK_Dynasty_History.zip!/YK_Dynasty_History/Info/ALL ACCESS - NBA Dynasty Rankings (February 18, 2026).xlsx',rawfile=path)
    bundle()
if __name__=='__main__':build()
