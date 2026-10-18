#!/usr/bin/env python3
"""Fetch LALIGA HYPERMOTION official matchday pages for 2026/27."""
from __future__ import annotations
import csv, json, requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE='https://www.laliga.com/laliga-hypermotion/resultados/2026-27/jornada-{}'
MADRID=ZoneInfo('Europe/Madrid')
OUT=ROOT/'laliga2_2026_27_matches_official.csv'
rows=[]
for rnd in range(1,43):
    url=BASE.format(rnd)
    r=requests.get(url,timeout=40,headers={'User-Agent':'Mozilla/5.0 DINMercadoDashboard/1.0'})
    r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    node=soup.find('script',id='__NEXT_DATA__')
    if not node or not node.string: raise RuntimeError(f'No official match payload for jornada {rnd}: {url}')
    props=json.loads(node.string)['props']['pageProps']
    matches=props.get('matches') or []
    if len(matches)!=11: raise RuntimeError(f'Jornada {rnd}: expected 11 fixtures, got {len(matches)}')
    for m in matches:
        dt=datetime.fromisoformat(m['date']) if m.get('date') else None
        local_date=dt.astimezone(MADRID).strftime('%Y-%m-%d') if dt else ''
        # LALIGA leaves time=null for future fixtures whose kickoff has not yet been set.
        time_dt=datetime.fromisoformat(m['time']) if m.get('time') else None
        kickoff=time_dt.astimezone(MADRID).strftime('%H:%M') if time_dt else ''
        raw=m.get('status') or 'Unknown'
        status={'FullTime':'finished','Abandoned':'abandoned','Postponed':'postponed','Cancelled':'cancelled','PreMatch':'scheduled'}.get(raw)
        if status is None:
            status='in_progress' if raw in ('Live','InPlay','FirstHalf','SecondHalf','HalfTime','ExtraTime','PenaltyShootout','BreakTime') or 'live' in raw.lower() else 'unknown:'+raw
        finished=status=='finished'
        rows.append({'round':rnd,'official_match_id':m.get('id',''),'date_local_madrid':local_date,'kickoff_local_madrid':kickoff,
          'home_team':m['home_team']['nickname'],'home_short':m['home_team'].get('shortname',''),
          'home_goals':m.get('home_score') if finished else '', 'away_goals':m.get('away_score') if finished else '',
          'away_team':m['away_team']['nickname'],'away_short':m['away_team'].get('shortname',''),
          'status':status,'source_status':raw,'official_match_slug':m.get('slug',''),'official_round_url':url})
rows.sort(key=lambda x:(x['round'],x['date_local_madrid'],x['kickoff_local_madrid'],str(x['official_match_id'])))
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(f'Saved {len(rows)} official fixtures / 42 jornadas to {OUT}')
