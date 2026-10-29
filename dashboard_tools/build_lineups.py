"""Build a content-addressed lineup bundle from explicitly selected local inputs."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from collection_state import atomic_json
from lineup_optimizer import analyze, validate
from workspace import ROOT


def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def public_input(data):
    """Explicit allowlist: pending claims, bids, cookies and manual strategy never publish."""
    def pick(obj, keys):return {k:obj[k] for k in keys.split() if k in obj}
    result=pick(data,'schema_version as_of owner team_name season assumptions')
    result['period']=pick(data['period'],'id fantrax_period start end planning_start opponent cap minimum cap_basis credited_gp reserved_gp')
    result['rules']=pick(data['rules'],'slots max_main max_reserve')
    result['claims']=pick(data['claims'],'weekly_limit observed_remaining observed_week_start planning_week_start planning_allowance basis')
    result['waivers']=pick(data['waivers'],'status reason')
    result['comparisons']=pick(data['comparisons'],'status reason')
    result['sources']=[]
    for source in data['sources']:
        row=pick(source,'label url as_of')
        if row.get('url'):
            u=urlparse(row['url'])
            if u.scheme!='https' or u.hostname!='www.fantrax.com' or u.query or u.username or u.password: raise ValueError('Unexpected source URL')
        result['sources'].append(row)
    result['period_evidence']=[pick(p,'id start end minimum maximum credited_gp') for p in data.get('period_evidence',[])]
    result['players']=[]
    for p in data['players']:
        row=pick(p,'id name status lineup_slot positions eligible_slots nba_team rostered_pct injury expected_return')
        row['projection']=pick(p['projection'],'fp_pg current current_gp historical historical_gp historical_seasons basis small_sample')
        row['games']=[pick(g,'id date start opponent availability settled locked_slot') for g in p['games']]
        result['players'].append(row)
    validate(result)
    return result


def build(root=ROOT):
    folder=root/'private/lineup_snapshots'; manifest=folder/'approved.json'
    bundle={'schema_version':1,'method_version':'lineup-1','teams':[],
            'method':'90% current YK FP/G + 10% GP-weighted prior three seasons; maximize projected points within the cap'}
    if manifest.exists():
        for relative in json.loads(manifest.read_text())['paths']:
            if Path(relative).name!=relative: raise ValueError('Input must be a local snapshot filename')
            data=public_input(json.loads((folder/relative).read_text()))
            entry={'input':data,'input_sha256':digest(data),'scenarios':{}}
            for key,conditional in [('conservative',False),('returns',True)]:
                entry['scenarios'][key]=analyze(data,conditional=conditional)
            bundle['teams'].append(entry)
    checksum=digest(bundle);path='data/lineups/'+checksum+'.json'
    atomic_json(root/'docs'/path,bundle)
    # Stable index is the final commit point. Immutable old plans stay readable.
    atomic_json(root/'docs/data/lineups.json',{'schema_version':1,'path':path,'sha256':checksum})
    return bundle


if __name__=='__main__':
    b=build()
    for t in b['teams']:
        for key,s in t['scenarios'].items():
            print(t['input']['team_name'],key,s['best']['status'],s['best']['games'],'starts',s['best']['points'],'points; depth',s['minimum_players']['players_used'])
