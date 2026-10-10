// 응가메이트 웹 — 모바일 메뉴 · 투명 헤더 · 첫 방문 로딩 · 여섯 가지 카드 넘기기 · 첫 화면 소개 영상 · 단어씩 올라오는 제목
// · 이렇게 써요 단계(들어오면 아이콘 → 영상) · 풀페이지 넘기기 · 이야기 분류 칩 · 등장 효과
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 모바일 전체 메뉴
  var sheet = document.getElementById('menu');
  var openers = document.querySelectorAll('[data-menu-open]');
  var closers = document.querySelectorAll('[data-menu-close]');
  function setMenu(open) {
    if (!sheet) return;
    sheet.classList.toggle('open', open);
    sheet.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.classList.toggle('menu-open', open);
    openers.forEach(function (b) { b.setAttribute('aria-expanded', open ? 'true' : 'false'); });
    if (open) { var first = sheet.querySelector('a, button'); if (first) first.focus(); }
    else if (openers[0]) openers[0].focus();
  }
  openers.forEach(function (b) { b.addEventListener('click', function () { setMenu(true); }); });
  closers.forEach(function (b) { b.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) {
    if (!sheet || !sheet.classList.contains('open')) return;
    if (e.key === 'Escape') { setMenu(false); return; }
    if (e.key !== 'Tab') return;
    // 메뉴가 열려 있으면 Tab이 메뉴 밖으로 나가지 않게
    var items = sheet.querySelectorAll('a, button');
    var first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  // 첫 방문 로딩 — 다 그려지면(최대 1.2초) 사라지고, 다음부터는 안 보인다
  var intro = document.querySelector('.intro');
  if (intro && document.documentElement.classList.contains('show-intro')) {
    var started = Date.now();
    var hide = function () {
      if (intro.classList.contains('done')) return;
      intro.classList.add('done');
      try { localStorage.setItem('pm_intro', '1'); } catch (e) {}
      setTimeout(function () { document.documentElement.classList.remove('show-intro'); }, 500);
    };
    window.addEventListener('load', function () { setTimeout(hide, Math.max(0, 700 - (Date.now() - started))); });
    setTimeout(hide, 1200);
  }

  // 여섯 가지 카드 — 화살표와 점
  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    var track = root.querySelector('.track');
    var prev = root.querySelector('[data-prev]');
    var next = root.querySelector('[data-next]');
    var dots = root.querySelectorAll('.dots i');
    var cards = track.children;
    function step() { return cards.length > 1 ? cards[1].offsetLeft - cards[0].offsetLeft : track.clientWidth; }
    function update() {
      var i = Math.round(track.scrollLeft / step());
      dots.forEach(function (d, k) { d.classList.toggle('on', k === Math.min(i, dots.length - 1)); });
      if (prev) prev.disabled = track.scrollLeft < 4;
      if (next) next.disabled = track.scrollLeft + track.clientWidth > track.scrollWidth - 4;
    }
    if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: reduce ? 'auto' : 'smooth' }); });
    if (next) next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: reduce ? 'auto' : 'smooth' }); });
    track.addEventListener('scroll', function () { window.requestAnimationFrame(update); }, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  // 첫 화면 소개 영상 — 소리 없이 바로 돌고, 소리 켜기를 누르면 처음부터 소리와 함께
  document.querySelectorAll('[data-film]').forEach(function (box) {
    var v = box.querySelector('video');
    var b = box.querySelector('[data-sound]');
    var label = b.querySelector('span');
    var restarted = false;
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); v.controls = true; }
    b.addEventListener('click', function () {
      v.muted = !v.muted;
      if (!v.muted && !restarted) { restarted = true; v.currentTime = 0; }
      var p = v.play(); if (p && p.catch) p.catch(function () {});
      b.setAttribute('aria-pressed', v.muted ? 'false' : 'true');
      label.textContent = b.getAttribute(v.muted ? 'data-on' : 'data-off');
      box.classList.toggle('sound', !v.muted);
    });
    // 화면에서 벗어나면 멈췄다가 돌아오면 이어서
    if ('IntersectionObserver' in window && !reduce) {
      new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } else v.pause();
      }, { threshold: 0.2 }).observe(box);
    }
  });

  // 제목 글자 — 단어마다 감싸서 모션그래픽처럼 하나씩 올라오게 (형광펜 알약은 한 덩어리로)
  var mos = [].slice.call(document.querySelectorAll('[data-mo]'));
  mos.forEach(function (el) {
    var i = 0;
    function wrap(node) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'w';
            var inner = document.createElement('span'); inner.textContent = part; inner.style.setProperty('--i', i++);
            w.appendChild(inner); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') {
          var w = document.createElement('span'); w.className = 'w';
          node.replaceChild(w, n);
          var inner = document.createElement('span'); inner.style.setProperty('--i', i++);
          inner.appendChild(n); w.appendChild(inner);
        }
      });
    }
    wrap(el);
  });
  // 단계 밖의 제목은 화면에 들어오면 한 번
  var moOnce = mos.filter(function (el) { return !el.closest('[data-live]'); });
  function showMo(el) { el.classList.add('on'); if (el.parentNode) el.parentNode.classList.add('mo-on'); }
  if (reduce || !('IntersectionObserver' in window)) moOnce.forEach(showMo);
  else {
    var mio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { showMo(e.target); mio.unobserve(e.target); } });
    }, { threshold: 0.3 });
    moOnce.forEach(function (el) { mio.observe(el); });
  }

  // 이렇게 써요 단계 — 화면에 가장 크게 들어온 단계만 아이콘이 영상으로 바뀌고 재생된다
  var steps = [].slice.call(document.querySelectorAll('[data-live]'));
  function updateSteps() {
    if (!steps.length) return;
    var vh = window.innerHeight, best = null, score = 0.55;
    steps.forEach(function (sec) {
      var r = sec.getBoundingClientRect();
      var seen = (Math.min(r.bottom, vh) - Math.max(r.top, 0)) / Math.min(r.height, vh);
      if (seen > score) { score = seen; best = sec; }
    });
    steps.forEach(function (sec) {
      var on = sec === best;
      if (sec.classList.contains('live') === on) return;
      sec.classList.toggle('live', on);
      var mo = sec.querySelector('[data-mo]');
      if (mo) { mo.classList.toggle('on', on); mo.parentNode.classList.toggle('mo-on', on); }
      var v = sec.querySelector('video');
      if (!v) return;
      if (on && !reduce) { try { v.currentTime = 0; } catch (e) {} var p = v.play(); if (p && p.catch) p.catch(function () {}); }
      else v.pause();
    });
  }

  // 헤더 — 맨 위에선 투명, 조금이라도 내리면 흰 바탕
  var gnb = document.querySelector('.gnb');
  var ticking = false;
  function frame() {
    ticking = false;
    if (gnb) gnb.classList.toggle('solid', window.scrollY > 8);
    updateSteps();
  }
  function request() { if (!ticking) { ticking = true; window.requestAnimationFrame(frame); } }
  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', request);
  window.addEventListener('load', request);
  frame();

  // 풀페이지 (이렇게 써요, 넓은 화면) — 휠 한 번·방향키 한 번에 다음 화면으로 스르륵. 화면보다 긴 구역 안에서는 그냥 스크롤
  var pager = document.documentElement.classList.contains('snap') && !reduce && window.matchMedia('(min-width: 900px) and (min-height: 680px)').matches;
  if (pager) {
    var secs = [].slice.call(document.querySelectorAll('.snap-sec'));
    var foot = document.querySelector('.footer');
    if (foot) secs.push(foot);
    var lock = 0, last = 0, lastAbs = 0;
    var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
    var glide = function (to) {
      var from = window.scrollY, start = performance.now(), dur = 750;
      lock = Date.now() + dur + 80;
      (function step(now) {
        var k = Math.min(1, (now - start) / dur);
        window.scrollTo(0, from + (to - from) * ease(k));
        if (k < 1) window.requestAnimationFrame(step);
      })(start);
    };
    var target = function (dir) {
      var y = window.scrollY, vh = window.innerHeight, max = document.documentElement.scrollHeight - vh;
      var cur = 0;
      secs.forEach(function (sec, i) { if (sec.offsetTop <= y + 2) cur = i; });
      var sec = secs[cur], top = sec.offsetTop, end = top + sec.offsetHeight;
      if (dir > 0) {
        if (end > y + vh + 2) return null;            // 긴 구역 — 끝까지 그냥 스크롤
        if (cur === secs.length - 1 || y >= max - 2) return null;
        return Math.min(secs[cur + 1].offsetTop, max);
      }
      if (y > top + 2) return sec.offsetHeight > vh + 2 ? null : top;  // 긴 구역은 맨 위까지 그냥 스크롤
      return cur > 0 ? secs[cur - 1].offsetTop : null;
    };
    window.addEventListener('wheel', function (e) {
      if (e.ctrlKey || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
      var now = Date.now(), abs = Math.abs(e.deltaY);
      var fresh = now - last > 160 || abs - lastAbs > 15;  // 트랙패드 관성 꼬리는 새 동작으로 치지 않는다
      last = now; lastAbs = abs;
      var to = target(e.deltaY > 0 ? 1 : -1);
      if (to === null) return;
      e.preventDefault();
      if (now < lock || !fresh) return;
      glide(to);
    }, { passive: false });
    // 아래 카드의 단계 링크 — 그 단계 화면으로 스르륵
    document.querySelectorAll('a[href^="#step-"]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        var target = document.querySelector(link.getAttribute('href'));
        if (!target) return;
        e.preventDefault();
        glide(target.offsetTop);
        history.replaceState(null, '', link.getAttribute('href'));
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey || /input|textarea|select/i.test(e.target.tagName)) return;
      if (e.key === ' ' && e.target.closest && e.target.closest('a, button, summary, [tabindex]')) return;  // 버튼·링크 위의 스페이스는 원래 동작대로
      var dir = { ArrowDown: 1, PageDown: 1, ' ': e.shiftKey ? -1 : 1, ArrowUp: -1, PageUp: -1 }[e.key];
      if (!dir) return;
      var to = target(dir);
      if (to === null) return;
      e.preventDefault();
      if (Date.now() >= lock) glide(to);
    });
  }

  // 목록이 비어 있으면 머리 긁는 응댕이
  document.querySelectorAll('.post-grid').forEach(function (grid) {
    var empty = grid.parentNode.querySelector('.empty');
    if (empty && !grid.querySelector('.post-card')) { grid.hidden = true; empty.hidden = false; }
  });

  // 이야기 분류 칩
  document.querySelectorAll('[data-filter]').forEach(function (bar) {
    var root = bar.parentNode;
    var cards = root.querySelectorAll('.post-card');
    var empty = root.querySelector('.empty');
    bar.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        var cat = b.getAttribute('data-cat');
        bar.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        var shown = 0;
        cards.forEach(function (c) { var on = cat === 'all' || c.getAttribute('data-cat') === cat; c.hidden = !on; if (on) shown++; });
        if (empty) empty.hidden = shown > 0;
      });
    });
  });

  // 새 글 표시 — 올린 날부터 14일 동안
  var today = new Date();
  document.querySelectorAll('[data-new]').forEach(function (el) {
    var d = new Date(el.getAttribute('data-new') + 'T00:00:00+09:00');
    if (today - d >= 0 && today - d < 14 * 864e5) el.hidden = false;
  });

  // 들어올 때 살짝 떠오름
  var rises = document.querySelectorAll('.rise');
  if (reduce || !('IntersectionObserver' in window)) {
    rises.forEach(function (el) { el.classList.add('in'); });
  } else {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); ro.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    rises.forEach(function (el) { ro.observe(el); });
  }
})();
