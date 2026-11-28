#!/usr/bin/env python3
"""Give every screen of the site its own address.

The site is written as one file per language (dist/index.html, dist/en/index.html)
whose screens are <section class="page" data-route="/people/"> blocks switched by
the address after "#". Search engines see such a site as a single page.

This script runs when the site is published (.github/workflows) and writes one
HTML file per screen: /people/index.html, /en/people/index.html and so on. Each
file holds the shared header, footer, styles and scripts plus only its own
screen, with its own title, description and canonical address. Links written as
"#/people/" become "/people/". Nothing in the repository is changed; the files
exist only in the published copy.

Usage: python3 tools/build_pages.py <dist directory>
"""
import html
import json
import re
import sys
from pathlib import Path

HOST = 'https://robotics.snu.ac.kr'
LANGS = {
    'ko': {'file': 'index.html', 'base': '', 'site': '서울대학교 로보틱스연구소',
           'home': '서울대학교 로보틱스연구소 | SNU Robotics Institute',
           'nrl_home': '국가연구소 NRL 2.0 | 서울대학교 로보틱스연구소', 'ced_home': '창의공학설계 | 서울대학교',
           'nrl': '국가연구소 NRL 2.0', 'ced': '창의공학설계', 'locale': 'ko_KR'},
    'en': {'file': 'en/index.html', 'base': '/en', 'site': 'SNU Robotics Institute',
           'home': 'SNU Robotics Institute | Seoul National University',
           'nrl_home': 'National Research Lab (NRL 2.0) | SNU Robotics Institute', 'ced_home': 'Creative Engineering Design | SNU',
           'nrl': 'NRL 2.0', 'ced': 'Creative Engineering Design', 'locale': 'en_US'},
}
NRL_STACK = ['/nrl/', '/nrl/tc-pg/', '/nrl/faculty/']
NOINDEX = {'/search/'}
SECTION = re.compile(r'<section class="page[^"]*"[^>]*\bdata-route="([^"]+)"[^>]*>')

SHIM = r'''<script>/* Added by tools/build_pages.py: this page has its own address. */
window.__STATIC=%s;
(function(){var S=__STATIC;
function toPath(h){var p=h.replace(/^#/,'')||'/';if(p.charAt(0)!=='/')p='/'+p;var R=S.routes;if(R.indexOf(p)>=0)return S.base+p;
var c=p.replace(/\/$/,'').lastIndexOf('/'),b=p.slice(0,c+1),t=p.slice(c+1).replace(/\/$/,'');return R.indexOf(b)>=0?S.base+b+(t?'#'+t:''):S.base+'/';}
if(location.hash.indexOf('#/')===0){location.replace(toPath(location.hash));return;}   /* addresses shared before the change */
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#/"]');if(!a)return;e.preventDefault();location.href=toPath(a.getAttribute('href'));},true);
document.addEventListener('submit',function(e){var f=e.target;if(!f.closest||!f.closest('#search-panel')||document.querySelector('section[data-route="/search/"]'))return;
e.preventDefault();var v=(f.querySelector('input[name="q"]').value||'').trim();if(v)location.href=S.base+'/search/#'+encodeURIComponent(v);},true);
})();</script>
'''


def split(doc):
    """Return (text before the screens, {route: section html} in order, text after)."""
    starts = [(m.start(), m.group(1)) for m in SECTION.finditer(doc)]
    end = doc.index('</main>')
    if not starts or starts[-1][0] > end:
        raise SystemExit('cannot find the page sections')
    sections = {}
    for i, (pos, route) in enumerate(starts):
        nxt = starts[i + 1][0] if i + 1 < len(starts) else end
        block = doc[pos:nxt]
        if not block.rstrip().endswith('</section>'):
            raise SystemExit(f'section {route} does not end where the next one starts')
        if route in sections:
            raise SystemExit(f'route {route} appears twice')
        sections[route] = block
    return doc[:starts[0][0]], sections, doc[end:]


def to_path(target, routes, base):
    """'#/ced/ced-intro' -> '/ced/#ced-intro', following the router's own rule."""
    p = target or '/'
    if not p.startswith('/'):
        p = '/' + p
    if p in routes:
        return base + p
    cut = p.rstrip('/').rfind('/')
    head, tail = p[:cut + 1], p[cut + 1:].rstrip('/')
    if head in routes:
        return base + head + ('#' + tail if tail else '')
    return base + '/'


def plain_text(block):
    block = re.sub(r'<(script|style|template)\b.*?</\1>', ' ', block, flags=re.S)
    block = re.sub(r'<[^>]+>', ' ', block)
    return re.sub(r'\s+', ' ', html.unescape(block)).strip()


def attr(value):
    return html.escape(value, quote=True)


def set_head(head, tag_re, new):
    out, n = re.subn(tag_re, lambda m: new, head, count=1)
    if n != 1:
        raise SystemExit(f'head tag not found: {tag_re}')
    return out


def build(dist):
    dist = Path(dist)
    docs = {}
    for lang, cfg in LANGS.items():
        before, sections, after = split((dist / cfg['file']).read_text(encoding='utf-8'))
        routes = list(sections)
        if '/nrl/' in sections:
            routes.append('/nrl/about/')
        docs[lang] = (before, sections, after, routes)

    sitemap = []
    for lang, cfg in LANGS.items():
        before, sections, after, routes = docs[lang]
        other = 'en' if lang == 'ko' else 'ko'
        other_routes, other_base = docs[other][3], LANGS[other]['base']
        ko_routes = docs['ko'][3]

        def links(text):
            text = re.sub(r'(href|action)="#(/[^"]*)"', lambda m: f'{m.group(1)}="{attr(to_path(html.unescape(m.group(2)), routes, cfg["base"]))}"', text)
            # the English site links some cards to Korean articles as "/#/updates/…"
            text = re.sub(r'href="/#(/[^"]*)"', lambda m: f'href="{attr(to_path(html.unescape(m.group(1)), ko_routes, ""))}"', text)
            # files are no longer all at the top of the site, so asset addresses start from the root
            return re.sub(r'(?<![\w/.\-])(?:\.\./)?assets/', '/assets/', text)

        for route in routes:
            if route == '/nrl/about/':
                keep, main = ['/nrl/'], sections['/nrl/']
            elif route == '/nrl/' and all(r in sections for r in NRL_STACK):
                keep, main = NRL_STACK, sections['/nrl/']
            elif route == '/search/':
                keep, main = list(sections), sections[route]          # the search looks through every screen
            else:
                keep, main = [route], sections[route]
            shown = set(keep) if route != '/search/' else {route}
            body = ''
            for r in keep:
                block = sections[r]
                tag = SECTION.match(block).group(0)
                new_tag = re.sub(r'\s+hidden(?=>)', '', tag) if r in shown else (tag if tag.endswith(' hidden>') else tag[:-1] + ' hidden>')
                body += new_tag + block[len(tag):]

            tag = SECTION.match(main).group(0)
            site = re.search(r'data-site="([^"]*)"', tag).group(1)
            name = html.unescape((re.search(r'data-title="([^"]*)"', tag) or [None, ''])[1])
            if route == '/':
                title = cfg['home']
            elif route in ('/nrl/', '/nrl/about/', '/ced/'):
                title = cfg['nrl_home'] if site == 'nrl' else cfg['ced_home']
            else:
                title = name + ' | ' + (cfg['nrl'] if site == 'nrl' else cfg['ced'] if site == 'ced' else cfg['site'])
            url = HOST + cfg['base'] + route
            alt = route if route in other_routes else ('/updates/' if route.startswith('/updates/') and '/updates/' in other_routes else '/')

            head = before
            head = set_head(head, r'<title>.*?</title>', f'<title>{html.escape(title)}</title>')
            if route != '/':
                paras = [plain_text(x) for x in re.findall(r'<p(?![^>]*class="crumb")[^>]*>(.*?)</p>', main, flags=re.S)]
                text = ' '.join(x for x in paras if len(x) > 25)
                if len(text) > 150:
                    text = text[:150].rsplit(' ', 1)[0] + '…'
                desc = f'{name} | {text}' if len(text) > 40 else f'{name} | {cfg["site"]}'
                head = set_head(head, r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{attr(desc)}">')
                head = set_head(head, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{attr(desc)}">')
                head = set_head(head, r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{attr(title)}">')
                head = set_head(head, r'<script type="application/ld\+json">.*?</script>\n?', '')
            head = set_head(head, r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">')
            head = set_head(head, r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">')
            head = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', '', head)
            pair = route in other_routes
            if pair and route not in NOINDEX:
                ko, en = HOST + route, HOST + '/en' + route
                alts = f'<link rel="alternate" hreflang="ko" href="{ko}">\n<link rel="alternate" hreflang="en" href="{en}">\n<link rel="alternate" hreflang="x-default" href="{ko}">\n'
            else:
                alts = ''
            robots = '<meta name="robots" content="noindex">\n' if route in NOINDEX else ''
            state = json.dumps({'route': route, 'base': cfg['base'], 'routes': routes}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
            head = head.replace('</head>', alts + robots + SHIM % state + '</head>', 1)
            head = head.replace('<body>', f'<body data-site="{site}">', 1)
            # the language button goes to the same screen in the other language
            page = links(head + body + after)
            page = re.sub(r'(<a class="lang"[^>]*href=")[^"]*(")', lambda m: m.group(1) + other_base + alt + m.group(2), page)

            out = dist / (cfg['base'] + route).strip('/') / 'index.html'
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page, encoding='utf-8')
            if route not in NOINDEX:
                sitemap.append((url, (HOST + route, HOST + '/en' + route) if pair else None))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for url, pair in sitemap:
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{h}"/>' for l, h in zip(('ko', 'en'), pair)) if pair else ''
        lines.append(f'  <url><loc>{url}</loc>{alt}</url>')
    lines.append('</urlset>')
    (dist / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'built {len(sitemap)} pages (+ search)')


if __name__ == '__main__':
    build(sys.argv[1])
