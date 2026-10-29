#!/usr/bin/env python3
"""언어별 페이지를 만든다 — 틀 하나(templates/page.html) + 언어별 문구(locales/*.json).

    python3 build.py

- en.json이 메인 언어(/)다. 그 밖의 언어는 서브(/ko/ 처럼 path 아래)다.
- **새 언어를 더할 때**: locales/en.json을 복사해 <언어>.json을 만들고 lang·path·og_locale·문구를 바꾼다.
  화면 속 앱 스크린샷이 그 언어로 있으면 img/<언어>/에 두고 shot_dir를 바꾼다(없으면 img/ 그대로 영어 화면).
- 키가 빠지거나 남으면 멈춘다 — 한 언어만 문구가 비는 일을 막는다.
- 결과물(index.html · <path>index.html · <path>support/ · <path>notes/ · sitemap.xml)은 직접 고치지 않는다. 여기서 다시 만든다.
- 개발노트(/notes/)에 새 버전을 더할 때: 각 언어 파일의 notes_entries 맨 앞에 항목을 더한다(공개된 기능만).
"""
import html
import json
import os
import re
import sys

def esc(text):
    """html.escape + 줄바꿈 자리 <wbr>만 살린다(일본어 제목을 구 단위로 꺾기 · 2026-10-29). en·ko 문구엔 <wbr>이 없어 결과가 같다."""
    return html.escape(text).replace('&lt;wbr&gt;', '<wbr>')


ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://mauvelabsinc.com/'
# CSS·JS·애니메이션을 고치면 올린다 — 브라우저가 옛 파일을 붙들지 않게
VERSION = '54'
# 언어 버튼 아이콘(지구본 · 장식이라 읽지 않게)
GLOBE = '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>'



def lang_menu(current, locales, href):
    """상단 언어 선택 드롭다운(2026-10-21 대표님 「드롭다운으로 선택」). 지금 언어가 버튼에 보이고, 펼치면 전부 고른다."""
    items = []
    for l in locales:
        cur = ' aria-current="true"' if l is current else ''
        items.append(f'        <li><a href="{href(l)}" lang="{l["lang"]}" hreflang="{l["lang"]}"{cur}>{html.escape(l["language_name"])}</a></li>')
    return (f'    <details class="lang-menu">\n'
            f'      <summary aria-label="{html.escape(current["lang_menu_label"])}">{GLOBE}'
            f'<span class="lang-full">{html.escape(current["language_name"])}</span>'
            f'<span class="lang-short" aria-hidden="true">{current["lang"].upper()}</span>'
            f'<svg class="chev" aria-hidden="true" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg></summary>\n'
            f'      <ul>\n' + '\n'.join(items) + '\n      </ul>\n    </details>')

# 하위 페이지(templates/<이름>.html → /<이름>/ · /<언어>/<이름>/). 더하면 sitemap에도 같이 들어간다
SUBPAGES = ['support', 'notes', 'news', 'faq', 'guide']


def has(loc, sub):
    """그 언어에 하위 페이지가 있나 — 문구 파일의 `_hide_pages`(예: ja의 [\"guide\"] · 내용이 준비 중인 페이지)에 있으면 만들지도 링크하지도 않는다(2026-10-29)."""
    return sub not in loc.get('_hide_pages', [])


def notes_html(loc):
    """개발노트 항목(locales의 notes_entries)을 HTML로. 새 버전은 목록 맨 앞에 더한다."""
    out = []
    for e in loc['notes_entries']:
        items = '\n'.join(f'        <li>{it}</li>' for it in e['items'])
        out.append(f'    <article class="note" id="v{e["version"]}">\n'
                   f'      <p class="note-meta"><span class="note-ver">{html.escape(e["version"])}</span> {html.escape(e["dates"])}</p>\n'
                   f'      <h2>{esc(e["title"])}</h2>\n'
                   f'      <ul class="note-list">\n{items}\n      </ul>\n    </article>')
    return '\n'.join(out)


def news_html(loc, sb):
    """공지사항 게시판(locales의 news_entries) — 최신이 위. 글마다 분류(공지 · 개발 업데이트) · 날짜 · 제목 · 링크."""
    rows = []
    for e in loc['news_entries']:
        href = e['href'].replace('{b}', sb + loc['path'])
        tag = html.escape(loc['news_tag_' + e['tag']])
        title = f'<a class="board-title" href="{href}">{esc(e["title"])}</a>'
        if e.get('sub'):  # 부제(시행일 등) — 있는 글만 · 없으면 예전 모양 그대로
            title = f'<span class="board-main">{title}<small class="board-sub">{esc(e["sub"])}</small></span>'
        rows.append(f'      <li class="board-row"><span class="board-tag tag-{e["tag"]}">{tag}</span>'
                    f'{title}'
                    f'<time class="board-date" datetime="{e["date"]}">{html.escape(e["date_label"])}</time></li>')
    return '    <ul class="board">\n' + '\n'.join(rows) + '\n    </ul>'


def guide_html(loc):
    """사용 가이드(locales의 guide_sections) — 뼈대: 절 제목 + 한 줄."""
    out = []
    for g in loc['guide_sections']:
        out.append(f'    <section class="guide-sec" id="{g["id"]}">\n      <h2>{html.escape(g["title"])}</h2>\n'
                   f'      <p>{g["body"]}</p>\n    </section>')
    return '\n'.join(out)


def hub_html(loc, sb):
    """고객지원 모음 — 공지사항 · 개발노트 · 자주 묻는 질문 · 사용 가이드 · 문의하기 카드."""
    base = sb + loc['path']
    cards = [('news/', loc['nav_news'], loc['hub_news_desc']),
             ('notes/', loc['nav_notes'], loc['hub_notes_desc']),
             ('faq/', loc['faq_title'], loc['hub_faq_desc']),
             ('guide/', loc['guide_title'], loc['hub_guide_desc'])]
    cards = [c for c in cards if has(loc, c[0].rstrip('/'))]
    out = [f'      <a class="hub-card" href="{base}{href}"><b>{html.escape(t)}</b><span>{html.escape(d)}</span></a>' for href, t, d in cards]
    out.append(f'      <a class="hub-card hub-contact" href="{loc["contact_mailto"]}"><b>{html.escape(loc["hub_contact_title"])}</b>'
               f'<span>{html.escape(loc["hub_contact_desc"])}</span></a>')
    return '    <div class="hub-grid">\n' + '\n'.join(out) + '\n    </div>'


def site_nav(loc, b, current):
    """상단 메뉴(2026-10-26 대표님 「메뉴에 공지사항 · 고객지원」) — 홈에선 사용법, 하위 페이지에선 홈으로."""
    base = b + loc['path']
    first = (f'    <a href="#how" class="hide-xs">{loc["nav_how"]}</a>' if current == 'home'
             else f'    <a href="{base}" class="hide-xs">{loc["sup_back"]}</a>')
    def link(sub, label):
        cur = ' aria-current="page"' if current == sub else ''
        return f'    <a href="{base}{sub}/"{cur}>{label}</a>'
    return '\n'.join([first, link('news', loc['nav_news']), link('support', loc['nav_support'])])


def site_footer(loc, b, lang_links):
    """하단(2026-10-26 대표님 예시 — 회사 · 탐색 · 문의 세 칸 + 약관·처리방침 + 사업자 정보)."""
    base = b + loc['path']
    col = lambda title, items: (f'      <div class="foot-col"><h2 class="foot-h">{html.escape(title)}</h2>\n'
                                + '\n'.join(f'        {i}' for i in items) + '\n      </div>')
    return f'''<footer class="wrap site-foot">
  <div class="foot-cols">
    <div class="foot-brand">
      <img src="{b}assets/brand/mauvelabs-logo@2x.png?v={VERSION}" alt="Mauve Labs" height="40">
      <p class="made">{loc["made_by"]}</p>
    </div>
{col(loc["foot_col_explore"], [f'<a href="{base}news/">{loc["nav_news"]}</a>', f'<a href="{base}notes/">{loc["nav_notes"]}</a>', f'<a href="{base}faq/">{loc["faq_title"]}</a>', *([f'<a href="{base}guide/">{loc["guide_title"]}</a>'] if has(loc, 'guide') else []), f'<a href="{base}#get">{loc["foot_download"]}</a>'])}
{col(loc["foot_col_contact"], [f'<a href="{base}support/">{loc["foot_help"]}</a>', f'<a href="{loc["contact_mailto"]}">{loc["foot_email_label"]}: mauvelabs@mauvelabsinc.com</a>'])}
  </div>
  <div class="foot-bottom">
    <nav aria-label="Footer">
      <a href="{loc["terms_url"]}">{loc["foot_terms"]}</a>
      <a href="{loc["privacy_url"]}"><b>{loc["foot_privacy"]}</b></a>
{lang_links}
    </nav>
{loc["legal"]}
  </div>
</footer>'''


def render_subpage(loc, locales, values, depth, sub):
    """하위 페이지 하나를 만든다 — 언어마다 서로를 가리키는 hreflang · 바닥 언어 링크 · 상단 언어 메뉴를 그 페이지 주소로."""
    sb = '../' * (depth + 1)
    alts = [f'  <link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}{sub}/">' for l in locales if has(l, sub)]
    alts.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE}{sub}/">')
    to = lambda l: f'{sb}{l["path"]}{sub}/' if has(l, sub) else f'{sb}{l["path"]}'  # 그 언어에 없는 페이지면 그 언어 홈으로
    links = [f'      <a href="{to(l)}" lang="{l["lang"]}" hreflang="{l["lang"]}">{html.escape(l["language_name"])}</a>'
             for l in locales if l is not loc]
    svalues = {**values, 'b': sb, 'sub_hreflang': '\n'.join(alts), 'sub_lang_links': '\n'.join(links),
               'sub_nav_lang': lang_menu(loc, locales, to),
               'notes_html': notes_html(loc), 'news_html': news_html(loc, sb), 'guide_html': guide_html(loc),
               'hub_html': hub_html(loc, sb), 'site_nav_links': site_nav(loc, sb, sub),
               'site_footer': site_footer(loc, sb, '\n'.join(links))}

    def sfill(m):
        key = m.group(1)
        if key not in svalues:
            sys.exit(f"[{loc['lang']}] {sub} 틀의 {{{{{key}}}}}가 문구 파일에 없다")
        return str(svalues[key])

    with open(os.path.join(ROOT, 'templates', f'{sub}.html'), encoding='utf-8') as f:
        page = re.sub(r'\{\{(\w+)\}\}', sfill, f.read())
    out_dir = os.path.join(ROOT, loc['path'], sub)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    print(f"✅ {loc['lang']:>3} → /{loc['path']}{sub}/index.html")


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
        # 상단 메뉴의 언어 변경 버튼(2026-10-21 대표님 「홈페이지 상단에 언어변경 메뉴」) — 다른 언어로 바로 간다
        nav_lang = lang_menu(loc, locales, lambda l: f'{b}{l["path"]}')
        values = {**loc, 'b': b, 'v': VERSION, 'url': SITE + loc['path'],
                  'hreflang': '\n'.join(alts), 'lang_links': '\n'.join(links), 'nav_lang': nav_lang,
                  'site_nav_links': site_nav(loc, b, 'home'), 'site_footer': site_footer(loc, b, '\n'.join(links))}

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

        # 하위 페이지 — 고객 지원(/support/ · App Store 지원 URL · Play 웹사이트가 가리킨다 · 2026-10-13)
        # · 개발노트(/notes/ · 1.1.0부터 · 2026-10-23)
        for sub in SUBPAGES:
            if has(loc, sub):
                render_subpage(loc, locales, values, depth, sub)

    # sitemap — 언어마다 서로를 가리킨다
    urls = []
    for loc in locales:
        alt = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}"/>' for l in locales)
        alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}"/>'
        urls.append(f'  <url>\n    <loc>{SITE}{loc["path"]}</loc>{alt}\n  </url>')
        for sub in SUBPAGES:
            if not has(loc, sub):
                continue
            salt = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}{sub}/"/>' for l in locales if has(l, sub))
            urls.append(f'  <url>\n    <loc>{SITE}{loc["path"]}{sub}/</loc>{salt}\n  </url>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                + '\n'.join(urls) + '\n</urlset>\n')
    print('✅ sitemap.xml')


if __name__ == '__main__':
    main()
