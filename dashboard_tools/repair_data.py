"""Add recovered evidence and broad NBA identities to the normalized dashboard."""
import json,hashlib
from pathlib import Path
from workspace import ROOT
def enrich(d):
    p=ROOT/'docs/data/nba_stats.json'
    if p.exists():
        nba=json.loads(p.read_text());d['nba_stats']=nba
        for season,snapshot in nba['seasons'].items():
            for row in snapshot['rows']:
                pid=row['player_id'];players=d['journeys']['player_index']
                if pid not in players:players[pid]={'player_id':pid,'player_name':row['player_name'],'position':row['position'],'identity_status':'fantrax' if pid.startswith('nba:') else 'source_identity','observations':[],'reported_moves':[],'stats':{}}
                per=row['per_game'];players[pid]['stats'][season]={'gp':row['gp'],**{a:per.get(b) for a,b in [('mpg','min'),('ppg','pts'),('rpg','reb'),('apg','ast'),('spg','stl'),('bpg','blk'),('topg','tov'),('fpts_pg','fp')]},'total_fpts':(row['totals'] or {}).get('fp'),'basis':row['basis']}
    p=ROOT/'source/context/recovered_league.json'
    if p.exists():
        r=json.loads(p.read_text());d['recovered']=r;obs={x['id']:x for x in r['observations']}
        duplicates=set()
        for c in r['reconciled']:
            event=next((t for t in d['trades']['trade_events'] if t['event_id']==c['event_id']),None)
            if not event:continue
            event['csv_evidence']=[obs[i] for i in c['observations']];event['original_date_iso']=event['date_iso'];event['source_date_conflict']=bool(event['date_iso'] and event['date_iso']!=c['date'][:10]);event['date_iso']=c['date'][:10]
            # CSV directions override an inferred route only for matched player IDs; picks retain their original uncertainty.
            for a in event['assets']:
                matches=[x for x in event['csv_evidence'] if a['player_id'] and x['player_id']==a['player_id']]
                if len(matches)==1:a.update(sender=matches[0]['sender'],recipient=matches[0]['recipient'],route_basis='CSV')
            duplicates.update(c.get('duplicate_event_ids',[]));event['duplicate_source_entries']=c.get('duplicate_event_ids',[])
        d['trades']['duplicate_source_entries']=sorted(duplicates)
        d['trades']['trade_events']=[t for t in d['trades']['trade_events'] if t['event_id'] not in duplicates]
        # Export batches remain separate from the legacy transaction counts: multiple deals may share one timestamp.
        d['trades']['trade_events'] += [t for t in r['additional_events'] if t['event_id'].startswith('workbook-')]
        for event in r['additional_events']:
            for a in event['assets']:
                pid=a['player_id']
                if pid and pid not in d['journeys']['player_index']:
                    d['journeys']['player_index'][pid]={'player_id':pid,'player_name':a['label'],'position':'','identity_status':'fantrax' if pid.startswith('nba:') else 'unresolved','observations':[],'reported_moves':[],'stats':{}}
        for x in r['observations']:
            pid=x['player_id']
            if pid:
                if pid not in d['journeys']['player_index']:d['journeys']['player_index'][pid]={'player_id':pid,'player_name':x['player_name'],'position':'','identity_status':'fantrax' if pid.startswith('nba:') else 'unresolved','observations':[],'reported_moves':[],'stats':{}}
                d['journeys']['player_index'][pid].setdefault('transfers',[]).append(x)
        from player_identity import Identity
        identity=Identity()
        for draft in d['context']['drafts']:
            for pick in draft['picks']:
                if not pick['player_id']:
                    pid=identity.resolve(pick['selected_player'].removesuffix(' (FA)'))
                    if pid.startswith('nba:'):
                        pick['player_id']=pid;pick['identity_basis']='Reviewed source spelling / exact Fantrax identity'
                        if pid not in d['journeys']['player_index']:
                            meta=identity.meta[pid]
                            d['journeys']['player_index'][pid]={'player_id':pid,'player_name':meta['player_name'],'position':meta['position'],'identity_status':'fantrax','observations':[],'reported_moves':[],'stats':{}}
        d['teams']['meta']['total_trade_events']=len(d['trades']['trade_events'])
    browser=ROOT/'source/context/fantrax_browser.json'
    if browser.exists():
        evidence=json.loads(browser.read_text());d['authenticated_evidence']=evidence
        d['matchups'].update(evidence['results'])
        for season,snapshot in evidence['standings'].items():
            d['standings']['season_standings']=[r for r in d['standings']['season_standings'] if r['season']!=season]+snapshot['rows']
            d['standings']['as_of'][season]=snapshot['captured_at'][:10]
        d['target']['browser_rules']=evidence['verified_rules']
        d['target']['blockers']=['Current browser display labels and supplied reports support franchise mappings. Full historical operator transition dates remain unresolved.', 'Authenticated snapshots are dated captures. Automatic authenticated refresh is not configured; public NBA box-score refresh remains available.']
        d['standings']['champions']['2025-26']="Ball Don't Lie"
        d['standings']['champion_sources']={'2025-26':'Fantrax playoff bracket: Ball Don’t Lie 4,429, Kentucky Fried Guards 3,888; captured 2026-10-21.'}
        d['refresh_status']['mode']='authenticated_ui_snapshot_with_public_nba_refresh'
        d['refresh_status']['stats_basis']='2025–26 Fantrax regular-season totals; 2026–27 collected final NBA box scores. Seasons remain separate.'
    for relative in ['docs/data/nba_stats.json','source/context/recovered_league.json','source/context/player_aliases.json','source/context/fantrax_browser.json']:
        path=ROOT/relative
        if path.exists():d['provenance'].append({'path':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return d
