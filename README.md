# DIN Mercado · LALIGA HYPERMOTION 2026/27

Standalone, mobile-first, interactive dashboard for Spain's Segunda División (LALIGA HYPERMOTION) only. This is a separate site, dataset, source log, validator, builder and repository from the LaLiga EA SPORTS top-flight panel.

## Public page and deployment

- **Repository:** `wildsonfranciscosilva1986-coder/laliga-hypermotion-2026-27-dashboard`
- **GitHub Pages:** `main` branch, repository root (`index.html`)
- GitHub Actions performs the fail-closed daily refresh at 06:10 America/Sao_Paulo (09:10 UTC) and supports manual dispatch; commits and Pages redeploys retain this same URL.

## Snapshot and validation

The dashboard and validation files are regenerated with the exact cutoff and result counts at each successful run. The season calendar is 462 official fixtures in 42 jornadas, 22 clubs, 21 home/21 away matches per club. Only confirmed LALIGA `FullTime` scores are counted; live, postponed, abandoned and unstarted matches remain scoreless. Every final is cross-checked against ESPN `STATUS_FULL_TIME`, and both the official LALIGA table and the independently recomputed ESPN table must match the final-only table for all 22 clubs across played, W-D-L, points, GF, GA and GD. No score or kickoff is inferred.
- Any future fixture without an officially published kickoff time displays “horário a confirmar”; the source's midnight placeholder is not treated as a kickoff.

## Verified competition format and zones

The official calendar has **22 clubs and 42 jornadas** (462 fixtures). Official LALIGA classification zones and the official play-off explainer establish: positions 1–2 direct promotion; places 3–6 contest the third promotion place through the play-off; positions 19–22 are the four relegation places. See `laliga2_2026_27_rules.json` and the official links within.

## Included dashboard

- Overview KPIs for 22 clubs, confirmed finals / 462 official fixtures, total goals and per-match average, BTTS and Over 2.5 numerator / denominator / rate, home wins / draws / away wins, next fixture, and the exact BRT cutoff. Only confirmed final scores enter score-derived KPIs.
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

The refresh script fetches LALIGA's 42 official round pages and overall/home/away table snapshots, pulls ESPN results to cross-check final scores, validates and rebuilds the standalone page. The GitHub Actions refresh runs daily at 06:10 America/Sao_Paulo (09:10 UTC), with a manual dispatch option. Each run refetches official fixtures/table and ESPN results, validates exact score and table agreement, rebuilds the page, and commits only after every check passes. Failed or mismatched runs do not publish. The workflow updates this repository in place, preserving the existing Pages URL.

## Project files

- `laliga2_2026_27_matches_official.csv` — season fixture dataset and LALIGA status/IDs.
- `laliga2_2026_27_official_*_snapshot.csv` — raw overall/home/away table snapshots.
- `laliga2_2026_27_espn_result_crosscheck.csv`, `espn_2026_27_standings_from_scores.csv` — independent result evidence and recomputation.
- `laliga2_2026_27_validation.json/.txt`, `laliga2_2026_27_source_log.json`, `laliga2_2026_27_rules.json` — reproducible audit trail.
- `fetch_official_laliga2.py`, `capture_official_standings.py`, `capture_espn_crosscheck.py`, `validate_laliga2.py`, `build_laliga2_dashboard.py`, `dashboard_template.html`, `refresh_laliga2_2026_27.sh` — per-league refresh/build tools.
