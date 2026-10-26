# Dashboard refresh tools

These are the implementation scripts for the reviewed static dashboard. Existing repository collectors remain in `scripts/`.

Set `YK_DASHBOARD_WORKSPACE` to the complete local evidence workspace before running these tools, for example:

```sh
YK_DASHBOARD_WORKSPACE=/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball/yk_working_copy python3 dashboard_tools/rebuild_public.py
```

The workspace must retain `source/`, `private/`, and `docs/`. Private authenticated captures, raw workbooks, transaction CSVs and ranking caches are deliberately not copied into this public repository. The released static files are directly usable without these inputs. Full data refresh requires the retained evidence workspace; rebuilding from this public checkout alone is not supported. Rebuild performs no network calls or deployment. See `REPAIR_NOTES.md` for refresh limits, dependencies, checks and remaining gaps.

Trade integration adds an offline evaluator, a persistent event registry and a proof manifest for complete season totals. The active copies live in the evidence workspace's `source/context/`; `dashboard_tools/manifests/` keeps the reviewed recovery copies. Restore those mappings when recovering this release into a new workspace rather than bootstrapping new positional IDs. Newly changed or removed source rows require mapping review.

Rebuild now stages and validates all outputs before promotion. Content-addressed evaluation files are written before the dashboard pointer; preserve previously published evaluation files for existing readers. A failed rebuild keeps the last valid public output. Optional grades fail locally without disabling the ledger.

Checks for these changes:

```sh
YK_DASHBOARD_WORKSPACE=/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball/yk_working_copy python3 -m unittest discover -s dashboard_tools/tests
node --test tests/trade-evaluations.test.js
```

Full existing regression checks remain in the complete workspace; they require its retained private baseline fixtures.
