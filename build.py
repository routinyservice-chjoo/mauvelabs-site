#!/usr/bin/env python3
"""언어별 페이지를 만든다 — 틀 하나(templates/page.html) + 언어별 문구(locales/*.json).

    python3 build.py

- en.json이 메인 언어(/)다. 그 밖의 언어는 서브(/ko/ 처럼 path 아래)다.
- **새 언어를 더할 때**: locales/en.json을 복사해 <언어>.json을 만들고 lang·path·og_locale·문구를 바꾼다.
  화면 속 앱 스크린샷이 그 언어로 있으면 img/<언어>/에 두고 shot_dir를 바꾼다(없으면 img/ 그대로 영어 화면).
- 키가 빠지거나 남으면 멈춘다 — 한 언어만 문구가 비는 일을 막는다.
- 결과물(index.html · <path>index.html · sitemap.xml)은 직접 고치지 않는다. 여기서 다시 만든다.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://mauvelabsinc.com/'
# CSS·JS·애니메이션을 고치면 올린다 — 브라우저가 옛 파일을 붙들지 않게
VERSION = '43'


def load_locales():
    out = []
    for name in sorted(os.listdir(os.path.join(ROOT, 'locales'))):
        if name.endswith('.json'):
            with open(os.path.join(ROOT, 'locales', name), encoding='utf-8') as f:
                out.append(json.load(f))
    out.sort(key=lambda l: (l['lang'] != 'en', l['lang']))  # 메인(en)이 먼저
    return out


def main():
    locales = load_locales()
    base_keys = {k for k in locales[0] if not k.startswith('_')}
    for loc in locales[1:]:
        keys = {k for k in loc if not k.startswith('_')}
        if keys != base_keys:
            sys.exit(f"[{loc['lang']}] 키가 en과 다르다 — 빠짐 {sorted(base_keys - keys)} · 남음 {sorted(keys - base_keys)}")

    with open(os.path.join(ROOT, 'templates', 'page.html'), encoding='utf-8') as f:
        tpl = f.read()

    for loc in locales:
        depth = loc['path'].count('/')
        b = '../' * depth
        alts = [f'  <link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}">' for l in locales]
        alts.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE}">')
        links = [f'      <a href="{b}{l["path"]}" lang="{l["lang"]}" hreflang="{l["lang"]}">{html.escape(l["language_name"])}</a>'
                 for l in locales if l is not loc]
        values = {**loc, 'b': b, 'v': VERSION, 'url': SITE + loc['path'],
                  'hreflang': '\n'.join(alts), 'lang_links': '\n'.join(links)}

        def fill(m):
            key = m.group(1)
            if key not in values:
                sys.exit(f"[{loc['lang']}] 틀에 있는 {{{{{key}}}}}가 문구 파일에 없다")
            return str(values[key])

        page = re.sub(r'\{\{(\w+)\}\}', fill, tpl)
        out_dir = os.path.join(ROOT, loc['path'])
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(page)
        print(f"✅ {loc['lang']:>3} → /{loc['path']}index.html")

    # sitemap — 언어마다 서로를 가리킨다
    urls = []
    for loc in locales:
        alt = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}"/>' for l in locales)
        alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}"/>'
        urls.append(f'  <url>\n    <loc>{SITE}{loc["path"]}</loc>{alt}\n  </url>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                + '\n'.join(urls) + '\n</urlset>\n')
    print('✅ sitemap.xml')


if __name__ == '__main__':
    main()
