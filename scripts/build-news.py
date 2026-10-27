"""Refresh all five newsletter story previews on both homepages."""
from pathlib import Path
from html import escape as e
import json,re
R=Path(__file__).resolve().parents[1];D=R/'dist';data=json.loads((R/'scripts/news-content.json').read_text())
def ext(url):return 'href="'+e(url,quote=True)+'" target="_blank" rel="noopener noreferrer"'
# Wire existing news navigation and homepage calls to action to the actual index.
for p in D.rglob('*.html'):
 if p not in (D/'index.html', D/'en/index.html'):continue
 en=p.relative_to(D).parts[0]=='en';prefix='en/' if en else '';s=p.read_text()
 if p==D/f'{prefix}index.html':
  s=s.replace('href="#community">'+('More updates' if en else '연구소 소식 더 보기'),'href="/'+prefix+'updates/">'+('More updates' if en else '연구소 소식 더 보기'))
  # Render every newsletter story on the homepage, using the same source as the index.
  lang='en' if en else 'ko'
  preview='<section class="section news" id="news"><div class="section-head"><div><p class="section-index">01 / News</p><h2 class="section-title">'+('Institute News' if en else '연구소 소식')+'</h2></div><a class="more-link" href="/'+prefix+'updates/">'+('More news' if en else '소식 더 보기')+'<span>→</span></a></div><div class="news-grid newsletter-preview">'
  for a in data['articles']:
   preview+='<article class="news-card"'+(' id="events"' if a['id']=='education' else '')+'><a class="home-story-link" '+ext(a['url'])+'><div class="home-news-photo"><img src="'+a['image']+'" alt="'+e(a['title'][lang],quote=True)+'" loading="lazy" decoding="async"></div><div class="news-body"><span class="news-date">'+e(a['category'][lang])+'</span><h3>'+e(a['title'][lang])+'</h3><p>'+e(a['summary'][lang])+'</p></div></a></article>'
  preview+='</div></section>'
  s,n=re.subn(r'<section class="section news" id="news">.*?</section>',preview,s,count=1,flags=re.S)
  assert n==1,p

 p.write_text(s)
