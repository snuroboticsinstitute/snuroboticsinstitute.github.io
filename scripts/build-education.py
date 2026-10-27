"""Keep only Creative Engineering Design, without a promotional preamble."""
from pathlib import Path
import re,runpy
D=Path(__file__).resolve().parents[1]/'dist'
for en in (False,True):
 pre='en/' if en else '';p=D/pre/'education/index.html';s=p.read_text();label='Creative Engineering Design' if en else '창의공학설계'
 s=re.sub(r'<div class="glance-intro">.*?</div>','',s,count=1,flags=re.S)
 tabs='<nav class="education-tabs" aria-label="'+('Education programs' if en else '교육 프로그램')+'"><a href="/'+pre+'education/" aria-current="page">'+label+'</a></nav>'
 s=re.sub(r'<nav class="education-tabs".*?</nav>',lambda m:tabs,s,count=1,flags=re.S)
 s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+label+' | '+('SNU Robotics Institute' if en else '서울대학교 로보틱스연구소')+'">',s)
 p.write_text(s)
 old=D/pre/'education/robot-ai-challenge/index.html'
 old.write_text('<!doctype html><html lang="'+('en' if en else 'ko')+'"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>'+label+'</title></head><body data-legacy-redirect><a href="/'+pre+'education/">'+label+'</a><script>location.replace("/'+pre+'education/"+location.search);</script></body></html>')
runpy.run_path(str(Path(__file__).resolve().parent/'build-breadcrumbs.py'))
print('Education contains Creative Engineering Design only; preamble removed in both languages.')
