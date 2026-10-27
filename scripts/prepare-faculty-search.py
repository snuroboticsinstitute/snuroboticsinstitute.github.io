"""Refresh bilingual search terms without changing faculty affiliations or visible copy."""
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    '의학': ['의과대학', '의대', '의학과', '의학교실', 'medicine', 'medical', 'college of medicine'],
    '기계공학': ['기계공학부', '기계공학과', '기계과', 'mechanical engineering'],
    '전기정보': ['전기정보공학부', '전기·정보공학부', '전기공학', '전자공학', '전기과', '전자과', 'electrical engineering', 'electrical and computer engineering', 'ECE'],
    '컴퓨터공학': ['컴퓨터공학부', '컴퓨터공학과', '컴공', '컴퓨터과', 'computer science', 'computer engineering', 'CSE'],
    '재료공학': ['재료공학부', '재료공학과', '재료과', 'materials science', 'materials engineering'],
    '항공우주': ['항공우주공학과', '항공우주공학', '항공과', 'aerospace engineering'],
    '건설': ['건설환경공학부', '건설환경공학', '토목공학', '토목과', 'civil engineering', 'environmental engineering'],
    '지능정보융합': ['지능정보융합학과', 'intelligence and information'],
    '데이터사이언스': ['데이터사이언스학과', '데이터사이언스대학원', '데이터과학', 'data science'],
    '첨단융합': ['첨단융합학부', '첨단융합대학', 'advanced convergence'],
    'AI연구원': ['인공지능연구원', '인공지능', 'artificial intelligence', 'AI institute'],
    '간호': ['간호학', '간호학과', '간호대학', '간호대', 'nursing'],
    '보건': ['보건학', '보건대학원', 'public health'],
    '법학': ['법학전문대학원', '법대', '로스쿨', 'law'],
    '의류': ['의류학', '의류학과', 'clothing', 'textiles'],
    '생명과학': ['생명', '생명과학부', '생명과학과', '생물학', '생물학과', 'biological sciences', 'biology'],
    '화학': ['화학부', '화학과', 'chemistry'],
    '심리학': ['심리학과', '심리', 'psychology'],
    '체육교육': ['체육교육과', '체교', 'physical education'],
    '뇌인지과학': ['뇌인지과학과', '뇌과학', 'brain and cognitive sciences'],
    '언론정보': ['언론정보학과', '언론학', '커뮤니케이션', 'communication'],
}
ENGINEERING = {'기계공학', '전기정보', '컴퓨터공학', '재료공학', '항공우주', '건설'}

def department_key(dept):
    dept = re.sub(r'\(.*?\)', '', dept)
    return {'전기·정보공학부': '전기정보', '데이터사이언스학과': '데이터사이언스',
            '첨단융합학부': '첨단융합', '생명': '생명과학'}.get(dept, dept)

def main():
    ko = json.loads((ROOT / 'dist/research/nrl/faculty/directory.json').read_text())
    en = {p['id']: p for p in json.loads((ROOT / 'dist/en/research/nrl/faculty/directory.json').read_text())}
    terms = {}
    for p in ko:
        key = department_key(p['dept'])
        values = [p.get(f, '') for f in ('name', 'dept', 'lab', 'org', 'category')]
        values += [en[p['id']].get(f, '') for f in ('name', 'dept', 'lab', 'org', 'category')]
        values += [en[p['id']].get('name_search_alias', '')]
        values += ALIASES.get(key, [])
        if key in ENGINEERING:
            values += ['공과대학', '공대', 'college of engineering']
        values += p['groups'] + [g[:2] + ' ' + g[2:] for g in p['groups']]
        terms[p['id']] = ' '.join(dict.fromkeys(v for v in values if v))
    for prefix in ('', 'en/'):
        for section in ('faculty', 'affiliated'):
            path = ROOT / f'dist/{prefix}research/nrl/{section}/index.html'
            source = path.read_text()
            def enrich(match):
                tag = match[0]
                person_id = re.search(r'\bid="([^"]+)"', tag)[1]
                return re.sub(r'data-search="[^"]*"', 'data-search="' + html.escape(terms[person_id], quote=True) + '"', tag)
            source = re.sub(r'<article\b[^>]*class="faculty-card"[^>]*>', enrich, source)
            source = re.sub(r'<script>\(\(\)=>\{const input=document.querySelector\(\'#faculty-search\'\).*?</script>',
                            '<script src="/assets/faculty-search.js"></script>', source, flags=re.S)
            path.write_text(source)

if __name__ == '__main__':
    main()
