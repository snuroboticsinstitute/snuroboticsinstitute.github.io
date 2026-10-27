"""Build a chronological updates feed and newsletter archive in Korean and English."""
from pathlib import Path
from html import escape as e
import json,re
R=Path(__file__).resolve().parents[1];D=R/'dist';data=json.loads((R/'scripts/news-content.json').read_text())
filters=[('all','전체','All'),('news','뉴스','News'),('events','행사','Events'),('newsletter','뉴스레터','Newsletter'),('notices','공지사항','Notices')]
def ext(url):return 'href="'+e(url,quote=True)+'" target="_blank" rel="noopener noreferrer"'
def frame(lang,title,slug,body):
 prefix='en/' if lang=='en' else '';s=(D/f'{prefix}about/director-message/index.html').read_text()
 s=re.sub(r'<title>.*?</title>','<title>'+title+' | '+('SNU Robotics Institute' if lang=='en' else '서울대학교 로보틱스연구소')+'</title>',s)
 s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+('News, events, newsletters and notices from the SNU Robotics Institute.' if lang=='en' else '서울대학교 로보틱스연구소의 뉴스, 행사, 뉴스레터, 공지사항을 모아봅니다.')+'">',s)
 # Only language links identify the route; other navigation is updated globally below.
 s=re.sub(r'<nav class="language-switch".*?</nav>', '<nav class="language-switch" aria-label="'+('Language' if lang=='en' else '언어 선택')+'"><a lang="ko" hreflang="ko" href="/'+slug+'/"'+(' aria-current="page"' if lang=='ko' else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/'+slug+'/"'+(' aria-current="page"' if lang=='en' else '')+'>English</a></nav>',s,flags=re.S)
 s=re.sub(r'(<a class="about-nav"[^>]*?) aria-current="page"',r'\1',s)
 s=re.sub(r'<p class="breadcrumb">.*?</p>','<p class="breadcrumb"><a href="/'+prefix+'updates/">'+('Updates' if lang=='en' else '소식')+'</a><span>›</span>'+title+'</p>',s,flags=re.S)
 s=re.sub(r'<h1 class="page-title">.*?</h1>','<h1 class="page-title">'+title+'</h1>',s)
 s=re.sub(r'<div class="about-tabs-wrap">.*?</div>','',s,flags=re.S)
 s=re.sub(r'<article class="message">.*?</main>',body+'\n</main>',s,flags=re.S)
 s=re.sub(r'href="(?:\.\./)+assets/themes.css"|href="/assets/themes.css(?:\?[^"]*)?"','href="/assets/themes.css?v=20261020-newsletter-original"',s)
 return s

def entries(lang):
 prefix='en/' if lang=='en' else '';items=[]
 for a in data['articles']:
  items.append(dict(id=a['id'],type='news',label=a['category'][lang],date=a['date'],title=a['title'][lang],summary=a['summary'][lang],image=a['image'],url=a['url'],external=True,action='Read article ↗' if lang=='en' else '기사 읽기 ↗'))
 for i,a in enumerate(data['talks']):
  items.append(dict(id='talk-'+str(i),type='events',label='Past Event · Video' if lang=='en' else '지난 행사 · 영상',date=a['date'].replace('.','-'),title=a['title'][lang],summary=a['speaker'][lang],image=a['image'],url=a['url'],external=True,action='Watch video ↗' if lang=='en' else '영상 보기 ↗'))
 for i,a in enumerate(data['media']):
  items.append(dict(id='media-'+str(i),type='news',label='In the Media' if lang=='en' else '언론보도',date=a['date'].replace('.','-'),title=a['title'][lang],summary=a['outlet'][lang],outlet=a['outlet'][lang],url=a['url'],external=True,action='Read coverage ↗' if lang=='en' else '보도기사 읽기 ↗'))
 items.append(dict(id='newsletter-01',type='newsletter',label='Newsletter' if lang=='en' else '뉴스레터',date='2026-09',title='SNU Robotics Newsletter · No. 1' if lang=='en' else '서울대학교 로보틱스연구소 뉴스레터 1호',summary='A new beginning, research, giving, education and conversations in robotics.' if lang=='en' else '연구소의 새로운 출발과 연구·기부·교육 소식, 로보틱스 토크를 모았습니다.',url='/'+prefix+'updates/newsletter-01/',external=False,action='View issue →' if lang=='en' else '1호 보기 →'))
 return sorted(items,key=lambda a:a['date'],reverse=True)

def card(a):
 search=' '.join([a['title'],a['summary'],a['label'],a['date']])
 for section in ('articles','talks','media'):
  for item in data[section]:
   if item['url']==a['url']:
    for field in ('title','summary','speaker','category','outlet'):
     if field in item:search+=' '+' '.join(item[field].values())
 if a['type']=='newsletter':
  return '<article class="update-card" data-update-type="newsletter" data-update-date="'+a['date']+'" data-update-search="'+e(search,quote=True)+'"><a href="'+a['url']+'"><span class="newsletter-list-label">'+e(a['label'])+'</span><h2>'+e(a['title'])+'</h2><time datetime="'+a['date']+'">'+a['date'].replace('-','.')+'</time><span class="newsletter-list-arrow" aria-hidden="true">→</span></a></article>'
 if a.get('image'):visual='<img src="'+a['image']+'" alt="" loading="lazy" decoding="async">'
 else:visual='<div class="update-cover media-cover"><span>'+e(a['label'])+'</span><strong>'+e(a['outlet'])+'</strong></div>'
 href=ext(a['url']) if a['external'] else 'href="'+a['url']+'"'
 return '<article class="update-card" data-update-type="'+a['type']+'" data-update-date="'+a['date']+'" data-update-search="'+e(search,quote=True)+'"><a '+href+'><div class="update-visual">'+visual+'</div><div class="update-copy"><div class="update-meta"><span>'+e(a['label'])+'</span><time datetime="'+a['date']+'">'+a['date'].replace('-','.')+'</time></div><h2>'+e(a['title'])+'</h2><p>'+e(a['summary'])+'</p><span class="update-action">'+a['action']+'</span></div></a></article>'

for lang in ('ko','en'):
 en=lang=='en';prefix='en/' if en else '';items=entries(lang)
 tabs='<nav class="updates-tabs" aria-label="'+('Update categories' if en else '소식 분류')+'">'+''.join('<a href="?type='+key+'" data-update-filter="'+key+'"'+(' aria-current="page"' if key=='all' else '')+'>'+ (eng if en else ko)+'</a>' for key,ko,eng in filters)+'</nav>'
 search_form='<form class="updates-search-form" role="search" method="get"><label class="visually-hidden" for="updates-search-input">'+('Search updates' if en else '소식 검색')+'</label><input id="updates-search-input" name="q" type="search" maxlength="120" placeholder="'+('Search updates' if en else '소식 검색')+'" autocomplete="off"><input type="hidden" name="type" value="all"><input type="hidden" name="theme" value="light"><button type="submit">'+('Search' if en else '검색')+'</button></form>'
 body='<div class="updates-content">'+tabs+'<div class="updates-toolbar"><p class="updates-status" role="status" aria-live="polite">'+('14 updates' if en else '전체 소식 14건')+'</p>'+search_form+'</div><div class="updates-grid" data-layout="list">'+''.join(card(a) for a in items)+'</div><p class="updates-empty" hidden>'+('No updates in this category yet.' if en else '등록된 소식이 없습니다.')+'</p></div><script src="/assets/updates.js?v=20261019-list"></script>'

 s=frame(lang,'Updates' if en else '소식','updates',body)
 path=D/f'{prefix}updates/index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s)
 # Keep previous /news links working as a news-filtered view.
 alias=s.replace('data-update-filter="all" aria-current="page"','data-update-filter="all"').replace('data-update-filter="news"','data-update-filter="news" aria-current="page"')
 alias=alias.replace('data-layout="list"','data-layout="cards"')
 alias=alias.replace('href="/updates/"','href="/news/"').replace('href="/en/updates/"','href="/en/news/"')
 (D/f'{prefix}news/index.html').write_text(alias)
 # Display the supplied issue in its original newsletter layout.
 archive='<div class="updates-content newsletter-original"><a class="about-text-link" href="/'+prefix+'updates/?type=newsletter">'+('← All newsletters' if en else '← 뉴스레터 목록')+'</a>'
 if en:archive+='<p class="newsletter-language-note">Original newsletter · Korean-language edition</p>'
 archive+='<iframe class="newsletter-document" src="/assets/newsletter-01.html?v=20261020-issue" title="'+('SNU Robotics Newsletter No. 1 (Korean)' if en else '서울대학교 로보틱스연구소 뉴스레터 1호 원문')+'" sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox" scrolling="no"></iframe><noscript><p><a href="/assets/newsletter-01.html">'+('Open newsletter' if en else '뉴스레터 원문 열기')+'</a></p></noscript></div><script src="/assets/newsletter-embed.js" defer></script>'
 path=D/f'{prefix}updates/newsletter-01/index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(frame(lang,'Newsletter No. 1' if en else '뉴스레터 1호','updates/newsletter-01',archive))
# Flatten the Updates menu and point all links to the unified feed.
for p in D.rglob('*.html'):
 if 'font-preview' in p.parts or 'assets' in p.relative_to(D).parts:continue
 en=p.relative_to(D).parts[0]=='en';prefix='en/' if en else '';s=p.read_text()
 active=p.relative_to(D).as_posix().startswith(prefix+'updates/') or p.relative_to(D).as_posix()==prefix+'news/index.html'
 nav='<a class="updates-nav" href="/'+prefix+'updates/"'+(' aria-current="page"' if active else '')+'>'+('Updates' if en else '소식')+'</a>'
 s=re.sub(r'<details class="nav-group"[^>]*>\s*<summary>(소식|Updates)</summary>.*?</details>',nav,s,flags=re.S)
 s=re.sub(r'<a class="updates-nav"[^>]*>.*?</a>',nav,s,flags=re.S)
 if p==D/f'{prefix}index.html':s=s.replace('href="/'+prefix+'news/"','href="/'+prefix+'updates/"')
 p.write_text(s)

# Reapply section breadcrumbs after generating page shells.
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "build-breadcrumbs.py"))

runpy.run_path(str(Path(__file__).resolve().parent / "build-about-navigation.py"))
