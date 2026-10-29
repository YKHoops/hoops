# Lineup setting — league-wide planning

Updated October 29, 2026. The planner covers all 10 teams and 251 owned players, with 50 team/matchup entries: the remaining current week and four future weeks through November 29. It uses reviewed Fantrax captures and does not submit lineup changes, claims or drops. The static page is published at https://ykhoops.github.io/hoops/lineup.html.

## What works

- Team-profile link and shared navigation to `lineup.html`; team, season, matchup, injury scenario, objective and selected day use URL state.
- Whole-period integer optimization, maximizing 90% current / 10% GP-weighted prior-three-season YK FP/G. Daily player/slot eligibility, reserve limits, off-day active fillers, credited GP and locked-game reservations are constraints.
- Conservative and conditional-return plans; points-first and maximum-games comparisons; daily starters, bench/availability explanations, full active placements, position gaps, usage and minimum-contributor/95%-points analysis.
- Player usage bars separate starts, benched games and unavailable/inactive games. Daily load charts expose thin days; a five-week heat table shows each player’s planned starts and scheduled games.
- Keep rostered / Droppable preferences for each player, stored on this browser by team across weeks. Players above 70% ownership, unknown ownership or stale inputs remain automatically protected. A preference never drops a player or changes a lineup. No drop recommendations are generated until the acquisition inputs are verified.
- A validated importer, immutable lineup bundles, staged offline rebuild integration, explicit missing-team/history states, and freshness warnings (24 hours or a newly started game).
- Read-only source inspection confirmed the standings Optimal switch exists. Its exact retrospective cap handling remains unverified.

## Important rule discovery

Fantrax **Team Roster → Min/Max** was inspected for actual scoring periods. Do not calculate the limit from calendar days:

| Period | Dates | Displayed minimum | Displayed maximum | Only Franz credited GP at capture |
|---|---|---:|---:|---:|
| 1 | October 20–25 | 29 | 48 | 46 |
| 2 | October 26–November 1 | 35 | 55 | 19 |
| 3 | November 2–8 | 29 | 48 | 0 |
| 4 | November 9–15 | 35 | 55 | 0 |
| 5 | November 16–22 | 35 | 55 | 0 |
| 6 | November 23–29 | 29 | 48 | 0 |

The league's normal maximum remains 55 and its enforcement is “Do nothing.” The planner uses each period's displayed maximum as its ceiling. The reason for Fantrax's adjustment is not inferred. Period 3 dates are explicitly shown as November 2–8; the matchup opponent is The Unction.

Period 1 is retained rule evidence, not a reconstructed historical plan. The current-week table counts remaining starts only; credited games are already included in the cap total. All future weeks hold the captured roster and player quality constant, with IR/minors inactive. Current remaining claims are verified only for Only Franz; other teams show unknown. Future weeks use the four-claim Monday reset.

For Only Franz, the October 29 capture produces these **conditional forecasts**, not guaranteed results:

| Matchup | Injury scenario | Future starts | Credited + future | Future projected points |
|---|---|---:|---:|---:|
| Current | Exclude unresolved returns | 26 | 45 / 55 | 729.6 |
| Current | Conditional returns available | 27 | 46 / 55 | 765.0 |
| November 2–8 | Exclude unresolved returns | 47 | 47 / 48 | 1,493.8 |
| November 2–8 | Conditional returns available | 48 | 48 / 48 | 1,555.6 |

The upcoming conservative plan uses 17 of 20 main-roster players. With conditional returns, the points-first plan uses 18; a separate optimization proves that 16 contributors can supply 48 starts. The conservative case cannot reach 48 with the captured roster. The UI also calculates the smaller set retaining 95% of points. These subset results do not recommend dropping anyone; all roster players remain available as non-scoring active fillers where reserve limits require them.

## Run and refresh

From the complete `yk_working_copy` evidence workspace:

```sh
python3 -m venv .lineup-venv
.lineup-venv/bin/python -m pip install -r requirements-lineup.txt
.lineup-venv/bin/python scripts/import_lineup_league.py private/lineup_snapshots/2026-10-29-league-reviewed.json
.lineup-venv/bin/python scripts/build_lineups.py
python3 -m http.server 8879 --bind 127.0.0.1 --directory docs
```

The existing HTTP server may already serve port 8879. Serve **only `docs/`**. Full `scripts/rebuild_public.py` also stages lineup output when `private/lineup_snapshots/approved.json` exists. Its existing collectors require their usual dependencies; the dedicated lineup requirements cover the solver. The already-created local environment also has requests for regression checks.

The reviewed capture format contains `as_of`, owner/team/season, an explicit period and cap basis, complete roster rows and a deduplicated game list. Each row carries name, current roster slot, league eligibility, NBA team, current FP/G and GP, roster percentage and injury label. Game rows carry ID, date, Eastern time, away and home team. Reconcile against the approved roster snapshot before import; identity or coverage mismatches fail without replacing the prior plan.

The league importer requires all ten teams, explicitly reviewed canonical membership and no player on multiple teams. It records changes from the older dashboard roster privately and writes owner/season-specific input filenames before replacing the approved manifest. It does not silently reuse older team membership. Single-team capture refresh remains available through `import_lineup_evidence.py`.

The raw snapshots are private. `approved.json` explicitly selects normalized files; it never selects the newest file implicitly. To remove an obsolete planning period from future bundles, edit this manifest deliberately. Public output is an allowlist; private bid details, pending claims and manual protections are excluded.

Standalone solver contract: use `schema_version=1`, explicit period start/end/cap/cap_basis/credited_gp/reserved_gp, rules/slots/main/reserve limits, and players with canonical IDs, statuses, eligible slots, a projection and dated games. For a current matchup, `planning_start` excludes already completed days; `credited_gp` must come from Fantrax. Started games require settled evidence or an explicit `locked_slot` (null means locked on the bench); counting locked games must already be included in `reserved_gp`. Do not reuse an old current-period capture as live advice.

SciPy MILP returns an optimum or an explicitly qualified result. See [SciPy's solver reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html). Time-limited results never prove a minimum or impossibility. Primary and secondary objectives are solved separately to preserve points-first behavior.

## Validation

```sh
.lineup-venv/bin/python -m unittest discover -s tests -p 'test_lineup.py' -v
node --test tests/lineup.test.js
```

Tests cover positional matching versus greedy sorting, cross-day cap allocation, zero/negative games, injuries and IR, reserve fillers, minimum subsets, locked-game budgets, timezone consistency, 70% protection, missing-history projections, exhaustive tiny-fixture optima, current-period accounting, public-field filtering and last-valid-output retention. Existing dashboard tests also ran successfully. Browser checks cover desktop/390px mobile, conditional scenarios, current-period accounting, day selection, protection persistence and missing-team navigation.

## Next increments

1. **Acquisition solver and 0–4-claim plans:** collect verified available candidates, full schedules, clearing/processing times, claim windows and center-limit counting; model chronological roster changes and net lost production. The current page shows thin days and the game shortfall but explicitly says the minimum number of pickups is not established.
2. **Rolling schedule refresh:** extend beyond November 29 using newly reviewed rosters, schedules and actual period caps. Unsupported selections stay unavailable.
3. **Historical optimal comparison:** collect daily actual lineups, roster/eligibility changes and credited scoring. Existing completed scores cannot reconstruct those decisions. Save these observations prospectively before claiming a historical optimum.
4. **Automated collection/execution:** no recurring collection, Fantrax auto-lineup action, claim, bid or roster write is enabled. A future execution feature needs fresh lock/roster validation and verified write behavior.

Remaining assumptions are shown on the page: all three flex slots accept the observed basketball positions; no IR/minors activation is assumed; injury return dates stay conditional; historical per-game data retains older precision/coverage limits. The schedule capture includes 228 unique NBA games across all 30 teams from October 29 through November 29. Available free-agent eligibility, ownership and processing evidence still need separate capture.
