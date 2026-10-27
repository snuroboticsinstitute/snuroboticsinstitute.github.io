"""Render Joint Faculty from the approved roster and four institute people tabs."""
from pathlib import Path
from html import escape as e
import json,re,importlib.util
D=Path(__file__).resolve().parents[1]/'dist';R=D.parent
joint=json.loads((R/'scripts/joint-faculty.json').read_text())
TABS=[('joint-faculty','겸무교수','Joint Faculty'),('postdoctoral-researchers','박사후 연구원','Postdoctoral Researchers'),('leadership','운영진','Leadership'),('technical-staff','테크니컬 스태프','Technical Staff'),('administration','행정실','Administrative Office')]
spec=importlib.util.spec_from_file_location('aliases',R/'scripts/prepare-faculty-search.py');aliases=importlib.util.module_from_spec(spec);spec.loader.exec_module(aliases)
def card(p,en):
 lang='en' if en else 'ko';pre='/en' if en else '';name=p['name_'+lang];dept=p['dept_'+lang]
 terms=' '.join(str(p.get(f,'')) for f in ['name_ko','name_en','dept_ko','dept_en','lab_ko','lab_en','name_search_alias'])+' '+' '.join(p['groups'])
 terms+=(' 연구그룹 미정 Group to be confirmed' if not p['groups'] else '')
 terms+=' '+' '.join(aliases.ALIASES.get(aliases.department_key(p['dept_ko'].replace('부','').replace('과','')),[]))
 groups=''.join('<a class="group-link" href="'+pre+'/research/nrl/#'+g.lower()+'"><span>'+g[:2]+' '+g[2:]+'</span>'+('<span class="role-badge">'+({'leader':'Leader','vice_leader':'Co-leader'} if en else {'leader':'리더','vice_leader':'부리더'})[p['roles'][g]]+'</span>' if g in p['roles'] else '')+'</a>' for g in p['groups'])
 if not groups:groups='<span class="group-pending">'+('Group to be confirmed' if en else '연구그룹 미정')+'</span>'
 lab=''
 if p.get('url_'+lang):lab='<p class="faculty-lab"><a href="'+e(p['url_'+lang],quote=True)+'" target="_blank" rel="noopener noreferrer">'+e(p['lab_'+lang] or ('Laboratory website' if en else '연구실 홈페이지'))+' ↗</a></p>'
 if p.get('profile_url_'+lang):lab+='<p class="faculty-lab"><a href="'+e(p['profile_url_'+lang],quote=True)+'" target="_blank" rel="noopener noreferrer">'+('Hospital profile' if en else e(p.get('profile_hospital_ko') or '병원 교수 소개'))+' ↗</a></p>'
 return '<article class="faculty-card" id="'+p['id']+'" role="listitem" data-search="'+e(terms,quote=True)+'" data-groups="'+(' '.join(p['groups']) or 'pending')+'"><div class="faculty-label faculty-groups">'+groups+'</div><h2>'+e(name)+'</h2><p>'+e(dept)+'</p>'+lab+'</article>'
for en in (False,True):
 pre='en/' if en else '';base='/'+pre;label='Joint Faculty' if en else '겸무교수'
 s=(D/pre/'research/nrl/faculty/index.html').read_text()
 s=re.sub(r'<title>.*?</title>','<title>'+label+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</title>',s)
 s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+('Joint faculty and their research groups at SNU Robotics Institute.' if en else '서울대학교 로보틱스연구소 겸무교수와 참여 연구그룹을 소개합니다.')+'">',s)
 s=re.sub(r'<nav class="language-switch".*?</nav>','<nav class="language-switch" aria-label="Language"><a lang="ko" hreflang="ko" href="/people/joint-faculty/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/people/joint-faculty/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',s,count=1,flags=re.S)
 s=re.sub(r'<section class="faculty-banner">.*?</section>','<section class="faculty-banner"><p class="breadcrumb"></p><h1>'+('People' if en else '구성원')+'</h1></section>',s,count=1,flags=re.S)
 s=re.sub(r'<nav class="nrl-tabs".*?</nav>','<nav class="faculty-tabs"></nav>',s,count=1,flags=re.S)
 s=re.sub(r'<div class="faculty-grid" role="list">.*?</div>\s*<p class="faculty-empty"',lambda m:'<div class="faculty-grid" role="list" data-faculty-order="random">'+''.join(card(p,en) for p in joint)+'</div><p class="faculty-empty"',s,count=1,flags=re.S)
 s=s.replace('faculty-search.js?v=20261020-roster','faculty-search.js?v=20261022-no-count')
 heading='SNU Robotics Institute Faculty' if en else '로보틱스연구소 교수진'
 description='Experts from diverse fields collaborate on physical AI robotics research.' if en else '다양한 분야의 전문가들이 피지컬 AI 로보틱스 연구를 위해 협력하고 있습니다'
 s=re.sub(r'(<div class="faculty-toolbar"><div>)<h2>.*?</h2><p>.*?</p>',lambda m:m[1]+'<h2>'+heading+'</h2><p>'+description+'</p>',s,count=1,flags=re.S)
 s=re.sub(r'<p[^>]*id="faculty-result"[^>]*>.*?</p>','',s,count=1,flags=re.S)
 s=s.replace('</select>','<option value="pending">'+('Group to be confirmed' if en else '연구그룹 미정')+'</option></select>',1)
 s=re.sub(r'<p class="faculty-source">.*?</p>','',s,count=1,flags=re.S)
 p=D/pre/'people/joint-faculty/index.html';p.write_text(s)
 public=[]
 for person in joint:
  public.append({k:v for k,v in person.items()})
 (p.parent/'directory.json').write_text(json.dumps(public,ensure_ascii=False,separators=(',',':')))
 # Leadership keeps the five previously confirmed institute appointments.
 p=D/pre/'people/leadership/index.html';s=p.read_text()
 s=s.replace('Leadership &amp; Staff','Leadership').replace('Leadership & Staff','Leadership').replace('Institute Team','Leadership').replace('운영인력','운영진')
 s=re.sub(r'(<div class="member-intro"><h2>[^<]*</h2>)<p>.*?</p>',r'\1',s,count=1,flags=re.S)
 s=re.sub(r'<p class="member-empty">.*?</p>','',s,count=1,flags=re.S)
 p.write_text(s)
 for slug,ko,eng in [t for t in TABS if t[0] not in ('joint-faculty','leadership')]:
  out=s;title=eng if en else ko
  out=re.sub(r'<title>.*?</title>','<title>'+title+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'</title>',out)
  out=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+title+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'">',out)
  out=re.sub(r'<section class="member-section".*?</section>','<section class="member-section"><div class="member-intro"><h2>'+title+'</h2></div><p class="member-empty">'+('Profiles will be added when confirmed.' if en else '명단은 확정 후 안내합니다.')+'</p></section>',out,count=1,flags=re.S)
  if slug=='postdoctoral-researchers':
   members=[
    ('ali-shtarbanov','Shtarbanov, Ali' if en else '알리 슈타르바노브'),
    ('jaein-lee','Lee, Jaein' if en else '이재인'),
   ]
   cards=''.join('<article class="faculty-card" id="'+member_id+'"><h2>'+name+'</h2></article>' for member_id,name in members)
   section='<section class="member-section" aria-label="'+title+'"><div class="member-intro"><h2>'+title+'</h2></div><div class="faculty-grid">'+cards+'</div></section>'
   out=re.sub(r'<section class="member-section".*?</section>',lambda m:section,out,count=1,flags=re.S)
  if slug=='technical-staff':
   description=('At SNU Robotics Institute, technical staff receive support throughout the research process, from project operations to technology development and validation. The Institute enables each staff member to contribute their expertise to research and helps ensure that technical knowledge and know-how are accumulated and shared.' if en else '서울대 로보틱스연구소에서는 테크니컬 스태프들의 연구과제 운영부터 기술개발과 실증까지 전 과정을 지원합니다. 각 스태프가 전문성을 바탕으로 연구에 참여하고 기술과 노하우가 축적되고 공유될 수 있도록 합니다.')
   members=['김승구','신준우','한용휘','송정률']
   section='<section class="member-section" aria-label="'+title+'"><div class="member-intro"><h2>'+title+'</h2><p>'+description+'</p></div><div class="faculty-grid">'+''.join('<article class="faculty-card"><h2>'+name+'</h2></article>' for name in members)+'</div></section>'
   out=re.sub(r'<section class="member-section".*?</section>',lambda m:section,out,count=1,flags=re.S)
  out=re.sub(r'(<span data-breadcrumb-current>).*?(</span>)',lambda m:m.group(1)+title+m.group(2),out,count=1)
  out=re.sub(r'<nav class="language-switch".*?</nav>','<nav class="language-switch" aria-label="Language"><a lang="ko" hreflang="ko" href="/people/'+slug+'/"'+(' aria-current="page"' if not en else '')+'>한국어</a><a lang="en" hreflang="en" href="/en/people/'+slug+'/"'+(' aria-current="page"' if en else '')+'>English</a></nav>',out,count=1,flags=re.S)
  target=D/pre/'people'/slug/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(out)
# The navigation order is consistent even on older People URLs.
for p in D.rglob('index.html'):
 rel=p.relative_to(D).as_posix()
 if not rel.removeprefix('en/').startswith('people/') or 'data-legacy-redirect' in p.read_text():continue
 en=rel.startswith('en/');pre='en/' if en else '';slug=p.parent.name;s=p.read_text()
 if slug not in [t[0] for t in TABS]:continue
 tabs='<nav class="faculty-tabs" aria-label="'+('People sections' if en else '구성원 분류')+'">'+''.join('<a href="/'+pre+'people/'+key+'/"'+(' aria-current="page"' if slug==key else '')+'>'+(eng if en else ko)+'</a>' for key,ko,eng in TABS)+'</nav>'
 s=re.sub(r'<nav class="faculty-tabs".*?</nav>',lambda m:tabs,s,count=1,flags=re.S)
 s=re.sub(r'(<a class="(?:research-nav|nrl-nav)"[^>]*?) aria-current="page"',r'\1',s)
 s=re.sub(r'(<a class="members-nav"[^>]*?)(?: aria-current="page")?>',r'\1 aria-current="page">',s)
 p.write_text(s)
for pre in ('','en/'):
 for old in ('committee','support'):
  target='/'+pre+'people/leadership/'
  (D/pre/f'people/{old}/index.html').write_text('<!doctype html><html lang="'+('en' if pre else 'ko')+'"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>People</title></head><body data-legacy-redirect><a href="'+target+'">'+('Leadership' if pre else '운영진')+'</a><script>location.replace("'+target+'"+location.search+location.hash);</script></body></html>')
print('Built 39 Joint Faculty cards and five institute People tabs in both languages.')
