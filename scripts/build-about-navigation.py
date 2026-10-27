"""Apply the approved About sequence and its first-page destination."""
from pathlib import Path
import re
D=Path(__file__).resolve().parents[1]/'dist'
for p in D.rglob('index.html'):
 if 'font-preview' in p.parts or 'assets' in p.relative_to(D).parts:continue
 s=p.read_text()
 if 'data-legacy-redirect' in s:continue
 en=p.relative_to(D).parts[0]=='en';pre='en/' if en else '';slug=p.parent.name
 s=re.sub(r'(<a class="about-nav" href=")[^"]*(")',lambda m:m[1]+'/'+pre+'about/at-a-glance/'+m[2],s)
 if 'class="about-tabs"' in s:
  labels=[('at-a-glance','At a Glance' if en else '한눈에 보기'),('director-message','Director’s Message' if en else '소장 인사말'),('vision','Vision' if en else '비전'),('history','History' if en else '연혁'),('directions','Directions' if en else '오시는 길')]
  tabs='<nav class="about-tabs" aria-label="'+('About sections' if en else '소개 페이지')+'">'+''.join('<a href="/'+pre+'about/'+key+'/"'+(' aria-current="page"' if slug==key else '')+'>'+text+'</a>' for key,text in labels)+'</nav>'
  s=re.sub(r'<nav class="about-tabs".*?</nav>',lambda m:tabs,s,count=1,flags=re.S)
  s=re.sub(r'(<p class="breadcrumb"><a href=")[^"]+(">(?:About|소개)</a>)',lambda m:m[1]+'/'+pre+'about/at-a-glance/'+m[2],s,count=1)
  s=re.sub(r'history.css\?v=[^"\s]+','history.css?v=20261021-about-order',s)
 p.write_text(s)
print('About tabs: At a Glance, Director’s Message, Vision, History, Directions.')
