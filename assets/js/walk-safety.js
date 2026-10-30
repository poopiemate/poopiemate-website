/* 산책 안전도 계산기 (/walk-safety-index/)
   계산은 앱 supabase/functions/_shared/outdoorSafetyRisk.ts를 그대로 옮긴 것 — 앱 쪽을 바꾸면 여기도 같이 바꾼다.
   날씨는 앱과 같은 Open-Meteo 시간별 체감온도·강수 확률. */
(function () {
  var root = document.querySelector('[data-walk-calc]');
  if (!root) return;

  var RAIN = 40;
  var profile = { size: 'medium', ageGroup: 'adult', isBrachycephalic: false, bodyCondition: 'normal', coatType: 'normal',
    coldAcclimated: false, heatSensitive: false, hasHeartOrRespiratoryCondition: false };

  // ── 앱과 같은 계산 ─────────────────────────────────────────────
  function baseLevel(t, size) {
    if (t === null) return 2;
    if (t >= 35) return 5;
    if (t >= 32) return 4;
    if (t >= 29) return size === 'large' ? 4 : 3;
    if (t >= 24) return size === 'large' ? 3 : 2;
    if (t >= 16) return 1;
    if (t >= 10) return size === 'small' ? 2 : 1;
    if (t >= 4) return size === 'large' ? 2 : 3;
    if (t >= -4) return size === 'large' ? 3 : 4;
    if (t >= -9) return size === 'small' ? 5 : 4;
    return 5;
  }
  var MOD = {
    brachycephalic: '단두종', obese: '비만', overweight: '과체중', ageHot: '나이', heatSensitive: '더위 민감', heavyCoatHot: '두꺼운 털', heart: '심장·호흡기',
    small: '소형견', ageCold: '나이', shortCoat: '짧은 털', heavyCoatCold: '이중모', coldAcclimated: '추위 적응', wet: '젖은 날씨'
  };
  function breakdown(apparent, rainProb, p) {
    var t = apparent === null ? null : Math.round(apparent);
    var hot = t !== null && t >= 24, cold = t !== null && t <= 10;
    var base = baseLevel(t, p.size), m = [];
    if (hot) {
      if (p.isBrachycephalic) m.push(['brachycephalic', 1]);
      if (p.bodyCondition === 'obese') m.push(['obese', 1]);
      if (p.bodyCondition === 'overweight') m.push(['overweight', 0.5]);
      if (p.ageGroup !== 'adult') m.push(['ageHot', 1]);
      if (p.heatSensitive) m.push(['heatSensitive', 1]);
      if (p.coatType === 'heavy' || p.coatType === 'double') m.push(['heavyCoatHot', 0.5]);
      if (p.hasHeartOrRespiratoryCondition) m.push(['heart', 1]);
    }
    if (cold) {
      if (p.size === 'small') m.push(['small', 1]);
      if (p.ageGroup !== 'adult') m.push(['ageCold', 0.5]);
      if (p.coatType === 'short') m.push(['shortCoat', 1]);
      if (p.coatType === 'double' || p.coatType === 'heavy') m.push(['heavyCoatCold', -1]);
      if (p.coldAcclimated) m.push(['coldAcclimated', -1]);
      if (rainProb >= RAIN) m.push(['wet', 1]);
    }
    var sum = base + m.reduce(function (s, x) { return s + x[1]; }, 0);
    return { t: t, base: base, mods: m, level: Math.min(5, Math.max(1, Math.round(sum))), hot: hot, season: hot ? 'hot' : cold ? 'cold' : 'mild' };
  }
  function copy(level, hot) {
    if (level === 1) return ['산책하기 최고예요', '평소 루틴대로 다녀와도 좋은 조건이에요.', ['평소 산책 루틴대로 다녀오기']];
    if (level === 2) return ['산책하기 괜찮아요', '최상의 조건은 아니지만 무리 없는 날씨예요.', ['물을 챙기고 평소보다 조금 관찰하기']];
    if (level === 3) return ['주의해서 짧게 다녀오세요', '노령견, 어린 강아지, 단두종, 비만견은 산책 시간을 줄이는 게 좋아요.', ['15~20분 안쪽으로 짧게 다녀오기', '헐떡임이나 떨림이 보이면 바로 귀가하기']];
    if (level === 4) return hot
      ? ['짧게 다녀오세요', '꼭 나가야 한다면 배변 후 바로 귀가하고, 그늘 위주로 이동하세요.', ['물을 챙기기', '그늘 위주로 짧게 다녀오기', '배변 후 바로 귀가하기', '격한 운동 피하기']]
      : ['짧게 다녀오세요', '꼭 나가야 한다면 배변 후 바로 귀가하고, 방한 준비를 하세요.', ['옷 챙겨서 짧게 다녀오기', '배변 후 바로 귀가하기', '발바닥 보호하기']];
    return hot
      ? ['배변만 빠르게 하고 귀가하세요', '폭염 수준이에요. 배변만 빠르게 하고 바로 들어오세요.', ['그늘 위주로 5분 이내로 다녀오기', '물을 챙기기', '아스팔트 화상 주의하기', '헐떡임이 심하면 바로 귀가하기']]
      : ['배변만 빠르게 하고 귀가하세요', '혹한 수준이에요. 배변만 빠르게 하고 바로 들어오세요.', ['옷 입혀서 5분 이내로 다녀오기', '발바닥 보호하기', '떨림이 보이면 바로 귀가하기']];
  }

  // ── 날씨 ───────────────────────────────────────────────────────
  var wx = null, place = '서울';
  var $ = function (s) { return root.querySelector(s); };
  var citySel = $('[data-city]');

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

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function load(lat, lon, name) {
    place = name;
    $('[data-wx]').textContent = name + ' 날씨를 불러오는 중이에요…';
    var u = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat + '&longitude=' + lon +
      '&hourly=temperature_2m,apparent_temperature,precipitation_probability&timezone=auto&forecast_days=2';
    fetch(u).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
      // 예보 지역 시각의 지금 시각(정시)부터 — 앱 processWeather와 같은 방식
      var now = new Date(Date.now() + (d.utc_offset_seconds || 0) * 1000);
      var iso = now.getUTCFullYear() + '-' + pad(now.getUTCMonth() + 1) + '-' + pad(now.getUTCDate()) + 'T' + pad(now.getUTCHours()) + ':00';
      var h = d.hourly, i0 = h.time.findIndex(function (t) { return t >= iso; });
      if (i0 < 0) throw 0;
      wx = [];
      for (var i = i0; i < Math.min(h.time.length, i0 + 24); i++) {
        var a = h.apparent_temperature[i]; if (a == null) a = h.temperature_2m[i];
        wx.push({ time: h.time[i], hour: +h.time[i].slice(11, 13), day: h.time[i].slice(0, 10), t: a, rain: h.precipitation_probability[i] || 0 });
      }
      render();
    }).catch(function () {
      wx = null;
      $('[data-wx]').textContent = '날씨를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.';
      render();
    });
  }
  function loadCity() {
    var v = citySel.value.split(',');
    load(v[0], v[1], citySel.options[citySel.selectedIndex].text);
  }
  citySel.addEventListener('change', loadCity);
  $('[data-loc]').addEventListener('click', function () {
    if (!navigator.geolocation) return;
    $('[data-wx]').textContent = '위치를 확인하는 중이에요…';
    navigator.geolocation.getCurrentPosition(function (pos) {
      load(pos.coords.latitude.toFixed(3), pos.coords.longitude.toFixed(3), '내 위치');
    }, function () {
      $('[data-wx]').textContent = '위치를 쓸 수 없어서 도시로 볼게요.';
      loadCity();
    }, { timeout: 8000, maximumAge: 600000 });
  });

  // ── 그리기 ─────────────────────────────────────────────────────
  var SIZE = { small: '소형견', medium: '중형견', large: '대형견' };
  var SEASON = { hot: '더운 날', cold: '추운 날', mild: '선선한 날' };
  function fmt(n) { return (n > 0 ? '+' : '−') + String(Math.abs(n)); }

  function render() {
    var table = document.querySelector('[data-table]');
    if (!wx) {
      $('[data-level]').textContent = '–';
      return;
    }
    var now = wx[0], r = breakdown(now.t, now.rain, profile), c = copy(r.level, r.hot);
    $('[data-wx]').innerHTML = '<b>' + place + '</b> 지금 체감 <b>' + r.t + '°</b> · 강수 확률 <b>' + now.rain + '%</b>';
    $('[data-ctx]').textContent = '지금 ' + place + ' · 체감 ' + r.t + '° · ' + SIZE[profile.size] + ' · ' + SEASON[r.season] + ' 기준';
    var card = $('[data-card]');
    card.className = 'cr-card ws lv' + r.level;
    $('[data-level]').textContent = r.level;
    $('[data-title]').textContent = c[0];
    $('[data-msg]').textContent = c[1];
    miniSet('레벨 ' + r.level, c[0], 'var(--s' + r.level + ')');
    $('[data-acts]').innerHTML = c[2].map(function (a) { return '<li>' + a + '</li>'; }).join('');
    $('[data-formula]').innerHTML = '<span class="f-base">표 ' + r.base + '</span>' +
      r.mods.map(function (m) { return '<span class="f-mod' + (m[1] < 0 ? ' dn' : '') + '">' + MOD[m[0]] + ' ' + fmt(m[1]) + '</span>'; }).join('') +
      '<span class="f-eq">= 레벨 ' + r.level + '</span>';

    // 오늘 남은 시간 + 내일 아침까지 24시간
    var best = null;
    $('[data-strip]').innerHTML = wx.map(function (w, i) {
      var b = breakdown(w.t, w.rain, profile);
      var day = w.hour >= 6 && w.hour <= 21;  // 사람이 산책 나가는 시간만 추천
      if (day && (!best || b.level < best.level)) best = { level: b.level, hour: w.hour, tomorrow: w.day !== wx[0].day };
      return '<div class="h lv' + b.level + '" title="' + w.hour + '시 체감 ' + Math.round(w.t) + '° · 강수 ' + w.rain + '%"><i style="--lv:' + b.level + '"></i><small>' +
        (i === 0 ? '지금' : i % 3 === 0 ? w.hour + '시' : '') + '</small></div>';
    }).join('');
    $('[data-best]').innerHTML = best
      ? '가장 좋은 시간: <b>' + (best.tomorrow ? '내일 ' : '') + best.hour + '시</b> (레벨 ' + best.level + ')'
      : '';

    // 기준표에 지금 칸 표시
    if (table) {
      table.querySelectorAll('.now').forEach(function (el) { el.classList.remove('now'); });
      var rows = table.querySelectorAll('tbody tr');
      for (var i = 0; i < rows.length; i++) {
        var th = +rows[i].dataset.t;
        if (r.t >= th || i === rows.length - 1) {
          rows[i].classList.add('now');
          var cell = rows[i].querySelector('[data-s="' + profile.size + '"]');
          if (cell) cell.classList.add('now');
          break;
        }
      }
    }
  }

  root.addEventListener('click', function (e) {
    var b = e.target.closest('.opt');
    if (!b) return;
    var k = b.dataset.k, v = b.dataset.v;
    profile[k] = v === 'true' ? true : v === 'false' ? false : v;
    root.querySelectorAll('.opt[data-k="' + k + '"]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    render();
  });

  loadCity();
})();
