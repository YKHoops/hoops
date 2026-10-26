import copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(os.environ['YK_DASHBOARD_WORKSPACE']).resolve();sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trade_registry import assign,digest
from build_trade_evaluations import grade,improvement,verdict,observed,validate,build,canonical_dashboard,WEIGHTS

class TradeEvaluationTests(unittest.TestCase):
 def fixture(self):
  assets=[{'player_id':'nba:a','type':'player','label':'A','sender':'X','recipient':'Y','recorded_operator':'Former X'}, {'player_id':'nba:b','type':'player','label':'B','sender':'Y','recipient':'X','recorded_operator':'Former Y'}]
  e={'event_id':'test','year':'2024-25','date_iso':'2025-01-01','parties':['X','Y'],'assets':assets}
  def stats(p):return {k:(p if k=='pts' else 0) for k in WEIGHTS}
  seasons={s:{'rows':[{'player_id':'nba:a','gp':10,'totals':stats(a)},{'player_id':'nba:b','gp':10,'totals':stats(b)}]} for s,a,b in [('2024-25',100,100),('2025-26',150,20)]}
  proofs={s:{'snapshot_sha256':digest(v),'complete_regular_season':True,'evidence':'Explicit test fixture'} for s,v in seasons.items()}
  return e,seasons,proofs
 def test_thresholds_and_zero(self):
  for delta,letter in [(8,'A+'),(7.99,'A'),(4,'A'),(1,'B'),(0,'C'),(-1,'C'),(-4,'D'),(-4.01,'F')]:self.assertEqual(grade(delta),letter)
 def test_f_is_zero_and_real_operator_is_kept(self):
  e,s,p=self.fixture();x=improvement(e,'X',s,p);self.assertEqual((x['grade'],x['gpa']),('F',0));self.assertEqual(x['recorded_operator'],'Former X')
 def test_missing_scoring_or_player_is_unknown(self):
  e,s,p=self.fixture();s['2025-26']['rows'][0]['totals'].pop('fgm');p['2025-26']['snapshot_sha256']=digest(s['2025-26'])
  r=improvement(e,'Y',s,p);self.assertIsNone(r['grade']);self.assertIsNone(r['score'])
 def test_complete_proof_is_tied_to_snapshot(self):
  e,s,p=self.fixture();s['2025-26']['rows'][0]['gp']=11
  self.assertEqual(improvement(e,'Y',s,p)['status'],'incomplete')
 def test_rounded_snapshots_and_future_seasons_are_ineligible(self):
  e,s,p=self.fixture();self.assertIsNone(improvement(e,'Y',s,{})['grade']);e['year']='2026-27';self.assertIsNone(improvement(e,'Y',s,p)['grade'])
 def test_minimum_gp_and_unresolved_route(self):
  e,s,p=self.fixture();s['2025-26']['rows'][0]['gp']=9;p['2025-26']['snapshot_sha256']=digest(s['2025-26']);self.assertIsNone(improvement(e,'Y',s,p)['grade'])
  e,s,p=self.fixture();e['assets'][1]['recipient']=None;self.assertIsNone(improvement(e,'Y',s,p)['grade'])
 def test_duplicate_asset_and_unknown_identity_do_not_grade(self):
  e,s,p=self.fixture();e['assets'].append(copy.deepcopy(e['assets'][0]));self.assertIsNone(improvement(e,'Y',s,p)['grade'])
  e,s,p=self.fixture();e['assets'][0]['player_id']='legacy:unknown';self.assertIsNone(improvement(e,'Y',s,p)['grade'])
 def test_verdict_requires_complete_player_only_two_party_packages(self):
  e,s,p=self.fixture();sides=[improvement(e,o,s,p) for o in e['parties']];self.assertEqual(verdict(e,sides)['favored'],'Y')
  sides[1]['gpa']=.5;self.assertIsNone(verdict(e,sides)['favored']);sides[1]['gpa']=.51;self.assertEqual(verdict(e,sides)['favored'],'Y')
  e['assets'].append({'type':'pick'});self.assertEqual(verdict(e,sides)['status'],'ineligible')
  e,s,p=self.fixture();e['parties'].append('Z');self.assertEqual(verdict(e,sides)['status'],'ineligible')
 def test_observed_excludes_same_day_deduplicates_and_preserves_zero(self):
  e,_,_=self.fixture();snap={'season':'2025-26','through':'2025-01-03','rows':[{'player_id':'nba:a','game_stats':[{'game_id':'1','date':'2025-01-01','stats':dict.fromkeys(WEIGHTS,10)},{'game_id':'2','date':'2025-01-02','stats':dict.fromkeys(WEIGHTS,0)}]}]}
  r=observed(e,snap);self.assertEqual(r['rows'][0]['games'],1);self.assertEqual(r['rows'][0]['points'],0);self.assertIsNone(r['rows'][1]['points'])
  snap['rows'][0]['game_stats'].append(snap['rows'][0]['game_stats'][1]);self.assertRaises(ValueError,observed,e,snap)
 def test_registry_survives_reorder_addition_and_identical_repeats(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'registry.json';rows=[{'asset':'A'},{'asset':'B'},{'asset':'A'}]
   self.assertEqual(assign('x',rows,'x-',p),['x-0','x-1','x-2'])
   self.assertEqual(assign('x',[rows[1],rows[0],rows[2]],'x-',p),['x-1','x-0','x-2'])
   ids=assign('x',[*rows,{'asset':'C'}],'x-',p);self.assertEqual(ids[:3],['x-0','x-1','x-2']);self.assertTrue(ids[3].startswith('x-new-'))
   self.assertRaises(ValueError,assign,'x',[{'asset':'Corrected'}],'x-',p)
 def test_live_archive_audit_and_missing_periods(self):
  d=json.loads((ROOT/'docs/data/dashboard.json').read_text());b=build(d);validate(b,d)
  self.assertEqual(b['audit']['archive_records'],138);self.assertEqual(b['audit']['archive_status'],{'linked':136,'duplicate_alias':2})
  self.assertEqual(b['audit']['canonical_events'],len(d['trades']['trade_events']))
  self.assertTrue(all(p['selected_player'] is None for p in b['pick_paths']))
  self.assertTrue(all(s['gpa'] is None for e in b['events'] if e['season']=='2026-27' for s in e['improvement']['sides']))
  d['default_season']='2025-26';self.assertRaises(ValueError,validate,b,d)
 def test_reimport_of_unchanged_rank_source_retains_capture_and_import_dates(self):
  from ranking_import import promote
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'source/rankings').mkdir(parents=True);source=json.loads((ROOT/'source/rankings/fantrax_yk_model.json').read_text());p=root/'source/rankings/fantrax_yk_model.json';p.write_text(json.dumps(source));before=p.read_bytes();incoming=copy.deepcopy(source);incoming.pop('imported_at')
   out=promote(incoming,root);self.assertEqual(p.read_bytes(),before);self.assertEqual(out['imported_at'],source['imported_at']);self.assertEqual(out['publication_precision'],'capture_only')
 def test_failed_staged_build_does_not_touch_public_outputs(self):
  import rebuild_public
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'docs/data').mkdir(parents=True);(root/'private').mkdir();(root/'source').mkdir();p=root/'docs/data/dashboard.json';p.write_text('last success')
   with patch.object(rebuild_public,'ROOT',root),patch.object(rebuild_public.subprocess,'run',side_effect=RuntimeError('rejected input')):
    self.assertRaises(RuntimeError,rebuild_public.main)
   self.assertEqual(p.read_text(),'last success')

if __name__=='__main__':unittest.main()
