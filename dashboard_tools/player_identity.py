"""Exact source-name crosswalk with reviewed aliases; ambiguous names never guessed."""
import json,re,unicodedata
from collections import defaultdict
from pathlib import Path
from workspace import ROOT
def key(v):return re.sub(r'[^a-z0-9]','', ''.join(c for c in unicodedata.normalize('NFD',v.lower()) if unicodedata.category(c)!='Mn'))
def index():
    names=defaultdict(set);meta={}
    for p in sorted((ROOT/'private/saved').glob('*/getPlayerIds.json'))+sorted((ROOT/'private/target/runs').glob('*/getPlayerIds.json')):
        for pid,r in json.loads(p.read_text()).items():
            n=' '.join(reversed(r['name'].split(', ',1))) if ', ' in r['name'] else r['name']
            names[key(n)].add('nba:'+pid);meta['nba:'+pid]={'player_name':n,'position':r.get('position',''),'nba_team':r.get('team','')}
    for r in json.loads((ROOT/'docs/data/dashboard.json').read_text())['journeys']['player_index'].values():
        if r['identity_status']=='fantrax': names[key(r['player_name'])]={r['player_id']}
    for p in (ROOT/'source/rankings').glob('*.json'):
        for r in json.loads(p.read_text())['rows']:
            if r['player_id'].startswith('nba:'): names[key(r['player_name'])].add(r['player_id'])
    aliases={'Kelly Oubre':'Kelly Oubre Jr.','Ronald Holland':'Ron Holland','Khaman Malauch':'Khaman Maluach','Nic Claxton':'Nicolas Claxton','Cam Johnson':'Cameron Johnson','Cam Thomas':'Cameron Thomas','Herb Jones':'Herbert Jones','Alexandre Sarr':'Alex Sarr','Ronald Holland II':'Ron Holland','Carlton Carrington':'Bub Carrington','Robert Dillingham':'Rob Dillingham','Enes Kanter':'Enes Freedom','Nene':'Nene Hilario','PJ Dozier':'P.J. Dozier'}
    reviewed=ROOT/'source/context/player_aliases.json'
    if reviewed.exists():aliases.update(json.loads(reviewed.read_text())['aliases'])
    for a,b in aliases.items():
        if key(b) in names:names[key(a)]=names[key(b)].copy()
    if reviewed.exists():
        for name,pid in json.loads(reviewed.read_text()).get('canonical_ids',{}).items():
            if pid not in meta:raise ValueError('Reviewed ID absent from player directory')
            names[key(name)]={pid}
    return names,meta
class Identity:
    def __init__(self):
        self.names,self.meta=index()
        self.legacy={key(p['player_name']):p['player_id'] for p in json.loads((ROOT/'docs/data/dashboard.json').read_text())['journeys']['player_index'].values() if p['player_id'].startswith('legacy:')}
    def resolve(self,name,fallback=None):
        ids=self.names.get(key(name),set())
        return next(iter(ids)) if len(ids)==1 else (self.legacy.get(key(name)) or fallback or 'historical:'+key(name))
