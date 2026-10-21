"""One request per public ranking source, immutable cache; never login or bypass access controls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URLS={
 "nbc_categories":"https://www.nbcsports.com/fantasy/basketball/news/fantasy-basketball-2026-27-preseason-top-200-rankings-wemby-jokic-sga-headline-the-board",
    "yahoo_categories": "https://www.nba.com/news/nba-fantasy-top-250-category-league-rankings",
 'hashtag_dynasty':'https://hashtagbasketball.com/fantasy-basketball-dynasty-rankings',
 'hashtag_ros':'https://hashtagbasketball.com/fantasy-basketball-projections',
 'ninecat':'https://9cat.app/rankings/',
 'dizzle':'https://docs.google.com/spreadsheets/d/1EmReTa5KUcFFMCy8Fq-NpQG3WU0pMY7XNW54G3EPbEM/export?format=xlsx',
 'rotowire_points':'https://www.rotowire.com/basketball/article/2026-27-fantasy-basketball-cheat-sheet-for-points-leagues-printable-excel-141449',
 'smartdraft_points':'https://smartdraftboard.com/espn-fantasy-basketball-rankings',
}
if __name__=='__main__':
 import requests
 root=ROOT/'private/ranking_evidence';root.mkdir(parents=True,exist_ok=True)
 report=[]
 for key,url in URLS.items():
  cached=root/(key+('.xlsx' if key=='dizzle' else '.html'))
  if cached.exists():
   report.append({'id':key,'url':url,'status':'cached','sha256':hashlib.sha256(cached.read_bytes()).hexdigest()});print(key,'cached');continue
  previous=root/'fetch_attempt.json'
  if previous.exists() and any(x['id']==key and x['status']=='blocked' for x in json.loads(previous.read_text())):
   report.append({'id':key,'url':url,'status':'blocked','error':'Prior failure; manual import required'});print(key,'prior blocker');continue
  try:
   r=requests.get(url,timeout=25);r.raise_for_status()
   raw=r.content; sha=hashlib.sha256(raw).hexdigest()
   if key=='dizzle' and not raw.startswith(b'PK'):raise ValueError('Not a public workbook export')
   cached.write_bytes(raw)
   report.append({'id':key,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'sha256':sha,'status':'received','bytes':len(raw)})
   print(key,'received',len(raw))
  except Exception as e:
   report.append({'id':key,'url':url,'status':'blocked','error':type(e).__name__})
   print(key,'blocked',type(e).__name__)
 (root/'fetch_attempt.json').write_text(json.dumps(report,indent=2))
