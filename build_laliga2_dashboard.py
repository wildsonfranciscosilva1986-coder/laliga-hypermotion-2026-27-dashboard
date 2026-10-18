#!/usr/bin/env python3
"""Build the standalone, self-contained LaLiga Hypermotion 2026/27 dashboard."""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parent
with (ROOT/'laliga2_2026_27_matches_official.csv').open(encoding='utf-8-sig',newline='') as f: matches=list(csv.DictReader(f))
with (ROOT/'laliga2_2026_27_official_table_snapshot.csv').open(encoding='utf-8-sig',newline='') as f: official=list(csv.DictReader(f))
with (ROOT/'laliga2_2026_27_official_zones.json').open(encoding='utf-8') as f: zone_data=json.load(f)
data={'matches':matches,'teams':sorted({m['home_team'] for m in matches}|{m['away_team'] for m in matches}),'officialTable':official,'zones':zone_data['zone_colors']}
jsdata=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
# The layout/nav/CSS follows the DIN Mercado Série A template but the second-tier
# dataset, marks, names, colors, source note, rules and publication are independent.
base=Path(ROOT/'dashboard_template.html').read_text(encoding='utf-8')
# The included template is this league's local presentation asset.
html="template=r'''"+base+"'''"
# Copy the static template's closing delimiter and strip its original data injection.
html=html.replace("html=html.replace('__DATA__',jsdata)\n(ROOT/'index.html').write_text(html,encoding='utf-8')\nprint('Built',ROOT/'index.html',len(html),'bytes')", "")
# Because the base template isn't part of the standalone repo, materialize it here
# by extracting raw HTML and maintaining all substitutions in this build artifact.
# Set unique league accents/identity and exact season/cutoff labels.
repls=[
("<title>LaLiga 2026/27 — Painel da temporada</title>","<title>LALIGA HYPERMOTION 2026/27 — DIN Mercado</title>"),
("<meta name=\"description\" content=\"Painel independente, verificável e responsivo da LaLiga 2026/27: classificação, forma, confronto e estatísticas calculadas de resultados confirmados.\">","<meta name=\"description\" content=\"Painel independente LALIGA HYPERMOTION 2026/27: classificação, forma, resultados oficiais, H2H, estatísticas e projeções descritivas.\">") ,
("--red:#d62855;--red2:#a91e48;","--red:#7048e8;--red2:#4c1d95;"),
("background:linear-gradient(145deg,#f0325e,#a81345)","background:linear-gradient(145deg,#8b5cf6,#4c1d95)"),
("#c4275a66","#6941c666"),
("#fbe9ee;color:#b51948","#f3e8ff;color:#6d28d9"),
("linear-gradient(90deg,#d62855,#f36d86)","linear-gradient(90deg,#7048e8,#22c3c6)"),
("<div class=\"brandmark\" aria-hidden=\"true\">LL</div>","<div class=\"brandmark\" aria-hidden=\"true\">H2</div>"),
("LaLiga EA SPORTS · 2026/27","LALIGA HYPERMOTION · 2026/27"),
("Corte: <b>18 out 2026 · 10:54 BRT</b>","Corte: <b>18 out 2026 · 12:05 BRT</b>"),
("LaLiga: <b>20 clubes · 38 jornadas</b>","Segunda: <b>22 clubes · 42 jornadas</b>"),
("Classificação por pontos, saldo e gols pró; a ordem exibida coincide com a tabela oficial no corte.","Tabela recalculada somente com jogos finalizados; o jogo em andamento fica fora. Desempates que exigem confronto direto não são modelados."),
("LaLiga EA SPORTS · temporada 2026/27","Segunda Divisão · temporada 2026/27"),
("H2H · LaLiga 2026/27","H2H · LaLiga Hypermotion 2026/27"),
("LaLiga 2026/27 · Painel de dados","LALIGA HYPERMOTION 2026/27 · DIN Mercado"),
("https://www.laliga.com/laliga-easports/resultados/2026-27/jornada-9","https://www.laliga.com/laliga-hypermotion/resultados/2026-27/jornada-10"),
("Fonte primária · LALIGA EA SPORTS","Fonte primária · LALIGA HYPERMOTION"),
("Resultados e calendário por jornada (1–38); ids oficiais dos 380 jogos; classificação e legenda oficial de Champions League, Europa League, Conference League e descenso. Consultado para o corte de 18/10/2026.","Calendário e placares oficiais por jornada (1–42), 462 partidas/IDs, classificação geral e legenda oficial de ascenso, play-off de ascenso e descenso. Snapshot do 18/10/2026; apenas FullTime entra nos cálculos."),
("https://www.espn.com/soccer/standings/_/league/esp.1","https://site.api.espn.com/apis/site/v2/sports/soccer/esp.2/scoreboard"),
("Conferência independente · ESPN standings","Conferência independente · placares ESPN"),
("Comparada por clube contra os cálculos; 18/20 linhas de estatísticas coincidem no snapshot recuperado. Osasuna e Racing ainda constavam com 8 jogos na tabela ESPN; a página de jogo da ESPN confirma o resultado final Osasuna 2–0 Racing: <a href=\"https://www.espn.com/soccer/match/_/gameId/401882840\" target=\"_blank\" rel=\"noopener\">ficha do jogo</a>. Após incorporar esse final confirmado por ambos os provedores, os 20 clubes coincidem com a tabela da LALIGA.","A API de placares ESPN foi consultada por data para conferir os 105 resultados oficiais encerrados: todos os placares finais coincidem. Uma tabela separada foi recomputada a partir dos próprios jogos FullTime da ESPN e também coincide com o quadro calculado neste painel. O jogo ao vivo Granada–Cádiz não é contado como resultado final."),
("84 jogos com resultado final verificado entram na tabela e em todas as taxas. Rayo Vallecano–Athletic Club (jornada 8) aparece como abandonado pela LALIGA e não recebe placar nem entra nas contas. Datas oficiais sem hora de início exibida aparecem como “horário a confirmar”.","105 jogos com placar final verificado entram na tabela e em todas as taxas. Granada CF–Cádiz CF (jornada 10) estava em andamento no corte; é exibido sem placar e não entra nas contas. A tabela ao vivo da LALIGA já contabilizava provisoriamente o jogo como empate 0–0: por isso, Granada e Cádiz aparecem com +1 PJ, +1 empate e +1 ponto cada na snapshot oficial face à tabela final-only. Datas sem hora publicada aparecem como “horário a confirmar”."),
("Snapshot solicitado: 18/10/2026 às 10:54 no fuso America/Sao_Paulo.","Corte solicitado: 18/10/2026 às 12:05 no fuso America/Sao_Paulo; snapshot oficial recuperado às 12:13 BRT. Sem novo placar final após o corte."),
("LaLiga 2026/27","LALIGA HYPERMOTION 2026/27"),
("'FC Barcelona'","'UD Almería'"),
("'Real Madrid'","'CD Castellón'"),
]
for a,b in repls: html=html.replace(a,b)
# Replace the source short-name map after league substitutions, so swapped sample-team defaults
# cannot accidentally relabel this league's clubs (e.g. Almería as Barcelona).
html=re.sub(r"const short=t=>\(\{.*?\}\[t\]\|\|t\);", "const short=t=>({'UD Almería':'Almería','CD Castellón':'Castellón','SD Eibar':'Eibar','Real Sporting':'Sporting','RCD Mallorca':'Mallorca','Real Oviedo':'Oviedo','CE Sabadell':'Sabadell','Girona FC':'Girona','Burgos CF':'Burgos','Granada CF':'Granada','Real Valladolid CF':'Valladolid','CD Tenerife':'Tenerife','Córdoba CF':'Córdoba','Celta Fortuna':'Celta Fortuna','CD Eldense':'Eldense','UD Las Palmas':'Las Palmas','CD Leganés':'Leganés','FC Andorra':'Andorra','R. Sociedad B':'Real Sociedad B','Cádiz CF':'Cádiz','AD Ceuta FC':'Ceuta','Albacete BP':'Albacete'}[t]||t);", html, count=1)
# Rename default team selections and short names in JS; extend readable compact names.
html=html.replace("const short=t=>({'Deportivo Alavés':'Alavés','RC Deportivo':'Deportivo','R. Racing Club':'Racing','RCD Espanyol de Barcelona':'Espanyol','Atlético de Madrid':'Atlético','CA Osasuna':'Osasuna','Málaga CF':'Málaga','FC Barcelona':'Barcelona','Real Betis':'Betis','Real Sociedad':'Real Sociedad','Villarreal CF':'Villarreal','Athletic Club':'Athletic','Celta':'Celta','Levante UD':'Levante','Getafe CF':'Getafe','Elche CF':'Elche','Valencia CF':'Valencia','Rayo Vallecano':'Rayo','Real Madrid':'Real Madrid','Sevilla FC':'Sevilla'}[t]||t);", "const short=t=>({'UD Almería':'Almería','CD Castellón':'Castellón','SD Eibar':'Eibar','Real Sporting':'Sporting','RCD Mallorca':'Mallorca','Real Oviedo':'Oviedo','CE Sabadell':'Sabadell','Girona FC':'Girona','Burgos CF':'Burgos','Granada CF':'Granada','Real Valladolid CF':'Valladolid','CD Tenerife':'Tenerife','Córdoba CF':'Córdoba','Celta Fortuna':'Celta Fortuna','CD Eldense':'Eldense','UD Las Palmas':'Las Palmas','CD Leganés':'Leganés','FC Andorra':'Andorra','R. Sociedad B':'Real Sociedad B','Cádiz CF':'Cádiz','AD Ceuta FC':'Ceuta','Albacete BP':'Albacete'}[t]||t);")
html=html.replace("const zoneClass=z=>z==='Champions League'?'ucl':z==='Europa League'?'uel':z==='Conference League'?'uecl':z==='Descenso'?'down':'';\nconst zoneLabel=z=>z==='Champions League'?'Champions League':z==='Europa League'?'Europa League':z==='Conference League'?'Conference League':z==='Descenso'?'Rebaixamento':'';", "const zoneClass=z=>z==='Ascenso direto'?'direct':z==='Play-off de ascenso'?'playoff':z==='Rebaixamento'?'down':'';\nconst zoneLabel=z=>z||'';")
html=html.replace("const standings=TEAMS.map(t=>({team:t,...statsFor(t)})).sort((a,b)=>b.points-a.points||b.gd-a.gd||b.gf-a.gf||Number(OFF[a.team].position)-Number(OFF[b.team].position));", "const standings=TEAMS.map(t=>({team:t,...statsFor(t)})).sort((a,b)=>b.points-a.points||b.gd-a.gd||b.gf-a.gf||Number(OFF[a.team].position)-Number(OFF[b.team].position));\nfor(let i=0;i<standings.length;i++) ZONES[standings[i].team]=i<2?'Ascenso direto':i<6?'Play-off de ascenso':i>=18?'Rebaixamento':'';")
html=html.replace("const order=[['ucl','Champions League'],['uel','Europa League'],['uecl','Conference League'],['down','Rebaixamento']];", "const order=[['direct','Acesso direto · posições 1–2'],['playoff','Play-off de ascenso · posições 3–6'],['down','Descenso · posições 19–22']];")
html=html.replace("'teamSelect','UD Almería'", "'teamSelect','UD Almería'")
html=html.replace("fillSelect('teamSelect','FC Barcelona');fillSelect('homeSelect','FC Barcelona');fillSelect('awaySelect','Real Madrid');", "fillSelect('teamSelect','UD Almería');fillSelect('homeSelect','UD Almería');fillSelect('awaySelect','CD Castellón');")
# Denominators are shown for raw counts too; rates include numerator / observed sample / percent.
old="${isRate?`${x.num}/${x.s.played} · ${(100*x.val).toFixed(0)}%`:x.val}"
new="${isRate?`${x.num}/${x.s.played} · ${(100*x.val).toFixed(0)}%`:`${x.val} · n=${x.s.played}`}"
html=html.replace(old,new)
# More zone-aware CSS: clear league-specific promotion coloring; enough width for 22 clubs.
html=html.replace(".ucl{background:#08237f}.uel{background:#ff6900}.uecl{background:#00aa20}.down{background:#00a5aa}", ".direct{background:#6d28d9}.playoff{background:#f97316}.down{background:#0891b2}")
html=html.replace("html=r'''", "html=r'''",1)
# Retain the template's theme color metadata.
html=html.replace('<meta name="theme-color" content="#0b1020">','<meta name="theme-color" content="#0b1020">')
# Save template end delimiter known from original source. Pull only template body (before old write lines).
start=html.index("template=r'''")+len("template=r'''")
end=html.index("'''",start)
template=html[start:end]
template=template.replace('LL','H2')
template=template.replace('LaLiga EA SPORTS','LALIGA HYPERMOTION')
# Remove the old source table's first-division European qualification copy, already rewritten above.
# Dataset injection.
page=template.replace('__DATA__',jsdata)
# Data-driven current result count text stays in header via JS. Use direct static explanatory label.
(ROOT/'index.html').write_text(page,encoding='utf-8')
print(f'Built {ROOT/"index.html"} ({len(page):,} bytes), {len(matches)} fixtures / {len(data["teams"])} clubs')
