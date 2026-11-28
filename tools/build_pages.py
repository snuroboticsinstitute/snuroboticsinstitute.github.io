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
           'nrl': '국가연구소 NRL 2.0', 'ced': '창의공학설계', 'locale': 'ko_KR',
           'proj': ['사업', '지원', '기간', '연구책임자'], 'count': '연구과제 %d건', 'watch': '영상 보기: ',
           'types': {'video': '영상', 'project': '프로젝트', 'article': '기사', 'paper': '논문', 'award': '수상', 'patent': '특허·기술이전'},
           'feed': '서울대학교 로보틱스연구소 소식', 'feed_desc': '서울대학교 로보틱스연구소의 소식과 행사'},
    'en': {'file': 'en/index.html', 'base': '/en', 'site': 'SNU Robotics Institute',
           'home': 'SNU Robotics Institute | Seoul National University',
           'nrl_home': 'National Research Lab (NRL 2.0) | SNU Robotics Institute', 'ced_home': 'Creative Engineering Design | SNU',
           'nrl': 'NRL 2.0', 'ced': 'Creative Engineering Design', 'locale': 'en_US',
           'proj': ['Program', 'Funding', 'Period', 'PI'], 'count': '%d research projects', 'watch': 'Watch video: ',
           'types': {'video': 'Video', 'project': 'Project', 'article': 'Article', 'paper': 'Paper', 'award': 'Award', 'patent': 'Patent & Tech Transfer'}},
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


TYPE_ORDER = ['video', 'project', 'article', 'paper', 'award', 'patent']


def pick(value, lang):
    if isinstance(value, dict):
        return value.get(lang) or value.get('ko') or ''
    return value or ''


def youtube_id(url):
    m = re.search(r'(?:youtu\.be/|v=|embed/|shorts/)([\w-]{11})', str(url))
    return m.group(1) if m else None


def ext_link(url, inner, extra=''):
    return f'<a{extra} href="{attr(url)}" target="_blank" rel="noopener noreferrer">{inner}</a>'


def projects_html(data, lang, cfg):
    """The research projects list as the page script draws it, so it can be read without running the script."""
    rows = []
    for p in data.get('projects', []):
        title, url = html.escape(pick(p.get('title'), lang)), pick(p.get('url'), lang)
        if url in ('/research/nrl/', '/en/research/nrl/'):
            head = f'<a href="#/nrl/">{title}</a>'
        elif url:
            head = ext_link(url, title)
        else:
            head = title
        pairs = zip(cfg['proj'], [pick(p.get('program'), lang), pick(p.get('agency'), lang), p.get('period'), pick(p.get('pi'), lang)])
        dl = ''.join(f'<div><dt>{html.escape(k)}</dt><dd>{html.escape(str(v))}</dd></div>' for k, v in pairs if v)
        rows.append(f'<li class="panel"><h3>{head}</h3><dl>{dl}</dl></li>')
    if not rows:
        return None
    return f'<div class="rx-head"><p class="rx-count">{html.escape(cfg["count"] % len(rows))}</p></div><ol class="proj">{"".join(rows)}</ol>'


def achievements_html(data, lang, cfg):
    """The research highlights as the page script draws them (all of them; the script then shows six at a time)."""
    items = sorted(data.get('achievements', []), key=lambda i: str(i.get('date')), reverse=True)
    cards = []
    for i in items:
        links = sorted(i.get('links') or [], key=lambda l: TYPE_ORDER.index(l.get('type')) if l.get('type') in TYPE_ORDER else 99)
        video = next((l for l in links if l.get('type') == 'video' and youtube_id(l.get('url'))), None)
        thumb = i.get('image') or (video and f'https://i.ytimg.com/vi/{youtube_id(video["url"])}/hqdefault.jpg')
        title = pick(i.get('title'), lang)
        if thumb:
            img = f'<img src="{attr(thumb)}" alt="" loading="lazy" decoding="async">'
            if video:
                media = ext_link(video['url'], img, f' class="media play" aria-label="{attr(cfg["watch"] + title)}"')
            else:
                media = ext_link(i.get('image_url') or (links[0].get('url') if links and links[0].get('url') else '#'), img, ' class="media" aria-hidden="true" tabindex="-1"')
        else:
            media = f'<div class="media tile" aria-hidden="true"><span>{html.escape(i.get("venue") or "")}</span></div>'
        body = f'<p class="date">{html.escape(str(i.get("date")).replace("-", ".", 1))}</p><h3>{html.escape(title)}</h3>'
        if pick(i.get('summary'), lang):
            body += f'<p class="sum">{html.escape(pick(i.get("summary"), lang))}</p>'
        if pick(i.get('people'), lang):
            body += f'<p class="who">{html.escape(pick(i.get("people"), lang))}</p>'
        if links:
            lis = ''
            for l in links:
                label = html.escape(' · '.join(x for x in (pick(l.get('title'), lang), pick(l.get('source'), lang)) if x))
                lis += f'<li><b>{html.escape(cfg["types"].get(l.get("type"), ""))}</b>' + (ext_link(l['url'], label + ' ↗') if l.get('url') else f'<span>{label}</span>') + '</li>'
            body += f'<ul>{lis}</ul>'
        cards.append(f'<article class="panel" id="achievement-{attr(str(i.get("id")))}">{media}<div class="body">{body}</div></article>')
    return f'<div class="hl">{"".join(cards)}</div>' if cards else None


def fill_box(block, marker, inner):
    """Put ready-made HTML inside <div class="rx" data-…="…">…</div> (the page script replaces it when it runs)."""
    if not inner:
        return block
    m = re.search(r'(<div class="rx" ' + marker + r'="[^"]*">)<div class="panel empty">.*?</div></div>', block, flags=re.S)
    if not m:
        raise SystemExit(f'{marker} box not found')
    return block[:m.start()] + m.group(1) + inner + '</div>' + block[m.end():]


def feed(dist, sections, cfg):
    """rss.xml: the institute's own articles (/updates/<name>/), newest first, with the full text."""
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    items = []
    for route, block in sections.items():
        if not re.fullmatch(r'/updates/[^/]+/', route):
            continue
        crumb = re.search(r'<p class="crumb">(.*?)</p>', block, flags=re.S)
        day = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', crumb.group(1)) if crumb else None
        art = re.search(r'<article\b[^>]*>(.*?)</article>', block, flags=re.S)
        if not day or not art:
            continue
        when = datetime(int(day.group(1)), int(day.group(2)), int(day.group(3)), 9, 0, tzinfo=timezone(timedelta(hours=9)))
        title = html.unescape(re.search(r'data-title="([^"]*)"', block).group(1))
        items.append((when, title, HOST + route, plain_text(art.group(1))))
    items.sort(reverse=True)
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '<channel>',
           f'<title>{html.escape(cfg["feed"])}</title>', f'<link>{HOST}/updates/</link>', f'<description>{html.escape(cfg["feed_desc"])}</description>',
           '<language>ko</language>', f'<atom:link href="{HOST}/rss.xml" rel="self" type="application/rss+xml"/>']
    if items:
        out.append(f'<lastBuildDate>{format_datetime(items[0][0])}</lastBuildDate>')
    for when, title, url, text in items:
        out.append(f'<item><title>{html.escape(title)}</title><link>{url}</link><guid isPermaLink="true">{url}</guid>'
                   f'<pubDate>{format_datetime(when)}</pubDate><description>{html.escape(text)}</description></item>')
    out += ['</channel>', '</rss>']
    (dist / 'rss.xml').write_text('\n'.join(out) + '\n', encoding='utf-8')
    return len(items)


def build(dist):
    dist = Path(dist)
    docs = {}
    for lang, cfg in LANGS.items():
        before, sections, after = split((dist / cfg['file']).read_text(encoding='utf-8'))
        data = {name: json.loads((dist / 'assets' / 'data' / f'{name}.json').read_text(encoding='utf-8')) for name in ('projects', 'achievements')}
        if '/research/' in sections:
            sections['/research/'] = fill_box(sections['/research/'], 'data-projects', projects_html(data['projects'], lang, cfg))
        if '/research/achievements/' in sections:
            sections['/research/achievements/'] = fill_box(sections['/research/achievements/'], 'data-achievements', achievements_html(data['achievements'], lang, cfg))
        before = before.replace('</head>', f'<link rel="alternate" type="application/rss+xml" title="{attr(LANGS["ko"]["feed"])}" href="/rss.xml">\n</head>', 1)
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
            # /nrl/about/ repeats the introduction that opens /nrl/, so search engines are pointed at /nrl/
            url = HOST + cfg['base'] + ('/nrl/' if route == '/nrl/about/' else route)
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
            if pair and route not in NOINDEX and route != '/nrl/about/':
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
            if route not in NOINDEX and route != '/nrl/about/':
                sitemap.append((url, (HOST + route, HOST + '/en' + route) if pair else None))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for url, pair in sitemap:
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{h}"/>' for l, h in zip(('ko', 'en'), pair)) if pair else ''
        lines.append(f'  <url><loc>{url}</loc>{alt}</url>')
    lines.append('</urlset>')
    (dist / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    n = feed(dist, docs['ko'][1], LANGS['ko'])
    print(f'built {len(sitemap)} pages (+ search), rss.xml with {n} articles')


if __name__ == '__main__':
    build(sys.argv[1])
