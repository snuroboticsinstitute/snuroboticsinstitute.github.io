"""Bilingual institute history, summarized from the supplied establishment record."""
from pathlib import Path
from html import escape as e
import re
D=Path(__file__).resolve().parents[1]/'dist'
# Earlier events: user-supplied image dated 2026-10-21. 2026 events: confirmed site facts.
years=[
('2026',[
 ('07','교육부·과학기술정보통신부 지정 국가연구소(NRL 2.0) 선정','Selected for the NRL 2.0 program by the Ministry of Education and the Ministry of Science and ICT.'),
 ('03','서울대학교 공과대학 주관연구소로 설립 · 초대소장 조규진 교수','Established as an institute under the SNU College of Engineering, with Professor Kyu-jin Cho as its inaugural director.')]),
('2024',[
 ('11.29','서울대 로보틱스 데이 개최 · 25개 연구실 참여','Held SNU Robotics Day with participation from 25 laboratories.'),
 ('09–11','공과대학 Keep Watch 프로그램을 통해 연구소 설립 준비','Prepared for the Institute’s establishment through the College of Engineering’s Keep Watch program.'),
 ('','서울대–현대기아차 로보틱스 공동연구실 과제 수행(2024–2027)','Began the SNU–Hyundai–Kia joint robotics laboratory project (2024–2027).')]),
('2023',[
 ('','서울대 삼성전자 로봇교육 Track 신설(2023–2028)','Launched the SNU–Samsung Electronics robotics education track (2023–2028).')]),
('2022',[
 ('07.27','서울대 로봇연구소 설립추진위원회 발족','Formed the committee to establish a robotics institute at SNU.')]),
('2021',[
 ('','SNU Robotics 홈페이지 개설','Launched the SNU Robotics website.')]),
('2016',[
 ('','인간중심소프트로봇연구센터 과제 수행(2016–2025)','Began the human-centered soft robotics research center project (2016–2025).')]),
('2013',[
 ('','국방생체모방 자율로봇 센터 과제 수행(2013–2021)','Began the defense biomimetic autonomous robotics center project (2013–2021).')]),
('2009',[
 ('','멀티스케일 로봇 기초연구실 과제 수행(2009–2014)','Began the multi-scale robotics basic research laboratory project (2009–2014).')])]
for en in (False,True):
 pre='en/' if en else '';s=(D/pre/'about/director-message/index.html').read_text();label='History' if en else '연혁'
 s=re.sub(r'<title>.*?</title>','<title>'+label+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</title>',s)
 s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+('Research collaborations and key milestones in the establishment of SNU Robotics Institute.' if en else '서울대학교 로보틱스연구소의 설립 기반과 주요 연혁을 소개합니다.')+'">',s)
 s=re.sub(r'<h1 class="page-title">.*?</h1>','<h1 class="page-title">'+label+'</h1>',s)
 s=re.sub(r'<p class="breadcrumb">.*?</p>','<p class="breadcrumb"><a href="/'+pre+'about/director-message/">'+('About' if en else '소개')+'</a><span aria-hidden="true">›</span><span>'+label+'</span></p>',s,flags=re.S)
 s=re.sub(r'<nav class="language-switch".*?</nav>','<nav class="language-switch" aria-label="Language"><a lang="ko" hreflang="ko" href="/about/history/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/about/history/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',s,count=1,flags=re.S)
 body='<section class="history-content" aria-label="'+label+'"><dl class="history-timeline">'+''.join('<div class="history-year"><dt>'+year+'</dt><dd><ul>'+''.join('<li><span class="history-date">'+date+'</span><p>'+e(english if en else korean)+'</p></li>' for date,korean,english in items)+'</ul></dd></div>' for year,items in years)+'</dl></section>'
 s=re.sub(r'<article class="message">.*?</main>',lambda m:body+'</main>',s,flags=re.S)
 if '/assets/history.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/history.css?v=20261021-vision"></head>')
 p=D/pre/'about/history/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
# Add History to each About tab bar, between Overview and Directions.
for p in D.rglob('index.html'):
 if 'font-preview' in p.parts or 'assets' in p.relative_to(D).parts:continue
 s=p.read_text()
 if 'class="about-tabs"' not in s:continue
 en=p.relative_to(D).parts[0]=='en';pre='en/' if en else ''
 labels=[('at-a-glance','At a Glance' if en else '한눈에 보기'),('director-message','Director’s Message' if en else '소장 인사말'),('vision','Vision' if en else '비전'),('history','History' if en else '연혁'),('directions','Directions' if en else '오시는 길')]
 slug=p.parent.name
 tabs='<nav class="about-tabs" aria-label="'+('About sections' if en else '소개 페이지')+'">'+''.join('<a href="/'+pre+'about/'+key+'/"'+(' aria-current="page"' if slug==key else '')+'>'+text+'</a>' for key,text in labels)+'</nav>'
 s=re.sub(r'<nav class="about-tabs".*?</nav>',lambda m:tabs,s,count=1,flags=re.S)
 if '/assets/history.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/history.css?v=20261021-vision"></head>')
 p.write_text(s)
print('Created bilingual History and added the About tabs.')

import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "build-about-navigation.py"))
