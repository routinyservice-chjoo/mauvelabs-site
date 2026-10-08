# mauvelabsinc.com — DailyCumulus(데일리몽글) 홈페이지

GitHub Pages로 나간다(무료 · `main`에 푸시하면 1분 안에 반영). 도메인 등록처는 Squarespace(DNS만 거기서 바꾼다).

## 구조 — 틀 하나 + 언어별 문구

| 파일 | 하는 일 |
| --- | --- |
| `templates/page.html` | 페이지 틀. `{{키}}` 자리에 문구가 들어간다 |
| `locales/en.json` | **메인 언어(영어, `/`)** — 기준은 미국 사용자 |
| `locales/<언어>.json` | 서브 언어(`/ko/` …). en의 뜻을 그 나라 말로 옮긴다(직역 금지) |
| `build.py` | 위 둘로 `index.html` · `<언어>/index.html` · `sitemap.xml`을 만든다 |

🔴 `index.html` · `ko/index.html` · `sitemap.xml`은 **직접 고치지 않는다** — `python3 build.py`가 덮어쓴다.

## 언어 하나 더하기

1. `locales/en.json`을 복사해 `locales/ja.json`처럼 만들고 `lang` · `path`(예 `ja/`) · `language_name` · `og_locale`과 문구를 바꾼다
2. 그 언어의 앱 스크린샷이 있으면 `img/ja/screen-{1,2,4,6}.webp`로 넣고 `shot_dir`을 `img/ja/`로. 공식 배지(Apple · Google)도 그 언어판을 `badge_dir`에
3. 라틴 문자가 아니면 `assets/site-v2.css`의 `html:lang(ko)` 규칙처럼 제목 글꼴을 정한다(Fraunces는 라틴 전용)
4. `python3 build.py` — 키가 빠지면 멈춘다 → 푸시

## 쓰는 것(전부 저장소 안 · 외부 계정 없음)

- 몽글이 애니메이션: 앱(`dailycumulus-rn/assets/animations`)의 Lottie를 웹용으로 줄인 `anim/*.json` + **lottie-web 5.13.0**(MIT · `assets/lottie_light.min.js`)
- 글꼴: Fraunces(OFL · `assets/fraunces.woff2`) · Pretendard(jsDelivr)
- 다운로드 배지: Apple·Google 공식 배지(`img/` · `img/ko/`)
- 앱 화면: App Store 스크린샷에서 휴대폰 부분만 잘라 씀(`img/screen-*.webp`)
- CSS·JS를 고치면 `build.py`의 `VERSION`을 올린다(브라우저가 옛 파일을 붙들지 않게)
