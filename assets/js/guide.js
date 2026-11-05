/* 가이드 글 — 앱에서 열면(?from=app) 앱 설치 카드를 숨긴다 */
if (/[?&]from=app\b/.test(location.search)) { var gApp = document.querySelector('.g-app'); if (gApp) gApp.remove(); }

/* 가이드 글 — 읽고 있는 소제목을 목차에 표시한다 */
(function () {
  var links = [].slice.call(document.querySelectorAll('.g-toc a'));
  if (!links.length || !('IntersectionObserver' in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      links.forEach(function (a) { a.removeAttribute('aria-current'); });
      var a = byId[e.target.id];
      if (a) a.setAttribute('aria-current', 'true');
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  Object.keys(byId).forEach(function (id) { var h = document.getElementById(id); if (h) io.observe(h); });
})();
