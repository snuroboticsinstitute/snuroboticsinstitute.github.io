"""Keep section breadcrumbs consistent across bilingual detail pages."""
from pathlib import Path
from html import escape as e
import re
D=Path(__file__).resolve().parents[1]/'dist'
for p in D.rglob('index.html'):
 if 'font-preview' in p.parts or 'assets' in p.relative_to(D).parts or 'data-legacy-redirect' in p.read_text():continue
 rel=p.relative_to(D).as_posix();en=rel.startswith('en/');local=rel.removeprefix('en/');pre='en/' if en else ''
 if local in ('index.html','search/index.html') or local.startswith('about/'):continue
 parent=current=href=None
 if local.startswith('people/'):
  parent='People' if en else '구성원';href='/'+pre+'people/joint-faculty/'
  slug=local.split('/')[1]
  labels={'postdoctoral-researchers':('박사후 연구원','Postdoctoral Researchers'),'joint-faculty':('겸무교수','Joint Faculty'),'faculty':('참여교수','Participating Faculty'),'affiliated':('연계교수','Affiliated Faculty'),'leadership':('운영진','Leadership'),'technical-staff':('테크니컬 스태프','Technical Staff'),'administration':('행정실','Administrative Office'),'support':('운영인력','Leadership & Staff'),'committee':('운영위원회','Steering Committee')}
  current=labels[slug][en]
 elif local.startswith('education/'):
  parent='Education' if en else '교육';href='/'+pre+'education/'
  current=('Robot AI Challenge' if en else '로봇 AI 챌린지') if 'robot-ai-challenge' in local else ('Creative Engineering Design' if en else '창의공학설계')
 elif local.startswith('research/nrl/'):
  parent='NRL' if en else '국가연구소';href='/'+pre+'research/nrl/'
  slug=local.removeprefix('research/nrl/').split('/')[0]
  current=({'faculty':'Participating Faculty','affiliated':'Affiliated Faculty'}.get(slug,'Technology Core') if en else {'faculty':'참여교수','affiliated':'연계교수'}.get(slug,'핵심기술'))
 elif local=='research/index.html':
  continue
 elif local.startswith(('updates/','news/')):
  parent='Updates' if en else '소식';href='/'+pre+'updates/'
  current=('Newsletter No. 1' if en else '뉴스레터 1호') if 'newsletter-01' in local else ('News' if en else '뉴스') if local.startswith('news/') else ('All' if en else '전체')
 if not parent:continue
 s=p.read_text();crumb='<p class="breadcrumb"><a href="'+href+'">'+parent+'</a><span aria-hidden="true">›</span><span data-breadcrumb-current>'+e(current)+'</span></p>'
 if local.startswith('research/nrl/'):
  crumb=crumb.replace('<p class="breadcrumb">','<p class="breadcrumb"><a href="/'+pre+'research/">'+('Research' if en else '연구')+'</a><span aria-hidden="true">›</span>',1)
 if 'class="faculty-banner"' in s:
  s=re.sub(r'(<section class="faculty-banner">)<p class="(?:section-index|breadcrumb)">.*?</p>',lambda m:m[1]+crumb,s,count=1,flags=re.S)
 else:s=re.sub(r'<p class="breadcrumb">.*?</p>',lambda m:crumb,s,count=1,flags=re.S)
 s=s.replace('/assets/breadcrumbs.js"','/assets/breadcrumbs.js?v=20261020-nrl"')
 if '/assets/breadcrumbs.js' not in s:s=s.replace('</body>','<script src="/assets/breadcrumbs.js" defer></script></body>')
 p.write_text(s)
