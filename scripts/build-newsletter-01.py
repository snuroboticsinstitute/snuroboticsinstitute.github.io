"""Prepare the supplied first newsletter as an isolated responsive document."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape as e
from urllib.parse import urlparse
import re
R=Path(__file__).resolve().parents[1];D=R/'dist'
source=(R/'scripts/newsletter-01-source.html').read_text()
source=re.sub(r'<style\b.*?</style>','',source,flags=re.S|re.I)
class Clean(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in ('script','iframe','object','form'):self.skip+=1;return
  if self.skip:return
  allowed={'div','span','p','h1','h2','h3','h4','strong','b','em','i','br','table','tbody','thead','tfoot','tr','td','th','a','img'}
  if tag not in allowed:return
  out=[]
  for k,v in attrs:
   if k not in {'style','class','href','src','alt','title','width','height','align','valign','bgcolor','border','cellpadding','cellspacing','colspan','rowspan','target','rel'} or v is None:continue
   if k in ('href','src') and urlparse(v).scheme not in ('','https','http','mailto'):continue
   if k=='src':
    name=v.rsplit('/',1)[-1]
    if (D/'assets/news'/name).exists():v='/assets/news/'+name
   if k=='style' and re.search(r'expression\s*\(|javascript:',v,re.I):continue
   out.append(k+'="'+e(v,quote=True)+'"')
  if tag=='a':
   out=[x for x in out if not x.startswith('rel=')];out.append('rel="noopener noreferrer"')
  self.parts.append('<'+tag+(' '+' '.join(out) if out else '')+'>')
 def handle_endtag(self,tag):
  if tag in ('script','iframe','object','form'):
   self.skip=max(0,self.skip-1);return
  if not self.skip and tag in {'div','span','p','h1','h2','h3','h4','strong','b','em','i','table','tbody','thead','tfoot','tr','td','th','a'}:self.parts.append('</'+tag+'>')
 def handle_data(self,data):
  if not self.skip:self.parts.append(e(data))
p=Clean();p.feed(source)
css='''html,body{margin:0;padding:0}body{background:#edf1f4;font-family:Arial,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;-webkit-text-size-adjust:100%;text-size-adjust:100%}table{border-collapse:collapse;border-spacing:0}img{display:block;border:0;max-width:100%;height:auto}a{text-decoration:none}*{box-sizing:border-box}@media(max-width:620px){[class$=outer-pad]{padding:0!important}[class$=container]{width:100%!important;max-width:100%!important}[class$=content-pad]{padding:24px 22px 34px!important}[class$=header-pad]{padding:18px 16px!important}[class$=issue]{width:62px!important;padding-left:7px!important;padding-right:7px!important;font-size:28px!important}[class$=slogan-band]{padding:25px 18px!important}[class$=slogan-band] h1{font-size:28px!important}[class$=talk-pad]{padding-left:22px!important;padding-right:22px!important}[class$=talk-image]{width:92px!important;padding-right:14px!important}[class$=talk-image] img{width:92px!important;max-width:92px!important}[class$=footer-pad]{padding:26px 22px 38px!important}td{overflow-wrap:break-word}}'''
out='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>서울대학교 로보틱스연구소 뉴스레터 1호</title><style>'+css+'</style></head><body>'+''.join(p.parts)+'</body></html>'
target=D/'assets/newsletter-01.html';target.parent.mkdir(exist_ok=True);target.write_text(out)
print('Prepared newsletter with original text, photographs, video/article links and subscription link.')
