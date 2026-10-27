"""Present the NRL program prominently within institute Research."""
from pathlib import Path
import re
D=Path(__file__).resolve().parents[1]/'dist'
for en in (False,True):
 pre='/en' if en else '';p=D/pre.lstrip('/')/'research/index.html';s=p.read_text()
 title='Research Programs' if en else '연구사업'
 name='National Research Lab (NRL)' if en else '국가연구소(NRL)'
 focus='Human-centered Physical AI Robotics' if en else '인간중심 피지컬 AI 로보틱스'
 description=('The NRL program develops physical AI robotics through research on embodied physical intelligence and distributed intelligence. Technology Cores and Project Groups connect foundational technologies with applications in daily living, wearables and in-body robotics.' if en else '국가연구소 사업은 체화된 물리지능과 분산지능을 바탕으로 인간중심 피지컬 AI 로보틱스 기술을 개발합니다. 핵심기술(TC)과 프로젝트 그룹(PG)을 연계하여 원천기술을 일상생활 지원, 웨어러블, 체내 로봇 분야에 적용하는 연구를 수행합니다.')
 links=[('Technology Core' if en else '핵심기술','MORPHI Body · MOSAIC Intelligence · Digital Twin · Human Value','#technical-cores'),('Project Group' if en else '프로젝트 그룹','Life Companion · Wearable · Intra-Body','#project-groups'),('Participating Faculty' if en else '참여교수','', 'faculty/'),('Affiliated Faculty' if en else '연계교수','', 'affiliated/')]
 body='<div class="research-page" data-research-landing><section class="research-programs"><h2>'+title+'</h2><article class="research-program-feature"><p class="program-kicker">NRL 2.0 · 2026–2035</p><h3><a href="'+pre+'/research/nrl/">'+name+'</a></h3><p class="program-focus">'+focus+'</p><p class="program-description">'+description+'</p><a class="program-enter" href="'+pre+'/research/nrl/">'+('Explore NRL' if en else '국가연구소 사업 보기')+' <span aria-hidden="true">→</span></a><nav class="program-sections" aria-label="'+('NRL sections' if en else '국가연구소 세부 메뉴')+'">'+''.join('<a href="'+pre+'/research/nrl/'+target+'"><span>'+label+' <span aria-hidden="true">↗</span></span>'+('<small>'+detail+'</small>' if detail else '')+'</a>' for label,detail,target in links)+'</nav></article></section></div>'
 s=re.sub(r'<div class="research-page"[^>]*>.*?(?=</main>)',lambda m:body,s,count=1,flags=re.S)
 if 'research-programs.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/research-programs.css?v=20261022"></head>')
 p.write_text(s)
