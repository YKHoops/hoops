# YK trade feature integration plan

Restore the trade-analysis features inside the current blue-and-white, buildless dashboard. Reuse the existing trade ledger, navigation, filters, dialogs, team preference and player profiles. Add one versioned evaluation bundle that every page reads, so a deal has the same grade and explanation everywhere.

Implementation completed locally October 26, 2026. Milestones 1–6 are implemented and validated within their evidence limits; repaired numeric grades and verified pick outcomes remain unavailable until qualifying evidence exists. Publication is pending. Detailed results are in REPAIR_NOTES.md. This plan records the implemented design. The [feature review](https://chatgpt.com/space/page_e20fa3e879ac81918c62b1ddbfc023ce) supplies the findings and pinned source links. The reviewed develop tip, `68ce780`, is already in main’s ancestry; selective adaptation is the integration path.

# Scope and first release

The first useful release should provide richer two-sided trade cards, linked player and pick breakdowns, a searchable grades view, and historical grades with their original method and date visible. Repaired grades, owner summaries and featured trades follow after the identity and calculation checks pass.

Keep the approved visual structure and existing URLs. Do not restore the old application shell, replace collectors, blend ranking horizons, or turn inferred pick outcomes into facts. Current rankings and team bubbles continue using their existing calculations.

# Integration points

Paths below are relative to `yk_working_copy/`. The reviewed original modules are in `private/develop_review_2026-10-26/docs/js/dashboards/`; use the pinned GitHub links in the feature review if that local snapshot is unavailable.

| Current location | Planned integration |
|---|---|
| `scripts/build_dashboard.py`, `recover_league.py`, `repair_data.py` | Keep reconciliation and explicit transfer directions. Add persistent source-to-event mappings before joining evaluations. |
| `scripts/player_identity.py`, `source/context/player_aliases.json` | Reuse canonical player identities and reviewed aliases. Ambiguous matches remain unresolved. |
| New `scripts/build_trade_evaluations.py` | Import archived evaluations, calculate eligible repaired results, validate coverage and emit one public bundle. |
| `scripts/rebuild_public.py`, `collection_state.py` | Add the offline evaluation step after the reconciled dashboard is built. Validate and stage related outputs together before promotion. |
| New `docs/data/trade_evaluations.json` | Store method definitions, input versions, event links, side results, asset evidence and eligibility reasons. |
| New `docs/js/trade-evaluations.js`, `trade-evaluations-ui.js` | Shared result selectors and reusable rendering. Browser code does not implement a second grading formula. |
| `docs/js/dashboard.js` | Connect `tradeList`, `tradeDetail`, `teams`, `playerProfile`, `reports/loadReport`, `render` and `showDialog` to the shared result layer. |
| `docs/js/repair-ui.js` | Reuse the observed-production view and remove duplicated calculations when the bundle supplies those results. Preserve analytics and replay controls. |
| `docs/trade.html`, `grades.html`, `team.html`, `player.html`, `players.html` | Load the shared modules before dashboard initialization wherever their hooks are used. Keep direct links and browser history working. |
| `docs/css/yk.css` | Add small card, badge and coverage styles using existing theme variables. Keep `dashboard.css` as the common layout foundation. |

Original feature references: `grades.js` for the explorer, report cards and featured deals; `trade.js` for two-sided badges; `team.js` and `players.js` for profile integration; `stats.js` for comparison layout only. Keep `docs/data/legacy/` immutable.

# Milestone 1  Make event and evaluation identities durable

Current IDs such as `yk-trade-17` and `workbook-2026-3` derive from source positions. Preserve those public IDs and existing deep links, but persist their assignments so reordering input cannot change their meaning.

Add `source/context/trade_event_registry.json` containing event IDs, source edition hashes, original source references, duplicate aliases and reviewed matching decisions. A source row index is usable only within its pinned edition. Reconcile subsequent editions using explicit transaction IDs when present; otherwise require an unambiguous asset, party and date match or a reviewed mapping. Identical-looking repeat trades must not collapse automatically.

Match all 138 archived grade records to canonical events where evidence supports it. Use the pinned source index as a candidate, verify the asset set, sides and season, and record any date conflict. Many-to-one duplicate aliases count once in summaries. An ambiguous or unmatched grade stays browsable as an unlinked archive record.

Keep the current distinction between 146 reconciled legacy/workbook events and 390 transfer observations. A timestamp batch alone is not a unique transaction. Store franchise identity separately from the recorded operator; unknown historical operator dates do not become the current owner’s record.

**Acceptance:** an audit accounts for every archive row as linked, duplicate alias, ambiguous or unmatched. Reordering fixtures cannot redirect links; adding an unrelated trade cannot alter existing evaluations. No player or owner is matched by an unreviewed fuzzy name.

# Milestone 2  Define one evaluation contract and repair the method

Each result needs `event_id`, a stable side/franchise key, recorded operator, `method_id`, `method_version`, status, nullable grade/GPA, coverage counts, included and excluded assets, reasons, input snapshot hashes and evaluation periods. Publication date, capture time and calculation time remain distinct. Validate that the bundle references the exact dashboard edition it accompanies.

Use three clearly named views:

| View | Meaning and default behavior |
|---|---|
| **Historical grade** | Original archived letter, basis and inputs, unchanged. It can be displayed immediately with its historical-method label. Old player/pick composites do not feed repaired owner averages. |
| **Player improvement grade** | Proposed repaired method: received players’ whole-season YK FP/G in the following season minus their trade-season FP/G. It measures improvement of the received package, not overall trade value. |
| **Observed production** | Collected final NBA games strictly after the transaction through an explicit cutoff. Show totals, GP, covered dates and missing evidence; no automatic letter grade or claim of fantasy lineup credits. |

For the repaired player-improvement method, retain the recognizable legacy thresholds as an explicitly documented heuristic: sum the received-player changes; A+ at 8 or above, A at 4, B at 1, C at −1, D at −4, F below −4. GPA remains 4.3, 4, 3, 2, 1, 0. Display package size and mean player change beside the summed score because package size affects the result.

Proposed eligibility rules are intentionally stricter than the archive: all received player identities and routes resolved; both season periods verified as complete and comparable; every scoring component present; and at least 10 GP per player in each season. The 10-GP threshold is a configurable sample-size rule, not a verified league requirement. No missing data penalties, injury assumptions, or bonuses. Partial and future periods return an incomplete status with a reason. Thus a 2026–27 trade cannot receive a completed following-season grade before the necessary 2027–28 evidence exists.

Use the verified YK points formula from `build_nba_stats.py`; expose both seasons and the formula version. Rounded archived per-game estimates may be shown separately but cannot silently qualify as complete counting totals. Picks remain visible and excluded from this player-only measure. Pick-only deals are ineligible; mixed deals receive a “players only; picks excluded” label and cannot enter whole-package comparisons.

For the first repaired comparison, include only fully covered, two-party, player-only trades. A GPA gap above 0.5 is labeled “favored by the player-improvement model”; 0.5 or less is “even by this model.” Both sides must qualify. Multi-party events retain their detail view without a forced two-side verdict.

**Acceptance:** numeric zero remains zero; F contributes 0 to averages. Missing values produce no grade. Boundary tests cover every threshold, ties and the 0.5 gap. Snapshot-only data, ambiguous routes, mixed packages and incomplete seasons cannot acquire an unqualified verdict.

# Milestone 3  Restore trade cards and the grades explorer

Enhance the current trade dialog with the original two-column layout: assets sent and received, player links, historical/repaired grade badges, per-player evidence, pick descriptions and provenance. Use the existing dialog focus handling and URL state.

Add **Grades** alongside the existing trade views, with player search, My Team/team, partner, season, asset type, method, grade and coverage filters. Share applicable filters with the current ledger; keep source selection separate from analysis mode. Preserve explicit season strings such as `2026-27`, back/forward behavior, reset controls and empty states.

Make `grades.html` a direct entry to the same shared grades view. Keep its existing season and `reportScope` links usable. Preserve archive access for `trade-cards.html`, `trade-leaderboard.html` and `trade-value-over-time.html`; never reinterpret their original values as repaired results.

**Acceptance:** a historical grade opens the correct canonical event or its clearly unlinked source card. Filters survive navigation and dialog close. An unavailable or mismatched evaluation bundle leaves the trade ledger usable and displays a local status message.

# Milestone 4  Add consistent team summaries and profile badges

Build report cards from the shared eligible side results, with mean GPA, eligible/total count, incomplete count, method, season and excluded assets. Offer franchise and recorded-operator scopes; never attribute an unknown historical operator to a current manager.

Show featured model gaps and best/worst eligible trades only under the same method, period and package rules. Use a proposed minimum of three eligible trades for a ranked owner summary; smaller samples remain visible but unranked. Do not mix methods or GPA scales in one average.

Add matching badges to team trade tabs and related player trades. A player profile’s badge describes that side of the transaction, not an individual player grade. Every badge opens the same explanation. The old owner “wins/losses” labels become model-favored/even counts to distinguish them from league standings.

**Acceptance:** the same event/side/method gives the same badge, verdict and included sample everywhere. Every summary drills down to its contributing trades. Duplicate aliases never inflate totals; missing GPA never becomes zero.

# Milestone 5  Restore pick paths and comparisons as evidence allows

Bring back pick transfer paths using documented original franchise, draft year, round, protections, swaps, transfers and final holder. Keep draft selections separate until the original-pick chain establishes the final slot and player. Align statuses to the current explicit unresolved state instead of reviving the old mismatched `used`/`pending` UI.

Reuse the old Give/Get comparison layout for compatible measures only. Observed production, dynasty ranks and projections remain separate tabs with their own source, scoring and horizon labels. The rank-plus-NBA-PPG meter and the automatic 60/40 player/pick composite are excluded from the new method.

**Acceptance:** every resolved outcome has a supporting chain. Unknown picks stay visible without a numeric value. Historical archive grades remain inspectable regardless of whether a repaired pick model is available.

# Milestone 6  Validate and stage the integrated release

Add `tests/test_trade_evaluations.py` for joins, duplicates, aliases, routes, operators, complete scoring inputs, zero/F grades, dates, minimum samples and eligibility. Add `tests/trade-evaluations.test.js` for shared selectors, filtering, coverage, summary denominators and missing-bundle behavior. Retain the October 21 historical fixtures and the source-reconciled weekly-refresh tests.

Test repeatable offline rebuilds, failed-input preservation and no-op rebuilds. Stage dashboard, evaluation bundle and method manifest as one release with matching content hashes. The existing per-file atomic writer is useful, but cannot alone guarantee a consistent multi-file release. Retain the last successful set; failed evaluation builds must not leave new dashboard data paired with unrelated grades.

At 1280px and 390px, check navigation, My Team, search/filter/reset, two-sided cards, keyboard and touch dialogs, direct URLs, long pick labels, loading/error states, and internal table scrolling. Recheck representative overview, rankings, bubbles, NBA stats, standings, drafts and history routes for regressions.

**Acceptance:** all relevant Python/JavaScript checks pass; desktop and phone flows work without page overflow; eligibility counts reconcile to sources; private/authenticated inputs and credentials remain outside public files.

# Delivery and refresh

Implement milestones 1–4 in small commits: durable mappings, evaluation contract, richer UI, then summaries. Milestone 5 can ship documented pick paths while unresolved outcomes remain deferred. Milestone 6 gates any release.

Develop in `yk_working_copy/` and retain the complete evidence there. After local review, copy approved public outputs to `yk_github/docs/` and necessary refresh changes to `yk_github/dashboard_tools/`; avoid activating the old root-level grading scripts. Update `PORT_PLAN.md` and `REPAIR_NOTES.md` with eligible coverage, method versions and remaining gaps.

Extend the existing weekly refresh only after the new builder is validated. Recalculate when reviewed inputs change, preserve source dates, and publish substantive changes rather than timestamp churn. Keep a rollback commit and the previous matched output set. Implementation is staged on the local review branch. No deployment or automation configuration changes have been made.

