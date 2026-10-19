#!/usr/bin/env python3
"""Validate LALIGA HYPERMOTION 2026/27 fixtures and final-only standings."""
import csv,json,os
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CUTOFF=os.environ.get('LALIGA2_CUTOFF','2026-10-19 08:08 America/Sao_Paulo')
def read(name):
 with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
fixtures=read('laliga2_2026_27_matches_official.csv')
official=read('laliga2_2026_27_official_table_snapshot.csv')
espn=read('espn_2026_27_standings_from_scores.csv')
espncheck=read('laliga2_2026_27_espn_result_crosscheck.csv')
assert len(fixtures)==462, f'Expected 462 official fixture slots, got {len(fixtures)}'
assert len({int(r['round']) for r in fixtures})==42
assert all(sum(int(x['round'])==rd for x in fixtures)==11 for rd in range(1,43))
assert len({r['official_match_id'] for r in fixtures})==462
clubs=sorted({r['home_team'] for r in fixtures}|{r['away_team'] for r in fixtures})
assert len(clubs)==22
for t in clubs:
 home=[r for r in fixtures if r['home_team']==t];away=[r for r in fixtures if r['away_team']==t]
 assert len(home)==21 and len(away)==21,(t,len(home),len(away))
 assert set(int(r['round']) for r in home+away)==set(range(1,43)),t
counts=Counter(r['status'] for r in fixtures)
assert set(counts).issubset({'scheduled','finished','abandoned','postponed','cancelled','in_progress'}),counts
finished=[r for r in fixtures if r['status']=='finished']
assert len(finished)==counts['finished']
overview={'clubs':len(clubs),'finished_fixtures':len(finished),'official_fixtures':len(fixtures),
 'total_goals':sum(int(r['home_goals'])+int(r['away_goals']) for r in finished),
 'btts':sum(int(r['home_goals'])>0 and int(r['away_goals'])>0 for r in finished),
 'over_2_5':sum(int(r['home_goals'])+int(r['away_goals'])>=3 for r in finished),
 'home_wins':sum(int(r['home_goals'])>int(r['away_goals']) for r in finished),
 'draws':sum(int(r['home_goals'])==int(r['away_goals']) for r in finished),
 'away_wins':sum(int(r['home_goals'])<int(r['away_goals']) for r in finished)}
assert overview['home_wins']+overview['draws']+overview['away_wins']==len(finished)
assert overview['total_goals']==sum(int(r['home_goals'])+int(r['away_goals']) for r in finished)
stats={t:{'played':0,'won':0,'drawn':0,'lost':0,'goals_for':0,'goals_against':0,'points':0,'home_played':0,'away_played':0} for t in clubs}
for m in fixtures:
 if m['status']=='finished':
  assert m['home_goals']!='' and m['away_goals']!='',m
  hg,ag=int(m['home_goals']),int(m['away_goals'])
  for t,gf,ga,side in [(m['home_team'],hg,ag,'home'),(m['away_team'],ag,hg,'away')]:
   s=stats[t];s['played']+=1;s['goals_for']+=gf;s['goals_against']+=ga;s[f'{side}_played']+=1
   if gf>ga:s['won']+=1;s['points']+=3
   elif gf==ga:s['drawn']+=1;s['points']+=1
   else:s['lost']+=1
 else: assert m['home_goals']=='' and m['away_goals']=='',(m['official_match_id'],m['status'])
for t,s in stats.items():s['goal_difference']=s['goals_for']-s['goals_against']
assert len(official)==22 and {r['team'] for r in official}==set(clubs)
off={r['team']:r for r in official}
fields=['played','won','drawn','lost','goals_for','goals_against','points','goal_difference']
computed_diff=[]
for t,s in stats.items():
 diffs=[f for f in fields if s[f]!=int(off[t][f])]
 if diffs:computed_diff.append({'team':t,'fields':diffs,'final_only':{f:s[f] for f in fields},'official_table_snapshot':{f:int(off[t][f]) for f in fields}})
# Any official live-table difference must be explained by a currently in-progress fixture.
live=[r for r in fixtures if r['status']=='in_progress']
if live:
 assert len(live)==1, f'Expected at most one active fixture, got {len(live)}'
 l=live[0]
 expected_live_delta={l['home_team']:{'played':1,'drawn':1,'points':1},l['away_team']:{'played':1,'drawn':1,'points':1}}
 assert {x['team'] for x in computed_diff}==set(expected_live_delta),(computed_diff,expected_live_delta)
 for x in computed_diff:
  t=x['team'];fd=x['final_only'];od=x['official_table_snapshot']
  assert od['played']==fd['played']+1 and od['drawn']==fd['drawn']+1 and od['points']==fd['points']+1
  for f in fields:
   if f not in ('played','drawn','points'):assert od[f]==fd[f],(t,f,fd,od)
else:
 assert not computed_diff, f'Official standings mismatch without an in-progress fixture: {computed_diff}'
# ESPN independently confirms every official final score and its table recomputed from ESPN finals equals our final-only stats.
assert len(espncheck)==counts['finished']
assert all(r['result_match']=='True' for r in espncheck)
e={r['team']:r for r in espn};assert set(e)==set(clubs)
for t,s in stats.items():
 for f in fields:assert s[f]==int(e[t][f]),('ESPN mismatch',t,f,s[f],e[t][f])
# Overall, home and away calculated tables for panel records.
def stat_rows(scope='all'):
 out=[]
 for t,s in stats.items():
  if scope=='home': games=[m for m in fixtures if m['status']=='finished' and m['home_team']==t]
  elif scope=='away': games=[m for m in fixtures if m['status']=='finished' and m['away_team']==t]
  else: games=[m for m in fixtures if m['status']=='finished' and (m['home_team']==t or m['away_team']==t)]
  x={'team':t,'played':len(games),'won':0,'drawn':0,'lost':0,'goals_for':0,'goals_against':0,'points':0,'btts':0,'over_2_5':0}
  for m in games:
   home=m['home_team']==t;hg,ag=int(m['home_goals']),int(m['away_goals']);gf,ga=(hg,ag) if home else (ag,hg)
   x['goals_for']+=gf;x['goals_against']+=ga;x['btts']+=int(hg>0 and ag>0);x['over_2_5']+=int(hg+ag>=3)
   if gf>ga:x['won']+=1;x['points']+=3
   elif gf==ga:x['drawn']+=1;x['points']+=1
   else:x['lost']+=1
  x['goal_difference']=x['goals_for']-x['goals_against'];out.append(x)
 return out
for scope in ('all','home','away'):
 rows=stat_rows(scope)
 with (ROOT/f'laliga2_2026_27_computed_{scope}_table.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(sorted(rows,key=lambda x:(-x['points'],-x['goal_difference'],-x['goals_for'],x['team'])))
report={'competition':'LALIGA HYPERMOTION / Segunda División 2026/27','cutoff':CUTOFF,
 'overview_kpis':{**overview,'average_goals_per_finished_match':round(overview['total_goals']/len(finished),4) if finished else None,
  'btts_rate':round(overview['btts']/len(finished),4) if finished else None,
  'over_2_5_rate':round(overview['over_2_5']/len(finished),4) if finished else None,
  'live_matches_excluded':counts['in_progress']},
 'official_source_snapshot_retrieved':f'Current LALIGA official fixture and table snapshots retrieved at {CUTOFF}',
 'coverage':{'clubs':len(clubs),'matchdays':42,'official_fixture_slots':len(fixtures),'unique_official_match_ids':len({r['official_match_id'] for r in fixtures}),'fixture_status_counts':dict(counts),'confirmed_final_scores_used':counts['finished'],'live_matches_excluded':counts['in_progress'],'unpublished_kickoff_times':sum(not r['kickoff_local_madrid'] for r in fixtures)},
 'score_table_rule':'Only LALIGA status FullTime rows with both scores are used. Win=3 points, draw=1, loss=0. W-D-L, played, GF, GA, GD and points are recomputed per club; home and away records are calculated separately.',
 'official_table_reconciliation':{'clubs_exactly_matching_all_fields':22-len(computed_diff),'clubs_with_live_table_delta':len(computed_diff),'differences':computed_diff,'reconciliation':('Exact match: official table equals the final-only score-derived table; no active fixtures.' if not live else 'The official live table differs only by the currently in-progress fixture; its provisional score is excluded from this panel.')},
 'independent_ESPN_crosscheck':{'source':'ESPN independent scoreboard API, current official final-result dates','official_final_results_checked':len(espncheck),'identical_final_scores':sum(r['result_match']=='True' for r in espncheck),'missing_or_different':sum(r['result_match']!='True' for r in espncheck),'independently_recomputed_ESPN_table_matches_final_only_table':sum(1 for t in clubs if all(int(stats[t][f])==int(e[t][f]) for f in fields))}, 
 'rules':{'clubs':22,'regular_season_rounds':42,'direct_promotion':'positions 1–2 (official LALIGA table zone: Ascenso)','promotion_playoff':'positions 3–6 (official LALIGA table zone: Promoción ascenso; LALIGA official playoff explainer specifies the third/fourth/fifth/sixth placed teams contest the third promotion place)','relegation':'positions 19–22 (official LALIGA table zone: Descenso; 2025/26 official end-of-season announcement confirms four relegated clubs after 42 rounds)'},
 'data_limitations':['Live standings can temporarily include in-progress match states; this build intentionally uses only completed full-time results.','Some future match dates are published without a kickoff time; those remain time TBC and are not rendered as 01:00.','Current results are a small early-season sample; H2H only includes 2026/27 completed fixtures.','The 1-X-2 display is an uncalibrated descriptive independent-Poisson projection using only this season’s home and away goal averages; it does not account for lineups, injuries, opponent strength, or odds.']}
(ROOT/'laliga2_2026_27_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[f"LALIGA HYPERMOTION 2026/27 validation — cutoff {CUTOFF}",f"Official calendar: {len(fixtures)}/462 fixtures; 42 matchdays × 11 fixtures; 22 clubs; each club plays 21 home and 21 away.",f"Statuses: {counts['finished']} confirmed final scores; {counts['in_progress']} active fixture excluded; {counts['scheduled']} future/unstarted; {counts.get('abandoned',0)} abandoned.",f"Overview KPIs from finals only: {overview['total_goals']} goals ({overview['total_goals']/len(finished):.2f}/match); BTTS {overview['btts']}/{len(finished)} ({100*overview['btts']/len(finished):.1f}%); Over 2.5 {overview['over_2_5']}/{len(finished)} ({100*overview['over_2_5']/len(finished):.1f}%); home/draw/away {overview['home_wins']}/{overview['draws']}/{overview['away_wins']}.",f"Independent ESPN: {len(espncheck)}/{counts['finished']} finished scores match; ESPN's independently recomputed table is compared club by club.",f"Official standings reconciliation: {22-len(computed_diff)}/22 club vectors match exactly; {len(computed_diff)} unexplained differences. No live score enters this panel's calculations.","Home/away tables and exact 22-team standings are in the computed table files.","No kickoff times are invented: any missing official time stays blank / TBC."]
(ROOT/'laliga2_2026_27_validation.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
