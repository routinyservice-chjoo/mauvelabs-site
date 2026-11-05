// 대표 주소 하나로 모은다(2026-11-05 · 검색 노출) — http:// · www. 로 온 요청을 https://mauvelabsinc.com 으로 301.
// 나머지는 정적 파일 그대로(env.ASSETS). 이미지·글꼴·애니메이션은 wrangler.jsonc run_worker_first에서 빼 Worker를 거치지 않는다.
const CANONICAL_HOST = 'mauvelabsinc.com';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const local = url.hostname === 'localhost' || url.hostname === '127.0.0.1';
    if (!local && (url.protocol !== 'https:' || url.hostname !== CANONICAL_HOST)) {
      url.protocol = 'https:';
      url.hostname = CANONICAL_HOST;
      url.port = '';
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
