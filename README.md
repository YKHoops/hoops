# YK Dynasty Basketball

A buildless basketball dashboard published through GitHub Pages from `main` → `docs/`.

Live site: https://ykhoops.github.io/hoops/

## Current release — October 21, 2026

- Navy/white interface with league artwork, shared navigation, selected-team preference, player search, filters, profiles and dialogs.
- 2026–27 public roster: 233 players across 10 franchises, captured October 21, 2026. Historical rosters retain their original seasons.
- Overview, teams, players, trades, standings, draft selections/picks and history. Weekly replay/comparisons, historical charts, ownership replay, trade routes/production and draft comparisons are included. Four completed regular seasons provide 64 periods and 320 matchups. Current Week 1 scores remain in progress.
- Rankings Explorer with Dynasty/Current Season, points/categories, full-season/ROS, team, position, availability and source filters.
- Team Bubble Rankings uses the same compatible-source mean ranks, with position grouping, score-proportional area, source coverage and unranked players. The roster-strength index is neither market value nor predicted wins; picks are excluded.

Category views each have two independent sources. The verified YK expert list remains a 25-player preview. A separate 574-player full-season Fantrax YK projection model covers 231/233 rostered players. Dizzle dynasty points (450) and RotoWire current points (200) are browsable separately because their formulas are unverified. February 2026 ALL ACCESS is available under 2025–26. Source dates, URLs, original ranks and limitations appear in the interface.

## Preview locally

```sh
python3 -m http.server 8879 --bind 127.0.0.1 --directory docs
```

Open http://127.0.0.1:8879/. No bundler, package installation, credentials or live API calls are required to view the site.

## Active files

- `docs/js/dashboard.js`: shared interface and basketball pages.
- `docs/js/league-insights.js`, `docs/js/repair-ui.js`: replay, comparison, trade, draft and NBA-stat features.
- `docs/js/normalize.js`: explicit basketball season selection.
- `docs/js/rankings-engine.js`, `docs/js/rankings-ui.js`: aggregation, imports, explorer and team bubbles.
- `docs/css/dashboard.css`, `docs/css/yk.css`: layout and theme.
- `docs/data/dashboard.json`, `docs/data/rankings.json`, `docs/data/nba_stats.json`: reviewed dated snapshots.
- `dashboard_tools/`: reproducible collection/import/build scripts; see its README for the retained evidence workspace requirement.
- `docs/data/legacy/`: explicitly labeled historical report outputs.

The original collectors, spreadsheets, historical JSON and old interface modules are retained for reference. They are not the active publishing pipeline. In particular, old scripts that write `docs/data/rankings.json` use the previous schema and must not overwrite the new source bundle without adaptation. Private raw responses and credentials from the dashboard working copy are not included in this release.

## Data limits

Incomplete transactions do not establish startup ownership. Unresolved original-pick outcomes and protections remain unresolved. The 2026–27 Sands/Berke franchise transition is based on supplied documentary evidence; current display labels and configured roster rules were checked through signed-in Fantrax, while exact historical operator transition dates remain uncertain. Historical trade grades retain their original methods and are not certified as complete or authoritative.

Release validation: 28 Python and 15 JavaScript checks passed, plus 20 final desktop/mobile route checks. NBA results cover 575 players in the completed 2025–26 baseline and 68 players across three final 2026–27 games. See [REPAIR_NOTES.md](REPAIR_NOTES.md) for coverage and remaining gaps.
