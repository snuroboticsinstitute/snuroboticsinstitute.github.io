"""Link each homepage NRL logo to the same-language research program."""
from pathlib import Path
import re
D=Path(__file__).resolve().parents[1]/'dist'
for en in (False,True):
 pre='en/' if en else '';p=D/pre/'index.html';s=p.read_text()
 target='/'+pre+'research/nrl/'
 label='Explore the National Research Lab (NRL)' if en else '국가연구소 사업 소개'
 def link(m):
  return '<a class="nrl-home-link" href="'+target+'" aria-label="'+label+'" style="display:flex;align-items:center;flex-shrink:0">'+m[0]+'</a>'
 if 'class="nrl-home-link"' not in s:
  s,n=re.subn(r'<img class="nrl-header-mark[^\"]*"[^>]*>',link,s,count=1)
  assert n==1,p
 p.write_text(s)
