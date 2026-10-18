#!/usr/bin/env python3
"""Capture the official overall and home/away LALIGA HYPERMOTION standings."""
import csv,json,requests
from bs4 import BeautifulSoup
from pathlib import Path
ROOT=Path(__file__).resolve().parent
URL='https://www.laliga.com/laliga-hypermotion/clasificacion'
r=requests.get(URL,timeout=40,headers={'User-Agent':'Mozilla/5.0 DINMercadoDashboard/1.0'});r.raise_for_status()
s=BeautifulSoup(r.text,'html.parser');node=s.find('script',id='__NEXT_DATA__')
if not node or not node.string: raise RuntimeError('Official table payload missing')
p=json.loads(node.string)['props']['pageProps']
def flatten(items):
 out=[]
 for x in items:
  out.append({'position':x['position'],'team':x['team']['nickname'],'short':x['team'].get('shortname',''),
   'played':x['played'],'won':x['won'],'drawn':x['drawn'],'lost':x['lost'],'goals_for':x['goals_for'],
   'goals_against':x['goals_against'],'goal_difference':int(x['goal_difference']),'points':x['points'],
   'competition_zone':(x.get('qualify') or {}).get('name','')})
 return out
for key,name in [('standings','laliga2_2026_27_official_table_snapshot.csv'),('standingsHome','laliga2_2026_27_official_home_table_snapshot.csv'),('standingsAway','laliga2_2026_27_official_away_table_snapshot.csv')]:
 rows=flatten(p[key]);
 with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
zone={'source':URL,'season':'2026/27','current_gameweek':p.get('currentGameweek'),
 'zone_colors':{'overall':p.get('standingsDefaultColors'),'home':p.get('standingsHomeColors'),'away':p.get('standingsAwayColors')},
 'official_zones':flatten(p['standings'])}
(ROOT/'laliga2_2026_27_official_zones.json').write_text(json.dumps(zone,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved official table snapshots: 22 overall, home and away rows')
