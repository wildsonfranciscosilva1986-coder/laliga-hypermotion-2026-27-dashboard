# DIN Mercado · LALIGA HYPERMOTION 2026/27

Standalone, mobile-first, interactive dashboard for Spain's Segunda División (LALIGA HYPERMOTION) only. This is a separate site, dataset, source log, validator, builder and repository from the LaLiga EA SPORTS top-flight panel.

## Public page and deployment

- **Repository:** `wildsonfranciscosilva1986-coder/laliga-hypermotion-2026-27-dashboard`
- **GitHub Pages:** `main` branch, repository root (`index.html`)
- No cron/workflow was created. Public hosting is independent and authorized.

## Snapshot and validation

- **Final-results cutoff:** 18 October 2026, 12:05 BRT (`America/Sao_Paulo`).
- Calendar: 462 official fixtures in 42 jornadas, 22 clubs, 21 home/21 away matches per club.
- Results used: 105 confirmed LALIGA `FullTime` scores. One active Granada CF–Cádiz CF fixture is shown without a score and excluded from every count/model; 356 future fixtures are retained. No score is inferred.
- All 105 LALIGA final scores match ESPN's independently published match scoreboard events. An independent table recomputed from ESPN `STATUS_FULL_TIME` results matches the final-only 22-club table.
- LALIGA's live overall table snapshot includes Granada–Cádiz while it was in progress as an extra 0–0 draw. Thus 20/22 team rows match the official table exactly; the only differences are the expected extra played/draw/point for Granada and Cádiz in the live table. The official fixture page was halftime with no confirmed final. The final-only dashboard deliberately does not count the live match. Raw official standings snapshots, ESPN cross-check rows and comparison details are retained.
- 209 future fixture entries have no officially published kickoff time. They display “horário a confirmar”; the source's midnight placeholder is not shown as an actual kickoff.

## Verified competition format and zones

The official calendar has **22 clubs and 42 jornadas** (462 fixtures). Official LALIGA classification zones and the official play-off explainer establish: positions 1–2 direct promotion; places 3–6 contest the third promotion place through the play-off; positions 19–22 are the four relegation places. See `laliga2_2026_27_rules.json` and the official links within.

## Included dashboard

- League table, official promotion/play-off/relegation zones, W-D-L and GF/GA/GD, calculated solely from confirmed final results.
- Club profiles: last five finished matches, total/home/away form, goal stats and next published fixture.
- Interactive home/away selector with season H2H, 1-X-2 probabilities, expected goals, modal score, BTTS and over 2.5.
- Top 5 for points, goals for, best defence (fewest against), wins, draws, losses, BTTS and over 2.5; all indicators have general/home/away cuts. Counts show `n` and rate metrics show successes / observed games / percentage.
- Source links, exact cutoff, calculation rules, live-match reconciliation and limitations.

The 1-X-2 panel is a descriptive, uncalibrated independent-Poisson estimate from small home/away goal samples, not a betting recommendation. It does not account for lineups, injuries, opponent strength or odds. Standings tie-breaking beyond points, goal difference and goals scored may depend on head-to-head rules, which are not independently reproduced here.

## Refresh, validate and rebuild

After the day's matches have finished, the independent 06:00 BRT updater can refresh only this league with the following local artifacts. It should not publish if source checks or validation fail:

```sh
cd laliga-hypermotion-2026-27-dashboard
python3 -m pip install -r requirements.txt
./refresh_laliga2_2026_27.sh
```

The refresh script fetches LALIGA's 42 official round pages and overall/home/away table snapshots, pulls ESPN results to cross-check final scores, validates and rebuilds the standalone page. A safe subsequent update must recapture the ESPN scoreboard snapshot and compare exact official/independent results and table vectors; retain all active and nonfinal fixtures scoreless. Upload/commit the changed artifacts to this repository's `main` root only after validation passes. GitHub Pages then serves the new `index.html`. **No scheduled job is configured in this repository.**

## Project files

- `laliga2_2026_27_matches_official.csv` — season fixture dataset and LALIGA status/IDs.
- `laliga2_2026_27_official_*_snapshot.csv` — raw overall/home/away table snapshots.
- `laliga2_2026_27_espn_result_crosscheck.csv`, `espn_2026_27_standings_from_scores.csv` — independent result evidence and recomputation.
- `laliga2_2026_27_validation.json/.txt`, `laliga2_2026_27_source_log.json`, `laliga2_2026_27_rules.json` — reproducible audit trail.
- `fetch_official_laliga2.py`, `capture_official_standings.py`, `capture_espn_crosscheck.py`, `validate_laliga2.py`, `build_laliga2_dashboard.py`, `dashboard_template.html`, `refresh_laliga2_2026_27.sh` — per-league refresh/build tools.
