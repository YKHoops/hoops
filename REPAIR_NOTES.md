# Trade feature integration · October 26, 2026

Implemented from `TRADE_FEATURE_INTEGRATION_PLAN.md`; the user authorized publication to `YKHoops/hoops` main / docs on October 27, 2026. The blue/white buildless shell is retained.

- Persistent `source/context/trade_event_registry.json` preserves existing event URLs across source reordering and additions. Changed/removed source records and indistinguishable new duplicates require mapping review. The archive edition is pinned; 138 grade rows reconcile to 136 linked records and two duplicate aliases across 146 canonical events. Twenty-five archived rows retain uncertain side attribution.
- `scripts/build_trade_evaluations.py` supplies one versioned contract for historical grades, repaired player improvement and observed NBA production. Historical fields are preserved; missing values remain unknown. Repaired grades retain F=0, require complete matching season evidence and all scoring inputs, and use the documented 10-GP minimum. Comparisons exclude mixed/pick-only and unresolved packages. Owner tables rank only samples with at least three eligible comparisons.
- `grades.html` and the Trades navigation expose shared player/team/My Team, partner, season, asset, method, grade, archived-confidence and coverage filters. Detailed dialogs include linked players, original before/after inputs, eligibility reasons, observed production, isolated dated ranking/projection sources and archived pick paths. Team and player trade lists use the same badges. Existing archived report URLs still work.
- **Evidence limit:** zero repaired comparisons currently qualify. Only the 2025–26 complete counting snapshot is certified; earlier snapshots are rounded with unverified completeness and 2026–27 is ongoing. Archived grades remain browsable, but new report-card GPA and model-gap rankings intentionally stay empty. All 138 original-pick outcomes remain unresolved; the displayed archived transfer associations do not certify protections, final holder or selected player.
- `rebuild_public.py` builds in a temporary workspace and validates before promotion. Immutable evaluation URLs and checksums tie each dashboard to its result bundle; the dashboard moves last. Previous public outputs survive failed builds. Unchanged NBA and ranking inputs retain build/import timestamps; a repeat rebuild changed zero public files. No new endpoint discovery or authentication was needed.
- Validation: 45 Python and 22 JavaScript tests pass. New cases cover stable IDs, duplicates, thresholds, zero/F grades, missing inputs, minimum samples, future seasons, historical operators, incomplete package comparisons, observed game deduplication, archive accounting, source freshness and failed-build preservation. Desktop 1280px and mobile 390px route checks passed with no page overflow or runtime errors. My Team/search/grade filters, modal focus return, historical/repaired/production/projection tabs and pick-path access were exercised. A separate missing-file preview confirmed the trade ledger and base dialog remain usable without evaluations.

Review evidence: `private/trade_integration_before/` and `tests/artifacts/trade-integration/`. Reviewed feature commits: `82a5172` and `89a370c`, based on release `2eabc09`. October 27 publication authorization supersedes the feature-release gate. Subsequent weekly refreshes should retain the integrated evaluation builder and matched output contract. The private publication receipt records the deployed commit and live-file verification; this feature release retains NBA data through October 25.

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

# Dashboard repair review · October 21, 2026

Local implementation: `yk_working_copy/`. GitHub review copy: `yk_github/`. Publication authorized by the user on October 21, 2026; this is the approved repair release. The approved buildless blue/white interface and graphics remain in place.

## Completed

- Weekly replay with period scrub/play, cumulative/period points or win percentage, two-team comparison, and linked profiles. All-team history chart supports metric/focus controls and accessible table details.
- Player journey replay uses dated transfers and roster observations, without inferring startup ownership or continuous tenure. Trades expose activity, partner routes, current roster destinations and NBA production; post-trade production counts only collected games after the deal.
- Draft comparisons support two classes, team filters, observed retention and historical ranks. All 123 workbook selections resolve to player identities; this does not resolve original pick lineage or conditional outcomes.
- NBA stats have independent NBA/fantasy seasons, broad available-player coverage, totals/per-game, sorting, search, team/position/availability filters, player histories and roster/profile integration. Shooting percentages use summed makes/attempts. Current results contain three completed October 20 games; no scheduled or live games are treated as final.
- Rankings expose compatible consensus and isolated source views, including dynasty points and a full-season YK model. Equal-weight mean rank remains the consensus rule. Models, unknown points formulas, categories and forecast horizons remain separate. Missing ranks remain unknown.
- Team bubbles use the same source/horizon and 233 unique roster players across ten teams. Score = `100 / (1 + (rank - 1) / 25)`; diameter = `54 * sqrt(score / 100)`, so area is proportional to score. Summed scores are a roster-strength index, not wins or market value. Picks are excluded.

## Coverage before → after

| Measure | Before | Review copy |
|---|---:|---:|
| Indexed players | 440 | 1,131 |
| NBA players 2020–21 / 2021–22 | 216 / 246 | 540 / 605 |
| NBA players 2022–23 / 2023–24 | 289 / 320 | 539 / 572 |
| NBA players 2024–25 / 2025–26 | 348 / 350 | 569 / 575 |
| NBA players 2026–27 | 0 | 68, three final games |
| Completed weekly periods / matchups | 8 / 40 | 64 / 320 |
| Unique reconciled trade events | 138 legacy + 10 workbook | 146 after two duplicate source entries removed |
| Explicit transfer observations | Not integrated | 390, from saved CSVs and 395 authenticated UI rows |
| Workbook draft selections | 123 | 123 matched; outcomes still qualified |
| Verified YK expert ranks | 25 | 25, still a preview |
| Separate full-season YK projection | None | 574; 231/233 current roster players |
| Dynasty points / current general points | Not browsable | Dizzle 450 / RotoWire 200 |

General points formulas remain unverified, so Dizzle and RotoWire are browsed independently. Dizzle covers 233/233 roster players; RotoWire covers 183/233. Fantrax's model lacks positive-GP projections for Cam Whitmore and Leonard Miller. Its date is a capture date, not a known publication date. Hashtag's separate ROS model remains a 30-player preview. ALL ACCESS remains a dated 527-player nine-category dynasty source. The legacy card composite is cumulative statistical production, not an independent dynasty opinion.

## Authenticated verification

Read-only Fantrax UI captures verify target `noz9r7uxmphcb74p`, season 2026–27, ten teams, H2H points, and:

`PTS + REB + 2 AST + 4 STL + 4 BLK + 2 FGM − FGA + FTM − FTA + 3PM − 2 TO`.

Main roster 20, active 10, reserve 10; IR 4 and minors 2 excluded from main limit; maximum five centers. Configured minors eligibility permits any player. Period GP limits are 35–55, prorated, with automatic enforcement set to “Do nothing.” Standings tiebreakers: season points for, tied-team H2H, fewest points against, random. Playoff ties favor higher seed.

All 320 regular-season results reconcile to official team wins, games, points for and points against. Current five Week 1 matchups remain separate and in progress. The 2025–26 final explicitly records Ball Don't Lie 4,429–3,888 Kentucky Fried Guards; champion is no longer inferred or missing. Current display labels and mapped franchise identities agree; exact historical operator transition dates remain uncertain. The Unction uses Jared Sands for 2026–27 and retains its historical franchise key.

Private evidence: `private/fantrax_browser/`, `private/nba_evidence/`, `private/transaction_csv/`. Public normalized fields and hashes only are promoted through `scripts/import_browser_evidence.py`, `build_nba_stats.py`, `recover_league.py`, `repair_data.py` and `rebuild_public.py`. Raw authenticated captures and credentials are excluded from the GitHub update.

## Checks and remaining gaps

28 Python checks and 15 JavaScript checks cover identity, seasons, complete scoring inputs, shooting ratios, final-game deduplication, failed-refresh preservation, official-results reconciliation, source compatibility, missing ranks, roster totals, and bubble area. Twenty final route checks at actual 1,280px desktop and 390px mobile widths found no page overflow; tables/lanes scroll internally. Player bubble dialogs, stats season/filter controls, replay and compare controls, draft comparisons and linked details were exercised. Review images and route results are in `tests/artifacts/`.

Remaining evidence gaps: full claim/drop history; pre-2022 league results; dated historical operator transitions; conditional pick outcomes and original-pick lineage; older daily NBA game histories for complete post-trade production. The current Fantrax draft grid has empty selection slots and cannot resolve picks. Older NBA snapshots retain their original partial/rounded qualifications. Fantrax 2025–26 does not provide 3PA or exact total minutes in the captured views, and current NBA affiliations are not backdated.

No automatic authenticated Fantrax refresh is configured. The validated UI captures can be re-imported offline; their three-page, 1,287-player manifest is intentionally strict and must be updated after checking a changed player pool. Public NBA refresh is bounded to seven dates, one request per endpoint, 20-second timeouts; failed fetches keep the last successful public snapshot. NBA.com/Stats NBA and Basketball Reference attempts were blocked/timed out; ESPN final box scores succeeded. No repeated endpoint probing is needed.

## Reproduce and preview

From this workspace:

```sh
python3 yk_working_copy/scripts/rebuild_public.py
python3 -m unittest discover -s yk_working_copy/tests -p 'test_*.py'
node --test yk_working_copy/tests/*.test.js
python3 -m http.server 8879 --directory yk_working_copy/docs
```

The existing preview server is already running at http://127.0.0.1:8879/ . Rebuild is offline and uses the retained local evidence; it does not publish. For new completed NBA games, run `scripts/refresh_nba_stats.py --start YYYY-MM-DD --end YYYY-MM-DD` within `yk_working_copy` (Python `requests` required). Ranking workbook ingestion additionally uses `openpyxl`. The user approved publishing this reviewed snapshot on October 21, 2026.
