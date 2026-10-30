/* 강아지 똥 상태 체크 (/poop-condition-guide/) — 색깔·굳기·같이 보이는 것으로 4단계 판단 (src/tools.py의 표와 같은 기준) */
(function () {
  var root = document.querySelector('[data-poop-check]');
  if (!root) return;

  // 1 괜찮아요 · 2 지켜봐요 · 3 병원 상담 · 4 바로 병원
  var COLOR = {
    brown: [1, '갈색이에요. 건강한 응가의 기본색이에요.'],
    yellow: [2, '노란색·주황색은 사료를 바꿨거나 소화가 빨리 된 날 나올 수 있어요.'],
    green: [2, '초록색은 풀이나 사료·간식 색소 때문일 수 있어요.'],
    red: [3, '피가 섞였어요. 대장이나 항문 쪽 출혈일 수 있어요.'],
    black: [4, '끈적한 검은 변은 위·소장 출혈 신호일 수 있어요.'],
    gray: [3, '회색·흰색은 담즙이나 췌장 쪽 이상일 수 있어요.']
  };
  var FIRM = {
    1: [2, '딱딱한 알갱이는 변비 신호예요. 물 마시는 양과 산책량을 늘려 보세요.'],
    2: [1, '마디 있는 통나무 모양, 황금똥 굳기예요.'],
    3: [1, '촉촉한 통나무 모양, 정상 범위예요.'],
    4: [2, '무른 변이에요. 사료·간식 변화나 스트레스 때문일 수 있어요.'],
    5: [2, '무른 변이에요. 사료·간식 변화나 스트레스 때문일 수 있어요.'],
    6: [2, '진흙 같은 설사예요. 물을 충분히 챙겨 주세요.'],
    7: [2, '물설사예요. 탈수되지 않게 물을 꼭 챙겨 주세요.']
  };
  var COPY = {
    1: ['괜찮아요', '건강한 응가예요', '오늘처럼만 싸면 돼요. 평소 상태를 알아 두면 달라졌을 때 바로 알아챌 수 있어요.'],
    2: ['지켜봐요', '하루 정도 지켜봐요', '한두 번이고 잘 먹고 잘 논다면 하루 정도 지켜봐도 괜찮은 경우가 많아요. 같은 상태가 이어지면 병원에 상담하세요.'],
    3: ['병원 상담', '병원에 상담해 보세요', '급하진 않아도 동물병원에 상담해 보는 게 좋아요. 응가 사진을 찍거나 조금 챙겨 가면 진료에 도움이 돼요.'],
    4: ['바로 병원', '바로 병원에 가세요', '기다리지 말고 바로 동물병원에 가세요. 응가 사진을 찍어 가면 진료에 도움이 돼요.']
  };

  var state = { color: null, firm: null, extra: {} };
  var $ = function (s) { return root.querySelector(s); };
  var card = $('[data-card]'), empty = $('[data-empty]');

  // 폰 — 고르는 동안 결과 카드가 화면 밖이면 아래에 결과 한 줄을 띄운다
  var mini = document.querySelector('[data-mini]'), miniReady = false, cardSeen = false, formSeen = false;
  function miniShow() { if (mini) mini.classList.toggle('on', miniReady && formSeen && !cardSeen); }
  if (mini && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.target === root.querySelector('.ck-result')) cardSeen = e.isIntersecting; else formSeen = e.isIntersecting; }); miniShow(); })
      .observe(root.querySelector('.ck-result'));
    new IntersectionObserver(function (es) { formSeen = es[0].isIntersecting; miniShow(); }).observe(root.querySelector('.ck-form'));
  }
  function miniSet(label, text, color) {
    if (!mini) return;
    mini.querySelector('[data-mini-l]').textContent = label;
    mini.querySelector('[data-mini-t]').textContent = text;
    mini.style.setProperty('--c', color);
    miniReady = true; miniShow();
  }

  function press(group, btn) {
    root.querySelectorAll('[data-' + group + ']').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
  }

  function judge() {
    var lv = 1, why = [];
    var c = COLOR[state.color], f = FIRM[state.firm], x = state.extra;
    lv = Math.max(c[0], f[0]);
    why.push(c[1]); why.push(f[1]);
    var loose = state.firm >= 6;
    if (state.color === 'red' && loose) { lv = 4; why.push('피가 섞인 설사는 바로 진료가 필요해요.'); }
    if (x.mucus) { lv = Math.max(lv, 2); why.push('점액은 장이 자극을 받았다는 신호예요.'); }
    if (x.specks) { lv = Math.max(lv, 3); why.push('흰 쌀알 같은 알갱이는 기생충일 수 있어요. 검사를 받아 보세요.'); }
    if (x.long && lv >= 2) { lv = Math.max(lv + 1, 3); why.push('하루 넘게 이어지면 지켜보기보다 상담이 좋아요.'); }
    if (x.vomit) { lv = Math.max(lv, loose || lv >= 2 ? 4 : 3); why.push('구토를 같이 하면 탈수가 빨리 올 수 있어요.'); }
    if (x.weak) { lv = Math.max(lv + 1, 3); why.push('기운이 없거나 밥을 안 먹는 건 응가보다 더 중요한 신호예요.'); }
    if (x.age && loose) { lv = Math.max(lv, 3); why.push('아기 강아지와 노령견은 설사로 탈수가 더 빨리 와요.'); }
    return { lv: Math.min(lv, 4), why: why };
  }

  function render() {
    var ready = state.color && state.firm;
    empty.hidden = !!ready;
    card.hidden = !ready;
    if (!ready) { miniReady = false; miniShow(); return; }
    var r = judge();
    card.className = 'cr-card v' + r.lv;
    $('[data-ill]').src = '/assets/img/poop/' + (state.color === 'brown' ? 'firm-' + state.firm : 'color-' + state.color) + '.webp?v=3';
    $('[data-level]').textContent = COPY[r.lv][0];
    $('[data-title]').textContent = r.lv === 1 && state.firm === 2 && state.color === 'brown' ? '황금똥이에요!' : COPY[r.lv][1];
    $('[data-msg]').textContent = COPY[r.lv][2];
    $('[data-why]').innerHTML = r.why.map(function (w) { return '<li>' + w + '</li>'; }).join('');
    miniSet(COPY[r.lv][0], $('[data-title]').textContent, ['', 'var(--s1)', 'var(--s3)', 'var(--s4)', 'var(--s5)'][r.lv]);
  }

  root.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.color) { state.color = b.dataset.color; press('color', b); }
    else if (b.dataset.firm) { state.firm = +b.dataset.firm; press('firm', b); }
    else if (b.dataset.extra) {
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', String(on));
      state.extra[b.dataset.extra] = on;
    } else if (b.hasAttribute('data-reset')) {
      state = { color: null, firm: null, extra: {} };
      root.querySelectorAll('[aria-pressed]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else return;
    render();
  });
})();
