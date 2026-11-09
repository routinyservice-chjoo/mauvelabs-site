#!/usr/bin/env python3
"""공유 미리보기(Open Graph) 이미지 만들기 — assets/og.png(영어) · assets/og-ko.png(한국어).

1200×630 · 크림 바탕(#FFF8F0) + 22px 간격 점 · 왼쪽 글자(Pretendard) · 오른쪽 몽글이(앱 공식 그림 그대로, 비율 유지 축소).
2026-10-06에 만든 이미지의 자리·크기·색을 픽셀로 맞춰 옮긴 것(2026-11-09) — 글자를 바꿀 때 이 파일의 문구만 고친다.

    python3 tools/og_image.py            # 두 장을 assets/에 다시 만든다
    python3 tools/og_image.py --out DIR  # 다른 폴더에 만든다(미리 보기)

필요한 것: Pillow · Pretendard(~/Library/Fonts) · 앱 저장소의 몽글이 그림(../dailycumulus-rn/assets/images/mongle/mongle_very_good.png)
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.expanduser('~/Library/Fonts')
MONGLE = os.path.join(ROOT, '..', 'dailycumulus-rn', 'assets', 'images', 'mongle', 'mongle_very_good.png')

W, H = 1200, 630
BG = (255, 248, 240)       # site-v2.css 바탕
DOT = (239, 230, 220)
PINK_DEEP = (232, 135, 159)  # --pink-deep #E8879F
INK = (74, 64, 56)           # --ink #4A4038
INK_SOFT = (107, 97, 87)     # --ink-soft #6B6157
INK_FAINT = (138, 128, 120)  # --ink-faint #8A8078
X = 90
MONGLE_W, MONGLE_XY = 330, (835, 330)

# 문구는 locales/<언어>.json의 og_title · og_description과 맞춘다
PAGES = {
    'og.png': {
        'name': 'DailyCumulus',
        'title': ["A little diary for how", "you're actually feeling."], 'title_size': 60, 'title_y': (180, 254),
        'lines': ['Tap Mongle, pick a mood, done. No pressure.', 'iPhone & Android'], 'lines_y': (380, 428),
        'url': 'mauvelabsinc.com',
    },
    'og-ko.png': {
        'name': '데일리몽글',
        'title': ['지금 내 기분,', '가볍게 남겨요.'], 'title_size': 66, 'title_y': (180, 260),
        'lines': ['몽글이 누르고 기분 선택하면 끝. 부담 없어요.', '아이폰 · 안드로이드'], 'lines_y': (390, 438),
        'url': 'mauvelabsinc.com/ko',
    },
}


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f'Pretendard-{weight}.otf'), size)


def render(spec):
    im = Image.new('RGB', (W, H), BG)
    px = im.load()
    for y in range(0, H, 22):
        for x in range(0, W, 22):
            px[x, y] = DOT
    d = ImageDraw.Draw(im)
    d.text((X, 110), spec['name'], font=font('Bold', 44), fill=PINK_DEEP)
    for text, y in zip(spec['title'], spec['title_y']):
        d.text((X, y), text, font=font('Bold', spec['title_size']), fill=INK)
    for text, y in zip(spec['lines'], spec['lines_y']):
        d.text((X, y), text, font=font('Medium', 34), fill=INK_SOFT)
    d.text((X, 530), spec['url'], font=font('Medium', 30), fill=INK_FAINT)
    m = Image.open(MONGLE).convert('RGBA')
    m = m.resize((MONGLE_W, round(m.height * MONGLE_W / m.width)), Image.LANCZOS)  # 비율 유지
    base = im.convert('RGBA')
    base.alpha_composite(m, MONGLE_XY)
    return base.convert('RGB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'assets'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name, spec in PAGES.items():
        path = os.path.join(a.out, name)
        render(spec).save(path, optimize=True)
        print(path)


if __name__ == '__main__':
    main()
