# Lineup setting — first release

Implemented locally October 29, 2026. The first release covers the current-roster planner (plan milestones 1–2), with a dated Only Franz capture for the current and upcoming matchups. It does not submit changes to Fantrax or publish the website.

## What works

- Team-profile link and shared navigation to `lineup.html`; team, season, matchup, injury scenario, objective and selected day use URL state.
- Whole-period integer optimization, maximizing 90% current / 10% GP-weighted prior-three-season YK FP/G. Daily player/slot eligibility, reserve limits, off-day active fillers, credited GP and locked-game reservations are constraints.
- Conservative and conditional-return plans; points-first and maximum-games comparisons; daily starters, bench/availability explanations, full active placements, position gaps, usage and minimum-contributor/95%-points analysis.
- Ownership protection above 70%, with local manual protection for any player. No drop recommendations are generated until the acquisition inputs are verified.
- A validated importer, immutable lineup bundles, staged offline rebuild integration, explicit missing-team/history states, and freshness warnings (24 hours or a newly started game).
- Read-only source inspection confirmed the standings Optimal switch exists. Its exact retrospective cap handling remains unverified.

## Important rule discovery

Fantrax **Team Roster → Min/Max** was inspected for actual scoring periods. Do not calculate the limit from calendar days:

| Period | Dates | Displayed minimum | Displayed maximum | Only Franz credited GP at capture |
|---|---|---:|---:|---:|
| 1 | October 20–25 | 29 | 48 | 46 |
| 2 | October 26–November 1 | 35 | 55 | 19 |
| 3 | November 2–8 | 29 | 48 | 0 |

The league's normal maximum remains 55 and its enforcement is “Do nothing.” The planner uses each period's displayed maximum as its ceiling. The reason for Fantrax's adjustment is not inferred. Period 3 dates are explicitly shown as November 2–8; the matchup opponent is The Unction.

The October 29 capture produces these **conditional forecasts**, not guaranteed results:

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
.lineup-venv/bin/python scripts/import_lineup_evidence.py private/lineup_snapshots/2026-10-29-reviewed.json
.lineup-venv/bin/python scripts/import_lineup_evidence.py private/lineup_snapshots/2026-10-29-current-reviewed.json
.lineup-venv/bin/python scripts/build_lineups.py
python3 -m http.server 8879 --bind 127.0.0.1 --directory docs
```

The existing HTTP server may already serve port 8879. Serve **only `docs/`**. Full `scripts/rebuild_public.py` also stages lineup output when `private/lineup_snapshots/approved.json` exists. Its existing collectors require their usual dependencies; the dedicated lineup requirements cover the solver. The already-created local environment also has requests for regression checks.

The reviewed capture format contains `as_of`, owner/team/season, an explicit period and cap basis, complete roster rows and a deduplicated game list. Each row carries name, current roster slot, league eligibility, NBA team, current FP/G and GP, roster percentage and injury label. Game rows carry ID, date, Eastern time, away and home team. Reconcile against the approved roster snapshot before import; identity or coverage mismatches fail without replacing the prior plan.

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
2. **More teams and future periods:** import complete fresh captures; unsupported selections stay unavailable. The current importer intentionally requires reviewed membership rather than borrowing stale season snapshots.
3. **Historical optimal comparison:** collect daily actual lineups, roster/eligibility changes and credited scoring. Existing completed scores cannot reconstruct those decisions. Save these observations prospectively before claiming a historical optimum.
4. **Automated collection/execution:** no recurring collection, Fantrax auto-lineup action, claim, bid or roster write is enabled. A future execution feature needs fresh lock/roster validation and verified write behavior.

Remaining assumptions are shown on the page: all three flex slots accept the observed basketball positions; no IR/minors activation is assumed; injury return dates stay conditional; historical per-game data retains older precision/coverage limits. The schedule capture is complete for the owned roster, not the whole NBA free-agent pool.
