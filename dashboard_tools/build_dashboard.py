"""Normalize saved YK evidence for the adapted static dashboard. No network requests."""
from datetime import datetime, timezone
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import re
import unicodedata
from collection_state import publish_snapshot

from workspace import ROOT
SOURCE = ROOT / 'source/yk/docs/data'
SAVED = ROOT / 'private/saved'
TARGET = ROOT / 'private/target'
# Reviewed public run; subsequent failed discovery cannot replace this input.
approved = TARGET / 'approved_run.json'
CURRENT = TARGET / (json.loads(approved.read_text())['path'] if approved.exists() else 'runs/2026-10-21T17-04-30.964717+00-00')
if CURRENT.resolve().parent != (TARGET/'runs').resolve(): raise ValueError('Approved run must be a retained target run')
MANIFEST = []


def read(path):
    raw = path.read_bytes()
    MANIFEST.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
    return json.loads(raw)


def normal(name):
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', name.lower())


def season_id(value):
    value = str(value).replace('–', '-').replace('—', '-')
    if not re.fullmatch(r'20\d\d-\d\d', value) or int(value[5:]) != (int(value[:4]) + 1) % 100:
        raise ValueError('Invalid basketball season')
    return value


def build(include_repairs=True):
    MANIFEST.clear()
    identity = read(SOURCE / 'owners.json')['owners']
    alias, team_alias, owners = {}, {}, []
    for index, o in enumerate(identity):
        name = o['realName']
        for v in [name, o['id'], *o['altNames'], *o['abbrevs'], o['fantraxAbbrev']]: alias[normal(v)] = name
        for s, team in o['teams'].items(): team_alias[normal(team)] = name
        owners.append({'real_name': name, 'owner_id': o['id'], 'color_index': index,
                       'aliases': [o['id'], *o['altNames'], *o['abbrevs']],
                       'current_team': o['teams']['2025-26'],
                       'history': [{'season': s, 'team_name': t} for s, t in o['teams'].items()]})
    team_alias[normal('Pure Sweat Farm')] = alias[normal('Moss')]
    def owner(v): return alias.get(normal(v or '')) or team_alias.get(normal(v or ''))
    # Exact canonical names + explicit aliases. No suffix-stripping or fuzzy identity merges.
    from fetch_fantrax_scoring import NAME_OVERRIDES
    player_aliases = {normal(a): normal(b) for a, b in NAME_OVERRIDES.items()}
    player_aliases.update({normal(a): normal(b) for a, b in {
        'Cam Johnson':'Cameron Johnson', 'Steph Curry':'Stephen Curry', "De'Angelo Russell":"D'Angelo Russell", 'Deandre Hunter':"De'Andre Hunter",
        'Nicholas Claxton':'Nicolas Claxton', 'Patrick Beverly':'Patrick Beverley',
        'Wendall Carter Jr.':'Wendell Carter Jr.', 'Jemai Grant':'Jerami Grant',
        'Brandon Podziemski':'Brandin Podziemski', 'Dennis Schroeder':'Dennis Schroder',
        'Ayo Dosumnu':'Ayo Dosunmu', 'Bilal Couliably':'Bilal Coulibaly',
        'Jaren Jackson':'Jaren Jackson Jr.', 'Gary Trent':'Gary Trent Jr.',
        'Michael Porter':'Michael Porter Jr.', 'Robert Williams':'Robert Williams III',
    }.items()})
    def pkey(v): return player_aliases.get(normal(v), normal(v))
    directory = read(SAVED / '2025_26/getPlayerIds.json')
    name_ids = defaultdict(set)
    for pid, p in directory.items():
        n = p.get('name', '')
        if ', ' in n: last, first = n.split(', ', 1); n = first + ' ' + last
        name_ids[pkey(n)].add(pid)
    # Disambiguate identical NBA names only with authoritative saved roster IDs.
    anchored = defaultdict(set)
    for season_path in sorted(SAVED.iterdir()):
        if not season_path.is_dir(): continue
        saved_dir = read(season_path / 'getPlayerIds.json')
        saved_rosters = read(season_path / 'getTeamRosters.json')['rosters']
        for roster in saved_rosters.values():
            for item in roster['rosterItems']:
                pid = item['id']; n = saved_dir.get(pid, {}).get('name', '')
                if ', ' in n:
                    last, first = n.split(', ', 1); n = first + ' ' + last
                if n: anchored[pkey(n)].add(pid)
                else: anchored[pkey(pid)].add(pid)
    for key, ids in anchored.items():
        if len(ids) == 1: name_ids[key] = ids
    players = {}
    unresolved = set()
    def player(name, position=''):
        name = re.sub(r'^(?:(?:PG|SG|SF|PF|C|G|F)(?:/(?:PG|SG|SF|PF|C|G|F))*\s+)', '', name).strip()
        ids = name_ids.get(pkey(name), set())
        pid = 'nba:' + next(iter(ids)) if len(ids) == 1 else 'legacy:' + pkey(name)
        if re.fullmatch(r'[0-9][a-z0-9]{4}', name): name = 'Unidentified player (' + name + ')'
        if len(ids) != 1: unresolved.add(name)
        if pid not in players:
            players[pid] = {'player_id': pid, 'player_name': name, 'position': position,
                            'identity_status': 'fantrax' if len(ids) == 1 else 'unresolved', 'observations': [], 'reported_moves': [], 'stats': {}}
        if position: players[pid]['position'] = position
        return pid
    rosters, league_ids, scoring, draft_results = {}, {}, {}, []
    for path in sorted(SOURCE.glob('rosters_*.json')):
        raw = read(path); s = season_id(raw['season']); league_ids[s] = raw['league_id']
        by_owner = {}; rows = []
        for key, team in raw['teams'].items():
            who = owner(key)
            if not who: raise ValueError('Unresolved saved owner: ' + key)
            by_owner[who] = []
            for p in team['players']:
                pid = player(p['name'], p['pos'])
                row = {'player_id': pid, 'player_name': players[pid]['player_name'], 'position': p['pos'], 'nba_team': p['nbaTeam'],
                       'roster_status': 'IR' if p['status'] == 'INJURED_RESERVE' else p['status'], 'owner_real_name': who,
                       'team_name': team['team_name'], 'acquisition_type': 'UNKNOWN', 'stint_start': None}
                rows.append(row); by_owner[who].append(row)
                players[pid]['observations'].append({'season': s, 'owner': who, 'team_name': team['team_name'], 'date': None, 'kind': 'saved_roster'})
        rosters[s] = {'meta': {'season': s, 'league_id': raw['league_id'], 'total_rostered': len(rows), 'as_of': None,
                             'basis': 'Saved archive roster; capture date unavailable'}, 'players': rows, 'by_owner': by_owner}
        info = read(SAVED / s.replace('-', '_') / 'getLeagueInfo.json')
        scoring[s] = {'type': info['scoringSystem']['type'], 'categories': info['scoringSystem']['scoringCategories']['PLAYER'],
                      'roster_rules': info['rosterInfo'], 'start': info['startDate'], 'end': info['endDate']}
        draft = read(SAVED / s.replace('-', '_') / 'getDraftResults.json')['responses'][0]['data']
        team_ids = {tid: owner(t['name']) for tid, t in info['teamInfo'].items()}
        # No scorers in any saved draft response. modifiedDate is NOT a selection timestamp.
        draft_results.append({'season': s, 'coverage': 'Draft order only; selected players unavailable', 'picks': [
            {'round': p['round'], 'pick_number': p['pickNumber'], 'owner': team_ids.get(p['teamId']),
             'team_id': p['teamId'], 'selected_player': None, 'status': 'selection_unknown'} for p in draft['draftPicksOrdered']]})
    standings_raw = read(SOURCE / 'seasons.json')['seasons']
    standings, champions, standings_audit, standings_as_of = [], {}, [], {}
    for saved_season in standings_raw:
        season = saved_season['year']; champions[season] = saved_season.get('champion')
        raw = read(SAVED / season.replace('-', '_') / 'getStandings.json')
        payload = raw['responses'][0]['data']
        end_ms = payload.get('displayedSelections', {}).get('displayedEndDate')
        standings_as_of[season] = datetime.fromtimestamp(end_ms / 1000, timezone.utc).date().isoformat() if end_ms else None
        table = next(t for t in payload['tableList'] if t.get('tableType') == 'H2hPointsBased1')
        keys = [c['key'] for c in table['header']['cells']]
        for r in table['rows']:
            team = r['fixedCells'][1]['content']; who = owner(team)
            if not who: raise ValueError('Unresolved standings owner')
            cells = dict(zip(keys, r['cells']))
            def number(key):
                raw_value = cells.get(key, {}).get('content')
                return float(str(raw_value).replace(',', '')) if raw_value not in [None, '', '-'] else None
            points = number('pointsFor'); against = number('pointsAgainst')
            old = next(x for x in saved_season['standings'] if owner(x['team']) == who)
            if old.get('fpts') != points:
                standings_audit.append({'season': season, 'owner': who, 'legacy_points': old.get('fpts'),
                                        'verified_points': points, 'basis': 'Archived Fantrax pointsFor column'})
            standings.append({'season': season, 'owner_real_name': who, 'team_name': team,
                              'rank': int(r['fixedCells'][0]['content']), 'pts': points,
                              'w': number('win'), 'l': number('loss'), 't': number('tie'),
                              'win_pct': number('winpc'), 'points_against': against})
    trade_events = []
    for index, t in enumerate(read(SOURCE / 'trades.json')):
        assets = []
        sides = []
        for side in ['give', 'get']:
            side_owners = set()
            for raw in t[side]:
                parts = raw.split(' ', 1); sender = owner(parts[0]); text = parts[1] if len(parts) > 1 else raw
                if sender: side_owners.add(sender)
                is_pick = bool(re.search(r'\b(20\d{2}|round|swap)\b', text, re.I))
                pid = None if is_pick else player(text)
                assets.append({'raw': raw, 'label': text, 'recorded_operator': {'VLAND':'Spencer Vlandis', 'KELL':'Brendan Kelley'}.get(parts[0], sender), 'sender': sender, 'recipient': None, 'side': side, 'type': 'pick' if is_pick else 'player', 'player_id': pid})
            sides.append(side_owners)
        parties = sorted(sides[0] | sides[1])
        clear = len(parties) == 2 and all(len(x) == 1 for x in sides) and not sides[0] & sides[1] and all(a['sender'] for a in assets)
        if clear:
            for a in assets: a['recipient'] = next(x for x in parties if x != a['sender'])
        # Multi-party / inconsistent prefixes stay explicit, never assigned to a guessed recipient.
        event = {'event_id': 'yk-trade-' + str(index), 'source_index': index, 'year': season_id(t['season']), 'date_iso': t.get('date'),
                 'parties': parties, 'assets': assets, 'route_status': 'two_party_record' if clear else 'recipient_unresolved',
                 'trade_type_label': 'Players + picks' if {a['type'] for a in assets} == {'player','pick'} else 'Picks' if all(a['type']=='pick' for a in assets) else 'Players',
                 'source': 'Saved YK trade log', 'fantrax_confirmed': bool(t.get('fantrax_confirmed'))}
        trade_events.append(event)
    moves = read(SOURCE / 'player_movement.json')['players']
    for name, record in moves.items():
        pid = player(name)
        for h in record['history']:
            if h['type'] == 'trade':
                players[pid]['reported_moves'].append({'season': h.get('season'), 'date': h.get('date'), 'from': owner(h.get('from')), 'to': owner(h.get('to')), 'basis': 'Derived legacy movement report; not a complete ledger'})
            # 'startup' was inferred from absence of trades; never promote it to an acquisition.
    stats = read(SOURCE / 'player_stats_historical.json')
    for s, entries in stats.items():
        for row in entries.values():
            matches = [pid for pid, p in players.items() if pkey(p['player_name']) == pkey(row['player_name'])]
            if len(matches) == 1:
                players[matches[0]]['stats'][s] = {k: row.get(k) for k in ['gp','mpg','ppg','rpg','apg','spg','bpg','topg','fpts_pg','total_fpts']}
    picks = read(SOURCE / 'picks.json')
    future = [{'draft_year': int(y), 'owner': owner(who), 'label': label, 'status': 'unverified_saved_holding'} for y, by_owner in picks.items() for who, labels in by_owner.items() for label in labels]
    ledger = read(SOURCE / 'pick_ledger.json')['picks']
    pick_records = [{'pick_id': k, 'draft_year': v['draft_year'], 'round': v['round'], 'original_owner': owner(v['original_owner']),
                     'reported_owner': owner(v['current_owner']), 'reported_status': v['status'], 'status': 'outcome_unresolved',
                     'is_swap': v.get('is_swap', False), 'trade_refs': [x['trade_index'] for x in v['trades']]} for k, v in ledger.items()]
    verification = read(CURRENT / 'verification_attempt.json')
    info = read(CURRENT / 'getLeagueInfo.json')
    target_roster = read(CURRENT / 'getTeamRosters.json')
    target = {'league_id': verification['league_id'], 'season': f"{info['seasonYear']}-{str(info['seasonYear']+1)[-2:]}",
              'name': info['leagueName'], 'sport': 'Basketball (BASKETBALL_PLAYER scoring group)', 'checked_at': verification['checked_at'],
              'start': info['startDate'], 'end': info['endDate'], 'scoring_type': info['scoringSystem']['type'],
              'scoring': info['scoringSystem']['scoringCategories']['PLAYER'], 'roster_rules': info['rosterInfo'],
              'team_count': len(info['teamInfo']), 'player_count': sum(len(x['rosterItems']) for x in target_roster['rosters'].values()),
              'teams': [{'team_id': tid, 'team_name': t['name'], 'mapped_owner': owner(t['name']),
                         'identity_status': 'saved_name_match_not_operator_verified' if owner(t['name']) else 'unresolved'} for tid,t in info['teamInfo'].items()],
              'blockers': ['Owner endpoint requires authentication after outdated-client retry; The Unction has no verified owner mapping.',
                           'Public roster rules omit full IR/minors eligibility and games limits; 20 main slots do not cap IR/minors observations.',
                           'Current-season standings and transaction history are not collected.'],
              'development_basis': 'Saved 2022-23 through 2025-26; target roster not promoted into historical data'}
    context = read(ROOT / 'source/context/supplied_context.json')
    def context_owner(label):
        label = re.sub(r'\(Compensation\)', '', label).strip(' *')
        return 'Jared Sands' if label == 'Sands' else owner(label)
    for draft in context['drafts']:
        for pick in draft['picks']:
            pick['owner'] = context_owner(pick['picker_label'])
            pick['picker_status'] = 'documented' if pick['owner'] else 'ambiguous_annotation'
            matches = [pid for pid,p in players.items() if pkey(p['player_name']) == pkey(re.sub(r'\s*\(FA\)$', '', pick['selected_player']))]
            pick['player_id'] = matches[0] if len(matches) == 1 else None
    for holding in context['holdings']:
        holding['owner'] = context_owner(holding['holder_label'])
        if not holding['owner']: raise ValueError('Unmapped context holding: ' + holding['holder_label'])
    for team in target['teams']:
        if team['team_name'] == 'The Unction':
            team.update(mapped_owner='Jared Sands', identity_status='documented_year_vii',
                        source='YK Dynasty Preseason Power Rankings - Year 7.docx, The Unction / Owner')
    target['blockers'][0] = 'Owner endpoint requires authentication; The Unction → Jared Sands is documented in Year VII, not authenticated through Fantrax.'
    target['blockers'][1] = 'Archived roster rules and Year VII’s 55-game maximum are documented separately; current IR/minors eligibility, enforcement and tie rules still need verification.'
    current_directory = read(CURRENT / 'getPlayerIds.json')
    current_season = season_id(target['season'])
    if current_season != '2026-27' or verification['league_id'] != 'noz9r7uxmphcb74p':
        raise ValueError('Current snapshot identity changed')
    if set(target_roster['rosters']) != set(info['teamInfo']): raise ValueError('Partial current roster')
    current_rows, current_owners = [], {o['real_name']: [] for o in owners}
    for team in target['teams']:
        # The existing owner key is a stable franchise key, not an assertion about its current operator.
        franchise = 'Logan Berke' if team['mapped_owner'] == 'Jared Sands' else team['mapped_owner']
        if franchise not in current_owners: raise ValueError('Unmapped current franchise')
        operator = team['mapped_owner']
        record = next(o for o in owners if o['real_name'] == franchise)
        record['operators_by_season'] = {'2026-27': operator}
        record['history'].append({'season':current_season, 'team_name':team['team_name']})
        record['current_team'] = team['team_name']
        if operator != franchise: record['aliases'].append(operator)
        team['franchise_key'] = franchise
        for item in target_roster['rosters'][team['team_id']]['rosterItems']:
            raw = current_directory[item['id']]
            name = raw['name']; last, first = name.split(', ', 1) if ', ' in name else ('', name)
            name = (first + ' ' + last).strip(); pid = 'nba:' + item['id']
            if pid not in players:
                players[pid] = {'player_id':pid,'player_name':name,'position':raw['position'],'identity_status':'fantrax','observations':[],'reported_moves':[],'stats':{}}
            row = {'player_id':pid,'player_name':name,'position':raw['position'],'lineup_slot':item['position'],
                   'nba_team':raw['team'],'roster_status':'IR' if item['status']=='INJURED_RESERVE' else item['status'],
                   'owner_real_name':franchise,'operator_name':operator,'team_name':team['team_name'],
                   'acquisition_type':'UNKNOWN','stint_start':None}
            current_rows.append(row); current_owners[franchise].append(row)
            players[pid]['observations'].append({'season':current_season,'owner':franchise,'operator_name':operator,
                'team_name':team['team_name'],'date':verification['checked_at'][:10],'kind':'public_roster'})
    rosters[current_season] = {'meta':{'season':current_season,'league_id':target['league_id'],'total_rostered':len(current_rows),
        'as_of':verification['checked_at'],'basis':'Public Fantrax roster; franchise crosswalk from saved teams and supplied Year VII documents'},
        'players':current_rows,'by_owner':current_owners}
    scoring[current_season] = {'type':target['scoring_type'],'categories':target['scoring'],'roster_rules':target['roster_rules'],'start':target['start'],'end':target['end']}
    target['development_basis'] = '2026-27 public roster, captured '+verification['checked_at']+'; archived seasons retained separately'
    seasons = sorted(set(rosters) | {x['year'] for x in trade_events})
    data = {'schema_version': 1, 'default_season': current_season, 'target': target,
            'teams': {'meta': {'seasons': seasons, 'total_trade_events': len(trade_events)}, 'owners': owners},
            'rosters_by_season': rosters, 'standings': {'season_standings': standings, 'champions': champions, 'as_of': standings_as_of, 'reconciliation': standings_audit},
            'journeys': {'player_index': players}, 'trades': {'trade_events': trade_events},
            'draft_results': draft_results, 'picks': {'holdings': context['holdings'], 'archived_holdings': future, 'ledger': pick_records},
            'context': context,
            'matchups': read(SOURCE / 'matchups.json'), 'scoring': scoring,
            'refresh_status': {'mode': 'public_roster_with_archive', 'source_as_of': verification['checked_at'], 'stats_basis': 'Saved NBA per-game data; 2025-26 is partial; no 2026-27 performance data',
                               'coverage': 'Partial trade history; roster observations do not establish acquisition or exit dates.'},
            'identity_gaps': sorted(unresolved), 'provenance': list(MANIFEST)}
    from repair_data import enrich
    return enrich(data) if include_repairs else data


if __name__ == '__main__':
    d = build()
    checksum = publish_snapshot(ROOT / 'docs/data/dashboard.json', d, ROOT / 'private')
    print(f"Validated {len(d['teams']['owners'])} franchises, {len(d['journeys']['player_index'])} players, {len(d['trades']['trade_events'])} trades; saved-season bundle {checksum[:12]}")
