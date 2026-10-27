"""Keep NRL research and faculty under Research, with legacy link compatibility."""
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit
from html import escape as e
import re,shutil,json
D=Path(__file__).resolve().parents[1]/'dist'
PEOPLE={p['id']:('faculty' if p['category']=='참여' else 'affiliated') for p in json.loads((D/'research/nrl/faculty/directory.json' if (D/'research/nrl/faculty/directory.json').exists() else D/'people/faculty/directory.json').read_text())}
LABELS=[('technical-cores','핵심기술','Technology Core'),('project-groups','프로젝트 그룹','Project Group'),('faculty/','참여교수','Participating Faculty'),('affiliated/','연계교수','Affiliated Faculty')]
def absolute(s,old):
 def attr(m):
  value=m[2]
  if not value or value.startswith(('#','?')) or urlsplit(value).scheme or value.startswith('//'):return m[0]
  return m[1]+'"'+urljoin(old,value)+'"'
 return re.sub(r'\b(href=|src=|action=)"([^"]*)"',attr,s)
def tabs(en,active):
 base='/'+('en/' if en else '')+'research/nrl/'
 return '<nav class="nrl-tabs" aria-label="'+('NRL sections' if en else '국가연구소 세부 메뉴')+'">'+''.join('<a href="'+(('#'+key) if active=='research' and not key.endswith('/') else base+('#'+key if not key.endswith('/') else key))+'"'+(' aria-current="page"' if (active=='research' and key=='technical-cores') or key==active else '')+'>'+e(eng if en else ko)+'</a>' for key,ko,eng in LABELS)+'</nav>'
def crumb(en,current):
 pre='/en' if en else '';research='Research' if en else '연구';nrl='NRL' if en else '국가연구소'
 return '<p class="breadcrumb"><a href="'+pre+'/research/">'+research+'</a><span aria-hidden="true">›</span><a href="'+pre+'/research/nrl/">'+nrl+'</a><span aria-hidden="true">›</span><span data-breadcrumb-current>'+e(current)+'</span></p>'

for en in (False,True):
 prefix='en/' if en else '';base='/'+prefix;label='NRL' if en else '국가연구소'
 nrldir=D/prefix/'research/nrl';nrldir.mkdir(parents=True,exist_ok=True)
 p=nrldir/'index.html'
 if not p.exists():p.write_text(absolute((D/prefix/'research/index.html').read_text(),base+'research/'))
 s=p.read_text()
 s=re.sub(r'<title>.*?</title>','<title>'+label+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</title>',s)
 s=re.sub(r'<h1 class="page-title">.*?</h1>','<h1 class="page-title">'+label+'</h1>',s)
 s=re.sub(r'<p class="breadcrumb">.*?</p>',lambda m:crumb(en,'Technology Core' if en else '핵심기술'),s,flags=re.S)
 s=re.sub(r'<nav class="(?:research-tabs|nrl-tabs)".*?</nav>',lambda m:tabs(en,'research'),s,count=1,flags=re.S)
 s=re.sub(r'(<nav class="language-switch".*?</nav>)',lambda m:re.sub(r'href="[^"]*"',lambda x:'href="'+('/en/research/nrl/' if 'hreflang="en"' in m[0][:x.start()].split('<a')[-1] else '/research/nrl/')+'"',m[0]),s,count=1,flags=re.S)
 s=s.replace('/assets/research-tabs.js"','/assets/research-tabs.js?v=20261020-nrl"')
 s=s.replace('3 PROJECT GROUPS · 4 TECHNICAL CORES','NRL · Technology Core &amp; Project Group')
 p.write_text(s)
 for kind in ('faculty','affiliated'):
  target=nrldir/kind/'index.html';target.parent.mkdir(exist_ok=True)
  if not target.exists():target.write_text(absolute((D/prefix/f'people/{kind}/index.html').read_text(),base+f'people/{kind}/'))
  s=target.read_text();current=('Participating Faculty' if kind=='faculty' else 'Affiliated Faculty') if en else ('참여교수' if kind=='faculty' else '연계교수')
  s=re.sub(r'<nav class="(?:faculty-tabs|nrl-tabs)".*?</nav>',lambda m:tabs(en,kind+'/'),s,count=1,flags=re.S)
  s=re.sub(r'<section class="faculty-banner">.*?</section>',lambda m:'<section class="faculty-banner">'+crumb(en,current)+'<h1>'+label+'</h1><p>'+('The faculty behind our NRL research' if en else '국가연구소 연구를 함께하는 교수진')+'</p></section>',s,count=1,flags=re.S)
  s=re.sub(r'<title>.*?</title>','<title>'+current+' · '+label+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</title>',s)
  s=re.sub(r'<nav class="language-switch".*?</nav>',lambda m:'<nav class="language-switch" aria-label="Language"><a lang="ko" hreflang="ko" href="/research/nrl/'+kind+'/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/research/nrl/'+kind+'/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',s,count=1,flags=re.S)
  target.write_text(s)
 # Keep the data file beside its canonical faculty page; old endpoint remains compatible.
 data=nrldir/'faculty/directory.json';old=D/prefix/'people/faculty/directory.json'
 if not data.exists():shutil.copy2(old,data)
 else:shutil.copy2(data,old)
 # Research becomes the institute-wide entry point, with NRL beneath it.
 landing=D/prefix/'research/index.html'
 if 'data-research-landing' not in landing.read_text():
  shell=s=(nrldir/'index.html').read_text()
  start=s.index('<div class="research-page">');end=s.index('</main>',start)
  body='<div class="research-page" data-research-landing><section class="intro"><p class="eyebrow">'+('Research programs' if en else '연구사업')+'</p><h2>'+('Research at SNU Robotics Institute' if en else '서울대학교 로보틱스연구소의 연구')+'</h2></section><nav class="nrl-tabs" aria-label="'+('Research programs' if en else '연구사업 메뉴')+'"><a href="'+base+'research/nrl/">'+label+'</a></nav><section class="nrl-entry"><p class="eyebrow">NRL 2.0 · National Research Lab</p><h2><a href="'+base+'research/nrl/">'+label+'</a></h2><p>'+('Explore the Technology Cores, Project Groups and faculty of our NRL program.' if en else '국가연구소 사업의 핵심기술(TC)과 프로젝트 그룹(PG), 참여·연계교수를 소개합니다.')+'</p><a class="more-link" href="'+base+'research/nrl/">'+('Explore NRL' if en else '국가연구소 바로가기')+' <span>→</span></a></section></div>'
  s=s[:start]+body+s[end:]
  s=re.sub(r'<title>.*?</title>','<title>'+('Research | SNU Robotics Institute' if en else '연구 | 서울대학교 로보틱스연구소')+'</title>',s)
  s=re.sub(r'<h1 class="page-title">.*?</h1>','<h1 class="page-title">'+('Research' if en else '연구')+'</h1>',s)
  s=re.sub(r'<p class="breadcrumb">.*?</p>','<p class="breadcrumb">'+('Research' if en else '연구')+'</p>',s,flags=re.S)
  s=re.sub(r'<script src="/assets/research-tabs.js[^\"]*" defer></script>','<script src="/assets/research-legacy.js" defer></script>',s)
  s=re.sub(r'<nav class="language-switch".*?</nav>','<nav class="language-switch" aria-label="Language"><a lang="ko" hreflang="ko" href="/research/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/research/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',s,count=1,flags=re.S)
  landing.write_text(s)
# Normalize all main-page links against their original location, then move references.
for p in D.rglob('index.html'):
 rel=p.relative_to(D).as_posix()
 if 'font-preview/' in rel or rel.startswith('assets/'):continue
 en=rel.startswith('en/');pre='/en' if en else '';local=rel.removeprefix('en/');s=absolute(p.read_text(),'/'+rel.removesuffix('index.html'))
 def move(m):
  u=urlsplit(m[1]);path=u.path
  if u.scheme or u.netloc:return m[0]
  if u.fragment in PEOPLE and re.search(r'/(people|research/nrl)/(faculty|affiliated)/$',path):
   prefix='/en' if path.startswith('/en/') else ''
   path=prefix+'/research/nrl/'+PEOPLE[u.fragment]+'/'
  for prefix in ('','/en'):
   for kind in ('faculty','affiliated'):
    if path==prefix+'/people/'+kind+'/':path=prefix+'/research/nrl/'+kind+'/'
   if path==prefix+'/research/' and (re.fullmatch(r'(tc[1-4]|pg[1-3])',u.fragment) or u.fragment in ('technical-cores','project-groups','participating-labs')):path=prefix+'/research/nrl/'
  return 'href="'+urlunsplit((u.scheme,u.netloc,path,u.query,u.fragment))+'"'
 s=re.sub(r'href="([^"]*)"',move,s)
 for prefix in ('','/en'):
  for anchor in ('joint-project','partnership','membership','donate'):
   s=s.replace('href="'+prefix+'/#'+anchor+'"','href="'+prefix+'/engage/#'+anchor+'"')
  s=s.replace('href="'+prefix+'/#tour"','href="'+prefix+'/visit/"')
  if local=='index.html':
   for anchor in ('joint-project','partnership','membership','donate'):
    s=s.replace('href="#'+anchor+'"','href="'+pre+'/engage/#'+anchor+'"')
   s=s.replace('href="#tour"','href="'+pre+'/visit/"')
 s=re.sub(r'((?:href|src)=")/(?:en/)?(?:updates|news)/assets/',r'\1/assets/',s)
 # NRL is a research program nested under Research.
 nav='<details class="nav-group research-nav-group"'+(' open' if local.startswith('research/') else '')+'><summary><a class="research-nav" href="'+pre+'/research/"'+(' aria-current="page"' if local.startswith('research/') else '')+'>'+('Research' if en else '연구')+'</a></summary><a class="nav-child" href="'+pre+'/research/nrl/"'+(' aria-current="page"' if local.startswith('research/nrl/') else '')+'>'+('NRL' if en else '국가연구소')+'</a></details>'
 s=re.sub(r'<a class="nrl-nav"[^>]*>.*?</a>','',s,flags=re.S)
 if 'research-nav-group' in s:s=re.sub(r'<details class="nav-group research-nav-group".*?</details>',lambda m:nav,s,flags=re.S)
 else:s=re.sub(r'<a class="research-nav"[^>]*>.*?</a>',lambda m:nav,s,flags=re.S)
 s=re.sub(r'<a class="members-nav"[^>]*>.*?</a>',lambda m:'<a class="members-nav" href="'+pre+'/people/joint-faculty/"'+(' aria-current="page"' if local.startswith('people/') else '')+'>'+('People' if en else '구성원')+'</a>',s)
 if local.startswith('people/') and local not in ('people/faculty/index.html','people/affiliated/index.html'):
  current=local.split('/')[1]
  membertabs='<nav class="faculty-tabs" aria-label="'+('People sections' if en else '구성원 분류')+'">'+''.join('<a href="'+pre+'/people/'+k+'/"'+(' aria-current="page"' if k==current else '')+'>'+text+'</a>' for k,text in [('joint-faculty','Joint Faculty' if en else '겸무교수'),('postdoctoral-researchers','Postdoctoral Researchers' if en else '박사후 연구원'),('leadership','Leadership' if en else '운영진'),('technical-staff','Technical Staff' if en else '테크니컬 스태프'),('administration','Administrative Office' if en else '행정실')])+'</nav>'
  s=re.sub(r'<nav class="faculty-tabs".*?</nav>',lambda m:membertabs,s,flags=re.S)
  s=re.sub(r'(<p class="breadcrumb"><a href=")[^"]+(">(?:People|구성원)</a>)',lambda m:m[1]+pre+'/people/joint-faculty/'+m[2],s)
 # Shared Engage menu links to its own content, never deleted home anchors.
 engage='<details class="nav-group"><summary>'+('Engage' if en else '참여하기')+'</summary>'+''.join('<a class="nav-child" href="'+pre+'/engage/#'+anchor+'">'+label+'</a>' for anchor,label in [('joint-project','Research Collaboration' if en else '공동과제 제안'),('partnership','Industry Partnerships' if en else '산학협력·기술이전'),('membership','Membership' if en else '멤버십'),('donate','Giving' if en else '기부하기')])+'</details>'
 s=re.sub(r'<details class="nav-group"[^>]*><summary>(?:참여하기|Engage)</summary>.*?</details>',lambda m:engage,s,flags=re.S)
 if local=='index.html':
  # Home group previews now identify the NRL program explicitly.
  s=s.replace('<h2 class="section-title">연구</h2>','<h2 class="section-title">국가연구소</h2>').replace('<h2 class="section-title">Research</h2>','<h2 class="section-title">NRL</h2>')
  s=s.replace('href="'+pre+'/research/">전체 연구 보기','href="'+pre+'/research/nrl/">국가연구소 전체 보기').replace('href="'+pre+'/research/">Explore our research','href="'+pre+'/research/nrl/">Explore NRL')
 if '/assets/nrl-structure.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/nrl-structure.css?v=20261022-people"></head>')
 p.write_text(s)
# Former faculty URLs remain stable entry points, preserving filters and person anchors.
for en in (False,True):
 pre='/en' if en else ''
 for kind in ('faculty','affiliated'):
  target=pre+'/research/nrl/'+kind+'/'
  label='Continue to NRL faculty' if en else '국가연구소 교수 명단으로 이동'
  s='<!doctype html><html lang="'+('en' if en else 'ko')+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>'+label+'</title><link rel="canonical" href="'+target+'"></head><body data-legacy-redirect><p><a href="'+target+'">'+label+'</a></p><script>location.replace('+repr(target)+'+location.search+location.hash);</script></body></html>'
  (D/(pre.lstrip('/')+'/' if pre else '')/f'people/{kind}/index.html').write_text(s)
print('NRL routes and shared navigation updated in both languages.')

# Apply the editorial rule on every structure rebuild.
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "normalize-nrl-copy.py"))

runpy.run_path(str(Path(__file__).resolve().parent / "build-research-landing.py"))
