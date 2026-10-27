"""Refresh public TC/PG assignments and reciprocal links from canonical NRL data."""
from pathlib import Path
from html import escape as e
import re,json
D=Path(__file__).resolve().parents[1]/'dist'
ko=json.loads((D/'research/nrl/faculty/directory.json').read_text());ko_by={p['id']:p for p in ko}
for en in (False,True):
 pre='en/' if en else '';people=json.loads((D/pre/'research/nrl/faculty/directory.json').read_text());by={p['id']:p for p in people}
 rolelabels={'leader':'Leader','vice_leader':'Co-leader'} if en else {'leader':'리더','vice_leader':'부리더'}
 for kind in ('faculty','affiliated'):
  p=D/pre/f'research/nrl/{kind}/index.html';s=p.read_text()
  def update(m):
   card=m[0];ident=re.search(r'\bid="([^"]+)"',card)[1];person=by[ident]
   card=re.sub(r'data-groups="[^"]*"','data-groups="'+' '.join(person['groups'])+'"',card,count=1)
   label='<div class="faculty-label faculty-groups"><span class="member-status">'+('Participating' if kind=='faculty' else 'Affiliated' if en else '')+'</span>' if en else '<div class="faculty-label faculty-groups"><span class="member-status">'+('참여' if kind=='faculty' else '연계')+'</span>'
   for group in person['groups']:
    label+='<a class="group-link" href="/'+pre+'research/nrl/#'+group.lower()+'"><span>'+group[:2]+' '+group[2:]+'</span>'+('<span class="role-badge">'+rolelabels[person['roles'][group]]+'</span>' if group in person['roles'] else '')+'</a>'
   if person.get('groups_status')=='pending':label+='<span class="group-pending">'+('Group to be confirmed' if en else '연구그룹 미정')+'</span>'
   label+='</div>'
   return re.sub(r'<div class="faculty-label faculty-groups">.*?</div>',lambda _:label,card,count=1,flags=re.S)
  s=re.sub(r'<article class="faculty-card".*?</article>',update,s,flags=re.S)
  s=re.sub(r'<p class="faculty-source">.*?</p>','<p class="faculty-source">'+('Group labels reflect confirmed TC and PG assignments.' if en else '연구그룹 표기는 확인된 TC·PG 배정 정보를 따릅니다.')+'</p>',s,count=1,flags=re.S)
  p.write_text(s)
 p=D/pre/'research/nrl/index.html';s=p.read_text()
 def person_link(person,g,department=False):
  kind='faculty' if ko_by[person['id']]['category']=='참여' else 'affiliated'
  role=person['roles'].get(g)
  return '<a href="/'+pre+'research/nrl/'+kind+'/#'+person['id']+'" class="person-link"><span>'+e(person['name'])+'</span>'+('<span class="role-badge">'+rolelabels[role]+'</span>' if role else '')+('<span class="roster-dept">'+e(person['dept'])+'</span>' if department else '')+'</a>'
 def connection(m):
  group=m[1];members=[person for person in people if group in person['groups']]
  result='<div class="group-connections" data-research-group="'+group+'"><div class="group-leads">'
  for role,title in [('leader','Leaders' if en else '리더'),('vice_leader','Co-leaders' if en else '부리더')]:
   selected=[person for person in members if person['roles'].get(group)==role]
   if selected:result+='<div class="group-lead-row"><strong>'+title+'</strong><div>'+''.join(person_link(person,group) for person in selected)+'</div></div>'
  result+='</div><details class="group-people"><summary><span>'+('View researchers' if en else '연구진 보기')+'</span><span class="group-count">'+str(len(members))+'</span></summary>'
  for category,title in [('참여','Participating Faculty' if en else '참여교수'),('연계','Affiliated Faculty' if en else '연계교수')]:
   selected=[person for person in members if ko_by[person['id']]['category']==category]
   if selected:result+='<h4><span>'+title+'</span><span>'+str(len(selected))+'</span></h4><ul class="group-roster">'+''.join('<li>'+person_link(person,group,True)+'</li>' for person in selected)+'</ul>'
  return result+'</details></div>'
 s,n=re.subn(r'<div class="group-connections" data-research-group="([^"]+)">.*?</details></div>',connection,s,flags=re.S);assert n==7
 p.write_text(s)
print('Refreshed reciprocal memberships for all seven TC/PG groups in both languages.')
