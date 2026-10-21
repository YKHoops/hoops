# YK Dynasty Basketball

A buildless basketball dashboard published through GitHub Pages from `main` → `docs/`.

Live site: https://ykhoops.github.io/hoops/

## Current release — October 21, 2026

- Navy/white interface with league artwork, shared navigation, selected-team preference, player search, filters, profiles and dialogs.
- 2026–27 public roster: 233 players across 10 franchises, captured October 21, 2026. Historical rosters retain their original seasons.
- Overview, teams, players, trades, standings, draft selections/picks and history. Current standings and player production are not yet collected; older performance is not relabeled current.
- Rankings Explorer with Dynasty/Current Season, points/categories, full-season/ROS, team, position, availability and source filters.
- Team Bubble Rankings uses the same compatible-source mean ranks, with position grouping, score-proportional area, source coverage and unranked players. The roster-strength index is neither market value nor predicted wins; picks are excluded.

Category views each have two independent sources. Verified YK-points coverage currently exposes only 25 players; compatible dynasty-points and ROS lists require dated manual imports. February 2026 ALL ACCESS is available under 2025–26. Source dates, URLs, original ranks and limitations appear in the interface.

## Preview locally

```sh
python3 -m http.server 8879 --bind 127.0.0.1 --directory docs
```

Open http://127.0.0.1:8879/. No bundler, package installation, credentials or live API calls are required to view the site.

## Active files

- `docs/js/dashboard.js`: shared interface and basketball pages.
- `docs/js/normalize.js`: explicit basketball season selection.
- `docs/js/rankings-engine.js`, `docs/js/rankings-ui.js`: aggregation, imports, explorer and team bubbles.
- `docs/css/dashboard.css`, `docs/css/yk.css`: layout and theme.
- `docs/data/dashboard.json`, `docs/data/rankings.json`: reviewed dated snapshots.
- `docs/data/legacy/`: explicitly labeled historical report outputs.

The original collectors, spreadsheets, historical JSON and old interface modules are retained for reference. They are not the active publishing pipeline. In particular, old scripts that write `docs/data/rankings.json` use the previous schema and must not overwrite the new source bundle without adaptation. Private raw responses and credentials from the dashboard working copy are not included in this release.

## Data limits

Incomplete transactions do not establish startup ownership. Unresolved original-pick outcomes and protections remain unresolved. The 2026–27 Sands/Berke franchise transition is based on supplied documentary evidence; authenticated owners and full current roster-rule enforcement remain open checks. Historical trade grades retain their original methods and are not certified as complete or authoritative.

Pre-publication validation: 17 Python and 8 Node checks passed in the isolated working copy, plus 16 desktop/mobile route checks. Publication retains these validated static artifacts.
