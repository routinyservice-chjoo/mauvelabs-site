# mauvelabsinc.com — DailyCumulus(데일리몽글) 홈페이지

**Cloudflare Workers `mauvelabs-site`로 나간다**(2026-10-12부터 · 무료 · 루트·`www`는 Workers 사용자 지정 도메인 · 인증서 자동). `main`에 푸시하면 GitHub Actions(`.github/workflows/deploy.yml`)가 배포한다 — 저장소 시크릿 `CLOUDFLARE_API_TOKEN`이 있어야 하고, 없으면 건너뛴다. 손으로 배포할 때는 `CLOUDFLARE_API_TOKEN=$(security find-generic-password -s dailycumulus -a cloudflare-api-token -w) CLOUDFLARE_ACCOUNT_ID=9c8bfa7b3a161a869b82e939d2c5a252 npx wrangler@4.149.0 deploy`. **DNS는 Cloudflare에서 고친다**(네임서버 Cloudflare · DNSSEC도 Cloudflare). 도메인 등록·결제만 Squarespace에 남는다.

## 구조 — 틀 하나 + 언어별 문구

| 파일 | 하는 일 |
| --- | --- |
| `templates/page.html` | 페이지 틀. `{{키}}` 자리에 문구가 들어간다 |
| `locales/en.json` | **메인 언어(영어, `/`)** — 기준은 미국 사용자 |
| `locales/<언어>.json` | 서브 언어(`/ko/` · `/ja/`(10/29 · 대표님 검수 전 초안 — `docs/ja-review-2026-10-29.md`)). en의 뜻을 그 나라 말로 옮긴다(직역 금지) · 일본어는 앱 저장소 `docs/tone-and-manner.md` §10-1 |
| `build.py` | 위 둘로 `index.html` · `<언어>/index.html` · 하위 페이지 · `sitemap.xml`을 만든다 · 상단 메뉴(`site_nav`)·하단(`site_footer`)은 여기 한 곳 |
| `templates/{support,notes,news,faq,guide}.html` | 하위 페이지 틀(10/26) — 고객지원 모음 · 개발노트 · 공지사항 게시판 · 자주 묻는 질문 · 사용 가이드 |

🔴 `index.html` · `ko/index.html` · 하위 페이지(`support/` `notes/` `news/` `faq/` `guide/`) · `sitemap.xml`은 **직접 고치지 않는다** — `python3 build.py`가 덮어쓴다.

## 글 더하기(10/26)

- **새 버전이 공개되면**: 언어마다 `notes_entries` 맨 앞에 항목(버전 · 날짜 · 제목 · 항목들) + `news_entries` 맨 앞에 글(`tag` `update` · `href` `{b}notes/#v<버전>`)
- **공지**: `news_entries` 맨 앞에 `tag` `notice`(링크는 전체 주소도 된다)
- **사용 가이드**: `guide_sections`의 `body`를 채운다(지금은 뼈대 — 「준비하고 있어요」)
- 영어 문구는 앱 저장소 `docs/copy-review-prompt.md`로 별도 검토를 받는다 · 회사 소개에 「작은 팀 · small indie」를 쓰지 않는다
- 「회사」 하단 칸(회사소개)은 회사소개 페이지를 만들 때 `site_footer`에 다시 넣는다

## 언어 하나 더하기

1. `locales/en.json`을 복사해 `locales/<언어>.json`처럼 만들고 `lang` · `path`(예 `ja/`) · `language_name` · `og_locale`과 문구를 바꾼다
2. 그 언어의 앱 스크린샷이 있으면 `img/ja/screen-{1,2,4,6}.webp`로 넣고 `shot_dir`을 `img/ja/`로. 공식 배지(Apple · Google)도 그 언어판을 `badge_dir`에
3. 라틴 문자가 아니면 `assets/site-v2.css`의 `html:lang(ko)` 규칙처럼 제목 글꼴을 정한다(Fraunces는 라틴 전용)
4. `python3 build.py` — 키가 빠지면 멈춘다 → 푸시(자동 배포) · 시크릿이 없으면 위 `wrangler deploy`

## 쓰는 것(전부 저장소 안 · 외부 계정 없음)

- 몽글이 애니메이션: 앱(`dailycumulus-rn/assets/animations`)의 Lottie를 웹용으로 줄인 `anim/*.json` + **lottie-web 5.13.0**(MIT · `assets/lottie_light.min.js`)
- 글꼴: Fraunces(OFL · `assets/fraunces.woff2`) · Pretendard(jsDelivr)
- 다운로드 배지: Apple·Google 공식 배지(`img/` · `img/ko/`)
- 앱 화면: App Store 스크린샷에서 휴대폰 부분만 잘라 씀(`img/screen-*.webp`)
- CSS·JS를 고치면 `build.py`의 `VERSION`을 올린다(브라우저가 옛 파일을 붙들지 않게)
