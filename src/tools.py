"""검색으로 들어오는 사람을 위한 도구 페이지 — 똥 상태 체크(/poop-condition-guide/)와 산책 안전도 계산기(/walk-safety-index/).

옛 가이드 글과 같은 주소를 써서 이미 쌓인 검색 노출을 그대로 잇는다. 한국어만 도구로 바꾸고, 영어는 옛 글 그대로.
산책 안전도 계산은 앱의 supabase/functions/_shared/outdoorSafetyRisk.ts를 assets/js/walk-safety.js로 그대로 옮겼다 — 앱 쪽을 바꾸면 같이 바꾼다.
"""
from html import escape

TOOL_SLUGS = ('poop-condition-guide', 'walk-safety-index')


def _crumb(title):
    return (f'<p class="post-meta"><a href="/">응가메이트</a> › <a href="/guide/">강아지 가이드</a> › {title}</p>')


def _breadcrumb_ld(slug, name):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': '응가메이트', 'item': 'https://poopiemate.com/'},
        {'@type': 'ListItem', 'position': 2, 'name': '강아지 가이드', 'item': 'https://poopiemate.com/guide/'},
        {'@type': 'ListItem', 'position': 3, 'name': name, 'item': f'https://poopiemate.com/{slug}/'}]}


def _app_ld(slug, name, desc):
    return {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': name, 'description': desc, 'url': f'https://poopiemate.com/{slug}/',
            'applicationCategory': 'HealthApplication', 'operatingSystem': 'Web', 'inLanguage': 'ko', 'isAccessibleForFree': True,
            'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'KRW'}, 'publisher': {'@type': 'Organization', 'name': '응가메이트'}}


# ═════════════════════════════════════════════════════════ 똥 그림 — ChatGPT 응가 시트를 잘라 쓴다 (src/poop_images.py)
POOP_V = '3'  # 응가 그림을 다시 만들면 올린다 (브라우저 캐시)


def poop_img(name, alt=''):
    return f'<img class="poop-ill" src="/assets/img/poop/{name}.webp?v={POOP_V}" alt="{alt}" width="120" height="90" loading="lazy">'


# 응가 색깔 — key(그림 color-<key>.webp), 이름, 판단 단계(1 괜찮아요 · 2 지켜봐요 · 3 병원 상담 · 4 바로 병원), 설명
POOP_COLORS = [
    ('brown', '갈색 · 초콜릿색', 1, '건강한 응가의 기본색이에요. 굳기까지 적당하면 흔히 말하는 황금똥이에요.'),
    ('yellow', '노란색 · 주황색', 2, '사료를 바꿨거나 소화가 빨리 된 날 나올 수 있어요. 2~3일 넘게 이어지면 간·담낭 쪽 확인이 필요할 수 있어요.'),
    ('green', '초록색', 2, '풀을 많이 먹었거나 사료·간식 색소 때문일 수 있어요. 며칠 이어지면 상담하세요.'),
    ('red', '피가 섞임 · 선홍색 줄', 3, '대장이나 항문 쪽 출혈일 수 있어요. 설사와 같이 나오거나 양이 많으면 바로 병원에 가세요.'),
    ('black', '검은색 · 끈적한 타르', 4, '위나 소장 쪽 출혈 신호일 수 있어요. 철분 영양제를 먹지 않았다면 바로 병원에 가세요.'),
    ('gray', '회색 · 흰색 · 기름짐', 3, '담즙이나 췌장 쪽 이상일 수 있어요. 기름져 보이고 양이 많으면 더 주의하세요.'),
]
POOP_EXTRAS_CHART = [
    ('mucus', '젤리 같은 점액', 2, '장이 자극을 받았다는 신호예요. 한 번이면 지켜보고, 계속 나오면 상담하세요.'),
    ('specks', '흰 쌀알 같은 알갱이', 3, '기생충(촌충) 마디일 수 있어요. 응가를 챙겨 동물병원에서 검사를 받아 보세요.'),
]
# 굳기 점수 — 수의사들이 쓰는 1~7 대변 점수표(Fecal Scoring Chart)를 쉬운 말로
FIRMNESS = [
    (1, '딱딱한 알갱이', '마르고 단단한 조각. 힘을 많이 줘요', 2, '변비 신호'),
    (2, '황금똥', '모양이 또렷하고 단단해요. 집어도 모양이 그대로예요', 1, '가장 이상적'),
    (3, '촉촉한 통나무', '표면이 촉촉하고 집으면 자국이 조금 남아요', 1, '정상 범위'),
    (4, '물렁한 무더기', '모양이 무너지고 집으면 바닥에 남아요', 2, '무른 변'),
    (5, '모양 없는 무더기', '형태는 조금 있지만 집기 어려워요', 2, '무른 변'),
    (6, '진흙 같은 설사', '질감은 있지만 모양이 없어요', 2, '설사'),
    (7, '물설사', '물처럼 퍼지고 모양이 전혀 없어요', 2, '설사'),
]
VERDICT_LABEL = {1: '괜찮아요', 2: '지켜봐요', 3: '병원 상담', 4: '바로 병원'}
# 하루 배변 횟수 카드 — 포즈, 이름, 나이, 최소~최대 횟수, 설명. 응가 그림 5칸 중 최소까지 진하게, 최대까지 옅게
POOP_COUNTS = [
    ('age-puppy', '아기 강아지', '6개월 미만', 3, 5, '밥을 자주 먹고 소화가 빨라서 먹고 나서 곧 싸요.'),
    ('age-adult', '성견', '1~7살', 1, 3, '아침·저녁 산책 때 한 번씩이 가장 흔해요.'),
    ('age-senior', '노령견', '7살 이상', 1, 2, '활동량이 줄면 횟수도 줄어요. 이틀 넘게 안 싸면 상담하세요.'),
]
POOP_FAQ = [
    ('강아지 황금똥은 어떤 똥인가요?', '초콜릿 같은 갈색에, 마디가 살짝 있는 통나무 모양이고, 집어 올려도 모양이 유지될 만큼 적당히 단단한 똥이에요. 대변 점수표로는 2점(1~7점 중)이에요.'),
    ('강아지 하루 배변 횟수는 몇 번이 정상인가요?', '성견은 하루 1~3번이 흔해요. 6개월 미만 강아지는 먹는 횟수만큼 하루 3~5번, 노령견은 1~2번으로 줄기도 해요. 횟수보다 평소와 달라졌는지가 더 중요해요.'),
    ('강아지 똥이 회색이거나 흰색이면 괜찮나요?', '회색·흰색 똥은 담즙이나 췌장 쪽 이상일 수 있어서 병원 상담을 권해요. 흰 쌀알 같은 알갱이가 보이면 기생충 검사를 받아 보세요.'),
    ('혈변이나 검은 변을 봤을 때는 어떻게 해야 하나요?', '끈적한 검은 변은 위·소장 출혈 신호일 수 있어 바로 병원에 가세요. 선홍색 피가 조금 묻은 정도라도 반복되거나 설사와 같이 나오면 병원 상담을 권해요.'),
    ('설사를 한 번 했는데 병원에 가야 하나요?', '한두 번이고 잘 먹고 잘 논다면 하루 정도 지켜보는 경우가 많아요. 하루 넘게 이어지거나, 피가 섞이거나, 구토를 같이 하거나, 기운이 없으면 병원에 가세요. 아기 강아지와 노령견은 더 빨리 데려가는 게 좋아요.'),
]


def _swatch_btn(key, name, group):
    return (f'<button type="button" class="pick" data-{group}="{key}" aria-pressed="false">'
            f'{poop_img("color-" + key)}<span>{name}</span></button>')


def poop_tool(page, faq_block, faq_ld, cta_band, ASSET_V):
    slug, name = 'poop-condition-guide', '강아지 똥 상태 체크'
    title = '강아지 똥 상태 체크 — 황금똥 기준·응가 색깔 차트 | 응가메이트'
    desc = '오늘 강아지 응가, 괜찮을까요? 색깔과 굳기를 고르면 바로 알려줘요. 황금똥 기준, 응가 색깔 차트(회색·검은색·혈변·초록색), 굳기 1~7점 차트, 하루 배변 횟수까지.'
    colors = ''.join(_swatch_btn(k, n, 'color') for k, n, _, _ in POOP_COLORS)
    firm = ''.join(f'<button type="button" class="pick" data-firm="{s}" aria-pressed="false">{poop_img(f'firm-{s}')}<span><b>{s}</b> {n}</span></button>' for s, n, _, _, _ in FIRMNESS)
    extras = [('mucus', '젤리 같은 점액'), ('specks', '흰 쌀알 알갱이'), ('vomit', '구토도 했어요'), ('weak', '기운이 없거나 밥을 안 먹어요'),
              ('long', '하루 넘게 이어져요'), ('age', '6개월 미만 아기 · 노령견이에요')]
    extra_btns = ''.join(f'<button type="button" class="tag" data-extra="{k}" aria-pressed="false">{n}</button>' for k, n in extras)

    color_cards = ''.join(
        f'<article class="pc-card"><div class="pc-ill">{poop_img("color-" + k, n)}</div><span class="vtag v{lv}">{VERDICT_LABEL[lv]}</span>'
        f'<h3>{n}</h3><p>{escape(d)}</p></article>' for k, n, lv, d in POOP_COLORS + POOP_EXTRAS_CHART)
    cnt_cards = ''.join(
        f'<div class="cnt"><div class="cnt-top"><img src="/assets/img/mascot/{pose}.webp" alt="" loading="lazy"></div>'
        f'<div class="cnt-in"><p class="cnt-h"><b>{name}</b><small>{age}</small></p>'
        f'<div class="cnt-dots" aria-hidden="true">' + ''.join(f'<i class="{"on" if k <= lo else "mid" if k <= hi else ""}"></i>' for k in range(1, 6)) + '</div>'
        f'<strong>하루 {lo}~{hi}번</strong><p>{d}</p></div></div>'
        for pose, name, age, lo, hi, d in POOP_COUNTS)
    firm_rows = ''.join(
        f'<li class="{"ideal" if s == 2 else ""}"><div class="fs-ill">{poop_img(f'firm-{s}', n)}</div><b class="fs-n">{s}</b>'
        f'<div class="fs-t"><strong>{n}</strong><span>{d}</span></div><span class="vtag v{lv}">{tag}</span></li>'
        for s, n, d, lv, tag in FIRMNESS)

    body = f'''
<section class="tool-hero t-poop"><div class="wrap-tool">
{_crumb(name)}
<div class="th-grid">
<div class="th-text"><h1 class="post-h1 th-h1">오늘 응가, 괜찮을까?<br><em>강아지 똥 상태 체크</em></h1>
<p class="th-lead">색깔과 굳기만 고르면 황금똥인지, 지켜봐도 되는지, 병원에 가야 하는지 바로 알려줘요.</p>
<nav class="th-jump" aria-label="이 페이지에서"><a href="#check">상태 체크</a><a href="#colors">응가 색깔 차트</a><a href="#firmness">굳기 차트</a><a href="#count">하루 배변 횟수</a></nav></div>
<div class="th-art"><img class="th-mascot" src="/assets/img/mascot/magnify.webp" alt="돋보기로 살펴보는 응댕이" width="390" height="387"></div>
</div></div></section>

<section class="tool-sec" id="check"><div class="wrap-tool">
<div class="checker" data-poop-check>
<div class="ck-form">
<div class="ck-step"><h2 class="ck-h"><i>1</i>무슨 색이에요?</h2><div class="pick-grid c3">{colors}</div></div>
<div class="ck-step"><h2 class="ck-h"><i>2</i>굳기는 어때요?</h2><div class="pick-grid c4 firm">{firm}</div></div>
<div class="ck-step"><h2 class="ck-h"><i>3</i>같이 보이는 게 있나요? <small>여러 개 골라도 돼요</small></h2><div class="tags">{extra_btns}</div></div>
</div>
<aside class="ck-result" id="check-result" aria-live="polite">
<div class="cr-empty" data-empty><img src="/assets/img/mascot/sit.webp" alt="" width="120" height="120"><b>색깔과 굳기를 골라 주세요</b><p>고르는 대로 바로 결과가 바뀌어요.</p></div>
<div class="cr-card" data-card hidden>
<div class="cr-head"><img class="cr-ill" data-ill src="/assets/img/poop/color-brown.webp?v={POOP_V}" alt="" width="240" height="180">
<span class="cr-level" data-level></span>
<h3 class="cr-title" data-title></h3>
<p class="cr-msg" data-msg></p></div>
<div class="cr-body"><p class="cr-sub">이렇게 봤어요</p>
<ul class="cr-why" data-why></ul>
<div class="cr-app"><b>매일 기록하면 변화를 바로 알아채요</b><p>응가메이트는 응가 상태와 시간을 가족과 같이 남겨요. 병원에서 “언제부터 어땠는지” 바로 보여줄 수 있어요.</p>
<a class="btn-app" href="/download/">응가메이트 무료로 받기</a></div>
<button type="button" class="cr-reset" data-reset>처음부터 다시</button>
</div></div>
</aside>
</div>
<a class="mini" href="#check-result" data-mini><i data-mini-l></i><b data-mini-t></b><span>결과 보기</span></a>
<p class="tool-note">이 체크는 일반적으로 알려진 기준을 정리한 참고 정보이고, 진단이 아니에요. 걱정되면 언제든 수의사와 상담하세요.</p>
</div></section>

<section class="tool-sec alt" id="colors"><div class="wrap-tool">
<p class="label">응가 색깔 차트</p><h2 class="h2">색깔로 보는 <em>강아지 똥 상태</em></h2>
<p class="sec-lead">갈색이 아니라고 다 위험한 건 아니에요. 색깔별로 무슨 뜻인지, 언제 병원에 가야 하는지 정리했어요.</p>
<div class="pc-grid">{color_cards}</div>
</div></section>

<section class="tool-sec" id="firmness"><div class="wrap-tool">
<p class="label">굳기 차트</p><h2 class="h2">황금똥은 <em>1~7점 중 2점</em></h2>
<p class="sec-lead">동물병원에서 쓰는 대변 점수표(Fecal Scoring Chart)를 쉬운 말로 옮겼어요. 2~3점이면 건강한 범위예요.</p>
<ol class="fs-list">{firm_rows}</ol>
</div></section>

<section class="tool-sec alt" id="count"><div class="wrap-tool">
<p class="label">하루 배변 횟수</p><h2 class="h2">하루에 <em>몇 번</em> 싸면 정상일까?</h2>
<p class="sec-lead">보통 밥 먹는 횟수와 비슷해요. 숫자보다 평소 우리 강아지 리듬에서 벗어났는지가 더 중요해요.</p>
<div class="cnt-grid">
{cnt_cards}
</div>
<a class="more-in" href="/potty-interval/">배변 텀과 하루 배변 횟수 더 알아보기 →</a>
</div></section>

<section class="tool-sec" id="vet"><div class="wrap-tool">
<div class="vet-box">
<div><p class="label on-dark">이럴 땐 바로 병원</p><h2 class="h2">기다리지 말고<br>동물병원에 가세요</h2></div>
<ul>
<li>끈적한 검은 변(타르변)을 봤어요</li>
<li>피가 섞인 설사를 해요</li>
<li>설사와 구토를 같이 해요</li>
<li>기운이 없고 밥을 안 먹어요</li>
<li>아기 강아지나 노령견이 물설사를 해요</li>
<li>힘을 주는데 하루 넘게 아무것도 안 나와요</li>
</ul>
</div>
</div></section>

{faq_block('ko', POOP_FAQ)}
{cta_band('ko')}
<script src="/assets/js/poop-check.js?v={ASSET_V}" defer></script>
'''
    ld = (_breadcrumb_ld(slug, name), _app_ld(slug, name, desc), faq_ld(POOP_FAQ))
    head = f'<link rel="stylesheet" href="/assets/css/tools.css?v={ASSET_V}">\n'
    return page('ko', None, title, desc, body, '/assets/og/poopiemate-ko.jpg', ko_path=f'/{slug}/', en_path=f'/en/{slug}/', active='guide',
                og_type='website', ld=ld, extra_head=head,
                keywords='강아지 똥 상태, 강아지 황금똥, 강아지 응가 색깔, 강아지 변 색깔, 강아지 회색똥, 강아지 검은변, 강아지 혈변, 강아지 설사, 강아지 하루 배변 횟수, 강아지 대변 점수')


# ═════════════════════════════════════════════════════════ 산책 안전도 계산기
def base_level(t, size):
    """앱 outdoorSafetyRisk.ts baseLevelForTemperature와 같은 표."""
    if t >= 35: return 5
    if t >= 32: return 4
    if t >= 29: return 4 if size == 'large' else 3
    if t >= 24: return 3 if size == 'large' else 2
    if t >= 16: return 1
    if t >= 10: return 2 if size == 'small' else 1
    if t >= 4: return 2 if size == 'large' else 3
    if t >= -4: return 3 if size == 'large' else 4
    if t >= -9: return 5 if size == 'small' else 4
    return 5


TEMP_ROWS = [(35, '35° 이상'), (32, '32~34°'), (29, '29~31°'), (24, '24~28°'), (16, '16~23°'), (10, '10~15°'), (4, '4~9°'), (-4, '-4~3°'), (-9, '-9~-5°'), (-10, '-10° 이하')]
LEVELS = [(1, '위험 없음', '평소 루틴대로 산책해도 좋아요'), (2, '위험 낮음', '무리 없지만 물을 챙기고 관찰하기'), (3, '주의 필요', '단두종·노령견·어린 강아지는 짧게 다녀오기'),
          (4, '위험', '꼭 나가야 한다면 배변 후 바로 귀가하기'), (5, '매우 위험', '야외 장시간 활동 금지, 배변만 5분 이내로')]
WALK_FAQ = [
    ('산책 안전도는 어떻게 계산하나요?', '체감온도로 강아지 크기별 기본 단계를 정하고, 더운 날엔 단두종·비만·나이·두꺼운 털·더위 민감·심장/호흡기 질환을, 추운 날엔 소형견·짧은 털·나이·젖은 날씨를 더하거나 빼서 1~5단계로 알려줘요. 응가메이트 앱과 똑같은 계산식이에요.'),
    ('산책지수는 몇 단계부터 위험한가요?', '3단계부터는 주의가 필요해요. 4단계는 배변만 하고 바로 들어오고, 5단계는 5분 이내로 배변만 하는 게 좋아요.'),
    ('여름에 강아지 산책하기 좋은 시간은 언제인가요?', '기온과 자외선이 낮은 이른 아침이나 해가 진 뒤가 안전해요. 아스팔트에 손등을 5초 대 보고 뜨거우면 강아지 발바닥에도 위험해요. 이 계산기의 시간별 안전도에서 오늘 가장 좋은 시간을 바로 확인할 수 있어요.'),
    ('겨울 산책은 몇 도까지 괜찮나요?', '체감온도 10° 아래부터 소형견은 위험이 올라가요. 영하 5° 아래에선 소형견은 5단계예요. 이중모이거나 추위에 적응한 강아지는 한 단계 낮게 봐요.'),
    ('체감온도는 어디서 가져오나요?', '오픈 날씨 데이터(Open-Meteo)의 시간별 체감온도와 강수 확률을 써요. 위치는 이 페이지에서만 쓰고 저장하지 않아요.'),
]


def _opt(group, value, label, sub='', on=False):
    return (f'<button type="button" class="opt" data-k="{group}" data-v="{value}" aria-pressed="{"true" if on else "false"}">'
            f'<b>{label}</b>{f"<small>{sub}</small>" if sub else ""}</button>')


def walk_tool(page, faq_block, faq_ld, cta_band, ASSET_V):
    slug, name = 'walk-safety-index', '강아지 산책 안전도 계산기'
    title = '강아지 산책지수 계산기 — 오늘 산책해도 될까? | 응가메이트'
    desc = '우리 강아지 크기·나이·체형·털에 지금 체감온도와 비 소식을 더해 오늘 산책 안전도를 1~5단계로 계산해요. 오늘 산책하기 좋은 시간까지 알려주는 무료 산책지수 계산기.'
    cities = [('37.5665,126.978', '서울'), ('37.4563,126.7052', '인천'), ('37.2636,127.0286', '수원'), ('37.8813,127.7298', '춘천'), ('36.3504,127.3845', '대전'),
              ('35.8714,128.6014', '대구'), ('35.1595,126.8526', '광주'), ('35.5384,129.3114', '울산'), ('35.1796,129.0756', '부산'), ('33.4996,126.5312', '제주')]
    city_opts = ''.join(f'<option value="{v}">{n}</option>' for v, n in cities)
    rows = ''.join(f'<tr data-t="{t}"><th scope="row">{lab}</th>' + ''.join(f'<td class="lv{base_level(t, s)}" data-s="{s}">{base_level(t, s)}</td>' for s in ('small', 'medium', 'large')) + '</tr>'
                   for t, lab in TEMP_ROWS)
    legend = ''.join(f'<li><span class="lv{n}">{n}</span><div><b>{t}</b><small>{d}</small></div></li>' for n, t, d in LEVELS)

    body = f'''
<section class="tool-hero t-walk"><div class="wrap-tool">
{_crumb(name)}
<div class="th-grid">
<div class="th-text"><h1 class="post-h1 th-h1">오늘 산책해도 될까?<br><em>강아지 산책 안전도 계산기</em></h1>
<p class="th-lead">우리 강아지 몸·털·컨디션에 지금 체감온도와 비 소식을 더해 1~5단계로 알려줘요. 응가메이트 앱과 똑같은 계산식이에요.</p>
<nav class="th-jump" aria-label="이 페이지에서"><a href="#calc">계산하기</a><a href="#table">기준표</a><a href="#factors">가산 요인</a><a href="#levels">단계별 행동</a></nav></div>
<div class="th-art"><img class="th-mascot" src="/assets/img/mascot/leash.webp" alt="산책줄을 맨 응댕이" width="452" height="395"></div>
</div></div></section>

<section class="tool-sec" id="calc"><div class="wrap-tool">
<div class="checker" data-walk-calc>
<div class="ck-form">
<div class="ck-step"><h2 class="ck-h"><i>1</i>어디서 산책해요?</h2>
<div class="wx-row"><button type="button" class="btn-loc" data-loc><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l18-8-8 18-2-8z"/></svg>내 위치 날씨</button><label class="sel"><span class="sr">도시</span><select data-city>{city_opts}</select></label></div>
<p class="wx-now" data-wx>날씨를 불러오는 중이에요…</p>
</div>
<div class="ck-step"><h2 class="ck-h"><i>2</i>강아지 크기와 나이</h2>
<p class="q">크기 <small>몸무게 기준</small></p><div class="opts c3">{_opt('size', 'small', '소형견', '10kg 미만')}{_opt('size', 'medium', '중형견', '10~25kg', True)}{_opt('size', 'large', '대형견', '25kg 이상')}</div>
<p class="q">나이</p><div class="opts c3">{_opt('ageGroup', 'puppy', '아기 강아지', '6개월 미만')}{_opt('ageGroup', 'adult', '성견', '6개월~7살', True)}{_opt('ageGroup', 'senior', '노령견', '7살 이상')}</div>
</div>
<div class="ck-step"><h2 class="ck-h"><i>3</i>몸은 어떤 편인가요? <small>더위에 얼마나 약한지 몸에 맞춰 계산해요</small></h2>
<p class="q">짧은 코/단두종인가요? <small>프렌치불독·퍼그·시추 등</small></p><div class="opts c2">{_opt('isBrachycephalic', 'true', '네')}{_opt('isBrachycephalic', 'false', '아니요', '', True)}</div>
<p class="q">체형</p><div class="opts c3">{_opt('bodyCondition', 'normal', '보통', '갈비뼈가 살짝 만져져요', True)}{_opt('bodyCondition', 'overweight', '과체중', '허리선이 덜 보여요')}{_opt('bodyCondition', 'obese', '비만', '더위 위험을 높게 봐요')}</div>
</div>
<div class="ck-step"><h2 class="ck-h"><i>4</i>털은 어떤가요? <small>털에 맞춰 추위·더위 기준을 바꿔요</small></h2>
<div class="opts c4">{_opt('coatType', 'short', '짧은 털', '추위에 민감')}{_opt('coatType', 'normal', '보통 털', '일반 기준', True)}{_opt('coatType', 'double', '이중모', '추위엔 강, 더위엔 약')}{_opt('coatType', 'heavy', '두꺼운 털', '더운 날 보수적으로')}</div>
<p class="q">추위에 적응된 강아지인가요?</p><div class="opts c2">{_opt('coldAcclimated', 'true', '적응됐어요')}{_opt('coldAcclimated', 'false', '아니요', '', True)}</div>
</div>
<div class="ck-step"><h2 class="ck-h"><i>5</i>컨디션을 알려주세요 <small>폭염·한파 날 산책해도 되는지 판단할 때 봐요</small></h2>
<p class="q">더위에 약한 편인가요?</p><div class="opts c2">{_opt('heatSensitive', 'true', '약해요')}{_opt('heatSensitive', 'false', '보통이에요', '', True)}</div>
<p class="q">심장/호흡기 주의가 있나요?</p><div class="opts c2">{_opt('hasHeartOrRespiratoryCondition', 'true', '있어요')}{_opt('hasHeartOrRespiratoryCondition', 'false', '없어요', '', True)}</div>
</div>
</div>
<aside class="ck-result" id="calc-result" aria-live="polite">
<div class="cr-card ws" data-card>
<div class="cr-head">
<div class="ws-top"><span class="ws-badge" data-level aria-hidden="true">–</span><div><p class="ws-lvname" data-lvname>산책 안전도</p><h3 class="cr-title" data-title>날씨를 불러오는 중이에요</h3></div></div>
<div class="ws-scale" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
<p class="cr-msg" data-msg></p>
<p class="ws-chips" data-ctx></p>
</div>
<div class="cr-body">
<p class="cr-sub">오늘 할 일</p><ul class="cr-acts" data-acts></ul>
<p class="cr-sub">어떻게 계산했나요</p><div class="ws-formula" data-formula></div>
<div class="ws-hours"><p class="cr-sub">앞으로 24시간</p><div class="ws-strip" data-strip></div><p class="ws-best" data-best></p></div>
<div class="cr-app"><b>매일 계산하기 번거롭다면</b><p>앱에선 산책 시간마다 안전도를 알려주고, 비 소식은 먼저 알려줘요. 가족 모두에게요.</p><a class="btn-app" href="/download/">응가메이트 무료로 받기</a></div>
</div></div>
</aside>
</div>
<a class="mini" href="#calc-result" data-mini><i data-mini-l></i><b data-mini-t></b><span>자세히</span></a>
<p class="tool-note">체감온도는 기온·습도·바람을 합친 값이에요. 날씨 데이터 Open-Meteo · 위치는 저장하지 않아요. 참고용 안내이며, 강아지가 헐떡이거나 떨면 바로 쉬게 해 주세요.</p>
</div></section>

<section class="tool-sec alt" id="table"><div class="wrap-tool">
<p class="label">산책 안전도 기준표</p><h2 class="h2">체감온도 × 크기로 정하는 <em>기본 단계</em></h2>
<p class="sec-lead">대형견은 더위에, 소형견은 추위에 더 약해요. 지금 날씨와 고른 크기는 표에 표시돼요.</p>
<div class="ws-table-wrap"><table class="ws-table" data-table><thead><tr><th scope="col">체감온도</th><th scope="col">소형견</th><th scope="col">중형견</th><th scope="col">대형견</th></tr></thead><tbody>{rows}</tbody></table></div>
</div></section>

<section class="tool-sec" id="factors"><div class="wrap-tool">
<p class="label">가산 요인</p><h2 class="h2">우리 강아지에 맞춰 <em>더하고 빼요</em></h2>
<p class="sec-lead">해당하는 항목만큼 기준표의 단계에 더하거나 빼요. 0.5는 반올림해요.</p>
<div class="fac-grid">
<div class="fac hot"><h3>더운 날 · 체감 24° 이상</h3><ul>
<li><span>단두종 (프렌치불독·퍼그 등)</span><b>+1</b></li><li><span>비만</span><b>+1</b></li><li><span>과체중</span><b>+0.5</b></li><li><span>6개월 미만 또는 노령견</span><b>+1</b></li>
<li><span>더위에 민감한 강아지</span><b>+1</b></li><li><span>이중모·두꺼운 털</span><b>+0.5</b></li><li><span>심장·호흡기 질환</span><b>+1</b></li></ul></div>
<div class="fac cold"><h3>추운 날 · 체감 10° 이하</h3><ul>
<li><span>소형견</span><b>+1</b></li><li><span>짧은 털</span><b>+1</b></li><li><span>6개월 미만 또는 노령견</span><b>+0.5</b></li><li><span>비·습한 날씨 (강수 확률 40% 이상)</span><b>+1</b></li>
<li><span>이중모·두꺼운 털 (추위 유리)</span><b class="dn">−1</b></li><li><span>추위 적응 완료</span><b class="dn">−1</b></li></ul></div>
</div>
</div></section>

<section class="tool-sec alt" id="levels"><div class="wrap-tool">
<p class="label">단계별 행동</p><h2 class="h2">단계마다 <em>이렇게</em> 다녀오세요</h2>
<ul class="lv-legend">{legend}</ul>
<div class="tips"><div><img src="/assets/img/emoji/sun_behind_small_cloud.webp" alt="" width="40" height="40"><b>손등 5초 테스트</b><p>아스팔트에 손등을 5초 대 보고 뜨거우면 발바닥 화상 위험이 있어요.</p></div>
<div><img src="/assets/img/emoji/alarm_clock.webp" alt="" width="40" height="40"><b>여름엔 이른 아침·해 진 뒤</b><p>한낮 아스팔트는 기온보다 20° 넘게 뜨거워질 수 있어요.</p></div>
<div><img src="/assets/img/emoji/paw_prints.webp" alt="" width="40" height="40"><b>겨울엔 발바닥 확인</b><p>제설제와 얼음에 발바닥이 상할 수 있어요. 다녀오면 닦아 주세요.</p></div></div>
</div></section>

{faq_block('ko', WALK_FAQ)}
{cta_band('ko')}
<script src="/assets/js/walk-safety.js?v={ASSET_V}" defer></script>
'''
    ld = (_breadcrumb_ld(slug, name), _app_ld(slug, name, desc), faq_ld(WALK_FAQ))
    head = (f'<link rel="preconnect" href="https://api.open-meteo.com" crossorigin>\n'
            f'<link rel="stylesheet" href="/assets/css/tools.css?v={ASSET_V}">\n')
    return page('ko', None, title, desc, body, '/assets/og/poopiemate-ko.jpg', ko_path=f'/{slug}/', en_path=f'/en/{slug}/', active='guide',
                og_type='website', ld=ld, extra_head=head,
                keywords='강아지 산책지수, 산책지수, 강아지 산책 안전도, 강아지 산책 온도, 강아지 여름 산책, 강아지 겨울 산책, 강아지 산책 몇도, 반려견 산책 날씨')
