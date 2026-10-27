"""NRL overview is the default tab. Preserve all TC/PG and faculty deep links."""
from pathlib import Path
from html import escape as e
import re
D=Path(__file__).resolve().parents[1]/'dist'
COPY={
'ko':{
'label':'국가연구소(NRL 2.0) 소개','title':'국가연구소 사업',
'lead':'서울대학교 로보틱스연구소는 국가연구소(NRL 2.0) 사업을 통해 로봇의 몸과 지능을 함께 설계하는 인간중심 피지컬 AI 원천기술을 연구합니다.',
'sections':[
('국가연구소 사업과 서울대 로보틱스연구소','국가연구소(NRL 2.0)는 교육부와 과학기술정보통신부가 공동으로 추진하는 대학 부설연구소 육성 사업입니다. 서울대학교 로보틱스연구소는 2026년 이 사업에 선정되어, 최대 10년간의 장기 지원을 바탕으로 「인간중심 피지컬 AI 로보틱스 연구소」 과제를 수행합니다. 국가연구소는 로보틱스연구소가 수행하는 연구사업으로, 공학·의학·보건학·뇌인지과학·사회과학 등 여러 분야의 연구진이 함께 참여합니다.'),
('연구 목표: 물리지능과 분산지능의 결합','서울대학교 로보틱스연구소는 이 사업을 통해 로봇의 몸과 지능을 함께 설계하는 인간중심 피지컬 AI 원천기술을 연구합니다. 로봇의 모든 판단과 제어를 중앙의 AI에 집중하는 방식은 복잡한 실제 환경에서 연산량, 에너지 소비, 반응 속도에 한계가 있습니다. 이 과제는 소재와 구조, 접촉과 변형이 계산과 적응의 일부를 담당하는 체화된 물리지능과, 로봇의 각 부위가 정보를 처리하고 학습하며 상위 지능과 협력하는 분산지능을 결합합니다. 이를 통해 환경과 사용자에 적응하는 로봇의 설계·학습·제어 원리를 개발하는 것이 목표입니다.'),
('인간중심의 설계와 검증','인간중심이라는 목표는 로봇의 기능뿐 아니라 사람이 로봇을 사용하는 조건을 연구한다는 뜻입니다. 안전성, 임상적 신뢰성, 사용자 자율성, 사회적 수용성을 설계 단계부터 반영하고 평가합니다. 로봇·인간·환경의 상호작용을 재현하는 디지털 트윈과 실제 실험을 연계해 기술의 성능과 적용 가능성을 검증합니다.'),
('연구성과의 실증과 사업화','공통 원천기술을 실제 사용 환경에 적용하고, 실증 결과를 다시 기술 개발에 반영하는 연구 체계를 지향합니다. 연구성과가 연구실에 머무르지 않도록 제작·데이터·컴퓨팅 등 공동 연구 기반을 마련하고, 산학협력과 기술사업화·창업을 연계하는 Lab-to-Market 체계를 추진합니다.')],
'groups':'연구 체계: 핵심기술과 프로젝트 그룹',
'groupintro':'핵심기술(TC)은 여러 응용에 공통으로 필요한 원천기술을 개발하고, 프로젝트 그룹(PG)은 사용 환경과 연구 요구를 구체화하며 기술을 적용·검증합니다.',
'tcs':[('MORPHI Body','소재·구조의 물리적 특성을 활용하는 적응형 로봇 몸체'),('MOSAIC Intelligence','국소 지능과 전역 지능이 협력하는 분산지능'),('Digital Twin','로봇·인간·환경의 설계, 학습, 검증을 위한 디지털 트윈'),('Human Value','안전성, 임상적 신뢰성, 사회적 수용성의 평가')],
'pgs':[('Life Companion','생활 공간에서 사용자의 의도와 환경 변화에 적응하는 일상 지원 로봇'),('Wearable','사람의 동작·힘·균형을 보조하거나 확장하는 웨어러블 로봇'),('Intra-Body','인체 내부 환경과 상호작용하는 로봇 및 진단·치료용 인터페이스')],
},
'en':{
'label':'About NRL 2.0','title':'The National Research Lab program',
'lead':'Through the National Research Lab (NRL 2.0) program, SNU Robotics Institute develops foundational technologies for human-centered physical AI by co-designing robot bodies and intelligence.',
'sections':[
('The NRL program at SNU Robotics Institute','NRL 2.0 is a national program jointly administered by the Ministry of Education and the Ministry of Science and ICT to develop university-affiliated research institutes. Selected in 2026, SNU Robotics Institute undertakes the Human-centered Physical AI Robotics (H-PAIR) Institute project with support for up to ten years. NRL is a research program within SNU Robotics Institute, bringing together researchers from engineering, medicine, public health, brain and cognitive sciences, and the social sciences.'),
('Research goal: physical and distributed intelligence','Through this program, SNU Robotics Institute develops foundational technologies for human-centered physical AI by co-designing robot bodies and intelligence. Concentrating all decisions and control in a central AI creates challenges in computation, energy use and response time in complex real-world settings. The project combines embodied physical intelligence, in which materials, structures, contact and deformation contribute to computation and adaptation, with distributed intelligence, in which local modules process information, learn and cooperate with higher-level intelligence. The goal is to establish design, learning and control principles for robots that adapt to their environments and users.'),
('Human-centered design and evaluation','Human-centered research addresses both robot capabilities and the conditions in which people use them. Safety, clinical reliability, user autonomy and social acceptance are considered and assessed from the design stage. Digital twins of robot–human–environment interactions complement physical experiments to evaluate performance and practical applicability.'),
('Validation and translation','The program aims to apply foundational technologies in realistic settings and use the results to guide further development. Shared fabrication, data and computing infrastructure supports this work. A Lab-to-Market framework connects research with industry collaboration, technology commercialization and entrepreneurship.')],
'groups':'Research framework: Technology Cores and Project Groups',
'groupintro':'Technology Cores (TCs) develop foundational technologies shared across applications. Project Groups (PGs) define use environments and research requirements, then apply and evaluate these technologies.',
'tcs':[('MORPHI Body','Adaptive robot bodies using the physical properties of materials and structures'),('MOSAIC Intelligence','Distributed intelligence coordinating local and global modules'),('Digital Twin','Robot–human–environment models for design, learning and evaluation'),('Human Value','Assessment of safety, clinical reliability and social acceptance')],
'pgs':[('Life Companion','Everyday assistance robots that adapt to user intentions and changing living environments'),('Wearable','Wearable robots that assist or augment movement, strength and balance'),('Intra-Body','Robots and diagnostic or therapeutic interfaces operating inside the human body')],
}}
labels=[('nrl-introduction','국가연구소(NRL 2.0) 소개','About NRL 2.0'),('technical-cores','핵심기술','Technology Core'),('project-groups','프로젝트 그룹','Project Group'),('faculty/','참여교수','Participating Faculty'),('affiliated/','연계교수','Affiliated Faculty')]
for en in (False,True):
 lang='en' if en else 'ko';c=COPY[lang];base=('/en' if en else '')+'/research/nrl/'
 for kind in ('','faculty/','affiliated/'):
  p=D/(base+kind).lstrip('/')/'index.html';s=p.read_text()
  tabs='<nav class="nrl-tabs" aria-label="'+('NRL sections' if en else '국가연구소 세부 메뉴')+'">'
  for key,ko,eng in labels:
   href=base+key if key.endswith('/') else (('#'+key) if not kind else base+('#'+key if key!='nrl-introduction' else ''))
   active=(not kind and key=='nrl-introduction') or key==kind
   tabs+='<a href="'+href+'"'+(' aria-current="page"' if active else '')+'>'+e(eng if en else ko)+'</a>'
  tabs+='</nav>'
  s=re.sub(r'<nav class="nrl-tabs".*?</nav>',lambda m:tabs,s,count=1,flags=re.S)
  if not kind:
   sections=[]
   for h,t in c['sections'][1:3]:sections.append('<section class="nrl-overview-section"><h3>'+e(h)+'</h3><p>'+e(t)+'</p></section>')
   groups='<section class="nrl-overview-section"><h3>'+e(c['groups'])+'</h3><p>'+e(c['groupintro'])+'</p><div class="nrl-overview-groups">'
   for typ,items,title in [('tc',c['tcs'],'Technology Core' if en else '핵심기술'),('pg',c['pgs'],'Project Group' if en else '프로젝트 그룹')]:
    groups+='<section><h4>'+title+'</h4><ul>'+''.join('<li><a href="#'+typ+str(i)+'"><span>'+typ.upper()+' '+str(i)+'</span> '+e(name)+'</a><p>'+e(desc)+'</p></li>' for i,(name,desc) in enumerate(items,1))+'</ul></section>'
   groups+='</div></section>'
   h,t=c['sections'][3]
   body='<section class="research-tab-panel nrl-overview" id="nrl-introduction"><header><h2>'+e(c['title'])+'</h2><p class="nrl-overview-lead">'+e(c['sections'][0][1])+'</p></header>'+''.join(sections)+groups+'<section class="nrl-overview-section"><h3>'+e(h)+'</h3><p>'+e(t)+'</p></section></section>'
   s=re.sub(r'<section class="research-tab-panel nrl-overview" id="nrl-introduction">.*?</section></section>(?=<section class="detail-section)', '',s,flags=re.S)
   s=s.replace(tabs,tabs+body,1)
   s=re.sub(r'(<span data-breadcrumb-current>).*?</span>',lambda m:m[1]+e(c['label'])+'</span>',s)
   s=s.replace('id="technical-cores">','id="technical-cores" hidden>').replace('id="project-groups">','id="project-groups" hidden>')
   if '/assets/nrl-introduction.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/nrl-introduction.css?v=20261026"></head>')
  s=re.sub(r'<body(?![^>]*data-nrl-page)', '<body data-nrl-page', s, count=1)
  if '/assets/nrl-typography.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/nrl-typography.css?v=20261026"></head>')
  p.write_text(s)
print('Built bilingual NRL introduction and five-section navigation.')
