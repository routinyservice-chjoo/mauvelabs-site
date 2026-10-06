/* 스크롤 효과 — 애플 제품 페이지처럼 내릴수록 장면이 바뀐다. 라이브러리 없이 브라우저 기본 기능만 쓴다.
   「동작 줄이기」를 켠 사람에게는 아무것도 움직이지 않는다(모든 요소가 처음부터 보인다). */
(function () {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  var root = document.documentElement;
  root.classList.add('motion');

  // ① 화면에 들어오면 떠오르기. 묶음(data-reveal-group)은 자식이 하나씩 차례로
  document.querySelectorAll('[data-reveal-group]').forEach(function (g) {
    Array.prototype.forEach.call(g.children, function (c, i) {
      c.setAttribute('data-reveal', ''); c.style.setProperty('--d', (i * 90) + 'ms');
    });
  });
  var reveal = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); reveal.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -12% 0px' });
  document.querySelectorAll('[data-reveal]').forEach(function (el) { reveal.observe(el); });

  // ② 이야기 절: 화면 가운데를 지나는 단계에 맞춰 고정된 휴대폰 화면을 바꾼다
  var screens = document.querySelectorAll('.stage-screens img');
  var steps = document.querySelectorAll('.story-steps .step');
  var tape = document.querySelector('.stage-tape');
  var tapes = ['pink', 'mint', 'lilac'];
  var stepIO = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var n = e.target.getAttribute('data-step');
      steps.forEach(function (s) { s.classList.toggle('is-active', s === e.target); });
      screens.forEach(function (img) { img.classList.toggle('on', img.getAttribute('data-step') === n); });
      if (tape) tape.className = 'tape stage-tape ' + tapes[+n];
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  steps.forEach(function (s) { stepIO.observe(s); });

  // ③ 첫 화면 시차: 내릴수록 휴대폰은 세워지고 몽글이는 서로 다른 속도로 떠오른다
  var phone = document.querySelector('.hero-art .phone-main');
  var side = document.querySelector('.hero-art .phone-side');
  var pol = document.querySelector('.hero-art .polaroid');
  var m1 = document.querySelector('.float.m1');
  var m2 = document.querySelector('.float.m2');
  var ticking = false;
  function frame() {
    ticking = false;
    var p = Math.min(Math.max(window.scrollY / 700, 0), 1);
    if (phone) { phone.style.rotate = (3 * p) + 'deg'; phone.style.translate = '0 ' + (-30 * p) + 'px'; }
    if (side) { side.style.translate = '0 ' + (-80 * p) + 'px'; side.style.rotate = (4 * p) + 'deg'; }
    if (pol) { pol.style.translate = '0 ' + (-90 * p) + 'px'; pol.style.rotate = (-6 * p) + 'deg'; }
    if (m1) m1.style.translate = '0 ' + (-30 * p) + 'px'; // 홈 휴대폰과 함께 — 더 올리면 설명 글 위로 올라간다
    if (m2) m2.style.translate = '0 ' + (-70 * p) + 'px';
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
  frame();
})();
