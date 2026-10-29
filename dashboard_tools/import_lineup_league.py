"""Import an explicitly reviewed league-wide roster and schedule capture, offline."""
import argparse
import json
from pathlib import Path
from collection_state import atomic_json
from import_lineup_evidence import normalize, input_filename
from player_identity import Identity
from workspace import ROOT


def import_league(capture, dashboard, root=ROOT):
    owners={o['current_team']:o for o in dashboard['teams']['owners']}
    if set(capture['teams']) != set(owners): raise ValueError('Complete league team coverage required')
    identity=Identity(); all_ids=set(); normalized=[]; audit=[]
    if len({p['id'] for p in capture['periods']})!=len(capture['periods']): raise ValueError('Duplicate periods')
    for name,team in capture['teams'].items():
        owner=owners[name]['real_name']
        ids=[identity.resolve(row[0]) for row in team['rows']]
        if not all(pid.startswith('nba:') for pid in ids): raise ValueError('Unresolved roster identity')
        if set(ids)!=set(team['reviewed_player_ids']): raise ValueError('Reviewed membership mismatch')
        if all_ids.intersection(ids): raise ValueError('Player assigned to multiple teams')
        all_ids.update(ids)
        old={p['player_id'] for p in dashboard['rosters_by_season'][capture['season']]['by_owner'][owner]}
        audit.append({'team':name,'added':sorted(set(ids)-old),'removed':sorted(old-set(ids))})
        for source_period in capture['periods']:
            period=dict(source_period)
            current=period['id']==capture['current_period']
            period['credited_gp']=team['credited_gp'] if current else 0
            period['reserved_gp']=0
            period['opponent']=team['opponents'].get(period['id'])
            raw={**team,'season':capture['season'],'team_name':name,'owner':owner,
                 'source':capture['source'],'period':period,'games':capture['games'],
                 'claims_remaining_observed':team.get('claims_remaining_observed')}
            data=normalize(raw,dashboard,reviewed_membership=team['reviewed_player_ids'])
            data['assumptions'].append('Future weeks hold this captured roster and player quality constant. Recheck injuries and transactions before setting lineups.')
            data['period_evidence']=[{'id':p['id'],'start':p['start'],'end':p['end'],'minimum':p['minimum'],
                'maximum':p['cap'],'credited_gp':team['credited_gp'] if p['id']==capture['current_period'] else 0} for p in capture['periods']]
            normalized.append(data)
    folder=root/'private/lineup_snapshots'
    paths=[]
    for data in normalized:
        name=input_filename(data);atomic_json(folder/name,data);paths.append(name)
    atomic_json(folder/'membership-review.json',{'capture_as_of':capture['as_of'],'changes_from_dashboard':audit})
    atomic_json(folder/'approved.json',{'paths':sorted(paths)})
    return normalized


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('capture',type=Path);args=parser.parse_args()
    data=import_league(json.loads(args.capture.read_text()),json.loads((ROOT/'docs/data/dashboard.json').read_text()))
    print('Validated',len(data),'team/matchup plans; approved manifest updated.')
