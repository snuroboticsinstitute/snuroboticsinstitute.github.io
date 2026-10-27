"""Publish the approved institute vision and its English translation."""
from pathlib import Path
from html import escape as e
import re
D=Path(__file__).resolve().parents[1]/'dist'
content={
 'ko':{
  'title':'교육·연구·창업이 연계되는 로보틱스 생태계 구축',
  'intro':'서울대학교 로보틱스연구소는 다양한 분야의 연구 역량을 결합하고, 교육과 연구의 성과가 기술의 활용과 창업으로 이어지는 생태계를 구축하고자 합니다. 이를 통해 세계적 경쟁력을 갖춘 연구소로 발전하고, 대한민국 로봇 산업의 경쟁력 강화에 기여하겠습니다.',
  'sections':[
   ('융합연구를 통한 창의적 기술 개발','서로 다른 분야의 연구자들이 공동으로 문제를 정의하고 해결하는 연구 환경을 조성합니다. 학과와 전공의 경계를 넘어 지식과 연구 방법을 결합하고, 개별 분야의 연구만으로는 도출하기 어려운 새로운 로봇 기술을 개발합니다.'),
   ('사회적 수요에 기반한 기술 혁신','사회와 산업에서 실제로 필요한 기술을 연구합니다. 기술을 사용할 사람과 적용 환경의 요구를 연구 기획에 반영하고, 개발한 기술의 유용성을 현장에서 검증합니다. 이러한 과정을 통해 연구성과가 실제 활용으로 이어지도록 합니다.'),
   ('실습 중심 교육을 통한 인력 양성','학생들이 직접 설계하고 제작하며 실험할 수 있는 교육 기반을 마련합니다. 연구 장비와 공간, 연구자의 전문성을 교육에 연결해 실제 문제를 해결하는 경험을 제공합니다. 이를 통해 이론과 구현 능력을 함께 갖춘 로보틱스 인재를 양성합니다.'),
   ('기술 개발부터 사업화·창업까지 이어지는 지원','연구성과의 기술 개발, 스케일업, 사업화를 연속적으로 지원하는 Lab to Market 체계를 구축합니다. 테크니컬 스태프는 상용화에 필요한 기술 고도화를 지원하고, 시장 전문가와 창업가는 기술의 적용 시장과 사업 기회를 구체화합니다. 연구자가 기술을 발전시키는 과정과 창업을 준비하는 과정이 연결되도록 합니다.'),
   ('새로운 도전을 지속할 수 있는 연구 환경','연구자가 창업에 도전한 뒤에도 연구소로 돌아와 후속 연구와 새로운 시도를 이어갈 수 있는 ‘Return to RI’ 지원체계를 지향합니다. 창업 과정의 위험을 줄이고, 현장에서 얻은 경험이 다시 연구와 교육에 축적되도록 하겠습니다.') ]},
 'en':{
  'title':'A robotics ecosystem connecting education, research and entrepreneurship',
  'intro':'SNU Robotics Institute aims to bring together research expertise across disciplines and build an ecosystem in which education and research lead to practical technology applications and new ventures. Through this approach, we seek to become an internationally competitive research institute and strengthen the competitiveness of Korea’s robotics industry.',
  'sections':[
   ('Creative technologies through interdisciplinary research','We foster a research environment in which researchers from different fields define and solve problems together. By combining knowledge and research methods across departments and disciplines, we develop robotics technologies that would be difficult to achieve within a single field.'),
   ('Technology innovation driven by societal needs','We pursue technologies that address real needs in society and industry. The requirements of users and application environments inform research planning, and the usefulness of new technologies is validated in the field. This process helps research outcomes translate into practical applications.'),
   ('Developing talent through hands-on education','We establish an educational foundation that enables students to design, build and experiment directly. Research equipment, spaces and expertise are connected with education to give students experience in solving real problems. We aim to develop robotics talent with both theoretical knowledge and practical implementation skills.'),
   ('Support from technology development to commercialization and entrepreneurship','We are building a Lab to Market framework that provides continuous support for technology development, scale-up and commercialization. Technical staff help advance technologies toward commercial use, while market experts and entrepreneurs identify application markets and business opportunities. Our aim is to connect the development of research technologies with preparations for launching new ventures.'),
   ('A research environment that supports continued experimentation and new ventures','We envision a “Return to RI” support framework that enables researchers to return to the Institute after pursuing entrepreneurship and continue with further research and new initiatives. We aim to reduce the risks of entrepreneurship and bring experience gained in the field back into research and education.') ]}}
for en in (False,True):
 pre='en/' if en else '';c=content['en' if en else 'ko'];label='Vision' if en else '비전'
 s=(D/pre/'about/director-message/index.html').read_text()
 s=re.sub(r'<title>.*?</title>','<title>'+label+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</title>',s)
 s=re.sub(r'<meta name="description" content="[^"]*">',lambda m:'<meta name="description" content="'+e(c['title'],quote=True)+'">',s)
 s=re.sub(r'<h1 class="page-title">.*?</h1>','<h1 class="page-title">'+label+'</h1>',s)
 s=re.sub(r'<p class="breadcrumb">.*?</p>','<p class="breadcrumb"><a href="/'+pre+'about/director-message/">'+('About' if en else '소개')+'</a><span aria-hidden="true">›</span><span>'+label+'</span></p>',s,flags=re.S)
 s=re.sub(r'<nav class="language-switch".*?</nav>','<nav class="language-switch" aria-label="Language"><a lang="ko" hreflang="ko" href="/about/vision/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/about/vision/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',s,count=1,flags=re.S)
 body='<article class="vision-content"><header class="vision-intro"><h2>'+e(c['title'])+'</h2><p>'+e(c['intro'])+'</p></header>'+''.join('<section class="vision-principle"><h3>'+e(title)+'</h3><p>'+e(text)+'</p></section>' for title,text in c['sections'])+'</article>'
 s=re.sub(r'<article class="message">.*?</main>',lambda m:body+'</main>',s,flags=re.S)
 s=s.replace('</head>','<link rel="stylesheet" href="/assets/vision.css?v=20261021"></head>')
 p=D/pre/'about/vision/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
# One tab sequence across all About pages.
for p in D.rglob('index.html'):
 if 'font-preview' in p.parts or 'assets' in p.relative_to(D).parts:continue
 s=p.read_text()
 if 'class="about-tabs"' not in s:continue
 en=p.relative_to(D).parts[0]=='en';pre='en/' if en else '';slug=p.parent.name
 labels=[('at-a-glance','At a Glance' if en else '한눈에 보기'),('director-message','Director’s Message' if en else '소장 인사말'),('vision','Vision' if en else '비전'),('history','History' if en else '연혁'),('directions','Directions' if en else '오시는 길')]
 tabs='<nav class="about-tabs" aria-label="'+('About sections' if en else '소개 페이지')+'">'+''.join('<a href="/'+pre+'about/'+key+'/"'+(' aria-current="page"' if slug==key else '')+'>'+text+'</a>' for key,text in labels)+'</nav>'
 s=re.sub(r'<nav class="about-tabs".*?</nav>',lambda m:tabs,s,count=1,flags=re.S)
 s=re.sub(r'history.css\?v=[^"\s]+','history.css?v=20261021-vision',s)
 p.write_text(s)
print('Published approved Korean vision copy and English translation to bilingual source pages.')

import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "build-about-navigation.py"))
