#!/usr/bin/env python3
"""Pull ESPN's independent 2026/27 scoreboard by match date and recompute its table."""
from __future__ import annotations
import csv,json,re,requests,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
fixtures=list(csv.DictReader((ROOT/'laliga2_2026_27_matches_official.csv').open(encoding='utf-8-sig')))
source='https://site.api.espn.com/apis/site/v2/sports/soccer/esp.2/scoreboard?dates=YYYYMMDD'
def norm(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+',' ',s).strip()
# The map makes common provider display-name differences explicit and reviewable.
aliases={
 'almeria':'UD Almería','ud almeria':'UD Almería',
 'castellon':'CD Castellón','cd castellon':'CD Castellón',
 'eibar':'SD Eibar','sd eibar':'SD Eibar',
 'sporting gijon':'Real Sporting','sporting gijon':'Real Sporting','real sporting':'Real Sporting',
 'mallorca':'RCD Mallorca','rcd mallorca':'RCD Mallorca',
 'real oviedo':'Real Oviedo','oviedo':'Real Oviedo',
 'cd sabadell':'CE Sabadell','sabadell':'CE Sabadell','ce sabadell':'CE Sabadell',
 'girona':'Girona FC','girona fc':'Girona FC',
 'burgos':'Burgos CF','burgos cf':'Burgos CF',
 'granada':'Granada CF','granada cf':'Granada CF',
 'real valladolid':'Real Valladolid CF','real valladolid cf':'Real Valladolid CF',
 'tenerife':'CD Tenerife','cd tenerife':'CD Tenerife',
 'cordoba':'Córdoba CF','cordoba cf':'Córdoba CF',
 'celta fortuna':'Celta Fortuna','rc celta fortuna':'Celta Fortuna',
 'eldense':'CD Eldense','cd eldense':'CD Eldense',
 'las palmas':'UD Las Palmas','ud las palmas':'UD Las Palmas',
 'leganes':'CD Leganés','cd leganes':'CD Leganés',
 'fc andorra':'FC Andorra','andorra':'FC Andorra',
 'real sociedad ii':'R. Sociedad B','real sociedad b':'R. Sociedad B','real sociedad ii b':'R. Sociedad B',
 'cadiz':'Cádiz CF','cadiz cf':'Cádiz CF',
 'ceuta':'AD Ceuta FC','ad ceuta fc':'AD Ceuta FC',
 'albacete':'Albacete BP','albacete bp':'Albacete BP'}
# Accept only aliases that map to an official club in the season schedule.
clubs=sorted({r['home_team'] for r in fixtures}|{r['away_team'] for r in fixtures})
assert set(aliases.values())==set(clubs),(set(aliases.values())-set(clubs),set(clubs)-set(aliases.values()))
# ESPN's scoreboard date is keyed in UTC; querying the Madrid calendar date and adjacent days
# covers late kickoffs around midnight.  Scores are accepted only when ESPN marks STATUS_FULL_TIME.
session=requests.Session();session.headers['User-Agent']='Mozilla/5.0 DINMercadoDashboard/1.0'
dates=set()
for r in fixtures:
 if r['status']=='finished':
  d=datetime.strptime(r['date_local_madrid'],'%Y-%m-%d').date()
  for delta in (-1,0,1):dates.add((d+timedelta(days=delta)).strftime('%Y%m%d'))
bykey={}
for d in sorted(dates):
 resp=session.get('https://site.api.espn.com/apis/site/v2/sports/soccer/esp.2/scoreboard',params={'dates':d},timeout=35)
 resp.raise_for_status();payload=resp.json()
 for e in payload.get('events',[]):
  comp=e['competitions'][0]; status=comp['status']['type'].get('name','')
  comps={x['homeAway']:x for x in comp['competitors']}
  h=comps.get('home',{});a=comps.get('away',{})
  hn=aliases.get(norm(h.get('team',{}).get('displayName','')));an=aliases.get(norm(a.get('team',{}).get('displayName','')))
  if not hn or not an: continue
  key=(hn,an)
  rec={'espn_event_id':e.get('id',''),'date_utc':e.get('date',''),'home_team':hn,'home_provider_name':h.get('team',{}).get('displayName',''),
       'home_goals':h.get('score',''),'away_team':an,'away_provider_name':a.get('team',{}).get('displayName',''),
       'away_goals':a.get('score',''),'espn_status':status,'source_url':source.replace('YYYYMMDD',d)}
  if key not in bykey or (status=='STATUS_FULL_TIME' and bykey[key]['espn_status']!='STATUS_FULL_TIME'):bykey[key]=rec
rows=[];missing=[];mismatch=[]
for f in fixtures:
 if f['status']!='finished':continue
 key=(f['home_team'],f['away_team']);e=bykey.get(key)
 if not e:missing.append({'round':f['round'],'home':f['home_team'],'away':f['away_team'],'date':f['date_local_madrid']});continue
 same=(e['espn_status']=='STATUS_FULL_TIME' and str(e['home_goals'])==str(f['home_goals']) and str(e['away_goals'])==str(f['away_goals']))
 rows.append({'official_match_id':f['official_match_id'],'round':f['round'],'date_local_madrid':f['date_local_madrid'],'home_team':f['home_team'],'official_home_goals':f['home_goals'],'espn_home_goals':e['home_goals'],'away_team':f['away_team'],'official_away_goals':f['away_goals'],'espn_away_goals':e['away_goals'],'espn_status':e['espn_status'],'result_match':same,'espn_event_id':e['espn_event_id'],'espn_source_url':e['source_url']})
 if not same:mismatch.append(rows[-1])
with (ROOT/'laliga2_2026_27_espn_result_crosscheck.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
# ESPN independently computed overall table using only its own finished scorelines for the same clubs.
stats={t:{'played':0,'won':0,'drawn':0,'lost':0,'goals_for':0,'goals_against':0,'points':0} for t in clubs}
for e in bykey.values():
 if e['espn_status']!='STATUS_FULL_TIME' or e['home_goals']=='' or e['away_goals']=='':continue
 hg,ag=int(e['home_goals']),int(e['away_goals'])
 for t,gf,ga in [(e['home_team'],hg,ag),(e['away_team'],ag,hg)]:
  s=stats[t];s['played']+=1;s['goals_for']+=gf;s['goals_against']+=ga
  if gf>ga:s['won']+=1;s['points']+=3
  elif gf==ga:s['drawn']+=1;s['points']+=1
  else:s['lost']+=1
for t,s in stats.items():s['goal_difference']=s['goals_for']-s['goals_against']
out=sorted([{'team':t,**s} for t,s in stats.items()],key=lambda x:(-x['points'],-x['goal_difference'],-x['goals_for'],x['team']))
with (ROOT/'espn_2026_27_standings_from_scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
report={'source':'ESPN independent match scoreboard API','scoreboard_endpoint':source,'finished_official_fixtures':sum(r['status']=='finished' for r in fixtures),'distinct_queried_UTC_dates':len(dates),
 'ESPN_match_records_available':len(rows),'matched_results':sum(x['result_match'] for x in rows),'mismatches':mismatch,'missing_fixtures':missing,
 'ESPN_table_recomputed_from_ESPN_final_scores':len(out),'note':'Result comparison requires ESPN to mark the event STATUS_FULL_TIME. Table above is independently recomputed from ESPN event scores, not copied from LALIGA.'}
(ROOT/'laliga2_2026_27_espn_crosscheck.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
