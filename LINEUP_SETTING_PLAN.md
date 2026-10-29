# Lineup setting feature plan

Planning date: October 29, 2026. Status: current-roster planning implemented for all ten teams, current week plus four future weeks, with player usage charts, weekly starts and local roster preferences; acquisition planning, wider history and execution remain later milestones. See [implementation notes](LINEUP_SETTING_README.md). Published as a static dashboard; no Fantrax roster changes. Paths below are relative to `yk_working_copy/`.

**Verified during implementation:** Fantrax Min/Max shows period 3 (November 2–8) at **29–48 GP**, despite seven calendar days. Period 2 is **35–55** and the six-day opening period is **29–48**. The implementation uses the actual displayed limit, not a calendar-day prorating formula. The original design below remains the roadmap.

Add **Lineup setting** to each team's dashboard. It should recommend legal daily lineups across an entire matchup, explain roster usage and schedule gaps, and compare acquisition plans against keeping the current roster.

## Product decisions

- **Maximize projected fantasy points, even if that uses fewer games.** The user confirmed this objective. The normal seven-day planning ceiling is 55; reaching it is a separate diagnostic, not a requirement to start a weaker or negative-value game.
- **Never recommend dropping a player over 70% rostered.** At exactly 70% or below, a player is a potential drop candidate. Manual protection adds protection at any ownership level. Injury does not remove protection. Missing or stale ownership data blocks a drop recommendation until refreshed.
- Model up to four claims per Monday-based weekly allowance, using actual claims remaining. A matchup and a claim-reset week are separate concepts.
- Use **90% current-season FP/G + 10% historical FP/G** for player quality, calculated under YK scoring. Keep availability separate from quality.
- The first release recommends actions. Automatic Fantrax lineup execution is a later feature.

## Evidence and rules

The supplied photos and saved authenticated verification agree on the following. The saved rules capture is `private/fantrax_browser/rules.txt`; a summary appears in `REPAIR_NOTES.md`.

| Rule | Planning treatment |
|---|---|
| Period GP minimum 35, maximum 55; prorating enabled | Display both. Treat the maximum as the user's planning ceiling. Read the actual period dates and effective limit. |
| Automatic maximum and minimum enforcement: “Do nothing” | Do not claim Fantrax automatically stops scoring at 55. Confirm commissioner practice, over-limit treatment, and prorating/rounding before matching official results or enabling execution. |
| Daily lineup changes; lock at scheduled game start | Respect player/game lock times and freeze completed and locked decisions during replanning. Verify exact behavior for bench players and positional moves. |
| Ten active slots | PG, SG, G, SF, PF, F, C, Flx, Flx2, Flx3, one each. Verify the accepted eligibility set for each flex slot. |
| Main roster 20, reserve maximum 10; IR 4 and minors 2 outside main limit | Model every status and legal activation. A healthy minor or returning IR player is not automatically an available starter. |
| Center total maximum 5 | Verify how Fantrax counts multi-position players against this rule; do not infer from display position alone. |
| Illegal roster transactions prevented; IR enforcement can lock transactions | Validate intermediate roster states, including healthy players occupying IR. |
| Four claims per week, reset Monday | Use the remaining allowance and reset timezone; verify which completed claims consume it. Do not multiply a matchup's claim budget by its length blindly. |
| Bidding; daily free-agent processing shown as 6:30 PM EDT | Verify effective acquisition time, waiver clearance, bid budget, and whether the same day's game remains eligible. Use timezone-aware processing times, not a fixed UTC offset. |

Prorating should use Fantrax's displayed effective limit when available. `55 × period_days / 7` is only a provisional calculation until the base-period and rounding behavior are verified. Allow a visibly labeled commissioner-specified limit. Do not silently round a six-day opener or an extended holiday period.

YK scoring: `PTS + REB + 2 AST + 4 STL + 4 BLK + 2 FGM − FGA + FTM − FTA + 3PM − 2 TO`.

Read-only inspection of the existing Fantrax roster tab on October 29 exposed detailed eligibility, FP/G, GP, Schedule – Week, Schedule – Full, roster statuses, and Claims Remaining (Week). The selected daily lineup was October 28, and the page showed a connection warning; this is field-discovery evidence, not a refreshed planning snapshot. Ownership percentages, reliable injury detail, and the full schedule still need structured capture.

## Page design

Entry: **Teams → selected team → Lineup setting**, preserving team and season. Proposed route: `lineup.html?owner=...&season=2026-27&period=...`, linked from the team profile. Default to the next matchup; provide a prominent current-matchup option for managing remaining games. Past and future periods use actual league boundaries.

| Section | What the manager learns |
|---|---|
| Matchup summary | Dates/opponent, actual GP so far, planned remaining starts, expected GP when supported, effective ceiling, projected points, claims remaining, injury uncertainty, and capture times. |
| Daily lineup | Day columns and eligible-slot rows; starter, opponent/time, blended FP/G, injury state, and lock state. Selecting a player reveals alternatives and why each was benched. Mobile shows one day at a time. |
| Daily opportunities | Scheduled players, usable players, filled slots, bench collisions, and position-specific gaps. Distinguish an avoidable gap from an intentional benching to preserve the cap. |
| Roster usage | Per player: scheduled games, available games, recommended starts, bench games, injury/DNP risk, projected contribution, ownership, and protection. Include an accessible player-by-day table. |
| Roster depth | Number and percentage of players used by the recommended plan; smallest feasible group that reaches the cap; smallest group retaining nearly all projected points; sensitivity to unavailable players. |
| Waiver scenarios | No-add baseline and plans with 1–4 remaining acquisitions for a normal week; names, acquisition/drop timing, usable dates/positions, net extra starts, net projected points, and drop consequences. |
| Comparisons | Current saved lineup, our recommended lineup, verified Fantrax auto-lineup output when available, and retrospective optimal results where history is sufficient. |

Keep the existing navy/blue/white styling, team preference, URL/back navigation, and player links. Statuses must have text labels, not color alone. Show missing data explicitly; an absent plan is not a zero-game forecast.

## What roster usage means

Avoid one ambiguous “roster utilization” percentage. Show these separately:

1. **Players used:** distinct current-roster players with at least one recommended start, divided by current main-roster player count. Show IR/minors separately and also offer an all-owned denominator. Acquired players are reported separately.
2. **Games used:** recommended starts divided by the roster's available scheduled player-games. Explain losses to slot congestion, position eligibility, injuries, and the matchup cap with a documented, non-overlapping attribution order.
3. **Minimum players to reach the cap:** choose the smallest feasible subset of the current eligible roster whose schedule and positions can supply the required starts. This is a separate optimization; if impossible, show its best attainable total and reason.
4. **Players needed to preserve points:** smallest subset retaining at least a displayed threshold, proposed default 95%, of the best projected point total. This aligns roster-depth analysis with the user's points-first goal.
5. **Ready-now depth:** players currently available and legally activatable, plus how many starts they can actually supply in this matchup. Show conditional return scenarios separately.

Illustration only, assuming 20 main-roster players and no pickups: at 4 usable games each, the raw lower bound is `ceil(55 / 4) = 14` players (70%). At 3.5 usable games each it is 16 (80%); at 3 it is 19 (95%). These are arithmetic bounds, not roster recommendations. Fifteen players with four scheduled games each offer 60 raw games, but if six cannot fit into legal daily slots, only 54 are usable. Thus “75% of the roster” has no fixed answer.

For a genuine depth answer, solve on the actual schedule, then repeat across future matchups and specified injury scenarios. Report which positions and nights fail, rather than treating all healthy players as interchangeable.

## Projection and injury model

Base quality: `0.90 × current_season_YK_FP_per_game + 0.10 × historical_YK_FP_per_game`.

Proposed historical default: GP-weighted performance across the previous three NBA seasons with usable evidence, recomputed using the same YK scoring. Show included seasons, GP, completeness and precision. A prior-season-only option can be added, but do not silently change the 90/10 split.

Fallbacks must be explicit: no historical games → use current FP/G with “no history” labeling; no current games → historical-only provisional estimate; neither → unranked unless a clearly separate projection is available. Zero games is missing evidence, not zero ability. Flag small current-season samples while retaining the requested weighting. Use NBA player performance, not fantasy-team-specific starts, for the average.

For a game, expected points may be `base_quality × probability_of_playing`, but only when the probability has an identified basis. Do not invent calibrated probabilities from Questionable/Out labels. MVP uses available, unavailable, and conditional scenarios; expected totals can remain unavailable until an availability model is validated.

Exclude confirmed unavailability for its documented time window. A player out tonight is not necessarily out all next week. Questionable players get alternate lineups and a conditional flag. IR is a fantasy roster status, not a medical forecast; clearing an injury also requires legal activation. Healthy NBA bench players can still record a DNP.

Keep three quantities distinct: **scheduled starts**, **expected actual appearances**, and **credited fantasy GP**. Future starts cannot guarantee 55 credited games. Replan after injury updates, transactions, postponements and results. Reserve cap space for already locked games still in progress; never rely on fractional expected GP to authorize more than the allowed number of potential counting games.

## Optimization approach

Use one solver over the entire scoring period. Assigning the best ten players independently each day can waste late-week capacity or fill a flexible slot needed by another player.

For the no-transaction case, define a binary assignment for each player/game/eligible slot. Enforce one slot per player-game, one player per slot, actual NBA schedule, ownership, availability scenario, legal statuses, and locks. Bound remaining potential counting games by the effective ceiling minus credited GP and reserved in-progress appearances. If the team has already exceeded the ceiling, show that state and do not rewrite history.

Maximize projected points. Tie-break by fewer acquisitions and fewer lineup changes; never add zero- or negative-value games merely to hit 55. Offer a separate **Reach the cap** scenario that maximizes feasible GP up to the limit and then projected points, displaying the point tradeoff against the recommendation.

For fixed rosters, weighted matching/min-cost flow is sufficient for the basic assignment problem. Roster-subset minimization and sequential add/drop decisions introduce binary roster-state constraints; use an exact mixed-integer or constraint-programming solver for those. Select the dependency during implementation after a small correctness/performance spike. Prefer one authoritative optimizer in the Python pipeline to duplicated Python/JavaScript logic.

Every solve records objective, assumptions, time limit, status, best bound/gap when available, input versions and execution time. “Optimal” and “minimum pickups” require a proven result within the declared eligible candidate pool. Time-limited search returns “best plan found”; it cannot prove a smaller acquisition count impossible.

## Acquisition planning and player protection

Evaluate the entire acquisition sequence, not individual players' weekly game counts. A pickup with four scheduled games may add zero usable games if they all fall on full nights. Dropping a player can also remove valuable future starts or create a new position gap.

For each scenario, model ownership over time, claim submission and processing, waiver availability, bid affordability, remaining claims in each reset window, and every intermediate roster/status limit. Failed bids are conditional alternatives, not guaranteed acquisitions. Use an existing vacancy when legal; do not require an unnecessary drop. Do not assume a dropped player can be reacquired immediately.

Compare each plan with the fully optimized **no-add roster**, using net points and net starts after subtracting the dropped player's lost contribution. A pickup can be worthwhile at 55 already if it replaces a weaker game. Conversely, fewer than 55 can remain the best points outcome.

Protection is a hard constraint: ownership above 70%, manual lock, or unknown/stale ownership excludes a player from drops. A manual unlock cannot defeat the above-70% rule. At 70% or below, show current/historical FP/G, role, injury context, available dynasty ranking evidence and a proposed 2–4 week schedule comparison. Rank/projection sources remain separate. Low ownership or a busy-week benching alone must not be presented as evidence that a player is expendable.

Return a comparison table for each permitted acquisition count: maximum feasible GP, best projected points, named sequence, gain versus no adds, remaining gap, and feasibility/proof status. Identify the fewest acquisitions capable of reaching the cap, but recommend the points-maximizing plan. If all allowed plans fall short, say why: unavailable candidates, timing, protected roster, positional limits, injuries or schedule capacity. If a searched subset is incomplete, qualify that conclusion.

## Fantrax integration and historical comparisons

Fantrax's official [feature list](https://www.fantrax.com/premium-league-features) lists auto-start active players and optimal/projected standings. It does not establish that those tools enforce this league's 55-game ceiling or implement the requested 90/10 projection.

The October 29 read-only team-preferences inspection showed “Automatically submit lineup changes” and “Apply lineup changes to future periods by default.” Those settings do not by themselves establish an optimization algorithm. Neither was changed. The attempted standings inspection timed out, so the exact optimal-lineup toggle semantics remain unverified.

Use an initial evidence task to establish:

- What the auto-lineup action optimizes, which period it affects, whether it submits immediately, how it treats injuries/positions, and whether it respects the matchup ceiling. Do not execute it merely to investigate; inspect help/previews or use an explicitly authorized test later.
- What the standings toggle measures: actual versus projected production, daily versus period-wide optimization, available roster/status pool, GP ceiling, and any historical roster reconstruction.
- Whether accessible exports or supported read interfaces provide repeatable snapshots. Existing public roster endpoints do not yet supply the full planning contract.

Keep four comparison labels distinct: **Actual credited result**, **Recommended before games**, **Best possible after results**, and **Fantrax optimal**. Reuse the same eligibility and scoring rules where verified; disclose differences instead of forcing totals to agree.

Historical optimal analysis needs dated daily rosters/transactions, eligibility/status changes, actual starters, actual player-game points, credited GP, and historical rules. Today's roster or a season-end snapshot cannot reconstruct a week. Existing historical scores alone are insufficient. Start saving these snapshots prospectively in the MVP; backfill only periods with enough evidence.

For fair model evaluation, use FP/G and injury information available before each historical decision. A hindsight optimum can use actual outcomes, but must be labeled hindsight and respect the roster available on each date. Separate missed starts from start/sit hindsight differences and projection error; do not call every unpredictable breakout a managerial mistake.

## Existing assets and missing inputs

| Input | Available foundation | Required work |
|---|---|---|
| Team/player identity and ownership | `build_dashboard.py`, `player_identity.py`, reviewed roster imports | Fresh roster capture, dated changes and stable franchise mapping. Current bundle roster capture is October 26. |
| FP/G and scoring | `build_nba_stats.py`, `docs/data/nba_stats.json`, exact YK weights | Fresh cutoff, GP/season completeness, historical blend. Current results stop at October 25. |
| Lineup slots/rules | Saved public settings plus authenticated rules capture | League-specific multi-position eligibility, flex acceptance, IR legality, center-count semantics, effective limits. Existing display position/lineup slot are insufficient. |
| Matchup history | `recover_league.py`, saved completed results | Structured start/end dates and IDs for current/future/extended periods and playoffs; current results collection excludes these. |
| NBA schedules | Existing game collection and visible roster schedule views | Future game IDs, teams, league-local dates, start times, postponements and schedule revisions. Weekly game counts alone are insufficient. |
| Availability and ownership % | Visible Fantrax views, not yet normalized | Player-level injury windows, capture time, ownership %, candidate availability and complete player-pool coverage. |
| Acquisition constraints | Photos, rules, roster claims-remaining field | Used/pending claims, reset windows, processing/effective times, bid budget and waiver clearance. |
| Historical optimal | Actual matchup totals and partial daily NBA results | Daily lineup/roster/eligibility records and credited scoring; publish coverage limits. |

## Implementation structure

Preserve the static GitHub Pages frontend and existing offline, validated publication pipeline. No frontend Fantrax credentials or authenticated requests.

| Proposed location | Responsibility |
|---|---|
| `scripts/import_lineup_evidence.py` | Normalize schedules, rules, daily roster/eligibility, injury/ownership and claim snapshots; reuse reviewed identities. |
| `scripts/lineup_optimizer.py` | Pure optimization model, projection blend, scenario handling, acquisition plans and roster-depth queries. |
| `scripts/build_lineups.py` | Build team/period results and diagnostics with exact source hashes and coverage. |
| `scripts/rebuild_public.py` | Optional lineup bundle generation and validation before atomic promotion; retain last valid release on failure. |
| `docs/data/lineups/<hash>.json` | Versioned, allowlisted inputs/results; link to the matching dashboard edition. Split by period/team if size warrants. |
| `docs/lineup.html`, `docs/js/lineup-ui.js` | Period navigation, daily lineup, usage tables, scenario comparisons and missing/stale states. |
| `docs/js/dashboard.js`, `docs/team.html`, `docs/css/yk.css` | Team-profile link/tab and shared styles/navigation. |
| `private/lineup_snapshots/` | Raw captures, acquisition details, injury/projection history and replay evidence outside public assets. |

Core contracts: period ID/dates/timezone/effective cap; rules version; player/team/game IDs; dated eligibility/status; FP/G components and evidence cutoffs; ownership/protection; claim reset/effective times; locked assignments; credited GP; scenario objective; assignments/acquisitions/bench reasons; source freshness; solver status.

Manual protections and personal candidate plans belong in private/local state. A public league page must not expose pending claims or personal bid strategy. In the static MVP, precomputed scenarios work immediately; changing private protection settings requires a local recomputation/import workflow. If instant arbitrary what-if solving is desired, explicitly add a local service or browser solver in a later milestone rather than pretending static filters recompute an optimum.

Weekly refresh is too slow for lineup advice. Add refresh capability on demand and around decision windows, with visible per-source timestamps. Implement freshness gates before publishing actionable recommendations. Scheduling a recurring collector or automatic roster changes requires a separate implementation task; none is created by this plan.

## Delivery sequence and acceptance

1. **Rules and data spike.** Capture one complete upcoming matchup plus an irregular period. Verify cap treatment, rounding, eligibility, locks, claim windows, acquisition timing, and Fantrax comparison semantics. Produce one normalized, dated fixture and a data-coverage report.
2. **Current-roster MVP.** Ship the linked page, points-first weekly solver, daily lineup, bench explanations, injury scenarios, roster usage, minimum-player analysis and current-period replanning. Save decision-time snapshots from day one.
3. **Acquisition planner.** Add protected-player handling and 0–4-claim scenarios, chronological add/drop plans, net contribution and future drop context. Extended matchups respect each weekly reset. Named plans remain conditional on successful claims.
4. **Historical/future analysis.** Add several-week positional coverage, retrospective optimal comparisons on supported periods, and projection replay without future-information leakage.
5. **Optional lineup execution.** After explicit implementation authorization, add preview/dry run, fresh-state/lock validation, conflict handling with Fantrax auto tools, idempotent writes, result verification and an audit log. Lineup execution and acquisition/bid execution are separate capabilities; do not combine them implicitly.

Meaningful acceptance cases:

- Multi-position assignment fills a scarce slot where naive FP/G sorting fails; no player is counted twice.
- Crowded Wednesday benches excess players while thin Thursday exposes exactly which positions can be filled. A team with no NBA game cannot be streamed into a start.
- The weekly plan retains a later high-value game over an earlier low-value start when the cap binds; negative-value games can remain unused.
- Credited GP plus reserved in-progress games plus future planned starts stays within the ceiling; DNPs and postponements trigger correct replanning.
- Missing-current, missing-history, zero-GP and small-sample projections are labeled; all valid estimates retain 90/10 weighting.
- Ownership at 70.01% is protected, 70.00% is eligible for consideration, manual locks always hold, and missing/stale ownership blocks drops. Injured stars remain protected.
- An add/drop producing four raw games but losing three useful starts reports only the actual net gain; it can be rejected on points.
- Late processing cannot claim an already locked game's points; failed bids do not become owned players; intermediate roster/IR states stay legal.
- A matchup spanning Monday uses the correct remaining allowance in each window; nonstandard period limits use verified rounding/override.
- Minimum-player and minimum-acquisition claims agree with exhaustive tiny fixtures; timeouts and incomplete candidate pools never claim proof.
- Hindsight comparisons use dated rosters and position eligibility; missing history yields unavailable results, not fabricated optimal totals.
- Small-screen/keyboard use, direct links/back navigation, stale/missing inputs, deterministic rebuilds and failed-refresh retention work within the existing dashboard.

First build recommendation: complete the data spike and current-roster MVP before the acquisition solver. That produces useful daily decisions and a defensible answer to “how much of my roster do I need?” while the more complex transaction timing and protection rules are verified.
