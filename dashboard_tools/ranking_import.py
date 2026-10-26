"""Validated, dated manual imports and immutable ranking snapshots. No network access."""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs
from collection_state import atomic_json
from workspace import ROOT
FIELDS=('id','publisher','label','url','published_at','season','scoring_format','horizon','rank_scope','coverage','notes')
FORMATS={'nine_category','yk_points','general_points','general_dynasty','custom_categories','yk_projection'}
HORIZONS={'dynasty','full_season','rest_of_season'}

def validate(source):
    if not all(source.get(k) for k in FIELDS): raise ValueError('Source metadata is incomplete')
    if not re.fullmatch(r'[a-z0-9_-]+',source['id']): raise ValueError('Unsafe source ID')
    if not source['url'].startswith(('https://','http://','file:')): raise ValueError('Invalid provenance URL')
    parsed=urlparse(source['url'])
    if parsed.username or parsed.password or any(k.lower() in {'token','api_key','apikey','cookie','authorization'} for k in parse_qs(parsed.query)): raise ValueError('Credentials must not appear in source URLs')
    date.fromisoformat(source['published_at'])
    if date.fromisoformat(source['published_at']) > date.today(): raise ValueError('Future publication date')
    from build_dashboard import season_id
    season_id(source['season'])
    if source['scoring_format'] not in FORMATS or source['horizon'] not in HORIZONS or source['rank_scope']!='overall': raise ValueError('Unsupported compatibility group')
    if source['scoring_format'] in {'yk_points','yk_projection'} and source.get('points_weights')!={'PTS':1,'REB':1,'AST':2,'STL':4,'BLK':4,'FGM':2,'FGA':-1,'FTM':1,'FTA':-1,'3PM':1,'TO':-2}: raise ValueError('Points formula does not match YK')
    rows=source['rows'];ids=[r['player_id'] for r in rows]
    if not rows or len(ids)!=len(set(ids)): raise ValueError('Empty list or duplicate player IDs')
    for r in rows:
        if not r.get('player_name') or not re.fullmatch(r'(nba|unmatched):[a-z0-9]+',r['player_id']): raise ValueError('Invalid player identity')
        rank=r.get('original_rank')
        if isinstance(rank,bool) or not isinstance(rank,(int,float)) or rank<1 or rank!=int(rank): raise ValueError('Missing or invalid original rank')
    return source

def promote(source, root=ROOT):
    validate(source)
    for path in (root/'source/rankings').glob('*.json'):
        previous=json.loads(path.read_text())
        if previous['id']!=source['id'] and all(previous[k]==source[k] for k in ['publisher','season','scoring_format','horizon','rank_scope']):
            raise ValueError('Publisher already represented; update its existing source ID')
    # Public bundles receive only ranking/provenance fields, never arbitrary import content.
    source={k:v for k,v in source.items() if k in {*FIELDS,'rows','points_weights','raw_sha256','imported_at','publication_precision'}}
    source['rows']=[{k:v for k,v in row.items() if k in {'player_id','player_name','position','original_rank','identity_status','source_original_rank','projected_fp_pg','projection_inputs'}} for row in source['rows']]
    source['imported_at']=source.get('imported_at') or datetime.now(timezone.utc).isoformat()
    source['list_size']=len(source['rows']);source['max_rank']=max(r['original_rank'] for r in source['rows'])
    current=root/'source/rankings'/f"{source['id']}.json"
    if current.exists():
        old=json.loads(current.read_text())
        if source['published_at'] < old['published_at']: raise ValueError('Would replace a newer source snapshot')
        if len(source['rows']) < len(old['rows'])*.8: raise ValueError('Unexpected coverage shrink; review as a separate source ID')
    if current.exists() and {k:v for k,v in old.items() if k!='imported_at'}=={k:v for k,v in source.items() if k!='imported_at'}:
        return old
    encoded=json.dumps(source,sort_keys=True,ensure_ascii=False).encode()
    checksum=hashlib.sha256(encoded).hexdigest()
    atomic_json(root/'private/ranking_snapshots'/source['id']/(checksum+'.json'),source)
    atomic_json(current,source)
    return source

def validate_manual_identity(source, root=ROOT):
    from build_dashboard import normal
    names={}
    for p in (root/'source/rankings').glob('*.json'):
        for r in json.loads(p.read_text())['rows']:names.setdefault(r['player_id'],set()).add(normal(r['player_name']))
    for r in json.loads((root/'docs/data/dashboard.json').read_text())['journeys']['player_index'].values():
        names.setdefault(r['player_id'],set()).add(normal(r['player_name']))
    for r in source['rows']:
        if r['player_id'].startswith('nba:') and normal(r['player_name']) not in names.get(r['player_id'],set()):
            raise ValueError('Player ID/name pairing requires review: '+r['player_name'])

def bundle(root=ROOT):
    sources=[validate(json.loads(p.read_text())) for p in sorted((root/'source/rankings').glob('*.json'))]
    payload={'schema_version':1,'built_at':datetime.now(timezone.utc).isoformat(),'sources':sources}
    inv=root/'source/context/ranking_inventory.json'
    payload['inventory']=json.loads(inv.read_text()) if inv.exists() else []
    atomic_json(root/'docs/data/rankings.json',payload)
    return payload

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);args=p.parse_args()
    source=validate(json.loads(args.file.read_text()));validate_manual_identity(source)
    promote(source);bundle();print('Validated source promoted; previous snapshots retained.')
