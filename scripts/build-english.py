from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import json, re, posixpath

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
TEXT = json.loads((ROOT / 'scripts/english-text.json').read_text())
NAMES = json.loads((ROOT / 'scripts/faculty-names-en.json').read_text())
TEXT.update(NAMES)
unknown = set()
PROFILE_URLS = {p['profile_url']:p['profile_url_en'] for p in json.loads((DIST / 'research/nrl/faculty/directory.json').read_text()) if p.get('profile_url_en')}


def translate(value):
    value = unescape(value)
    if value in TEXT:
        return TEXT[value]
    if not re.search('[가-힣]', value):
        return value
    if value.startswith('참여 - '):
        return 'Participating - ' + value.removeprefix('참여 - ')
    if value.startswith('연계 - '):
        return 'Affiliated - ' + value.removeprefix('연계 - ')
    if value in ('참여', '연계'):
        return 'Participating' if value == '참여' else 'Affiliated'
    if value.endswith(' ↗'):
        return translate(value[:-2]) + ' ↗'
    if ' | ' in value:
        return ' | '.join(translate(part) for part in value.split(' | '))
    if ' · ' in value:
        return ' · '.join(translate(part) for part in value.split(' · '))
    unknown.add(value)
    return value

def local_url(value, source_path):
    if not value or value.startswith(('http:', 'https:', 'mailto:', 'tel:', 'data:', '#', '?')):
        return value
    resolved = urlsplit(urljoin('/' + source_path.as_posix(), value))
    path = resolved.path
    if path.startswith('/assets/'):
        return path
    return '/en' + path + ('?' + resolved.query if resolved.query else '') + ('#' + resolved.fragment if resolved.fragment else '')

class English(HTMLParser):
    def __init__(self, source_path):
        super().__init__(convert_charrefs=False)
        self.path = source_path
        self.raw = None
        self.out = []

    def handle_decl(self, decl):
        self.out.append('<!' + decl + '>')

    def handle_comment(self, data):
        self.out.append('<!--' + data + '-->')

    def handle_starttag(self, tag, attrs):
        result = []
        for key, value in attrs:
            if value is not None:
                if tag == 'html' and key == 'lang': value = 'en'
                elif key == 'src' and 'nrl2-official-' in value: value = '/assets/nrl2-official-en-reversed.png'
                elif key in ('href', 'src'): value = local_url(value, self.path)
                elif key in ('alt', 'title', 'aria-label', 'placeholder'): value = translate(value)
                elif key == 'content' and re.search('[가-힣]', value): value = 'SNU Robotics Institute: connecting robotics research, people and collaboration.'
                elif key == 'class' and value in ('nrl-header-mark', 'nrl-mark'): value += ' nrl-en'
                elif key == 'data-search':
                    # Keep Korean search aliases while adding all English directory terms.
                    translated = value
                    for ko, en in sorted(TEXT.items(), key=lambda x: -len(x[0])):
                        translated = translated.replace(ko, en)
                    value = translated + ' ' + value
            result.append(key if value is None else key + '="' + escape(value, quote=True) + '"')
        self.out.append('<' + tag + (' ' + ' '.join(result) if result else '') + '>')
        if tag in ('script', 'style'): self.raw = tag

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.out.append('</' + tag + '>')
        if self.raw == tag: self.raw = None

    def handle_data(self, value):
        if self.raw:
            if self.raw == 'script': value = value.replace("count+'명의 교수'", "count+' faculty members'")
            self.out.append(value)
        elif value.strip():
            self.out.append(value[:len(value)-len(value.lstrip())] + escape(translate(value.strip()), quote=False) + value[len(value.rstrip()):])
        else:
            self.out.append(value)

    def handle_entityref(self, name): self.out.append('&' + name + ';')
    def handle_charref(self, name): self.out.append('&#' + name + ';')

def language_control(lang, rel):
    korean_path = '/' + rel.as_posix().removesuffix('index.html')
    english_path = '/en' + korean_path
    return '<nav class="language-switch" aria-label="' + ('Language' if lang == 'en' else '언어 선택') + '"><a lang="ko" hreflang="ko" href="' + korean_path + '"' + (' aria-current="page"' if lang == 'ko' else '') + '>한국어</a><a lang="en" hreflang="en" href="' + english_path + '"' + (' aria-current="page"' if lang == 'en' else '') + '>English</a></nav>'

sources = [p for p in DIST.rglob('*.html') if 'en' not in p.relative_to(DIST).parts]
for source in sources:
    rel = source.relative_to(DIST)
    korean = source.read_text()
    korean = re.sub(r'<nav class="language-switch".*?</nav>', '', korean, flags=re.S)
    parser = English(rel)
    parser.feed(korean)
    english = ''.join(parser.out)
    for old_url, new_url in PROFILE_URLS.items():
        pattern = r'<a href="' + re.escape(escape(old_url, quote=True)) + r'"[^>]*>.*?</a>'
        english = re.sub(pattern, lambda m: m[0].replace(escape(old_url, quote=True), escape(new_url, quote=True)).replace('Hospital profile (Korean)', 'Hospital profile'), english)

    english = re.sub(r'(<style>)(.*?)(</style>)', lambda m: m[1] + re.sub(r'letter-spacing:\s*-\d*\.?\d+(?:em|px|rem)', 'letter-spacing:normal', m[2]) + m[3], english, flags=re.S)
    english = re.sub(r'(<div class="university-en">)Seoul National University<br>\s*Robotics Institute(</div>)', r'\1Seoul National University\2', english)
    english = english.replace('<div class="theme-bar">', '<div class="theme-bar">' + language_control('en', rel), 1)
    # English pages share a single stylesheet and script with Korean pages.
    english = re.sub(r'(<(?:link|script)[^>]+(?:href|src)=")[^"]*(assets/themes\.(?:css|js))', r'\1/\2', english)
    if rel.as_posix() == 'index.html':
        english = re.sub(
            r'<h1 id="hero-title">.*?</h1><div class="hero-sub">.*?</div>',
            '<h1 id="hero-title"><span>Dreams into Questions</span><span>Questions into Research</span><span>Research into Technology</span><span>Technology into Reality</span></h1><div class="hero-sub">— We turn dreams into reality</div>',
            english, count=1, flags=re.S)
    target = DIST / 'en' / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(english)
    korean = korean.replace('<div class="theme-bar">', '<div class="theme-bar">' + language_control('ko', rel), 1)
    source.write_text(korean)

directory = json.loads((DIST / 'research/nrl/faculty/directory.json').read_text())
translated = []
for item in directory:
    en = dict(item)
    for key in ('name', 'dept', 'org', 'category', 'lab'):
        en[key] = translate(item[key])
    en['name_ko'] = item['name']
    if item.get('profile_url_en'): en['profile_url'] = item['profile_url_en']
    translated.append(en)
target = DIST / 'en/research/nrl/faculty/directory.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(translated, ensure_ascii=False, indent=2))
print('Generated English pages:', len(sources))
print('Untranslated text:', json.dumps(sorted(unknown), ensure_ascii=False, indent=2))
