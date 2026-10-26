"""Persistent IDs for immutable source editions; ambiguous edits require review."""
import json, hashlib
from collections import defaultdict
from collection_state import atomic_json
from workspace import ROOT

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def assign(name, records, prefix, path=None):
    path=path or ROOT/'source/context/trade_event_registry.json'
    registry=json.loads(path.read_text()) if path.exists() else {'schema_version':1,'collections':{}}
    edition=digest(records); collection=registry['collections'].get(name)
    if collection is None:
        collection={'bootstrap_edition':edition,'bootstrap_ids':[prefix+str(i) for i in range(len(records))],
                    'entries':[{'event_id':prefix+str(i),'fingerprint':digest(r),'original_source_index':i,'source_edition':edition} for i,r in enumerate(records)],'editions':{}}
        registry['collections'][name]=collection
    if edition in collection['editions']:return collection['editions'][edition]
    old=defaultdict(list); new=defaultdict(list)
    for e in collection['entries']:old[e['fingerprint']].append(e['event_id'])
    for i,r in enumerate(records):new[digest(r)].append(i)
    # A disappearance or changed multiplicity could be a correction, not a new event.
    # Do not silently repurpose an existing ID or collapse indistinguishable repeats.
    if any(len(new[k])!=len(v) for k,v in old.items()):
        raise ValueError('Trade source correction/removal needs registry review: '+name)
    result=[None]*len(records)
    for fingerprint,indices in new.items():
        if fingerprint not in old:
            if len(indices)!=1:raise ValueError('New indistinguishable trades need reviewed IDs')
            event_id=prefix+'new-'+fingerprint[:16]
            collection['entries'].append({'event_id':event_id,'fingerprint':fingerprint,'original_source_index':indices[0],'source_edition':edition})
            old[fingerprint]=[event_id]
        for i,event_id in zip(indices,old[fingerprint]):result[i]=event_id
    collection['editions'][edition]=result
    atomic_json(path,registry)
    return result

def bootstrap_ids(name, path=None):
    path=path or ROOT/'source/context/trade_event_registry.json'
    return json.loads(path.read_text())['collections'][name]['bootstrap_ids']
