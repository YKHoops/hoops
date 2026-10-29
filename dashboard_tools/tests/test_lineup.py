import copy
import itertools
import json
import os
import sys
import unittest
from pathlib import Path

CODE_ROOT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('YK_DASHBOARD_WORKSPACE',CODE_ROOT))
sys.path.insert(0,str(CODE_ROOT/'scripts' if (CODE_ROOT/'scripts').is_dir() else CODE_ROOT))
from lineup_optimizer import solve, analyze, blend, protection, validate


def fixture(players, cap=2, slots=None):
    return {'schema_version':1,'as_of':'2026-10-29T16:00:00+00:00',
            'period':{'start':'2026-11-02','end':'2026-11-03','cap':cap,'cap_basis':'Test explicit limit','credited_gp':0,'reserved_gp':0},
            'rules':{'slots':slots or ['PG','SG'],'max_main':20,'max_reserve':20},'players':players}


def player(id,slots,fp,days=(2,),status='ACTIVE'):
    return {'id':id,'name':id,'eligible_slots':slots,'status':status,'projection':{'fp_pg':fp},'rostered_pct':50,
            'games':[{'id':id+str(d),'date':f'2026-11-{d:02}','start':f'2026-11-{d:02}T19:00:00-05:00','opponent':'X','availability':'available'} for d in days]}


class LineupTests(unittest.TestCase):
    def test_position_matching_not_greedy(self):
        d=fixture([player('flex',['PG','SG'],40),player('guard',['PG'],39)])
        r=solve(d);self.assertEqual(r['points'],79)
        self.assertEqual({a['player_id']:a['slot'] for a in r['assignments']},{'flex':'SG','guard':'PG'})

    def test_whole_period_cap_preserves_later_quality(self):
        d=fixture([player('early',['PG'],5),player('late',['PG'],50,(3,))],1)
        self.assertEqual(solve(d)['player_ids'],['late'])

    def test_negative_and_zero_are_not_forced(self):
        d=fixture([player('negative',['PG'],-2),player('zero',['SG'],0)])
        self.assertEqual(solve(d)['games'],0)
        self.assertEqual(solve(d,'games')['games'],2)

    def test_injuries_and_ir(self):
        p=player('conditional',['PG'],50);p['games'][0]['availability']='conditional'
        d=fixture([p,player('IR',['SG'],100,status='IR')])
        self.assertEqual(solve(d)['games'],0)
        self.assertEqual(solve(d,conditional=True)['games'],1)

    def test_reserve_limit_requires_offday_fillers(self):
        d=fixture([player('A',['PG'],40),player('B',['SG'],30,(3,))])
        d['rules']['max_reserve']=0
        r=solve(d)
        self.assertEqual(len(r['active_placements']),4)
        self.assertEqual(r['games'],2)

    def test_minimum_subset_and_95_percent(self):
        d=fixture([player('A',['PG'],50,(2,3)),player('B',['SG'],1,(2,3))])
        r=analyze(d)
        self.assertEqual(r['minimum_players']['players_used'],1)
        self.assertEqual(r['preserve_95']['players_used'],1)

    def test_locked_reserved_games_are_not_reselected(self):
        a=player('locked',['PG'],40);a['games'][0]['locked_slot']='PG'
        d=fixture([a,player('other',['SG'],20,(3,))],1);d['period']['reserved_gp']=1
        r=solve(d)
        self.assertEqual(r['games'],0)
        self.assertTrue(any(x['locked'] for x in r['active_placements']))

    def test_exact_ownership_boundaries_and_manual(self):
        p=player('A',['PG'],20);p['rostered_pct']=70
        self.assertIsNone(protection(p));p['rostered_pct']=70.01
        self.assertEqual(protection(p),'Over 70% rostered')
        p['rostered_pct']=10
        self.assertEqual(protection(p,['A']),'Manually protected')
        self.assertIsNotNone(protection(p,ownership_fresh=False))
        p['rostered_pct']=None;self.assertIsNotNone(protection(p))

    def test_projection_weighting_and_missing_seasons(self):
        h=[{'season':'2025-26','gp':10,'fp_pg':20},{'season':'2024-25','gp':30,'fp_pg':40}]
        self.assertEqual(blend({'gp':2,'fp_pg':50},h)['fp_pg'],48.5)
        self.assertEqual(blend({'gp':0,'fp_pg':0},h)['fp_pg'],35)
        self.assertEqual(blend({'gp':2,'fp_pg':50},[])['fp_pg'],50)
        self.assertIsNone(blend({'gp':0,'fp_pg':0},[])['fp_pg'])

    def test_invalid_and_started_game_inputs_rejected(self):
        d=fixture([player('A',['PG'],10)])
        d['players'].append(copy.deepcopy(d['players'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate player'):validate(d)
        d=fixture([player('A',['PG'],10)]);d['as_of']='2026-11-03T00:01:00+00:00'
        with self.assertRaisesRegex(ValueError,'locked-slot'):validate(d)
        d=fixture([player('A',['PG'],10)]);d['period']['cap']=47.1
        with self.assertRaisesRegex(ValueError,'integer cap'):validate(d)

    def test_tiny_bruteforce_optimum(self):
        ps=[player('A',['PG','SG'],8,(2,3)),player('B',['PG'],7,(2,)),player('C',['SG'],6,(3,))]
        d=fixture(ps,3);best=0
        pairs=[(p,g,s) for p in ps for g in p['games'] for s in p['eligible_slots']]
        for n in range(4):
            for chosen in itertools.combinations(pairs,n):
                if len({(p['id'],g['date']) for p,g,s in chosen})!=n:continue
                if len({(g['date'],s) for p,g,s in chosen})!=n:continue
                best=max(best,sum(p['projection']['fp_pg'] for p,g,s in chosen))
        self.assertEqual(solve(d)['points'],best)

    def test_real_snapshot_reconciles_assignments(self):
        p=ROOT/'private/lineup_snapshots/input-2026-11-02.json'
        if not p.exists():self.skipTest('Local reviewed capture absent')
        d=json.loads(p.read_text());r=analyze(d);assigned=r['best']['assignments']
        self.assertEqual(len(d['players']),26)
        self.assertLessEqual(len(assigned),d['period']['cap'])
        self.assertEqual(len({(a['player_id'],a['date']) for a in assigned}),len(assigned))
        self.assertEqual(len({(a['slot'],a['date']) for a in assigned}),len(assigned))
        self.assertEqual(sum(x['starts'] for x in r['daily']),len(assigned))
        self.assertTrue(all(a['player_id'] not in {p['id'] for p in d['players'] if p['status'] in ['IR','MINORS']} for a in assigned))

    def test_invalid_lock_budget_and_date(self):
        d=fixture([player('A',['PG'],20)]);d['players'][0]['games'][0]['locked_slot']='PG'
        with self.assertRaisesRegex(ValueError,'reserved'):validate(d)
        d=fixture([player('A',['PG'],20)]);d['players'][0]['games'][0]['start']='2026-11-03T19:00:00-05:00'
        with self.assertRaisesRegex(ValueError,'timezone'):validate(d)

    def test_current_week_subtracts_actual_and_reserved(self):
        d=fixture([player('A',['PG'],20,(2,3))],2);d['period'].update(credited_gp=1,planning_start='2026-11-03')
        d['players'][0]['games']=d['players'][0]['games'][1:]
        self.assertEqual(solve(d)['games'],1)

    def test_public_allowlist_and_failed_build_retains_index(self):
        import tempfile
        from build_lineups import public_input,build
        p=ROOT/'private/lineup_snapshots/input-2026-11-02.json'
        if not p.exists():self.skipTest('Local reviewed capture absent')
        data=json.loads(p.read_text());data['cookie']='secret';data['claims']['pending_bid']=20
        data['players'][0]['private_note']='strategy'
        safe=public_input(data)
        self.assertNotIn('cookie',safe);self.assertNotIn('pending_bid',safe['claims']);self.assertNotIn('private_note',safe['players'][0])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'private/lineup_snapshots').mkdir(parents=True);(root/'docs/data').mkdir(parents=True)
            (root/'private/lineup_snapshots/approved.json').write_text('{"paths":["bad.json"]}')
            (root/'private/lineup_snapshots/bad.json').write_text('{}')
            index=root/'docs/data/lineups.json';index.write_text('last good')
            with self.assertRaises((ValueError,KeyError)):build(root)
            self.assertEqual(index.read_text(),'last good')

if __name__=='__main__':unittest.main()
