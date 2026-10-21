"""Selected safeguards adapted from baseball collection_state.py; no collector replacement."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()

def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
            f.write('\n')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def validate_snapshot(data):
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(data['schema_version'] == 1, 'Unsupported snapshot version')
    require(data['default_season'] in data['rosters_by_season'], 'Default season has no roster')
    owners = {o['real_name'] for o in data['teams']['owners']}
    require(len(owners) == len(data['teams']['owners']) == 10, 'Saved franchise coverage changed')
    for season, roster in data['rosters_by_season'].items():
        require(roster['meta']['season'] == season, 'Roster season mismatch')
        require(set(roster['by_owner']) == owners, 'Missing roster teams')
        ids = [p['player_id'] for p in roster['players']]
        require(len(ids) == len(set(ids)) and ids, 'Empty roster or duplicate player IDs')
        require(all(p['owner_real_name'] in owners for p in roster['players']), 'Unresolved roster owner')
        require(all(p['acquisition_type'] == 'UNKNOWN' for p in roster['players']), 'Unsupported acquisition inference')
        require(roster['meta']['total_rostered'] == len(ids), 'Roster count mismatch')
        grouped_ids = [p['player_id'] for rows in roster['by_owner'].values() for p in rows]
        require(sorted(grouped_ids) == sorted(ids), 'Grouped roster disagrees with player list')
    ids = [t['event_id'] for t in data['trades']['trade_events']]
    require(len(ids) == len(set(ids)), 'Duplicate trade event IDs')
    require(all(p.get('selected_player') is None for s in data['draft_results'] for p in s['picks']), 'Unsupported draft selection inference')
    context = data.get('context', {})
    for draft in context.get('drafts', []):
        slots = [(p['round'], p['slot']) for p in draft['picks']]
        require(len(slots) == len(set(slots)), 'Duplicate workbook draft slot')
        require(draft['season'].startswith(str(draft['draft_year'])+'-'), 'Draft belongs to wrong season')
        require(all(p['source_cell'] and p['raw'] and p['selected_player'] and p['status']=='workbook_record'
                    for p in draft['picks']), 'Draft selection lacks workbook evidence')
    require(all(p['owner'] and p['source_cell'] for p in context.get('holdings', [])), 'Holding lacks owner or source')
    require(all(t['date'] and t['give'] and t['get'] and t['source_range'] for t in context.get('recent_trades', [])), 'Incomplete new trade record')

    def walk(value):
        if isinstance(value, dict):
            forbidden = {'jsessionid', 'fx_rm', 'cookie', 'cookies', 'password', 'authorization', 'email'}
            require(not any(k.lower() in forbidden for k in value), 'Sensitive field in public payload')
            for item in value.values(): walk(item)
        elif isinstance(value, list):
            for item in value: walk(item)
    walk(data)

def publish_snapshot(path, data, evidence_root):
    """Validate first, retain immutable evidence, then atomically promote one public bundle."""
    validate_snapshot(data)
    encoded = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    checksum = digest_bytes(encoded)
    atomic_json(Path(evidence_root) / 'snapshots' / (checksum + '.json'), data)
    atomic_json(path, data)
    return checksum

def validate_roster(result, season, league_id, expected_team_ids):
    if result.get('season') != season or result.get('league_id') != league_id:
        raise ValueError('Roster identity mismatch')
    teams = result.get('teams', {})
    if not expected_team_ids or {t.get('fantrax_id') for t in teams.values()} != expected_team_ids:
        raise ValueError('Incomplete team coverage')
    if any((not t.get('players') for t in teams.values())):
        raise ValueError('Team-only fallback is not a valid roster snapshot')
    ids = [p.get('player_id') for t in teams.values() for p in t['players']]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError('Missing or duplicate player IDs')
