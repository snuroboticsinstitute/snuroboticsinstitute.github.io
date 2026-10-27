"""Build reciprocal links from the authoritative faculty directory."""
from pathlib import Path
from html import escape, unescape
import json, re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
people = json.loads((DIST / 'research/nrl/faculty/directory.json').read_text())
by_name = {p['name']: p for p in people}
GROUPS = ['TC1', 'TC2', 'TC3', 'TC4', 'PG1', 'PG2', 'PG3']
ROLES = {'leader': '리더', 'vice_leader': '부리더'}

def person_link(person, group, show_department=False):
    page = 'faculty' if person['category'] == '참여' else 'affiliated'
    role = person['roles'].get(group)
    badge = '<span class="role-badge">' + ROLES[role] + '</span>' if role else ''
    department = '<span class="roster-dept">' + escape(person['dept']) + '</span>' if show_department and person['dept'] else ''
    return '<a href="/research/nrl/' + page + '/#' + person['id'] + '" class="person-link"><span>' + escape(person['name']) + '</span>' + badge + department + '</a>'

def group_people(group):
    members = [p for p in people if group in p['groups']]
    leaders = [p for p in members if p['roles'].get(group) == 'leader']
    deputies = [p for p in members if p['roles'].get(group) == 'vice_leader']
    result = '<div class="group-connections" data-research-group="' + group + '"><div class="group-leads">'
    for label, selected in [('리더', leaders), ('부리더', deputies)]:
        if selected:
            result += '<div class="group-lead-row"><strong>' + label + '</strong><div>' + ''.join(person_link(p, group) for p in selected) + '</div></div>'
    result += '</div><details class="group-people"><summary><span>연구진 보기</span><span class="group-count">' + str(len(members)) + '</span></summary>'
    for category, heading in [('참여', '참여교수'), ('연계', '연계교수')]:
        subset = [p for p in members if p['category'] == category]
        if subset:
            result += '<h4><span>' + heading + '</span><span>' + str(len(subset)) + '</span></h4><ul class="group-roster">'
            result += ''.join('<li>' + person_link(p, group, True) + '</li>' for p in subset) + '</ul>'
    return result + '</details></div>'

research = DIST / 'research/nrl/index.html'
text = research.read_text()
def research_card(match):
    card = match.group(0)
    kind, number = re.search(r'(TC|PG) 0([1-4])', card).groups()
    group = kind + number
    card = re.sub(r'<article class="detail-card"(?: id="[^"]+")?>', '<article class="detail-card" id="' + group.lower() + '">', card, count=1)
    card = re.sub(r'<div class="group-connections".*?</details></div>', '', card, flags=re.S)
    return card.replace('</article>', group_people(group) + '</article>')
text = re.sub(r'<article class="detail-card"(?: id="[^"]+")?>.*?</article>', research_card, text, flags=re.S)
research.write_text(text)

for slug in ['faculty', 'affiliated']:
    path = DIST / 'research' / 'nrl' / slug / 'index.html'
    text = path.read_text()
    def faculty_card(match):
        card = match.group(0)
        name = unescape(re.search(r'<h2>(.*?)</h2>', card).group(1))
        member = by_name[name]
        card = re.sub(r'(<article class="faculty-card")\s+id="[^"]+"', r'\1', card, count=1)
        card = card.replace('<article class="faculty-card"', '<article class="faculty-card" id="' + member['id'] + '"', 1)
        label = '<div class="faculty-label faculty-groups"><span class="member-status">' + member['category'] + '</span>'
        for group in member['groups']:
            label += '<a class="group-link" href="/research/nrl/#' + group.lower() + '"><span>' + group[:2] + ' ' + group[2:] + '</span>'
            role = member['roles'].get(group)
            if role: label += '<span class="role-badge">' + ROLES[role] + '</span>'
            label += '</a>'
        label += '</div>'
        card = re.sub(r'<span class="faculty-label">.*?</span>', lambda m: label, card, count=1, flags=re.S)
        # Idempotent on future rebuilds as well.
        card = re.sub(r'<div class="faculty-label faculty-groups">.*?</div>', lambda m: label, card, count=1, flags=re.S)
        return card
    text = re.sub(r'<article class="faculty-card".*?</article>', faculty_card, text, flags=re.S)
    path.write_text(text)

# Make the overview cards lead directly to the corresponding group description.
home = DIST / 'index.html'
text = home.read_text()
def overview(match):
    card = match.group(0)
    kind, number = re.search(r'(TC|PG) 0([1-4])', card).groups()
    if 'class="group-overview-link"' not in card:
        card = re.sub(r'<h3>(.*?)</h3>', lambda m: '<h3><a class="group-overview-link" href="/research/nrl/#' + (kind + number).lower() + '">' + m.group(1) + '</a></h3>', card, count=1, flags=re.S)
    return card
text = re.sub(r'<article class="(?:research-card|program-card)">.*?</article>', overview, text, flags=re.S)
home.write_text(text)
print('Linked 7 groups and', len(people), 'faculty cards from one membership and role dataset.')
