# Dashboard refresh tools

These are the implementation scripts for the reviewed static dashboard. Existing repository collectors remain in `scripts/`.

Set `YK_DASHBOARD_WORKSPACE` to the complete local evidence workspace before running these tools, for example:

```sh
YK_DASHBOARD_WORKSPACE=/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball/yk_working_copy python3 dashboard_tools/rebuild_public.py
```

The workspace must retain `source/`, `private/`, and `docs/`. Private authenticated captures, raw workbooks, transaction CSVs and ranking caches are deliberately not copied into this public repository. The released static files are directly usable without these inputs. Full data refresh requires the retained evidence workspace; rebuilding from this public checkout alone is not supported. Rebuild performs no network calls or deployment. See `REPAIR_NOTES.md` for refresh limits, dependencies, checks and remaining gaps.
