"""Add shared search, social links and the bilingual static search index."""
from pathlib import Path
from html import escape as e, unescape
from html.parser import HTMLParser
import json,re
R=Path(__file__).resolve().parents[1];D=R/'dist';settings=json.loads((R/'scripts/site-settings.json').read_text())
icons={
 'youtube':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 7s-.2-1.7-.9-2.4c-.8-.9-1.7-.9-2.1-1C17.1 3.4 12 3.4 12 3.4s-5.1 0-8 .2c-.4.1-1.3.1-2.1 1C1.2 5.3 1 7 1 7S.8 9 .8 11v2C.8 15 1 17 1 17s.2 1.7.9 2.4c.8.9 1.9.9 2.4 1 1.7.2 7.7.2 7.7.2s5.1 0 8-.2c.4-.1 1.3-.1 2.1-1 .7-.7.9-2.4.9-2.4s.2-2 .2-4v-2C23.2 9 23 7 23 7ZM9.6 15.5v-7l6.2 3.5-6.2 3.5Z"/></svg>',
 'linkedin':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5.4 7.4H1V22h4.4V7.4ZM3.2 1a2.6 2.6 0 1 0 0 5.2 2.6 2.6 0 0 0 0-5.2ZM23 13.5c0-4.4-2.4-6.4-5.6-6.4-2.6 0-3.8 1.5-4.4 2.5V7.4H8.6V22H13v-8.1c0-2.1.4-4.1 3-4.1s2.6 2.4 2.6 4.2v8H23v-8.5Z"/></svg>',
 'facebook':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.6 24V13.1h3.7l.5-4.2h-4.2V6.2c0-1.2.3-2 2.1-2H20V.4C19.6.3 18.2.2 16.6.2c-3.4 0-5.7 2.1-5.7 5.8v2.9H7v4.2h3.9V24h4.7Z"/></svg>'}
labels={'youtube':'YouTube','facebook':'Facebook','linkedin':'LinkedIn'}
for en in (False,True):
 pre='en/' if en else '';s=(D/f'{pre}about/director-message/index.html').read_text()
 s=re.sub(r'<title>.*?</title>','<title>'+('Search | SNU Robotics Institute' if en else '검색 | 서울대학교 로보틱스연구소')+'</title>',s)
 s=re.sub(r'<nav class="language-switch".*?</nav>','<nav class="language-switch" aria-label="'+('Language' if en else '언어 선택')+'"><a lang="ko" hreflang="ko" href="/search/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/search/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',s,flags=re.S)
 s=re.sub(r'(<a class="about-nav"[^>]*?) aria-current="page"',r'\1',s)
 s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+('Search people, research groups, news and information at the SNU Robotics Institute.' if en else '서울대학교 로보틱스연구소의 연구진, 연구그룹, 뉴스와 안내를 검색합니다.')+'">',s)
 s=re.sub(r'<p class="breadcrumb">.*?</p>','<p class="breadcrumb">'+('Search' if en else '검색')+'</p>',s,flags=re.S)
 s=re.sub(r'<h1 class="page-title">.*?</h1>','<h1 class="page-title">'+('Site Search' if en else '사이트 검색')+'</h1>',s)
 s=re.sub(r'<div class="about-tabs-wrap">.*?</div>','',s,flags=re.S)
 body='<section class="site-search-results" aria-label="'+('Search results' if en else '검색 결과')+'"><h2 id="search-heading">'+('Find people, research and news' if en else '연구진·연구·소식을 찾아보세요')+'</h2><p id="search-status" role="status" aria-live="polite">'+('Enter a keyword in the search box above.' if en else '상단 검색창에 검색어를 입력해 주세요.')+'</p><ol id="search-results"></ol><noscript>'+('Please enable JavaScript to search this website.' if en else '검색을 사용하려면 자바스크립트를 활성화해 주세요.')+'</noscript></section><script src="/assets/site-search.js" defer></script>'
 s=re.sub(r'<article class="message">.*?</main>',body+'</main>',s,flags=re.S)
 p=D/f'{pre}search/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
for p in D.rglob('*.html'):
 if 'font-preview' in p.parts or 'assets' in p.relative_to(D).parts or 'data-legacy-redirect' in p.read_text():continue
 en=p.relative_to(D).parts[0]=='en';pre='en/' if en else '';s=p.read_text()
 # Remove an existing utility form before rebuilding to keep this repeatable.
 s=re.sub(r'<form class="site-search-form".*?</form>','',s,flags=re.S)
 search='<form class="site-search-form" role="search" action="/'+pre+'search/" method="get"><label class="visually-hidden" for="site-search-input">'+('Search the website' if en else '홈페이지 검색')+'</label><input id="site-search-input" type="search" name="q" placeholder="'+('Search' if en else '검색')+'" autocomplete="off" maxlength="120" required><input type="hidden" name="theme" value="light"><button type="submit" aria-label="'+('Search' if en else '검색')+'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg></button></form>'
 s,n=re.subn(r'(<nav class="theme-options".*?</nav>)',lambda m:m[1]+search,s,count=1,flags=re.S);assert n==1,p
 socials='<nav class="footer-socials" aria-label="'+('Social media' if en else '소셜 미디어')+'">'+''.join('<a href="'+e(url,quote=True)+'" target="_blank" rel="noopener noreferrer" aria-label="'+labels[key]+'" title="'+labels[key]+'">'+icons[key]+'</a>' for key,url in settings['socials'].items() if url)+'</nav>'
 contact=settings['contact']
 phone=contact['phone_international'] if en else contact['phone']
 address='<address class="footer-contact"><span>'+'<br>'.join(e(line) for line in (contact['address_en'] if en else contact['address_ko']).splitlines())+'</span><span class="footer-contact-links"><a href="tel:+8228801638">'+phone+'</a><a href="mailto:'+e(contact['email'],quote=True)+'">'+e(contact['email'])+'</a></span></address>'
 name='<a class="footer-name" href="/'+pre+'">'+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</a>'
 footer='<footer class="footer"><div class="footer-compact">'+name+address+socials+'<p class="footer-copyright">© 2026 SNU Robotics Institute. All rights reserved.</p></div></footer>'
 s,n=re.subn(r'<footer class="footer">.*?</footer>',lambda m:footer,s,flags=re.S);assert n==1,p
 if '/assets/site-utilities.js' not in s:s=s.replace('</body>','<script src="/assets/site-utilities.js" defer></script></body>')
 p.write_text(s)

class Extract(HTMLParser):
 def __init__(self):super().__init__();self.main=False;self.skip=0;self.bits=[];self.title=False;self.titlebits=[];self.description=''
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='main':self.main=True
  if t=='title':self.title=True
  if t in ('script','style'):self.skip+=1
  if t=='meta' and a.get('name')=='description':self.description=a.get('content','')
 def handle_endtag(self,t):
  if t=='main':self.main=False
  if t=='title':self.title=False
  if t in ('script','style'):self.skip-=1
 def handle_data(self,d):
  if self.title:self.titlebits.append(d)
  if self.main and not self.skip:self.bits.append(d.strip())
def plain(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',s))).strip()
ko=json.loads((D/'research/nrl/faculty/directory.json').read_text());english={p['id']:p for p in json.loads((D/'en/research/nrl/faculty/directory.json').read_text())}
news=json.loads((R/'scripts/news-content.json').read_text())
for en in (False,True):
 pre='en/' if en else '';lang='en' if en else 'ko';entries=[]
 for path in sorted((D/pre).rglob('index.html')):
  rel=path.relative_to(D).as_posix()
  if (not en and rel.startswith('en/')) or any(x in rel for x in ('font-preview/','/search/')) or rel.startswith('search/'):continue
  local=rel.removeprefix(pre)
  if local in ('news/index.html','people/support/index.html') or 'data-legacy-redirect' in path.read_text():continue
  parser=Extract();source=path.read_text();parser.feed(source);title=''.join(parser.titlebits).split(' | ')[0]
  text=' '.join(parser.bits)
  if local in ('index.html','updates/index.html','research/nrl/faculty/index.html','research/nrl/affiliated/index.html','people/joint-faculty/index.html'):text=title+' '+parser.description
  entries.append(dict(title=title,text=text,url='/'+rel.removesuffix('index.html'),kind='Page' if en else '페이지',description=parser.description or title))
 joint=json.loads((R/'scripts/joint-faculty.json').read_text()) if (R/'scripts/joint-faculty.json').exists() else []
 joint_by={p['id']:p for p in joint};ko_by={p['id']:p for p in ko}
 for ident in dict.fromkeys([p['id'] for p in ko]+list(joint_by)):
  member=joint_by.get(ident)
  if member:
   person=dict(name=member['name_'+lang],dept=member['dept_'+lang],lab=member['lab_'+lang],groups=member['groups'])
   route='/'+pre+'people/joint-faculty/'
   kind='Joint Faculty' if en else '겸무교수'
  else:
   original=ko_by[ident];person=english[ident] if en else original
   section='faculty' if original['category']=='참여' else 'affiliated'
   route='/'+pre+'research/nrl/'+section+'/'
   kind='Faculty' if en else '교수'
  source=(D/route.lstrip('/')/'index.html').read_text()
  m=re.search(r'<article\b[^>]*\bid="'+ident+'"[^>]*>',source);assert m
  aliases=unescape(re.search(r'data-search="([^"]*)"',m[0])[1])
  title=person['name']+(' · '+person['dept'] if person['dept'] else '')
  description=' · '.join(filter(None,[person['lab'],person['dept'],' / '.join(person['groups'])]))
  entries.append(dict(title=title,text=aliases,url=route+'#'+ident,kind=kind,description=description))
 source=(D/f'{pre}research/nrl/index.html').read_text()
 for m in re.finditer(r'<article class="detail-card" id="((?:tc|pg)\d)">(.*?)</article>',source,re.S):
  anchor,body=m.groups();h=re.search(r'<h3>(.*?)</h3>',body,re.S)
  entries.append(dict(title=anchor[:2].upper()+' '+anchor[2:]+' · '+plain(h[1]),text=plain(body),url='/'+pre+'research/nrl/#'+anchor,kind='Research Group' if en else '연구그룹',description=plain(re.search(r'</h3>.*?<p>(.*?)</p>',body,re.S)[1])))
 for a in news['articles']:
  entries.append(dict(title=a['title'][lang],text=' '.join([a['title']['ko'],a['title']['en'],a['summary'][lang],a['category'][lang]]),url=a['url'],kind='News' if en else '뉴스',description=a['summary'][lang]))
 for a in news['talks']:
  entries.append(dict(title=a['speaker'][lang]+' · '+a['title'][lang],text=' '.join(a['speaker'].values())+' '+' '.join(a['title'].values()),url=a['url'],kind='Event · Video' if en else '행사 · 영상',description=a['date']))
 for a in news['media']:
  entries.append(dict(title=a['title'][lang],text=' '.join(a['title'].values())+' '+' '.join(a['outlet'].values()),url=a['url'],kind='In the Media' if en else '언론보도',description=a['outlet'][lang]+' · '+a['date']))
 for anchor,ko_title,en_title in [('joint-project','공동과제 제안','Joint Projects'),('partnership','산학협력·기술이전','Industry Partnerships'),('membership','멤버십','Membership'),('donate','기부','Giving')]:
  entries.append(dict(title=en_title if en else ko_title,text=ko_title+' '+en_title,url='/'+pre+'engage/#'+anchor,kind='Engage' if en else '참여하기',description=en_title if en else ko_title))
 out=D/'assets'/('search-index-en.json' if en else 'search-index-ko.json');out.write_text(json.dumps(entries,ensure_ascii=False,separators=(',',':')))
 print(lang+': indexed '+str(len(entries))+' pages, faculty, research groups and updates')

# Reapply section breadcrumbs after generating page shells.
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "build-breadcrumbs.py"))

runpy.run_path(str(Path(__file__).resolve().parent / "build-about-navigation.py"))

runpy.run_path(str(Path(__file__).resolve().parent / "build-home-nrl-link.py"))

import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "build-nrl-introduction.py"))
