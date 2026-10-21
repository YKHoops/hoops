"""Two bounded, read-only standings checks using the existing basketball collector."""
import json
from datetime import datetime,timezone
from pathlib import Path
from fantrax_yk import FantraxAPI
from collection_state import atomic_json
from workspace import ROOT
def main():
    dest=ROOT/'private/league_repair';api=FantraxAPI({'api_version':'187.3.6','request_delay':0.5,'jsessionid':'','fx_rm':''});report=[]
    historical=json.loads((ROOT/'source/yk/docs/data/rosters_2024_25.json').read_text())['league_id']
    for tag,league,data in [('current','noz9r7uxmphcb74p',{}),('historical_period1',historical,{'period':1,'timeframeType':'PERIOD','view':'SCHEDULE'})]:
        try:
            d=api.internal_request(league,[{'method':'getStandings','data':data}]);atomic_json(dest/(tag+'.json'),d)
            tables=[t for r in d.get('responses',[]) for t in r.get('data',{}).get('tableList',[])]
            report.append({'id':tag,'league_id':league,'method':'getStandings','request':data,'status':'tables_received' if tables else 'empty_or_blocked','tables':len(tables)})
        except Exception as e:
            report.append({'id':tag,'league_id':league,'method':'getStandings','status':'blocked','error':type(e).__name__,'reason':'authentication_required' if isinstance(e,RuntimeError) else 'request_failed'})
            break # Authentication/client errors do not justify probing other seasons.
    atomic_json(dest/'attempt.json',{'captured_at':datetime.now(timezone.utc).isoformat(),'attempt_limit':2,'results':report});print(report)
if __name__=='__main__':main()
