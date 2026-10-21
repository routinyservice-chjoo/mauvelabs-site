// 언어 드롭다운 — 바깥을 누르거나 Esc면 닫는다(2026-10-21)
document.addEventListener('click', function (e) {
  document.querySelectorAll('details.lang-menu[open]').forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
});
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') document.querySelectorAll('details.lang-menu[open]').forEach(function (d) { d.removeAttribute('open'); });
});
