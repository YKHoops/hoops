"""Bounded, read-only verification using the existing YK API client. No public promotion."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
from collection_state import atomic_json
from fantrax_yk import FantraxAPI

from workspace import ROOT


def verify(league_id, expected_season, authenticated=False, public_only=False):
    destination = ROOT / 'private/target'
    api = FantraxAPI({'jsessionid': os.environ.get('FANTRAX_JSESSIONID','') if authenticated else '',
                     'fx_rm': os.environ.get('FANTRAX_FX_RM','') if authenticated else '',
                     'api_version':'187.3.6', 'request_delay':0.5})
    report = {'league_id':league_id,'checked_at':datetime.now(timezone.utc).isoformat(),
              'prior_evidence':'Saved public league/roster/player lookups succeeded; transaction discovery methods returned empty responses.',
              'attempt_limit_per_endpoint':1, 'endpoints':[], 'blockers':[]}
    payloads = {}
    for endpoint in ['getLeagueInfo','getTeamRosters','getPlayerIds']:
        try:
            params = {'leagueId':league_id, **({'sport':'NBA'} if endpoint=='getPlayerIds' else {})}
            d = api.public_request(endpoint,params)
            required = {'getLeagueInfo':['seasonYear','scoringSystem','rosterInfo','teamInfo'],
                        'getTeamRosters':['rosters'],'getPlayerIds':[]}[endpoint]
            if any(k not in d for k in required): raise ValueError('Incomplete response')
            if endpoint=='getLeagueInfo':
                actual = f"{d['seasonYear']}-{str(d['seasonYear']+1)[-2:]}"
                if actual != expected_season: raise ValueError('Season mismatch')
            if endpoint=='getTeamRosters' and set(d['rosters']) != set(payloads['getLeagueInfo']['teamInfo']):
                raise ValueError('Roster/team coverage mismatch')
            payloads[endpoint]=d
            report['endpoints'].append({'endpoint':endpoint,'status':'validated'})
        except Exception as error:
            report['endpoints'].append({'endpoint':endpoint,'status':'blocked','error_class':type(error).__name__})
            report['blockers'].append(endpoint + ': verification failed; previous successful evidence retained')
            atomic_json(destination/'latest_attempt.json',report)
            return report
    try:
        if public_only: raise PermissionError('Previously blocked owner endpoint skipped')
        d=api.internal_request(league_id,[{'method':'getFantasyTeams','data':{}}])
        teams=[t for r in d.get('responses',[]) for t in r.get('data',{}).get('fantasyTeams',[])]
        if not teams: raise ValueError('Empty team identity response')
        payloads['getFantasyTeams']=d
        report['endpoints'].append({'endpoint':'getFantasyTeams','status':'received','operator_mapping':'review_required'})
    except Exception as error:
        report['endpoints'].append({'endpoint':'getFantasyTeams','status':'blocked','error_class':type(error).__name__})
        report['blockers'].append('Owner verification unavailable; no identity or current-roster promotion')
    run=destination/'runs'/report['checked_at'].replace(':','-')
    for name,d in payloads.items():atomic_json(run/(name+'.json'),d)
    atomic_json(run/'verification_attempt.json',report)
    atomic_json(destination/'latest_attempt.json',report)
    # Evidence is reviewed before replacing the inputs consumed by build_dashboard.py.
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--league-id',default='noz9r7uxmphcb74p')
    parser.add_argument('--season',default='2026-27')
    parser.add_argument('--authenticated',action='store_true',help='Use explicitly supplied Fantrax environment credentials; never print them')
    parser.add_argument('--public-only',action='store_true',help='Skip previously blocked authenticated owner discovery')
    args=parser.parse_args()
    report=verify(args.league_id,args.season,args.authenticated,args.public_only)
    for result in report['endpoints']:print(result['endpoint']+': '+result['status'])
    if report['blockers']:print('Verification blockers recorded privately; public dashboard unchanged.')
