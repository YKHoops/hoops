# Trade feature integration result · October 26, 2026

The current interface now includes the shared grades explorer, detailed trade cards, profile badges, report-card selectors, separate observed production and source-specific rank/projection comparisons, and qualified pick paths. See `yk_working_copy/TRADE_FEATURE_INTEGRATION_PLAN.md` and `yk_working_copy/REPAIR_NOTES.md` for implementation and validation.

All 138 archive rows are accounted for (136 linked, two duplicate aliases); 25 retain uncertain side attribution. Repaired grades require complete paired seasons and remain unassigned with current evidence. Original-pick outcomes remain unresolved. 45 Python and 22 JavaScript checks pass; desktop/mobile and missing-evaluation behavior are verified. The offline release is deterministic and retains the last valid output on failure. Local review branch only; main publication is pending.

---

# Weekly refresh · October 26, 2026

This section supersedes dated coverage below. Recurring validated publication is authorized to YKHoops/hoops, `main` / `docs`; the blue/white design is unchanged.

- **Target and rosters:** public league settings verify `noz9r7uxmphcb74p`, season 2026–27, unchanged team IDs and YK scoring. 244 unique roster players across ten teams (previously 233). The reviewed run is selected explicitly by private `target/approved_run.json`; failed/newer unreviewed runs cannot silently become build inputs. Owner mappings and the October 21 verified roster rules are retained; no rollover ID or owner discovery is inferred.
- **NBA results:** 400 players across 43 completed regular-season games, through October 25 in America/New_York (previously 68 / 3). Refreshed October 20–25 with the one-day correction overlap and bounded requests. Every collected game's player points reconcile to both official team scores. A confirmed coach-decision nonparticipant with `MIN=--` is excluded without adding GP; other missing-minute rows still fail validation. The first rejected refresh retained the prior snapshot.
- **League results:** Week 1's five matchups reconcile to official wins, losses, ties, points for and points against. Total historical/current coverage is 65 completed regular-season periods / 325 matches. Week 2 is explicitly in progress; future 0–0 placeholders do not become ties. Displayed coverage and current-period labels now come from data.
- **Rankings:** promoted October 26 Smart Draft Board top-25 and Hashtag 30-player ROS preview, keeping the custom-category list and derived YK model separate. 9cat's revised final four ranks retain its October 14 publication date. Dizzle, NBC, RotoWire, Hashtag dynasty and all 1,287 Fantrax projection rows were compared; unchanged lists retain their original freshness. Fantrax's 574-player model remains capture-only dated October 21 and covers 242/244 current roster players. Dynasty category coverage is 244/244. Manual ALL ACCESS/Lawson lists remain dated historical sources. Prior blocked discovery was not repeated.
- **Trades and uncertainty:** current executed-trade view is unchanged (31 current-season rows); canonical combined transfers remain 390 and reconciled legacy/workbook events remain 146. Claims/drops, pre-2022 results, historical operators and conditional/original pick outcomes remain incomplete. No new ownership or pick outcomes are inferred.
- **Validation:** 32 Python and 16 JavaScript checks pass, plus changed-JavaScript syntax checks. October 21 fixed counts remain baseline regressions, with additional source-reconciled roster/game/period checks. Desktop (1280px) standings and NBA filters, phone (390px) team filter and bubble detail dialog checked without page overflow. Source/horizon coverage, unique roster totals and score-proportional bubble area remain validated. Private evidence, raw authenticated captures and regression snapshots stay outside public assets and GitHub.

Run evidence and publication receipt: `yk_working_copy/private/weekly_runs/2026-10-26/`. Next NBA refresh starts October 25 for one-day overlap, through the previous New York calendar day, in batches of at most seven dates. Continue using the existing offline rebuild after reviewing/promoting inputs. Do not rerun dated bootstrap ranking import scripts over these newer snapshots.

---

# Repair review update · October 21, 2026

This update supersedes older coverage/verification claims below; the original plan remains as historical context. Full results and refresh commands: `yk_working_copy/REPAIR_NOTES.md`.

1. **Identity and contracts:** verified target 2026–27 H2H points, roster limits, GP enforcement and standings ties from signed-in Fantrax. Current display labels and franchise mappings checked; historical operator transitions remain qualified.
2. **Collection/build:** retained basketball collectors; added bounded NBA refresh, offline authenticated-UI import, canonical transfer reconciliation, cached source hashes and validated snapshot promotion. 575 complete prior-season player totals, 68 current players across three final games, 64 regular-season periods/320 matches, 390 explicit transfer observations. All official weekly standings totals reconcile.
3. **Page parity:** weekly replay/comparison, all-team historical chart, evidence-based ownership replay, trade activity/routes/destinations/production, draft comparisons/retention/historical ranks, and linked stats/profile filters implemented within the existing static shell.
4. **Rankings:** full dynasty points list browsable; current general points separate; 574-player Fantrax full-season YK projection covers 231/233 roster players. Independent exact-YK expert source still 25. Capture-only freshness is unknown. Categories, points, ROS/full-season and single models stay separate; equal-weight mean ranks only for compatible independent lists.
5. **Bubbles/review:** 233 unique player bubbles, ten teams, score-proportional area and explicit coverage; 28 Python and 15 JavaScript checks; final 20 desktop/mobile route checks. Blue/white artwork retained. Prepared `yk_github/` diff; publication subsequently authorized by the user on October 21, 2026.

Remaining: complete claims/drops, pre-2022 weekly history, exact historical operators, conditional/original pick outcomes, older daily post-trade production, full independent exact-YK ranking lists and authenticated scheduled refresh. Empty Fantrax draft slots do not resolve picks. These gaps are visible, not fabricated.

---

# YK basketball dashboard port plan

## GitHub Pages publication — 2026-10-21

Published to the user-selected repository [YKHoops/hoops](https://github.com/YKHoops/hoops), commit `4418f8fd12cfb781c1dd9d0834a8e4985e2e8e44`, using its existing `main` / `docs` GitHub Pages setup. **Live dashboard: https://ykhoops.github.io/hoops/**. [Deployment](https://github.com/YKHoops/hoops/actions/runs/39648286075) completed successfully. Seven live HTML, JavaScript, CSS and data files match the committed snapshot byte-for-byte. Local checkout: `yk_github/`; receipt: `yk_working_copy/private/github_deployment_receipt.json`.

Only the static dashboard and updated README were committed. Existing repository collectors and historical source files remain intact; the README warns that legacy rankings writers require adaptation to the new schema. Known scoring/source/history gaps remain visible. This GitHub Pages address supersedes the earlier Sites destination for future publication. The earlier Sites deployment remains unchanged.

## Earlier Sites snapshot — 2026-10-21

Published at the user’s request through Sites: [YK Dynasty Basketball](https://yk-dynasty-basketball-2026.noisyfawn1024.chatgpt.site). Deployment succeeded; audience remains Sites’ default **owner-only**. This publication supersedes the earlier no-publishing gate.

The isolated hosting checkout is `yk_site/`, with only the validated `yk_working_copy/docs/` snapshot copied into `dist/`. Private evidence, collectors, archive source, and credentials are excluded. Site identity is retained in `yk_site/.openai/hosting.json`; deployment/version/source receipt is `yk_working_copy/private/deployment_receipt.json`. Existing data limitations remain visible and unchanged. The user subsequently selected GitHub Pages as the publishing destination; see the latest publication above.

---

## 2026–27 rankings release candidate — 2026-10-21

**Latest status:** implemented locally in `/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball/yk_working_copy`. This section supersedes the dated implementation notes below. Rankings Explorer → Team Bubble Rankings → visual/verification pass are complete. **No publishing.** Evidence gaps are retained, not certified complete.

- **2026–27 roster:** refreshed the three previously successful public Fantrax endpoints through the existing basketball client; 233 players across ten franchises, captured **2026-10-21 17:04 UTC**. `scripts/build_dashboard.py` deliberately selects the reviewed run at `private/target/runs/2026-10-21T17-04-30.964717+00-00/`; ordinary builds are offline. It defaults to 2026–27 while preserving 2022–23 through 2025–26 snapshots unchanged. NBA positions come from the player directory; lineup slots remain separate.
- **Identity:** stable franchise keys retain historical continuity; `operators_by_season` and current roster `operator_name` show **Jared Sands / The Unction** in 2026–27, using the supplied Year VII report and workbook’s Logan (Sands) annotation. This does not rewrite Berke’s prior seasons or claim an authenticated Fantrax owner check. Nine other teams use existing exact team-name mappings. All roster IDs are unique.
- **Scoring:** current public settings reconfirm head-to-head points, **PTS + REB + 2AST + 4STL + 4BLK + 2FGM − FGA + FTM − FTA + 3PM − 2TO**, 10 active / 10 reserve main slots. Current standings, weekly results and NBA production are unavailable in this bundle; the interface never substitutes 2025–26 performance. Full eligibility, enforcement, ties and authenticated operator verification remain open. The known blocked owner endpoint was skipped rather than rediscovered.
- **Explorer:** `docs/rankings.html`, `docs/js/rankings-engine.js`, `docs/js/rankings-ui.js`. Reuses the old YK page’s useful filter/ownership concepts in the shared baseball-derived shell; discards stale embedded owner fields and exact-name statistics joins. Dynasty/Current Season, full-season/ROS, points/categories, player search, My Team/team, multi-position eligibility, availability and source filters work with URL state. Individual ranks, equal-weight mean, independent source count, rank spread, standard deviation in details, dates and freshness are visible. Missing ranks are null; single-source and uneven coverage are explicit. Lists older than 90 days are marked dated. Current and historical source seasons never mix automatically.
- **Bubbles:** `docs/team_rankings.html` uses the same selected sources and engine. Ten ranked team rows, position groups/colors, focusable player bubbles with hover titles and tap/click details, expandable source tables and team/profile links. All roster statuses count once; first listed position chooses a single display group. **Score = 100 / (1 + (mean rank − 1) / 25)**; rank 1 → 100, 26 → 50, 101 → 20. Diameter = **54 × √(score/100)** pixels, so area is proportional to score without a minimum-size distortion. Missing ranks have no score and an outlined “?” marker. The **roster-strength index** sums known scores, with ranked/total and full-source coverage shown; ties share rank, fully unknown teams have no rank/index. This is neither market value nor predicted wins. Generic pick tiers and speculative pick values are excluded.
- **Imports/cache:** `scripts/fetch_ranking_evidence.py` caches public evidence outside `docs/`, records failures and skips known blockers. `scripts/build_rankings.py` parses those caches and existing supplied JSON. `scripts/ranking_import.py` validates metadata, exact points coefficients, positive ranks, unique IDs, reviewed name/ID pairs, older replacements and unexpected coverage shrink; retains immutable per-source snapshots before atomic promotion. `source/rankings/*.json` is the reusable normalized source cache; `docs/data/rankings.json` is the public bundle. The browser supports dated JSON imports, allowlisted fields, last successful local snapshot and five prior manual-import states. Invalid imports retain the working snapshot. `docs/data/ranking-import-template.json` documents the input shape; it is an example, not a real source. Original rank gaps remain intact.
- **Design:** navy/blue/white theme variables and original supplied artwork are retained. The husky brands the shell, arena/draft/history art stays in its existing slots, and the supplied wordmark now anchors both ranking views. The unused arena poster remains available as an asset. No framework/build step or collector replacement was introduced. Overview and team pages link into rankings.

### Ranking inventory and compatibility decisions

Supplied material was inventoried before new research. Source rows retain publisher, URL (or explicit unavailable original URL), publication date, season, format, horizon, original rank, player ID, import time, coverage and raw SHA-256. Live sources are cached as evidence; no publisher prose or raw webpages are shipped publicly.

| Source / exact local evidence | Date / group | Decision |
|---|---|---|
| `source/yk/docs/data/rankings.json`; original `YK_Dynasty_History.zip!/YK_Dynasty_History/Info/ALL ACCESS - NBA Dynasty Rankings (February 18, 2026).xlsx` | 2026-02-18 filename date; 2025–26 nine-category dynasty | 527 rows in historical view only. Original source URL unavailable. Nikola Đurišić and Garrett Temple remain unresolved IDs/ownership. Existing JSON reused. |
| `/Users/Mattzujewski/Downloads/YK Dynasty Basketball.xlsx`, `Player rankings (Lawson Ranks)`; `/Users/Mattzujewski/Downloads/yk_trade_analysis.xlsx`, `Lawson Rankings`, `Current Snapshot`, ranking tracker | February 2026 and older revisions | Duplicate publisher history, not independent votes. Scoring and original URL unverified; excluded pending a compatible dated import. |
| `source/yk/docs/data/player_cards.json`; analysis workbook `Player Cards` | Generated 2026-02-24; cumulative production | Audited: Jokic composite 19,134 approximately equals Σ(FP/G × GP), 19,134.27 across recorded seasons. Reject as dynasty consensus/current projection. |
| Year VI/VII DOCX reports; workbook `Offseason PPG Projection` | Team opinions / old 2022 projections | Context only, no independent overall player-ranking source. |
| [Hashtag dynasty](https://hashtagbasketball.com/fantasy-basketball-dynasty-rankings); `private/ranking_evidence/hashtag_dynasty.html` → `source/rankings/hashtag_dynasty.json` | 2026-09-24; 2026–27 nine-category dynasty | 392 players after excluding eight generic pick tiers from the 400-entry list; keeper ranks ignored. Original rank gaps preserved. |
| [Dizzle public workbook](https://docs.google.com/spreadsheets/d/1EmReTa5KUcFFMCy8Fq-NpQG3WU0pMY7XNW54G3EPbEM/edit); `private/ranking_evidence/dizzle.xlsx`, `October 2026 Dynasty Ranks, 9Ca` → `source/rankings/dizzle.json` | 2026-10-13 tab date; 2026–27 nine-category dynasty | 450 players. Only the October category tab; older revisions and RotoBaller republication are not additional votes. Points tab quarantined: YK coefficients unverified. |
| [NBC / Rotoworld](https://www.nbcsports.com/fantasy/basketball/news/fantasy-basketball-2026-27-preseason-top-200-rankings-wemby-jokic-sga-headline-the-board); `private/ranking_evidence/nbc_categories.html` → `source/rankings/nbc_categories.json` | 2026-10-07; 2026–27 full-season nine-category draft list | Published 200 overall ranks; editorial availability judgments remain part of this source’s ordering. |
| [9cat.app](https://9cat.app/rankings/); `private/ranking_evidence/ninecat.html` → `source/rankings/ninecat.json` | 2026-10-14; 2026–27 full-season nine-category projections | Published top 200, per-game overall rank, all nine categories, no punts. Distinct method from editorial rankings, same format/horizon. No conversion to YK points. |
| [Smart Draft Board ESPN](https://smartdraftboard.com/espn-fantasy-basketball-rankings); `private/ranking_evidence/smartdraft_points.html` → `source/rankings/smartdraft_points.json` | 2026-10-21; 2026–27 full-season YK-compatible points | Exact scoring weights match YK; overall ranking is VORP-based. Public top 25 only, single-source and partial coverage explicitly labeled. |
| Hashtag ROS; `private/ranking_evidence/hashtag_ros.html` | 2026–27 ROS, public 25-player preview | Default TO weight 0.25, H2H mode and 20% missed-games penalty are incompatible with the standard category group. Full compatible dated import needed; no paywall bypass. |
| RotoWire standard points; `private/ranking_evidence/rotowire_points.html`; FantasyPros ESPN / Yahoo-on-NBA candidates | Format/access unresolved | RotoWire coefficient compatibility unverified; FantasyPros dynamic table unavailable; NBA.com retrieval rejected. Stop discovery and support manual exports. No silent substitution. |

All five active 2026–27 sources match reviewed Fantrax identities; suffix variants and Jaylin/Jalen Williams ambiguities are explicit audited mappings, not fuzzy merges. Dynasty categories provide **two independent sources / 464 ranked players / 233 of 233 rostered covered**. Current-season categories provide **two sources / 224 ranked players / 187 of 233 covered**. YK points provides **one source / 25 of 233 covered**. No compatible dynasty-points or ROS lists are currently loaded; those combinations show unavailable/unknown states rather than borrowed ranks.

### Milestone acceptance results

| Milestone | Result / remaining evidence |
|---|---|
| 1–3: identity, collection safeguards, page parity | Preserved and regression-checked. 2026–27 public roster promoted separately; historical snapshots retain their seasons. Authenticated owners and full rules remain documentary/verification gaps. No claims of complete transaction, pick-outcome or weekly history. |
| 4: reproducible rankings | Implemented. Source inventory, compatibility partitions, publisher deduplication, ID/alias audit, dates, original ranks, null handling, import validation and immutable last-success snapshots verified. Hand check: Jaren Jackson ranks 38 and 35 → mean **36.5**, spread **3**, score **41.3223**. No projected player/team fantasy totals are asserted as official Fantrax results. |
| 5: bubbles and local release candidate | Implemented. **233 unique bubbles / ten team rows**, no duplicate multi-position contributions; same engine powers both views. Formula and rendered dimensions checked. Current categories leave **46 unranked** markers; unknown scores stay null. No pick valuation inferred. |
| Automated checks | **17 Python + 8 Node tests pass**: data/scoring/ownership regressions, compatible horizons, means/ties/missing coverage, source rejection, last-success preservation, manual ID/name mismatch, public field allowlists, roster totals and proportional bubble area. Syntax checks pass. |
| Desktop/mobile | **16 route checks** across 1440×1000 and 390×844: overview, Sands team, players, standings, drafts, history, rankings, bubbles. No page-level overflow/load errors or console warnings/errors observed. Checked My Team + position, search, source deselection, YK points/ROS empty state, 2025–26 ALL ACCESS, unresolved identities, details/expansion/focus restoration, mobile drawer and rejected JSON import with snapshot retained. Wide tables/team lanes scroll inside their panels. |
| Evidence / delivery | `tests/artifacts/rankings-browser.json`, `rankings-desktop-bubbles.png`, `rankings-mobile-bubbles.png`; static preview [Explorer](http://127.0.0.1:8879/rankings.html) / [Team bubbles](http://127.0.0.1:8879/team_rankings.html). No deployment, publishing or recurring automation. |

**Remaining gaps:** broader verified YK-points lists, compatible ROS imports, two old ALL ACCESS identities, authenticated owner/rule checks, current performance data, full transactions/weekly coverage and unresolved pick lineage. These are visible data limits; no missing rank becomes zero, no missing trade establishes startup ownership, and no draft selection alone resolves an original pick chain.

---


## Blue-and-white context refresh — 2026-10-21

Implemented only in `/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball/yk_working_copy`. Original attachments and archive copies remain unchanged. No rankings additions or publishing.

- **Design:** adapted the active `docs/css/dashboard.css` palette to navy/blue/white, added responsive artwork treatments in `docs/css/yk.css`, and updated shared branding and all HTML favicons/theme metadata. The original baseball CSS remains unchanged in `source/baseball/docs/css/dashboard.css`. Navigation, preference, search, filters, dialogs, profiles and buildless delivery remain intact. Supplied originals are in `docs/assets/yk-husky.png`, `yk-arena.png`, `yk-draft-court.png`, `yk-history-collage.png`, `yk-arena-poster.png`, and `yk-wordmark.png`; the first four are used in the active design and the latter two are retained for later use.
- **Data:** `scripts/import_context.py` extracts narrowly bounded workbook ranges into `source/context/supplied_context.json`; normal builds reuse that JSON. `scripts/build_dashboard.py` normalizes documented owners and exact player matches, preserving the source labels. The public bundle adds **123 draft selections**, **144 future holdings**, and **10 dated summer 2026 trades**. Selections are sorted by round/slot, searchable by player/picker, and carry source cells plus expandable raw text. Future picks retain protection footnotes and extend through 2033. New trade records are visible under **Trades → Summer 2026 updates**, separate from the 138 archived records and their legacy report calculations.
- **Season mapping:** summer draft year is explicitly mapped to the incoming season (2021 → 2021–22 through 2026 → 2026–27). The derived trade-analysis workbook labels 2021–2025 drafts by the preceding season; dated primary recap headings take precedence. Draft year/future-pick year controls are independent of the top-bar saved-roster season and state this visibly.
- **Ownership/rules:** Year VII identifies **The Unction → Jared Sands**. The primary workbook labels the former Logan slot “Logan (Sands),” but the precise handover date and authenticated owner verification remain open. The Year VII **55-GP** maximum supersedes the February constitution's **50-GP** maximum as documentary evidence; current Fantrax enforcement remains unverified. Archived 20 main / 2 G-League / 4 IR slots, G-League eligibility and the primary-center cap are summarized as archived rules. The report's Jowkar championship claim is shown separately from partial saved standings.
- **Uncertainty:** multi-owner draft annotations are not collapsed into a guessed picker. Explicit post-draft trade notes do not alter the recorded selector. The 2026 redistribution sheet has proposal language and empty selection columns, so no outcomes are fabricated. The 138 legacy pick outcomes remain unresolved: selection records alone do not establish original-pick/protection lineage. Compensatory rounds, full trade reconciliation and exact operator transitions remain follow-up work. Saved rosters/stats remain labeled 2025–26 rather than being relabeled current.
- **Verification:** **13 Python + 2 Node checks passed**, including new attachment counts, source cells, draft chronology, missing-evidence rejection, ambiguous picker preservation and protected-pick text. **10 desktop route/view checks at 1440×1000 and 8 mobile checks at 390×844** found no page-level overflow or load errors. Reviewed overview/draft/history artwork, mobile navigation, draft-year changes, player search, Sands filtering, protection notes and summer-trade search. No browser errors or warnings observed. Evidence: `tests/artifacts/context-refresh-browser.json`, `blue-desktop-overview.jpg`, `blue-desktop-drafts.jpg`, `blue-mobile-overview.jpg`.

### Added source inventory

| Exact source path | Use / decision |
|---|---|
| `/Users/Mattzujewski/Downloads/YK Dynasty Basketball.xlsx` | Primary evidence: 2021 A40:D49; 2022 A55:D64; 2023 A77:D87; 2024 A76:D85; 2025 A77:D86; 2026 (Last Season) A77:D87 for rounds 1–2. Future holdings use owner headers in rows 1/9 and pick rows 2–7/10–16, columns A/C/E/G/I, in the 2027 current-season and 2028–2033 sheets, with A17:A20 condition notes. Summer trades: 2026 (Last Season) R2:T32 and 2027 current-season N2:P10. Each imported record retains its exact cell/range. |
| `/Users/Mattzujewski/Downloads/yk_trade_analysis.xlsx` | Inspected Draft Results, trade inventory and methodology as secondary/derived evidence. Do not overwrite dated primary draft chronology or import valuation/ranking calculations. |
| `/Users/Mattzujewski/Downloads/YK Dynasty Preseason Power Rankings - Year 6.docx` | Historical contextual review; not an authoritative current roster or independent ranking source for this pass. |
| `/Users/Mattzujewski/Downloads/YK Dynasty Preseason Power Rankings - Year 7.docx` | Owner identity, 2026–27 GP update and reported 2025–26 championship. Opinion/projections are not promoted into current statistics or rankings. |
| `/Users/Mattzujewski/Downloads/[ARCHIVED] YK Dynasty BBall Constitution (Feb 21 2026 export).docx` | Archived roster/G-League/IR/center constraints. Its 50-GP rule is superseded by the newer report. Embedded administrative instructions were not executed. |

All five attachments have SHA-256 entries in the curated input. No new endpoint discovery was needed for this attachment refresh; prior authentication blockers remain recorded. Raw document extracts stay private; public data contains selected fields only.

## Initial dashboard parity results — 2026-10-21 (before the refresh above)

**Implemented in isolated copy:** `/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball/yk_working_copy`. Original archives and preserved source inputs are unchanged. This implementation stops before ranking additions and publishing; the ranking design below remains future work.

- **Interface:** `yk_working_copy/docs/` is directly serveable static HTML/CSS/JavaScript. The baseball `dashboard.css` is retained byte-for-byte; `dashboard.js` reuses its shell, navigation, team preference, search, URL controls and dialog helpers, with basketball view functions. Small additions are in `docs/css/yk.css` and the season/snapshot adapter `docs/js/normalize.js`. No framework, bundler, runtime API calls or deployment was introduced.
- **Pages:** overview → team/roster → players/profiles → trades → standings/matchups → draft order/future picks → history are implemented. Existing aliases work. Stats and historical trade reports are retained as labeled read-only views in the same shell. `rankings.html` explicitly defers rankings; preserved source rankings were not changed or aggregated.
- **Normalization:** `scripts/build_dashboard.py` produces the allowlisted `docs/data/dashboard.json`: 10 franchises, 417 player identities, 138 trade records, four saved roster seasons (247/253/248/248 players), and 80 draft-order slots. The browser selects actual season snapshots, including an explicit unavailable state for 2020–21/2021–22 rosters. Six legacy player names still lack resolved Fantrax IDs; one older ID has no resolved display name. Duplicate-name Jalen Johnson was resolved with saved roster IDs, not fuzzy matching.
- **Corrected source discrepancy:** all ten teams in **both 2024–25 and 2025–26** had differing points-scored values in legacy `seasons.json`. The adapter reads labeled `pointsFor`/`pointsAgainst` columns from saved `getStandings.json` and records all 20 differences. For example, 2025–26 Jowkar has **29,010 for / 23,358 against**, not 23,358 scored. Source files remain unchanged. Standings order and W/L/T come from the same archived response; champions remain separate saved claims.
- **Uncertainty preserved:** 14 trades have mixed/multi-party sender records and retain unknown recipients. No untraded player is labeled a startup acquisition; roster observations do not establish continuous ownership. All four draft responses have empty scorers, so 80 selection results and all 138 legacy pick outcomes remain unresolved. Vlandis/Kelley source operator labels are retained separately from the Baden franchise. Legacy grade/value reports are evidence, not validation of their inferred outcomes.
- **Collector scope:** reused `scripts/fantrax_yk.py` with narrow safeguards: explicit season/league selection, retained player IDs, exact identity aliases, private output/cache, complete team coverage, duplicate-player checks, rejection of empty team-only fallbacks, shrink protection, immutable prior snapshots and atomic writes. `scripts/collection_state.py` adapts selected baseball safety patterns. `scripts/verify_target.py` uses the same client with a bounded endpoint list. Fresh collection is staged privately; promotion into the saved-data adapter is deliberate. No wholesale collector replacement or exhaustive transaction backfill was attempted.

### Target verification and bounded blockers

Public endpoints verified `noz9r7uxmphcb74p` as **YK Dynasty, 2026–27**, **HEAD_TO_HEAD_POINTS_BASED**, with the basketball scoring group, dates **2026-10-20 to 2027-03-28**, and the scoring coefficients documented below. Public roster rules show **10 active / 10 reserve / 20 main slots**, with the ten listed position constraints. The observed roster contains **233 players / 10 teams**, including IR and minors outside the main slots.

Known prior endpoint outcomes were checked before network requests. After one restricted-network failure, each of `getLeagueInfo`, `getTeamRosters` and `getPlayerIds` succeeded once. The known `getFantasyTeams` method returned `STALE_CLIENT`; one corrective retry using the supplied baseball client's API version required authentication. Discovery stopped. No archived credentials were used or copied.

Nine target team names match saved aliases, but **current operators are not independently verified**. **The Unction** has no verified owner mapping and is not silently assigned to Berke. Full IR/minors eligibility, games limits and tie rules remain unverified. The live target roster is **not promoted**: development defaults to saved **2025–26**, with its partial standings/stats and unknown roster capture date clearly labeled. Private evidence and blockers are in `yk_working_copy/private/target/verification_attempt.json`; the public history page exposes only the allowlisted summary.

### Acceptance results

| Check | Result |
|---|---|
| Offline data regression suite | **11 Python tests passed:** seasonal counts/IDs, explicit seasons, scoring coefficients, correct points columns, no startup/pick inference, ambiguous routes, corrected owner aliases, collector IDs/fallback rejection, cache scoping and failed-write preservation, public secret/ranking exclusions. |
| Browser season adapter | **2 Node tests passed**, including en-dash input, prior-season conversion, correct historical rosters and missing-season behavior. JavaScript syntax and Python compilation checks passed. |
| Desktop / mobile | **19 desktop route/view checks at 1440×1000 and 12 mobile route checks at 390×844** rendered without page-level horizontal overflow. No browser console errors were observed. |
| Interactions | Verified selected-team persistence independent of team browsing; keyboard/diacritic player search; filters, sorting, inline expansion, profiles and dialogs/Escape; browser-back season restoration; team comparison; pick-only trades and direct dialog links; draft/future-year filters; matchup periods; mobile drawer selection and Escape focus restoration. |
| Artifacts | `yk_working_copy/tests/artifacts/browser-results.json`, `desktop-overview.jpg`, `desktop-team.jpg`, `mobile-overview.jpg`. `yk_working_copy/README.md` documents local serving, normalization, checks and staged refresh boundaries. |
| Scope gate | No ranking aggregation/bubble work, scheduled refresh, deployment or publishing. Historical report views retain existing values only. |

**Milestone status:** identity/scoring verification is partial only where listed above; collection safeguards are implemented but exhaustive historical collection is not certified; core dashboard parity is implemented and checked; ranking milestones are deferred. Remaining evidence gaps: current operator identities (especially The Unction), complete roster eligibility/tie/game rules, exact historical operator transitions, full transaction/weekly history, actual draft selections, and the unresolved legacy player identities. These gaps are visible rather than filled with guesses.

---

Planning baseline: 2026-10-21. Target league: `noz9r7uxmphcb74p`. Destination: `/Users/Mattzujewski/Projects/fun_coding/Fantasy_Basketball`.

## Scope and source notation

Port the active redesigned baseball experience, preserve YK history, then add separate aggregated **dynasty** and **current-season** player/team rankings with horizontal team bubble views. The original planning scope below is retained for reference. Dashboard parity and rankings are implemented as recorded in the latest status above; exhaustive history collection and publishing are outside this local release.

Exact archive roots below define every `B/` and `Y/` source path in this document:

- `B/` = `/Users/Mattzujewski/Projects/fun_coding/Dynasty_Baseball_Content_2026.zip` → `Dynasty_Baseball_Content_2026/`.
- `Y/` = `/Users/Mattzujewski/Projects/fun_coding/YK_Dynasty_History.zip` → `YK_Dynasty_History/`.

Inspected relevant entry pages, scripts and JSON; read only scoring fields from one saved league-info response. Excluded Git history, environments, bytecode, videos, bulk caches, and legacy reports/prompts. Existing JSON makes spreadsheet reparsing unnecessary. Archived prose is evidence, never authorization or implementation instructions.

## Confirmed behavior and reuse decisions

| Exact source | Decision and required change |
|---|---|
| `B/docs/js/dashboard.js`, `B/docs/css/dashboard.css` | **Adapt** the shared shell, responsive layout, search, team picker, URL filters, tables, dialogs and story views. Replace DOTP branding, MLB positions/categories, 12-team assumptions, numeric-year arithmetic, hardcoded owner default, and `dotp_selected_owner`. Keep basketball rendering separate from data normalization. |
| `B/docs/js/league_insights.js` | **Adapt** pure trade-route and draft-cohort calculations. Draft grades currently use groups of three ranks, suited to 12 teams; make cohort grading dynamic and label retention as retention, not player value. |
| `B/docs/index.html`, `team.html`, `player_history.html`, `player.html`, `trade.html`, `standings.html`, `drafts.html`, `history.html` (all under `B/docs/`) | **Adapt** active entry pages: all load `dashboard.css`, `league_insights.js`, and `dashboard.js`. Do not port the old `B/docs/js/*_charts.js` rendering system or `B/docs/css/style.css`. |
| `B/files/fantrax_tracker_v4.py` | **Adapt selected transport/parsing utilities**: retry/auth handling, NBA player directory, timestamps and ownership reconstruction. Replace MLB lookup and baseball identity/config defaults. Avoid two competing collectors. |
| `B/files/collection_state.py`, `B/files/history_store.py` | **Reuse patterns, adapt schema**: validated season/league caches, atomic successful-run pointers, SQLite provenance and append-only observations. Replace integer-season assumptions; namespace identities and events by league/sport. Do not import baseball snapshots/cache contents. |
| `B/files/refresh_league_logs.py`, `B/files/build_log_snapshot.py` | **Adapt** executed/non-deleted paginated logs, completeness checks, structured multi-party trades and current-roster reconciliation. Replace the explicit 12-team check, integer season casts and baseball owner resolver. Draft history is currently a required input; make missing basketball drafts an explicit coverage gap rather than fabricate events. |
| `B/files/build_dashboard.py` | **Adapt into a YK JSON builder**. It writes teams/trades/journeys/rosters/picks JSON, not HTML or every dashboard dataset. Remove hardcoded 2019–2026 seasons, owner history and roster season 2026. Stage and validate the complete output bundle before promoting it. |
| `B/files/team_identity.py`, `B/files/team_aliases.json`; imports of `B/files/fetch_standings.py`, `B/files/player_directory.py`, `B/files/structured_trades.py` | **Replace baseball identity data; retain only needed helpers** after dependency review. Basketball standings and draft adapters must satisfy the new contract; copying the main six infrastructure files alone is insufficient. |
| `Y/scripts/fantrax_yk.py` | **Adapt as the roster entry point**: public API first, authenticated fallback. Preserve Fantrax player IDs, currently discarded from saved player rows; accept explicit season/league mapping; reject unresolved identities. Unknown seasons currently fall back to the configured current league, risking mislabeled snapshots. |
| `Y/scripts/fantrax_pull.py` | **Reuse endpoint discovery only after fixes**. Its owner fallback table still misassigns Charlotte Wobnets→Jowkar, Giddey Up→Berke, Kelvin got No Dimes→Gold. It also writes raw responses beneath public `docs/data/raw`; move private evidence outside `docs/`. |
| `Y/scripts/fetch_fantrax_scoring.py` | **Adapt calculation logic**, parameterized by verified season scoring. It scrapes Basketball Reference and derives points; it does not fetch official Fantrax player scores. Replace fixed seasons and failure behavior that can overwrite output with partial results. |
| `Y/docs/js/core.js`, `Y/docs/js/dashboards/rankings.js` | **Reuse** normalization/escaping, owner colors and filter concepts; **replace** duplicated identity tables, hardcoded season controls and rankings data joins. Rankings currently use embedded `owned_by`, exact-name stats lookup, and optional player-card badges—not consensus or team bubble rankings. |
| `Y/docs/data/*.json` | **Reuse named datasets below as historical evidence**, preserving originals and provenance. Adapt through a common contract rather than forcing YK data into baseball field meanings. |

Code/data supersede README claims: `Y/README.md` lists 49 ranked players and 246 current roster players; public JSON contains **527 rankings and 248 roster players across 10 teams** for 2025–26. The 49-player list survives in `Y/Info/rankings.json`. `Y/scripts/README.md` claims stdlib-only scripts, while the roster/pull scripts import `requests`; the baseball pipeline also uses pandas/YAML. Capture actual dependencies during implementation.

## Page parity

All destinations below are planned beneath destination `docs/`. Preserve existing YK links with compatible parameters or redirects.

| Baseball experience / source | YK destination and data |
|---|---|
| `B/docs/index.html` | `index.html`: overview, selected team, recent trades and standings; `Y/docs/data/seasons.json`, rosters and trades. Replace roto points with verified basketball scoring. Add links to both rankings views. |
| `B/docs/team.html` | `team.html`, retaining `roster.html` as the all-team roster view: roster/history/comparison, acquisitions and rankings; owners, team-name history, seasonal rosters and movement JSON. Historical season selection must not silently show today's ownership. |
| `B/docs/player_history.html`, `B/docs/player.html` | Preserve `players.html` explorer and add `player.html` detail; alias `player_history.html`. Use player movement, stats, rankings and stable IDs; mark inferred/unknown dates. |
| `B/docs/trade.html` | `trade.html`: filters, partner routes, detail dialogs and asset journeys. Start with `Y/docs/data/trades.json` and reconcile `trade_details.json`; preserve picks and multi-party trades. |
| `B/docs/standings.html`, `B/docs/history.html` | `standings.html`, new `history.html`: records, points, champions and season history. `seasons.json`, `scoring_periods.json`, `matchups.json`, `head_to_head.json`. Show weekly race only for verified periods; never infer playoffs/champion from regular-season rank. |
| `B/docs/drafts.html` | New `drafts.html` plus retained `picks.html`: draft results, pick ownership and outcomes from `Y/docs/data/picks.json`, `pick_ledger.json`; reconcile actual draft selections before enabling cohort grades. A pick ledger is not a complete draft board. |
| YK-specific pages | Retheme and retain `stats.html`, `rankings.html`, `grades.html`, `trade-cards.html`, `trade-leaderboard.html`, `trade-value-over-time.html`. Their corresponding `Y/docs/js/dashboards/{stats,rankings,grades,trade_cards,trade_leaderboard,tvot}.js` are implementation reference points; keep historical grades distinct from new ranking scores. |

The baseball initializer unconditionally requests `trade_production_2026.json`; replace this with season-aware, optional basketball production data. Its draft and weekly files are page-specific. Missing optional data must leave a useful page, not fail the whole shell.

## Season and owner contract

Use `season_id` strings, separate start/end years, explicit sort order, league ID and dataset-specific coverage/as-of dates. Never cast `2025-26` to a number or assign transactions by calendar year alone.

| Season | League ID | Saved coverage |
|---|---|---|
| 2020–21, 2021–22 | Unknown in inspected mappings | Trades and NBA statistical history exist; no saved league rosters/standings. |
| 2022–23 | `n7exgxhpl1ydddam` | `Y/docs/data/rosters_2022_23.json`: 247 players; standings. |
| 2023–24 | `tz7m8b61lhphjz9w` | `Y/docs/data/rosters_2023_24.json`: 253 players; standings. |
| 2024–25 | `26ihddrglvclsxav` | `Y/docs/data/rosters_2024_25.json`: 248 players; standings. |
| 2025–26 | `sz7vm5xwmancf4tr` | `Y/docs/data/rosters_2025_26.json`: 248 players; saved standings are partial, champion null. |
| 2026–27, verified target | `noz9r7uxmphcb74p` | Public identity/scoring/season and ten team names verified. Current operators remain unverified; The Unction is unresolved. Target roster is staged privately, not used as saved-season development data. |

`Y/docs/data/matchups.json` has only 10 matchups per season: periods 16–17, 15–16, 15–16 and 14–15 respectively. `scoring_periods.json` contains season summaries, not complete weekly history. NBA stats reach back to 2020–21; that does not establish league-history coverage.

Use `Y/docs/data/owners.json`, `team_name_history.json`, and corrected mappings in `Y/docs/js/core.js` / `Y/scripts/fantrax_yk.py`. Canonical franchise IDs below match lowercase `owners.json` IDs; adapt legacy capitalized keys at ingestion.

| Franchise | Saved owner / team-name aliases |
|---|---|
| `peterson` | Kelvin Peterson; PETE/DIME; Always Droppin Dimes. |
| `jowkar` | Nick Jowkar; JOWK; Ball Don't Lie. |
| `berke` | Logan Berke; BERK; Kelvin got No Dimes → Burner account (2024–25). |
| `baden` | VLAND/KELL/BADEN/FLAGGS; Charlotte Wobnets → BKs Whoppers → Flaming Flaggs (2025–26). Franchise continuity spans Spencer Vlandis, Brendan Kelley, Sam Baden; retain distinct historical operators. |
| `delaney` | David Delaney; DELA; Freshly Washed Kings. |
| `green` | Max Green; GREEN; Ice Trae. |
| `gold` | Sam Gold; GOLD; Giddey Up → No Shaime (2023–24) → Kentucky Fried Guards (2024–25). |
| `zujewski` | Matthew Zujewski; ZJEW/Franz; Only Franz. |
| `moss` | Max Moss; MOSS; Pure Sweat Fam / Pure Sweat Farm. |
| `haletrager` | Ryan HaleTrager / Ryan Trager; TRAG/HALE; Lob Land → Twin Towers (2023–24). |

Map `(league_id, team_id)` to franchise and effective-dated operator. Do not reuse old team IDs as current IDs. Baden succession dates conflict in code comments versus JSON periods: resolve exact boundaries from dated evidence; retain uncertainty meanwhile. Refresh target membership/names instead of assuming these ten operators remain unchanged.

## Scoring and ranking-source inventory

Saved `Y/docs/data/raw/2025_26/getLeagueInfo.json` explicitly reports points scoring:

`PTS + REB + 2×AST + 4×STL + 4×BLK + 2×FGM − FGA + FTM − FTA + 3PM − 2×TO`.

Verify the target's coefficients, lineup/bench/IR/minors eligibility, scoring periods, games limits and tie rules before season rankings or trade production. Compare sample player and team totals against official Fantrax results. Existing derived totals use rounded per-game values × games played; they are approximate NBA production, not exact credited fantasy-lineup production. Version scoring by season and retain original stat precision.

| Exact source | Inventory and disposition |
|---|---|
| `Y/docs/data/rankings.json`; `Y/Info/ALL ACCESS - NBA Dynasty Rankings (February 18, 2026).xlsx` | 527-player February nine-category dynasty list; JSON already contains rank/name/position/team/age/ownership. Workbook is provenance reference only, not reparsed. JSON lacks source metadata: add date, publisher attribution/usage status and scoring-format label. Treat as one historical source, not verified points-league consensus. |
| `Y/Info/rankings.json` | 49 entries dated 2026-01-01. Legacy snapshot; establish publisher/lineage before use. Do not count it as an independent vote alongside a newer edition of the same source. |
| `Y/docs/data/player_cards.json` | 75 cards generated 2026-02-24 with `lawson_rank`, `composite`, weighted FPG/FP-minute, age and trend. Reuse as optional legacy context; incomplete coverage and undocumented composite derivation prevent treating it as an independent consensus input. |
| `Y/docs/data/player_stats.json` | 248 player records, fetched 2026-02-20; metadata season 2024–25. Inspect each record's season before use; not a current-season ranking source. |
| `Y/docs/data/player_stats_historical.json`, `fantrax_scoring.json` | NBA history 2020–21 through partial 2025–26; scoring file has 1,071 players. Derived statistics, not independent expert rankings or 2026–27 projections. Reuse only with explicit dates, scoring basis and coverage. |
| Missing inputs | No verified target-season projections or multiple independent current dynasty rankings in inspected assets. Acquire permitted, dated sources during implementation; document publisher, URL/file, scope, format, revision and rights. A single available list must be labeled single-source. |

## Ranking and bubble design

1. Introduce a player identity crosswalk: Fantrax ID first; audited name aliases for legacy/accent/suffix differences; distinct provisional IDs for prospects. Never silently fuzzy-merge players. Refresh ownership from the selected roster snapshot rather than `rankings.json.owned_by`.
2. Publish separate dynasty and current-season aggregates. Default season view is projected rest-of-season value under verified YK scoring; observed season-to-date performance is a separately labeled mode. Do not substitute 2024–25 statistics when current inputs are absent, or blend nine-category ranks with points projections without an explicit format policy.
3. Proposed consensus: equal weights across independent, compatible sources; comparable percentile scores over a declared common eligible pool; retain raw ranks, source depth, dates, included-source count and disagreement. Use one revision per publisher. Missing players are missing, not rank zero; require at least two independent sources for a consensus label. Single-source/provisional rows remain usable and visibly labeled. Document ties and ranking version for reproducibility.
4. Team dynasty score: sum normalized player values across the selected full roster, with coverage and top-player/depth breakdown. Current-season score: aggregate projected points for a legal lineup/schedule under verified settings; expose bench depth separately. Pick values require a compatible pick model and remain separate initially. Rank only comparably covered teams; incomplete teams show provisional results or unavailable status, never invented zero-value players.
5. Add horizontal bubble rankings to `rankings.html` and an overview summary: one labeled team lane per row, stronger scores to the right, sorted by selected score, Dynasty/Current season toggle. Use score-proportional bubble area as required by the updated implementation scope; show rank, numeric score, coverage, snapshot date and sources on focus/hover and in an accessible table. Team clicks open profiles. Support ties, all-equal scores, missing data, keyboard access and mobile labels. Explain that dynasty scores and projected points have different scales.

Planned outputs: `docs/data/league.json`, `players.json`, `ranking_sources.json`, `player_rankings.json`, `team_rankings.json`, plus adapted page datasets and `refresh_status.json`. Include schema version, season/league, as-of dates, scoring/ranking method version and coverage. Private raw evidence, credentials and configuration stay outside `docs/`; publish only allowlisted fields, never archived cookies or raw authenticated responses.

## Milestones and acceptance checks

| Milestone | Exit checks |
|---|---|
| **1. Establish identity and contracts** | Verify target season/sport/settings/membership; reconcile all historical team aliases and operator ambiguity. Every roster team resolves once; retained player IDs and reviewed alias matches have no collisions. Preserve historical counts above or document reconciled differences. |
| **2. Port collection and build** | Successful public/auth collection records provenance; all log pages reconcile to reported event counts; multi-party and pick-only trades survive. Draft and weekly gaps are explicit. Failed/partial runs cannot replace the last good bundle; reruns are idempotent and historical refresh cannot replace current ownership. Dependency smoke check and secret/public-field checks pass. |
| **3. Deliver page parity** | Every page/alias in the parity table loads with basketball labels and data. Verify search, team selection, season changes, deep links/back navigation, dialogs, filtering/sorting, keyboard use and mobile layout. Optional missing data does not crash pages; no DOTP/MLB assumptions remain. |
| **4. Deliver reproducible rankings** | Inventory source provenance and compatibility; deduplicate publishers/revisions; verify scoring against official samples. Hand-check player consensus, ties, missing-source handling and team aggregation. Ownership matches the chosen snapshot. Missing current projections produce a dated unavailable state, not a stale “current” ranking. |
| **5. Validate bubbles and release candidate** | Exactly one row per verified target team; ordering and scores agree with accessible tables and team profiles in both modes. Check partial coverage, ties and narrow screens. Historical records and freshness metadata reconcile; the staged public bundle contains no secrets/raw responses. Deliver a reviewable local preview; deployment is a separate action. |

Outstanding evidence: current operator identities and full eligibility/tie/game-limit settings, exact historical operator transitions, complete draft/weekly coverage, remaining player-ID matches, ranking publisher/lineage/usage provenance, and current independent ranking/projection inputs. These are implementation gates, not reasons to reparse all archives or invent missing history.
