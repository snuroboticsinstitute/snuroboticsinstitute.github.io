"""Use factual research descriptions; keep promotional slogans out of NRL content."""
from pathlib import Path
from html import escape as e
import re,json
D=Path(__file__).resolve().parents[1]/'dist'
core_copy=json.loads((D.parent/'scripts/nrl-core-copy.json').read_text())
heads={
 'tc1':('적응형 로봇 소재·구조 및 물리 지능 연구','Adaptive Robot Materials, Structures and Physical Intelligence'),
 'tc2':('분산 지능 모듈의 협력 및 지속 학습 연구','Cooperative Distributed Intelligence and Continual Learning'),
 'tc3':('로봇·인간·환경 디지털 트윈','Robot–Human–Environment Digital Twin'),
 'tc4':('로봇의 안전성·임상적 신뢰성 및 사회적 수용성','Robot Safety, Clinical Reliability and Social Acceptance'),
 'pg1':('일상생활 지원 로봇 연구','Robots for Everyday Assistance'),
 'pg2':('신체 움직임 보조·증강 웨어러블 로봇 연구','Wearable Robots for Movement Assistance and Augmentation'),
 'pg3':('인체 내부 작동 로봇 연구','Robots Operating Inside the Human Body')}
for en in (False,True):
 p=D/('en/' if en else '')/'research/nrl/index.html';s=p.read_text()
 s=re.sub(r'<section class="intro">.*?</section>','',s,count=1,flags=re.S)
 s=re.sub(r'<section class="detail-section research-tab-panel" id="participating-labs">.*?</section>','',s,count=1,flags=re.S)
 # Keep group scopes and research topics; remove rhetorical umbrella headings.
 for group,(ko,eng) in heads.items():
  pat=r'(<article class="detail-card" id="'+group+r'">.*?<h3>).*?</h3>'
  s,n=re.subn(pat,lambda m:m[1]+e(eng if en else ko)+'</h3>',s,count=1,flags=re.S);assert n==1,group
 for group,translations in core_copy.items():
  copy=translations['en' if en else 'ko']
  content='<div class="tc-overview"><section class="tc-context"><h4>'+('Why it matters' if en else '연구 필요성')+'</h4><p>'+e(copy['why'])+'</p></section><section class="tc-approach"><h4>'+('Research approach' if en else '연구 방향')+'</h4><p>'+e(copy['approach'])+'</p></section></div><section class="tc-topics"><h4>'+('Key research topics' if en else '주요 연구 내용')+'</h4><ul>'+''.join('<li>'+e(item)+'</li>' for item in copy['topics'])+'</ul></section>'
  pat=r'(<article class="detail-card" id="'+group+r'">.*?</h3>).*?(?=<div class="group-connections)'
  s,n=re.subn(pat,lambda m:m[1]+content,s,count=1,flags=re.S);assert n==1,group
 if '/assets/nrl-core-details.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/nrl-core-details.css?v=20261022"></head>')
 tcdesc=('Research on adaptive robot materials and structures, distributed intelligence, digital twins, and safety and social acceptance.' if en else '적응형 로봇 소재·구조, 분산 지능, 디지털 트윈, 안전성 및 사회적 수용성을 연구합니다.')
 pgdesc=('Research on robots for everyday assistance, wearable movement assistance and augmentation, and operation inside the human body.' if en else '일상생활 지원, 신체 움직임 보조·증강, 인체 내부 작동을 위한 로봇을 연구합니다.')
 for ident,title,desc in [('technical-cores','Technology Core' if en else '핵심기술',tcdesc),('project-groups','Project Group' if en else '프로젝트 그룹',pgdesc)]:
  pat=r'(<section[^>]+id="'+ident+r'"[^>]*>)<div class="detail-head">.*?</div><div class="card-grid'
  replacement='<div class="detail-head"><div><h2 class="section-title">'+title+'</h2></div><p>'+desc+'</p></div><div class="card-grid'
  s,n=re.subn(pat,lambda m:m[1]+replacement,s,count=1,flags=re.S);assert n==1,ident
 s=re.sub(r'<section class="research-logic">.*?</section>','',s,count=1,flags=re.S)
 p.write_text(s)
print('Removed NRL preamble and labs panel; applied factual TC/PG headings in both languages.')

import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "build-nrl-introduction.py"))
