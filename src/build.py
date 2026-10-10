"""응가메이트 웹사이트 빌드 — 한국어(/)·영어(/en/) 페이지를 같은 틀로 만든다.

python3 src/build.py          # 페이지 HTML + sitemap.xml
에셋 준비는 src/prepare_assets.py, OG 이미지는 src/og.py.
"""
import html as html_mod, json, re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
SITE = 'https://poopiemate.com'
UPDATED = '2026-10-10'
ASSET_V = '25'  # css·js 캐시 갱신용 — 바꿀 때마다 올린다

# 한국어 페이지는 한국 스토어, 영어 페이지는 나라를 고정하지 않은 링크 (PC 브라우저는 나라 없는 App Store 링크를 미국 스토어로 연다)
APPSTORE = {'ko': 'https://apps.apple.com/kr/app/%EC%9D%91%EA%B0%80%EB%A9%94%EC%9D%B4%ED%8A%B8/id6781981502', 'en': 'https://apps.apple.com/app/id6781981502'}
PLAY = {'ko': 'https://play.google.com/store/apps/details?id=com.pixelberry.poopiemate&hl=ko', 'en': 'https://play.google.com/store/apps/details?id=com.pixelberry.poopiemate&hl=en'}
SNS = {
    'youtube': ('YouTube', 'https://www.youtube.com/@poopiemate'),
    'tiktok': ('TikTok', 'https://www.tiktok.com/@poopiemate'),
    'instagram': ('Instagram', {'ko': 'https://www.instagram.com/poopiemate_kr', 'en': 'https://www.instagram.com/poopiemate'}),
    'linkedin': ('LinkedIn', 'https://www.linkedin.com/company/poopiemate'),
    'email': ('Email', 'mailto:poopiemate@pixelberry.io'),
}
EMAIL = 'poopiemate@pixelberry.io'
# 유튜브 채널 @poopiemate에 올라간 영상
YT = {
    'service_long': {'ko': 'cnmU1xI7sSg', 'en': 'xiX6nDBh7yE'},
}


def icon(name, cls=''):
    s = (SRC / f'icons/{name}.svg').read_text()
    s = re.sub(r'<title>.*?</title>', '', s)
    s = s.replace('<svg ', f'<svg aria-hidden="true" focusable="false" fill="currentColor" {f"class={chr(34)}{cls}{chr(34)} " if cls else ""}', 1).replace(' role="img"', '')
    return s


CHEV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m{d}"/></svg>'
ARROW_R = CHEV.replace('m{d}', 'M5 12h14M13 6l6 6-6 6')
CHEV_L = CHEV.replace('m{d}', 'M15 18l-6-6 6-6')
CHEV_R = CHEV.replace('m{d}', 'M9 18l6-6-6-6')
PIN_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 3a1 1 0 0 1 .7 1.7L15.4 6v4.6l2.9 2.9a1 1 0 0 1-.7 1.7H13v6l-1 1-1-1v-6H6.4a1 1 0 0 1-.7-1.7l2.9-2.9V6L7.3 4.7A1 1 0 0 1 8 3h8Z"/></svg>'
EXT_ICON = CHEV.replace('m{d}', 'M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6')
CHEV_D = CHEV.replace('m{d}', 'M6 9l6 6 6-6')
PLAY_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72a1 1 0 0 0 1.52.85l10.6-6.86a1 1 0 0 0 0-1.7L9.52 4.29A1 1 0 0 0 8 5.14Z"/></svg>'
MENU_ICON = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
CLOSE_ICON = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
PRETENDARD = ('<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
              '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">')
GPLAY = ('<svg viewBox="0 0 27 30" aria-hidden="true"><path d="M0 0 L 16.4 15 L 0 30 Z" fill="#4285F4"/><path d="M0 0 L 20.6 11.1 L 16.4 15 Z" fill="#34A853"/>'
         '<path d="M0 30 L 20.6 18.9 L 16.4 15 Z" fill="#EA4335"/><path d="M20.6 11.1 L 27 15 L 20.6 18.9 L 16.4 15 Z" fill="#FBBC04"/></svg>')

# ── 공통 문구
T = {
    'ko': {
        'name': '응가메이트', 'nav': [('how', '이렇게 써요'), ('story', '이야기'), ('notice', '공지사항')], 'cta': '앱 다운로드', 'cta_short': '앱 받기',
        'menu': '메뉴 열기', 'close': '메뉴 닫기', 'skip': '본문으로 건너뛰기', 'get': '지금 다운로드', 'lang_label': '언어',
        'f_links': [('고객 지원', '/support/'), ('개인정보 처리방침', '/privacy/'), ('이용약관', '/terms/'), ('오픈소스 라이선스', '/licenses/')],
        'operator': f'운영 픽셀베리 · 문의 <a href="mailto:{EMAIL}">{EMAIL}</a>', 'copy': '© 2026 픽셀베리 · 응가메이트',
        'play': '영상 재생', 'more': '자세히 보기', 'back': '목록으로',
    },
    'en': {
        'name': 'POOPIEMATE', 'nav': [('how', 'How it works'), ('story', 'Stories'), ('notice', 'Notices')], 'cta': 'Get the app', 'cta_short': 'Get the app',
        'menu': 'Open menu', 'close': 'Close menu', 'skip': 'Skip to content', 'get': 'Download on the', 'lang_label': 'Language',
        'f_links': [('Support', '/en/support/'), ('Privacy Policy', '/en/privacy/'), ('Terms of Service', '/en/terms/'), ('Open-source licenses', '/en/licenses/')],
        'operator': f'Operated by Pixelberry · <a href="mailto:{EMAIL}">{EMAIL}</a>', 'copy': '© 2026 Pixelberry · POOPIEMATE',
        'play': 'Play video', 'more': 'Learn more', 'back': 'Back to list',
    },
}
# 페이지 키 → (한국어 경로, 영어 경로)
PATHS = {
    'home': ('/', '/en/'), 'how': ('/how-it-works/', '/en/how-it-works/'), 'story': ('/story/', '/en/story/'),
    'why': ('/story/why-we-built/', '/en/story/why-we-built/'), 'notice': ('/notice/', '/en/notice/'),
    'interview_notice': ('/notice/interview/', '/en/notice/interview/'),
    'privacy': ('/privacy/', '/en/privacy/'), 'terms': ('/terms/', '/en/terms/'), 'support': ('/support/', '/en/support/'), 'licenses': ('/licenses/', '/en/licenses/'),
}


def url(key, lang):
    return PATHS[key][0 if lang == 'ko' else 1]


def stores(lang, cls=''):
    t = T[lang]
    return (f'<div class="stores {cls}">'
            f'<a class="store" href="{APPSTORE[lang]}" rel="noopener">{icon("apple")}<span><small>{t["get"]}</small><b>App Store</b></span></a>'
            f'<a class="store" href="{PLAY[lang]}" rel="noopener">{GPLAY}<span><small>{"지금 다운로드" if lang == "ko" else "Get it on"}</small><b>Google Play</b></span></a></div>')


def sns_links(lang):
    out = []
    for key, (label, href) in SNS.items():
        h = href[lang] if isinstance(href, dict) else href
        if key == 'email':
            label = f'{"이메일" if lang == "ko" else "Email"} {EMAIL}'
        out.append(f'<a href="{h}"{"" if key == "email" else " target=" + chr(34) + "_blank" + chr(34) + " rel=" + chr(34) + "noopener" + chr(34)} aria-label="{label}">{icon(key)}</a>')
    return '<div class="sns">' + ''.join(out) + '</div>'


def org_ld(lang):
    """운영사 — 이메일과 모든 SNS를 sameAs로 묶어 검색엔진·AI가 같은 브랜드로 알아보게."""
    return {'@type': 'Organization', 'name': '응가메이트' if lang == 'ko' else 'POOPIEMATE', 'alternateName': ['POOPIEMATE', '응가메이트', '픽셀베리', 'Pixelberry'],
            'url': SITE, 'logo': f'{SITE}/assets/icons/apple-touch-icon.png', 'email': EMAIL,
            'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support', 'email': EMAIL, 'availableLanguage': ['ko', 'en']},
            'sameAs': [SNS['youtube'][1], SNS['tiktok'][1], SNS['instagram'][1]['ko'], SNS['instagram'][1]['en'], SNS['linkedin'][1]]}


def lang_links(lang, ko_path, en_path, cls):
    return (f'<a href="{ko_path}" hreflang="ko" lang="ko"{" aria-current=" + chr(34) + "true" + chr(34) if lang == "ko" else ""}>한국어</a>'
            f'{"<i></i>" if cls == "gnb" else ""}'
            f'<a href="{en_path}" hreflang="en" lang="en"{" aria-current=" + chr(34) + "true" + chr(34) if lang == "en" else ""}>English</a>')


def header(lang, active, ko_path, en_path):
    t = T[lang]
    nav = ''.join(f'<a href="{url(k, lang)}"{" aria-current=" + chr(34) + "page" + chr(34) if k == active else ""}>{label}</a>' for k, label in t['nav'])
    gl = lang_links(lang, ko_path, en_path, 'gnb').replace('>한국어<', '>KO<').replace('>English<', '>EN<')
    logo = f'<img src="/assets/brand/wordmark-{lang}-green.svg" alt="{t["name"]}" width="{"120" if lang == "ko" else "158"}" height="32">'
    return (f'<a class="skip" href="#main">{t["skip"]}</a>'
            f'<header class="gnb"><div class="wrap gnb-in">'
            f'<a class="gnb-logo" href="{url("home", lang)}">{logo}</a>'
            f'<nav class="gnb-nav" aria-label="{"주 메뉴" if lang == "ko" else "Main menu"}">{nav}</nav>'
            f'<div class="gnb-side"><nav class="gnb-lang" aria-label="{t["lang_label"]}">{gl}</nav>'
            f'<a class="gnb-cta" href="/download/?lang={lang}">{t["cta"]}</a>'
            f'<button class="gnb-menu" type="button" aria-label="{t["menu"]}" aria-controls="menu" aria-expanded="false" data-menu-open>{MENU_ICON}</button></div>'
            f'</div></header>'
            f'<div class="sheet" id="menu" role="dialog" aria-modal="true" aria-label="{t["name"]}" aria-hidden="true">'
            f'<div class="sheet-top"><a href="{url("home", lang)}">{logo}</a><button type="button" class="gnb-menu" aria-label="{t["close"]}" data-menu-close>{CLOSE_ICON}</button></div>'
            f'<nav aria-label="{"모바일 메뉴" if lang == "ko" else "Mobile menu"}">{nav}<a href="/download/?lang={lang}">{t["cta"]}</a></nav>'
            f'<div class="sheet-lang">{lang_links(lang, ko_path, en_path, "sheet")}</div>{sns_links(lang)}</div>')


def footer(lang, ko_path, en_path):
    t = T[lang]
    links = [(label, url(k, lang)) for k, label in t['nav']] + t['f_links']
    priv = t['f_links'][1][0]
    nav = ''.join(f'<a href="{h}"{" class=" + chr(34) + "strong" + chr(34) if label == priv else ""}>{label}</a>' for label, h in links)
    return (f'<footer class="footer"><div class="wrap">'
            f'<div class="f-row"><img src="/assets/brand/wordmark-{lang}-green.svg" alt="{t["name"]}" width="{"105" if lang == "ko" else "140"}" height="28">{sns_links(lang)}</div>'
            f'<nav class="f-links" aria-label="{"사이트 링크" if lang == "ko" else "Site links"}">{nav}</nav>'
            f'<div class="f-bottom"><span>{t["operator"]}</span><span>{t["copy"]}</span><span class="lang-switch">{lang_links(lang, ko_path, en_path, "foot")}</span></div>'
            f'</div></footer>')


def page(lang, key, title, desc, body, og_image, active=None, ko_path=None, en_path=None, og_type='website', ld=(), extra_head='', noindex=False, keywords='', intro=False, snap=False):
    ko_path = ko_path or url(key, 'ko')
    en_path = en_path or (url(key, 'en') if key in PATHS else None)
    path = ko_path if lang == 'ko' else en_path
    alt = ''
    if en_path:
        alt = (f'<link rel="alternate" hreflang="ko" href="{SITE}{ko_path}">\n<link rel="alternate" hreflang="en" href="{SITE}{en_path}">\n'
               f'<link rel="alternate" hreflang="x-default" href="{SITE}{ko_path}">\n')
    ld_html = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x}</script>\n' for x in ld)
    t = T[lang]
    return f'''<!doctype html>
<html lang="{lang}"{' class="snap"' if snap else ''}>
<head>
<meta charset="utf-8">
<script>document.documentElement.classList.add('js'){";try{if(!localStorage.getItem('pm_intro'))document.documentElement.classList.add('show-intro')}catch(e){}" if intro else ""}</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
{f'<meta name="keywords" content="{escape(keywords)}">' if keywords else ''}
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-image-preview:large'}">
<link rel="canonical" href="{SITE}{path}">
{alt}<meta name="theme-color" content="#18955A">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{t['name']}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'ko_KR' if lang == 'ko' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{SITE}{og_image}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/icons/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/NanumSquareNeo-cBd.woff2" as="font" type="font/woff2" crossorigin>
{PRETENDARD}
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
{extra_head}{ld_html}</head>
<body>
{intro_screen(lang) if intro else ''}{header(lang, active, ko_path, en_path or '/en/')}
<main id="main">
{body}
</main>
{footer(lang, ko_path, en_path or '/en/')}
<script src="/assets/js/store-region.js?v={ASSET_V}" defer></script>
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
</body>
</html>
'''


def intro_screen(lang):
    """첫 방문 로딩 — 앱 스플래시처럼 초록 바탕 + 응댕이 얼굴 + 흰 로고 + 세 점 (최대 1.2초, 한 번만)."""
    return (f'<div class="intro" aria-hidden="true"><img class="face" src="/assets/img/mascot/face.webp" alt="">'
            f'<img class="logo" src="/assets/brand/wordmark-{lang}-white.svg" alt=""><div class="dots"><i></i><i></i><i></i></div></div>\n')


def reel(key, lang, label):
    """릴스 모션그래픽 — 그 화면(단계)이 들어오면 재생된다 (site.js)."""
    return (f'<video data-step muted loop playsinline preload="none" controlslist="nodownload noremoteplayback" disablepictureinpicture poster="/assets/video/{key}-{lang}.webp" aria-label="{escape(label)}">'
            f'<source src="/assets/video/{key}-{lang}.mp4" type="video/mp4"></video>')


SOUND_OFF = '<svg class="i-off" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="m22 9-6 6M16 9l6 6"/></svg>'
SOUND_ON = '<svg class="i-on" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg>'


def intro_film(lang, label):
    """첫 화면 — 서비스 소개 영상(우리 사이트에 올린 mp4)이 화면 가득 바로 재생. 유튜브 버튼 없이, 소리는 버튼으로."""
    on, off = {'ko': ('소리 켜기', '소리 끄기'), 'en': ('Sound on', 'Sound off')}[lang]
    return (f'<section class="film" data-film aria-label="{escape(label)}">'
            f'<video data-film-video muted loop playsinline autoplay preload="auto" controlslist="nodownload noremoteplayback" disablepictureinpicture aria-label="{escape(label)}"'
            f' data-land="/assets/video/intro-{lang}.mp4" data-port="/assets/video/intro-{lang}-v.mp4" data-land-poster="/assets/video/intro-{lang}.webp" data-port-poster="/assets/video/intro-{lang}-v.webp">'
            f'<source src="/assets/video/intro-{lang}-v.mp4" type="video/mp4" media="(max-aspect-ratio: 1/1)">'
            f'<source src="/assets/video/intro-{lang}.mp4" type="video/mp4"></video>'
            f'<button class="film-sound" type="button" data-sound data-on="{on}" data-off="{off}" aria-pressed="false">{SOUND_OFF}{SOUND_ON}<span>{on}</span></button>'
            f'<a class="film-down" href="#start" aria-label="{"아래로" if lang == "ko" else "Scroll down"}">{CHEV_D}</a></section>')


def waver():
    return ('<div class="waver" aria-hidden="true"><img class="tail" src="/assets/img/mascot/wave-tail.webp" alt="">'
            '<img class="sh" src="/assets/img/mascot/wave-shoulder.webp" alt=""><img src="/assets/img/mascot/wave-body.webp" alt="">'
            '<img class="arm" src="/assets/img/mascot/wave-arm.webp" alt=""></div>')


def icons(items):
    return ''.join(f'<img class="ic" src="/assets/img/emoji/{n}.webp" alt="" style="left:{x}%;top:{y}%;rotate:{r}deg">' for n, x, y, r in items)


def sb(text):
    """문장이 끝나면 줄을 바꾼다 (한국어·영어 모두) — 설명 글이 문장 중간에서 어색하게 꺾이지 않게."""
    # 「네.」「Yes.」처럼 한 낱말짜리 대답 뒤에서는 끊지 않는다
    text = re.sub(r'(^|<br>|\s)([^\s<]+?[.!?。])\s+(?=[^\s<])', lambda m: m.group(0) if len(m.group(2)) <= 4 and m.group(1) in ('', '<br>') else f'{m.group(1)}{m.group(2)}<br>', text)
    return re.sub(r'([!?][”’"])\s+(?=[A-Z])', r'\1<br>', text)


def new_badge(date):
    """새 글 표시 — 올린 날부터 14일 동안만 보인다 (site.js가 오늘 날짜로 판단)."""
    return f'<span class="new-badge" data-new="{date}" hidden>NEW</span>'


def empty_state(lang, kind):
    """글이 없을 때 — 머리 긁는 응댕이 + 가벼운 한마디 (분류 탭에 글이 없거나 목록이 비면 site.js가 보여 준다)."""
    t = {('ko', 'story'): ('아직 아무 이야기도 없어요 ^^;;', '응댕이가 열심히 쓰는 중이에요.<br>곧 채워 넣을게요!'),
         ('ko', 'notice'): ('아직 아무 소식도 없어요 ^^;;', '새 소식이 생기면 제일 먼저 여기 올릴게요.<br>조금만 기다려 주세요!'),
         ('en', 'story'): ('Nothing here yet ^^;;', 'Poochie is busy writing.<br>We’ll fill this up soon!'),
         ('en', 'notice'): ('No news yet ^^;;', 'When something new happens, it lands here first.<br>Hang tight!')}[(lang, kind)]
    return (f'<div class="empty" hidden><img src="/assets/img/mascot/scratch.webp" alt="" width="160" height="185" loading="lazy">'
            f'<b>{t[0]}</b><p>{t[1]}</p></div>')


def list_head(icon_name, h, sub):
    """이야기·공지사항 목록 머리 — 3D 아이콘 + 제목 + 한 줄 설명 (공지사항 시안)."""
    return (f'<div class="list-head"><img src="/assets/img/emoji/{icon_name}.webp" alt="" width="56" height="56">'
            f'<div><h1 class="list-h1">{h}</h1><p class="list-sub">{sb(sub)}</p></div></div>')


def label(text, cls=''):
    return f'<p class="label{" " + cls if cls else ""}">{text}</p>'


def art_card(dog, ics):
    """글 머리 초록 카드 — 가운데 둥근 빛 + 3D 아이콘 + 응댕이 (v2 이야기·공지 상세)."""
    ic = ''.join(f'<img class="ic" src="/assets/img/emoji/{n}.webp" alt="" style="{pos};width:{w}px;rotate:{r}deg">' for n, pos, w, r in ics)
    return f'<div class="art-card" aria-hidden="true"><span class="glow"></span>{ic}<img class="dog" src="/assets/img/mascot/{dog}.webp" alt=""></div>'


def cta_band(lang, cls=''):
    """다운로드 — 초록 카드, 왼쪽 글·스토어 버튼, 오른쪽 손 흔드는 응댕이 (v3 지도 아래)."""
    c = {'ko': ('둘이 같이 키운다면,<br>둘이 같이 써보세요', '가족 초대도 기록도 알림도 무료예요'),
         'en': ('Raising your dog together?<br>Log it together.', 'Family invites, logs and alerts are all free.')}[lang]
    return (f'<section class="sec-cta {cls}"><div class="wrap"><div class="cta-card rise">'
            f'<div class="cta-text"><h2 class="h2" data-mo>{c[0]}</h2><p>{sb(c[1])}</p></div>{stores(lang)}{waver()}</div></div></section>')


def cta_soft(lang):
    """다운로드 — 연한 초록 상자 (v2 이렇게 써요 아래)."""
    c = {'ko': ('가족에게 매번 물어본다면,<br>같이 깔아보세요', '초대도 기록도 알림도 무료예요'),
         'en': ('Always asking your family?<br>Get it together.', 'Invites, logs and alerts are all free.')}[lang]
    return (f'<section class="sec-soft"><div class="wrap-mid"><div class="soft-cta rise"><div><h2 class="h3">{c[0]}</h2><p>{sb(c[1])}</p></div>{stores(lang)}</div></div></section>')


def faq_block(lang, items):
    h = {'ko': '자주 묻는 질문', 'en': 'Frequently asked questions'}[lang]
    rows = ''.join(f'<details{" open" if i == 0 else ""}><summary><span>{escape(q)}</span>{CHEV_D}</summary><p>{sb(escape(a))}</p></details>' for i, (q, a) in enumerate(items))
    return f'<section class="sec-faq"><div class="wrap-faq">{label("FAQ")}<h2 class="h2" data-mo>{h}</h2><div class="faq rise">{rows}</div></div></section>'


def faq_ld(items):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}


def video_ld(vid, name, desc, lang):
    return {'@context': 'https://schema.org', '@type': 'VideoObject', 'name': name, 'description': desc, 'inLanguage': lang,
            'thumbnailUrl': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg', 'uploadDate': '2026-10-09',
            'embedUrl': f'https://www.youtube.com/embed/{vid}', 'contentUrl': f'{SITE}/assets/video/intro-{lang}.mp4', 'duration': 'PT1M7S'}


def write(path, html):
    p = ROOT / path.lstrip('/') / 'index.html'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(re.sub(r'\n{3,}', '\n\n', html), encoding='utf-8')


# ═════════════════════════════════════════════════════════ 홈 (캔버스 「v3 지도 아래」)
FEATURES = {  # 여섯 가지 카드 — 바탕색, 칩, 제목, 설명, 3D 아이콘
    'ko': [('#EDE3FF', '가족 기록 공유', '한 명이 누르면<br>가족 폰이 울려요', '“응댕이 똥 쌌어?” 대신 알림 하나. 누가 산책하고 치웠는지 한눈에 봐요.', 'house'),
           ('#FFE9D6', '돌봄 부탁', '바쁜 날엔<br>버튼으로 부탁해요', '전화 대신 버튼으로 부탁해요. 누가 맡았는지 바로 보여요.', 'love_letter'),
           ('#FFE3F0', '하트', '다녀오면<br>고맙다고 하트', '가족이 남긴 기록에 하트를 보내요. 산책 당번이 덜 외로워져요.', 'growing_heart'),
           ('#FFE3F7', '응가 · 쉬 신호', '마지막 기록과 신호를<br>한눈에', '배변 텀으로 게이지가 차올라요. 가득 차면 가족에게 알림이 가요.', 'pile_of_poo'),
           ('#FFF3CC', '산책 루틴', '정해 둔 시간에<br>같이 알려줘요', '산책 시간을 정해 두세요. 가족 모두에게 같은 시간에 알려줘요.', 'alarm_clock'),
           ('#DDF4E6', '산책 안전도', '오늘 언제 나가면<br>좋을까요', '체형·털·나이와 날씨를 더해요. 다음 산책하기 좋은 때를 알려줘요.', 'sun_behind_small_cloud')],
    'en': [('#EDE3FF', 'Shared family log', 'One tap,<br>every phone buzzes', 'One alert, no more asking. See who walked and cleaned up.', 'house'),
           ('#FFE9D6', 'Help requests', 'Busy day?<br>Ask with a button', 'Ask for a walk with one button. See who picked it up.', 'love_letter'),
           ('#FFE3F0', 'Hearts', 'Back from a walk?<br>Send a heart', 'Send a heart on a family log. Walk duty feels less lonely.', 'growing_heart'),
           ('#FFE3F7', 'Potty signals', 'Last log and signals<br>at a glance', 'Gauges fill with your dog’s rhythm. The family hears when they’re full.', 'pile_of_poo'),
           ('#FFF3CC', 'Walk routines', 'Set the time,<br>everyone gets reminded', 'Pick your walk times. Everyone gets the same reminder.', 'alarm_clock'),
           ('#DDF4E6', 'Walk safety', 'When is it safe<br>to head out?', 'We add up body, coat, age and weather. Then show the next good time to walk.', 'sun_behind_small_cloud')],
}
HOME_FAQ = {
    'ko': [('가족 여러 명이 같이 쓸 수 있나요?', '네. 카톡이나 문자로 초대 코드를 보내면 같은 강아지를 함께 기록해요. 누가 기록해도 다른 가족 모두에게 바로 알림이 가요. 초대도 기록도 알림도 무료예요.'),
           ('맞벌이인데 산책·배변 당번을 나눠서 기록해도 되나요?', '네. 가족이 각자 다른 시간에 기록해도 하나의 강아지 프로필에 실시간으로 모여요. 오늘 누가 산책하고 기록했는지 바로 보여서, 바쁜 날엔 버튼 하나로 산책을 부탁할 수도 있어요.'),
           ('실외배변하는 강아지도 쓸 수 있나요?', '네. 응가메이트는 집에서는 안 싸고 산책에서만 싸는 강아지를 키우며 만들었어요. 산책 중 기록, 배변 텀 게이지, 산책 루틴 알림으로 실외배변 습관을 함께 챙길 수 있어요. 실내배변하는 강아지도 똑같이 쓸 수 있어요.'),
           ('강아지가 여러 마리여도 되나요?', '네. 강아지를 여러 마리 등록하고 위에서 바로 바꿔 가며 기록할 수 있어요. 가족도 강아지마다 함께 볼 수 있어요.'),
           ('산책 안전도는 어떻게 계산하나요?', '체형, 단두종 여부, 털 길이, 나이, 심장·호흡기 질환 여부 같은 강아지 정보에 실시간 체감온도와 강수확률을 더해 1~5단계로 알려줘요. 반려견 온열질환 예방 가이드를 참고해 만들었어요.')],
    'en': [('Can the whole family use it together?', 'Yes. Send an invite code by message and everyone logs the same dog. Whoever logs it, everyone else gets an alert right away. Invites, logs and alerts are all free.'),
           ('We both work. Can we split walk and potty duty?', 'Yes. Logs from different people at different times land on one shared dog profile in real time. You can see who walked today, and on busy days ask someone else to take the walk with one button.'),
           ('Does it work for dogs that only go outside?', 'Yes. POOPIEMATE was built by a family whose dog only goes on walks, never indoors. Logging on walks, potty gauges and walk reminders keep that routine on track. Indoor-trained dogs work just as well.'),
           ('Can I add more than one dog?', 'Yes. Add as many dogs as you have and switch between them from the top of the screen. Family members can follow each dog too.'),
           ('How is the walk safety score calculated?', 'It looks at your dog’s body type, short nose, coat, age and heart or breathing health. It adds the live feels-like temperature and rain chance. The result is a 1–5 score based on heatstroke-prevention guidance for dogs.')],
}



def home(lang):
    c = {
        'ko': {'title': '응가메이트 — 가족이 함께 보는 강아지 응가·산책 기록',
               'desc': '한 명이 기록하면 가족 모두가 바로 알아요. “응댕이 똥 쌌어?” 이제 안 물어봐도 돼요. 초대·기록·알림 모두 무료예요.',
               'h1': '“응댕이 똥 쌌어?”<br><span class="hl">이제 안 물어봐도 돼요</span>',
               'lead': '강아지를 여럿이 같이 돌보는 집을 위한 앱. <br>한 사람이 응가·쉬를 기록하면 가족 모두가 바로 알아요.',
               'v_label': '응가메이트 서비스 소개 영상 (1분)',
               'b_tag': '이렇게 같이 돌봐요', 'b_h': '가족이 함께 쓰는 여섯 가지', 'f_more': '이렇게 써요 자세히 보기',
               's_tag': '응가메이트 이야기', 's_h': '“응댕이 똥 쌌어?”<br>그 전화에서 시작됐어요', 's_cap': ('분홍이 시절', '지금 우리 집'),
               's_p': '밭 옆 견사에서 ‘분홍이’로 불리던 진도믹스는 이제 우리 가족이에요. 집에서는 절대 안 싸서 하루 세 번 똥책을 나가요. 맞벌이 엄마아빠는 매번 전화로 “응댕이 똥 쌌어?”를 물어야 했죠. 그래서 버튼 하나로 가족 모두가 아는 앱을 만들었어요.',
               's_btn': '이야기 더 보기'},
        'en': {'title': 'POOPIEMATE — Your dog’s potty & walk log, shared with family',
               'desc': 'When one of you logs it, everyone knows. No more “Did Poochie poop?” texts. Invites, logs and alerts are free.',
               'h1': '“Did Poochie poop?”<br><span class="hl">No need to ask anymore</span>',
               'lead': 'An app for families who look after one dog together. <br>When one person logs a poop or pee, everyone knows right away.',
               'v_label': 'POOPIEMATE intro video (1 min)',
               'b_tag': 'Care together', 'b_h': 'Six things families share', 'f_more': 'See how it works',
               's_tag': 'Our story', 's_h': '“Did she poop?”<br>It started with that call', 's_cap': ('Back at the kennel', 'Home with us now'),
               's_p': 'Our white Jindo mix was once “Bunhong-i” at a farm-side kennel. She never goes indoors, so she walks three times a day. As a working couple, we kept calling to ask “Did Poochie poop?” So we built an app where one tap tells the whole family.',
               's_btn': 'Read our story'},
    }[lang]
    cards = ''.join(f'<article class="fcard" style="background:{bg}"><span class="chip">{chip}</span><h3 class="h3">{h}</h3><p>{sb(p)}</p>'
                    f'<img src="/assets/img/emoji/{ic}.webp" alt="" loading="lazy" width="132" height="132"></article>' for bg, chip, h, p, ic in FEATURES[lang])
    dots = ''.join('<i></i>' for _ in FEATURES[lang])
    nav = (f'<div class="carousel-nav"><button type="button" data-prev aria-label="{"이전" if lang == "ko" else "Previous"}">{CHEV_L}</button>'
           f'<button type="button" data-next aria-label="{"다음" if lang == "ko" else "Next"}">{CHEV_R}</button></div>')
    body = f"""
{intro_film(lang, c['v_label'])}

<section class="hero" id="start"><div class="wrap">
<h1 class="hero-h1" data-mo>{c['h1']}</h1>
<p class="hero-lead mo-fade">{c['lead']}</p>
</div></section>

<section class="sec-feat" data-carousel>
<div class="wrap feat-head"><div>{label(c['b_tag'])}<h2 class="h2" data-mo>{c['b_h']}</h2></div>{nav}</div>
<div class="track" tabindex="0" role="region" aria-label="{re.sub('<[^>]+>', ' ', c['b_h'])}">{cards}</div>
<div class="wrap feat-foot"><div class="dots" aria-hidden="true">{dots}</div><a class="more-link" href="{url('how', lang)}">{c['f_more']}{ARROW_R}</a></div>
</section>

<section class="sec-story"><div class="wrap"><div class="story-card rise">
<div class="polaroids"><figure><img src="/assets/img/photo/kennel-900.webp" alt="" loading="lazy"><figcaption>{c['s_cap'][0]}</figcaption></figure>
<figure><img src="/assets/img/photo/home-first-900.webp" alt="" loading="lazy"><figcaption>{c['s_cap'][1]}</figcaption></figure></div>
<div class="story-text">{label(c['s_tag'], 'gold')}<h2 class="h2" data-mo>{c['s_h']}</h2><p>{sb(c['s_p'])}</p><a class="more-link" href="{url('why', lang)}">{c['s_btn']}{ARROW_R}</a></div>
</div></div></section>

{faq_block(lang, HOME_FAQ[lang])}
{cta_band(lang)}
"""
    app_ld = {'@context': 'https://schema.org', '@type': 'MobileApplication', 'name': '응가메이트' if lang == 'ko' else 'POOPIEMATE',
              'alternateName': ['POOPIEMATE', '응가메이트'], 'operatingSystem': ['iOS', 'Android'], 'applicationCategory': 'LifestyleApplication',
              'description': c['desc'], 'url': f'{SITE}{url("home", lang)}', 'inLanguage': lang,
              'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'KRW' if lang == 'ko' else 'USD'},
              'author': org_ld(lang),
              'sameAs': [SNS['youtube'][1], SNS['tiktok'][1], SNS['instagram'][1][lang], SNS['linkedin'][1], APPSTORE[lang], PLAY[lang]]}
    site_ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': '응가메이트' if lang == 'ko' else 'POOPIEMATE', 'alternateName': ['POOPIEMATE', '응가메이트'],
               'url': f'{SITE}{url("home", lang)}', 'inLanguage': lang, 'publisher': org_ld(lang)}
    verify = ('<meta name="google-site-verification" content="vezMm0ELRBYYTtSoNa8gk8Smo0MrxGzfDn1pjxSJAa0">\n'
              '<meta name="naver-site-verification" content="a236950cd48d38555cc3d88c121cdfe2971aa08c">\n'
              '<meta name="msvalidate.01" content="71EA6D0F5FA0EFBBA4609AA122BA853D">\n') if lang == 'ko' else ''
    write(url('home', lang), page(lang, 'home', c['title'], c['desc'], body, f'/assets/og/poopiemate-{lang}.jpg',
                                  ld=[app_ld, site_ld, faq_ld(HOME_FAQ[lang]), video_ld(YT['service_long'][lang], c['v_label'], c['desc'], lang)], extra_head=verify, intro=True,
                                  keywords='응가메이트, POOPIEMATE, 강아지 배변 기록, 강아지 가족 공유 앱, 반려견 산책 기록, 실외배변, 진도믹스, 배변 텀 알림, 산책 안전도' if lang == 'ko' else 'POOPIEMATE, dog potty log, shared dog care app, family dog walk tracker, potty alerts'))


# ═════════════════════════════════════════════════════════ 이렇게 써요 (캔버스 「v2 이렇게 써요」 + 풀페이지)
def how(lang):
    c = {
        'ko': {'title': '이렇게 써요 — 가족이 같이 쓰는 법 | 응가메이트', 'desc': '초대 → 기록 → 알림, 세 단계면 끝. 돌봄 부탁·하트·산책 안전도까지 영상으로 보세요.',
               'label': '이렇게 써요', 'h': '가족이 같이 쓰면<br>“응댕이 똥 쌌어?” 전화가 사라져요', 'lede': '초대 → 기록 → 알림. 세 단계면 충분해요.',
               'steps': [('가족을 초대해요', '카톡으로 초대 코드를 보내면 같은 강아지를 함께 돌보는 가족이 돼요. 엄마·아빠·형제·돌봄 도우미 누구든요.', 'invite', 'house', 'purple'),
                         ('한 명이 기록하면<br>모두에게 알림이 가요', '산책에서 응가·쉬를 버튼 하나로 기록해요. 다른 가족 폰에 바로 알림이 가서 따로 물어볼 필요가 없어요.', 'record', 'pile_of_poo', 'pink'),
                         ('지금 상태를 한눈에 봐요', '마지막 응가·쉬와 신호 게이지를 홈에서 바로 봐요. 오늘 누가 산책했는지도 한눈에 보여요.', 'alerts', 'mobile_phone', 'green'),
                         ('바쁜 날엔 부탁,<br>다녀오면 하트', '“저녁 산책 부탁해!” 전화 대신 버튼 하나로 부탁해요. 다녀온 가족에게는 고맙다고 하트를 보내요.', 'family', 'love_letter', 'peach'),
                         ('오늘 언제 나가면<br>좋을까요?', '정해 둔 산책 시간이 되면 가족 모두에게 알려줘요. 체형·털·나이와 날씨로 시간별 산책 안전도도 보여줘요.', 'walk', 'sun_behind_small_cloud', 'sky')],
               'labels': {'invite': '가족 초대하는 법 모션그래픽', 'record': '기록과 가족 알림 모션그래픽', 'alerts': '배변 신호 모션그래픽', 'family': '돌봄 부탁과 하트 모션그래픽', 'walk': '산책 루틴과 안전도 모션그래픽'},
               'more_tag': '더 함께 돌보는 기능', 'more_h': '산책은 나눠서 해도,<br>기록은 <em>가족 모두가</em> 함께 봐요',
               'b1': ('가족 기록 공유', '한 명이 누르면<br>가족 폰이 울려요', '“응댕이 똥 쌌어?” 대신 알림 하나. 누가 언제 산책하고 치웠는지 하루 타임라인으로 모아 봐요.'),
               'toasts': [('응댕이가 응가를 했어요 💩', '엄마가 방금 기록했어요', '방금'), ('아빠가 하트를 보냈어요 💜', '아침 산책 기록에', '1분 전')],
               'b2': ('돌봄 부탁 · 하트', '바쁜 날엔 부탁,<br>다녀오면 하트', '“저녁 산책 부탁해!” 전화 대신 버튼 하나로.'),
               'b3': ('가족 초대', '가족 초대는<br>코드 하나면 끝', '카톡으로 코드만 보내면 같은 강아지를 함께 기록해요.'),
               'b4': ('산책 루틴 · 안전도', '오늘 언제 나가면<br>좋을까요?', '산책 시간이 되면 가족 모두에게 알려줘요. 날씨와 우리 강아지 몸에 맞춘 산책 안전도도 보여줘요.')},
        'en': {'title': 'How it works — Sharing dog care with family | POOPIEMATE', 'desc': 'Invite, log, get alerts — three steps. Watch how help requests, hearts and walk safety work.',
               'label': 'How it works', 'h': 'Share it with family and<br>the “Did Poochie poop?” calls stop', 'lede': 'Invite → log → alert. Three steps is all it takes.',
               'steps': [('Invite your family', 'Send an invite code by message and you’re caring for the same dog. Parents, siblings, the dog sitter — anyone.', 'invite', 'house', 'purple'),
                         ('One person logs it,<br>everyone gets an alert', 'Log poops and pees on the walk with one button. Everyone else gets an alert right away, so nobody has to ask.', 'record', 'pile_of_poo', 'pink'),
                         ('See where things stand', 'See the last poop and pee and how full the gauges are. Who walked today is right there on the home screen too.', 'alerts', 'mobile_phone', 'green'),
                         ('Ask on busy days,<br>thank with a heart', 'Skip the “Can you take the evening walk?” call. Ask with one button, and send a heart when they’re back.', 'family', 'love_letter', 'peach'),
                         ('When should<br>we head out?', 'Everyone gets the same reminder when it’s walk time. You also see an hourly safety score for your dog and the weather.', 'walk', 'sun_behind_small_cloud', 'sky')],
               'labels': {'invite': 'How to invite your family, motion graphic', 'record': 'Logging and family alerts, motion graphic', 'alerts': 'Potty signals, motion graphic', 'family': 'Help requests and hearts, motion graphic', 'walk': 'Walk routine and safety, motion graphic'},
               'more_tag': 'More ways to care together', 'more_h': 'Split the walks,<br>share the log with <em>everyone</em>',
               'b1': ('Shared family log', 'One tap,<br>every phone buzzes', '“Did Poochie poop?” becomes one alert. See who walked and cleaned up on one timeline.'),
               'toasts': [('Poochie just pooped 💩', 'Mom logged it just now', 'now'), ('Dad sent a heart 💜', 'On the morning walk', '1m ago')],
               'b2': ('Requests · Hearts', 'Ask on busy days,<br>thank with a heart', 'Ask for the evening walk with one button. No phone call needed.'),
               'b3': ('Family invites', 'One code<br>brings them in', 'Send a code by message. Then log the same dog together.'),
               'b4': ('Walk routine · Safety', 'When should<br>we head out?', 'Everyone gets the walk reminder. Plus a safety score for the weather and your dog.')},
    }[lang]
    steps = ''
    for i, (h, p, key, ic, tone) in enumerate(c['steps'], 1):
        steps += (f'<section class="how-step snap-sec t-{tone}" id="step-{i}" data-live><div class="wrap-mid step-grid">'
                  f'<div class="step-text"><span class="step-num">{i:02d}</span><h2 class="h2" data-mo>{h}</h2><p class="mo-fade">{sb(p)}</p></div>'
                  f'<div class="step-media"><img class="step-icon" src="/assets/img/emoji/{ic}.webp" alt="">'
                  f'<div class="step-phone">{reel(key, lang, c["labels"][key])}</div></div></div></section>')
    toasts = ''.join(f'<div class="toast"><img src="/assets/icons/apple-touch-icon.png" alt="" width="36" height="36"><span><b>{b}</b><i>{sub}</i></span><time>{t}</time></div>'
                     for b, sub, t in c['toasts'])
    bento = f'''
<div class="bento">
<div class="bento-col">
<a class="bcard b-pink tall" href="#step-2"><span class="chip">{c['b1'][0]}</span><h3 class="h3">{c['b1'][1]}</h3><p>{sb(c['b1'][2])}</p>
<div class="toasts" aria-hidden="true">{toasts}</div><img class="dog" src="/assets/img/mascot/pooping.webp" alt="" loading="lazy"><span class="go">{ARROW_R}</span></a>
<a class="bcard b-lav" href="#step-4"><span class="chip">{c['b2'][0]}</span><h3 class="h3">{c['b2'][1]}</h3><p>{sb(c['b2'][2])}</p>
<img class="obj" src="/assets/img/emoji/love_letter.webp" alt="" loading="lazy"><span class="go">{ARROW_R}</span></a>
</div>
<div class="bento-col">
<a class="bcard b-green" href="#step-1"><span class="chip">{c['b3'][0]}</span><h3 class="h3">{c['b3'][1]}</h3><p>{sb(c['b3'][2])}</p><span class="go">{ARROW_R}</span></a>
<a class="bcard b-photo tall" href="#step-5"><img class="bg" src="/assets/img/photo/lawn-walk-900.webp" alt="" loading="lazy"><span class="chip">{c['b4'][0]}</span><h3 class="h3">{c['b4'][1]}</h3><p>{sb(c['b4'][2])}</p><span class="go">{ARROW_R}</span></a>
</div>
</div>'''
    body = f'''
<section class="how-hero snap-sec"><div class="wrap">{label(c['label'])}<h1 class="h1" data-mo>{c['h']}</h1><p class="lead mo-fade">{sb(c['lede'])}</p></div>
<div class="stage" aria-hidden="true"><div class="stage-art">{icons([('house', 8, 16, -10), ('pile_of_poo', 2, 54, -8), ('paw_prints', 15, 82, 10), ('sparkles', 84, 10, 8), ('green_heart', 90, 46, 12), ('bone', 80, 78, -16)])}{waver()}</div></div></section>
{steps}
<section class="sec-more snap-sec"><div class="wrap"><div class="center-head rise"><span class="pill-tag">{c['more_tag']}</span><h2 class="h2">{c['more_h']}</h2></div>{bento}</div></section>
{cta_soft(lang)}
'''
    write(url('how', lang), page(lang, 'how', c['title'], c['desc'], body, f'/assets/og/poopiemate-{lang}.jpg', active='how', snap=True))


# ═════════════════════════════════════════════════════════ 이야기 (캔버스 「v2 이야기」)
STORY = {
    'ko': {
        'title': '응가메이트를 만든 이유', 'cat': '우리 강아지 이야기', 'date': '2026.10.07', 'by': '응가메이트를 만든 보호자',
        'excerpt': '밭 옆 견사에서 온 우리 집 강아지, 그리고 하루에도 몇 번씩 하던 “응댕이 똥 쌌어?” 전화 이야기.',
        'blocks': [
            ('p', '안녕하세요, 응가메이트를 만든 보호자예요. 앱을 만들게 된 이야기를 처음부터 차근차근 해 볼게요. 조금 길어요.'),
            ('h2', '밭 옆 견사의 분홍이'),
            ('p', '우리 집 강아지는 이제 네 살, 13kg의 하얀 진도믹스예요. 진도에 비숑이 조금 섞였는지 털이 살짝 곱슬거려요.'),
            ('p', '처음 만났을 때 이 아이는 밭 옆 견사에 짧은 줄로 묶여 지내고 있었어요. 제대로 돌봄을 받지 못한 채 바깥에서 지냈고, 그때 불리던 이름은 ‘분홍이’였어요. 구조와 임시보호를 거쳐, 이 아이는 우리 가족이 됐어요.'),
            ('img', 'pair-kennel-home', '밭 옆 견사에서 지내던 분홍이 시절 · 우리 집에 막 왔을 무렵'),
            ('p', '집에 온 첫날부터 성격이 보였어요. 낯선 사람과 큰 소리, 트럭과 움직이는 사다리를 무서워하는 겁쟁이인데, 먹을 것 앞에서는 누구보다 용감한 먹보였어요. 당근과 닭가슴살을 제일 좋아하고, 배가 고프면 앞발을 공손하게 내밀어요. 혼자서도 잘 지내는 독립적인 아이라 처음엔 곁을 잘 내주지 않았지만, 이제는 엄마아빠를 제일 좋아해요.'),
            ('h2', '집에서는 절대 안 싸는 아이'),
            ('p', '바깥에서만 지낸 시간이 길어서인지, 우리 집 강아지는 집 안에서는 절대 응가도 쉬도 하지 않아요. 패드를 깔아 줘도, 아무리 오래 참아도 꼭 밖에서만 해요. 나가고 싶을 때는 현관에서 신발을 물어 와요.'),
            ('p', '그래서 비가 오나 눈이 오나 하루 세 번, 꼭 산책을 나가요. 산책에서 하는 일은 하나예요. 최고의 똥 스팟 찾기. 바싹 마른 낙엽, 폭신한 흙바닥, 솔방울이 잔뜩 떨어진 곳이면 합격이에요.'),
            ('h2', '하루에도 몇 번씩 하던 전화'),
            ('p', '맞벌이인 저희 부부는 산책을 나눠서 해요. 문제는 그다음이었어요. 아침에 누가 데리고 나갔는지, 응가는 했는지, 쉬는 몇 번 했는지, 저녁엔 누가 나갈지. 매번 전화나 카톡으로 확인해야 했거든요.'),
            ('quote', '“응댕이 똥 쌌어?” “아침 산책은 누가 갔어?” “저녁엔 누가 나갈래?”'),
            ('p', '바쁜 날엔 전화를 놓치고, 같은 걸 두 번 묻고, 결국 산책을 두 번 나가거나 아무도 못 나가는 날도 생겼어요. 실외배변만 하는 아이라 응가를 언제 했는지는 건강과도 바로 이어지는 문제였어요. 하루 종일 참고 있는 건 아닌지, 마지막 응가가 몇 시간 전이었는지 늘 마음이 쓰였어요.'),
            ('h2', '그 전화를 버튼 하나로'),
            ('p', '그래서 그 전화를 버튼 하나로 바꾸기로 했어요. 한 사람이 응가·쉬를 기록하면 가족 모두의 폰에 바로 알림이 가는 앱이요. 누가 언제 산책하고 치웠는지는 하루 타임라인으로 모아 보고, 바쁜 날엔 산책을 부탁하고, 다녀오면 고맙다고 하트를 보내요.'),
            ('p', '한여름에는 언제 나가야 발바닥이 뜨겁지 않을지가 늘 고민이었어요. 그래서 우리 강아지의 체형과 털, 나이에 날씨를 더한 산책 안전도를 넣었어요. 배변 텀으로 차오르는 응가·쉬 게이지는 “오늘은 좀 오래 참고 있네”를 가족 모두가 같이 알아차리게 해 줘요.'),
            ('img', 'pair-walk-family', '같이 나간 산책 · 가족이 다 같이 모인 날'),
            ('h2', '응댕이는 우리 집 강아지를 닮았어요'),
            ('p', '응가메이트의 캐릭터 응댕이는 우리 집 강아지에서 왔어요. 똥 모양 얼굴에 축 처진 큰 귀, 먹보에 겁쟁이, 배고프면 앞발을 내미는 것까지요. 앱을 켤 때마다 손을 흔드는 응댕이를 보면, 현관에서 신발을 물고 기다리는 우리 집 강아지가 떠올라요.'),
            ('p', '강아지를 여럿이 같이 돌보는 집이라면, 응가메이트가 “응댕이 똥 쌌어?” 전화를 조금이라도 줄여 주면 좋겠어요. 오늘도 우리 집 강아지는 최고의 똥 스팟을 찾아 산책을 나가요.'),
        ]},
    'en': {
        'title': 'Why we built POOPIEMATE', 'cat': 'Our dog', 'date': 'Oct 7, 2026', 'by': 'The family behind POOPIEMATE',
        'excerpt': 'Our dog from a farm-side kennel, and the “Did she poop?” calls we made every single day.',
        'blocks': [
            ('p', 'Hi, we’re the family behind POOPIEMATE. Here’s how the app came to be, from the very beginning. It’s a bit of a long one.'),
            ('h2', 'Bunhong-i, from a kennel by the field'),
            ('p', 'Our dog is now four, a 13 kg white Jindo mix. There’s a little Bichon in her somewhere — her fur curls slightly.'),
            ('p', 'When we first met her, she lived on a short chain in a kennel next to a farm field. She hadn’t been looked after properly, and back then she was called “Bunhong-i” — little pinky. After a rescue and a stay in foster care, she became part of our family.'),
            ('img', 'pair-kennel-home', 'Her days at the farm kennel · her first weeks with us'),
            ('p', 'Her personality showed from day one. She’s a scaredy-cat around strangers, loud voices, trucks and moving ladders — but the bravest of us all in front of food. She loves carrots and chicken breast, and when she’s hungry she politely offers a paw. She’s independent and kept her distance at first, but now her favorite people are Mom and Dad.'),
            ('h2', 'A dog who never goes indoors'),
            ('p', 'Maybe because she spent so long outside, our dog never poops or pees indoors. Not on a pad, not even when she’s been holding it for hours. When she wants to go out, she brings us a shoe from the doorway.'),
            ('p', 'So rain or snow, she goes out three times a day. On every walk she has one mission: find the best poop spot. Crunchy dry leaves, soft dirt, or a patch covered in pinecones all pass the test.'),
            ('h2', 'The calls we made every day'),
            ('p', 'We’re a working couple, so we split the walks. The trouble came after. Who took her out this morning? Did she poop? How many pees? Who’s going tonight? We had to check by phone or message every time.'),
            ('quote', '“Did she poop?” “Who took the morning walk?” “Who’s going out tonight?”'),
            ('p', 'On busy days we missed calls, asked the same thing twice, and sometimes she got walked twice — or not at all. For a dog who only goes outside, when she last pooped is a health question too. We always wondered whether she’d been holding it all day.'),
            ('h2', 'Turning that call into a button'),
            ('p', 'So we decided to turn that call into a single button. One person logs a poop or pee and everyone in the family gets an alert right away. A daily timeline shows who walked and cleaned up, you can ask someone else to take the walk on a busy day, and send a heart when they’re back.'),
            ('p', 'In summer we always worried about hot pavement, so we added a walk safety score that combines her body type, coat and age with the weather. The potty gauges, filling up with her rhythm, let the whole family notice when she’s been holding it a little too long.'),
            ('img', 'pair-walk-family', 'Out for a walk together · a day with the whole family'),
            ('h2', 'Poochie looks just like her'),
            ('p', 'Our mascot Poochie comes straight from our dog: a poop-shaped face, big floppy ears, a foodie and a scaredy-cat who offers a paw when she’s hungry. Every time Poochie waves on the app’s screen, we think of her waiting at the door with a shoe in her mouth.'),
            ('p', 'If your family shares one dog, we hope POOPIEMATE cuts down on the “Did Poochie poop?” texts, even a little. And today, as always, our dog is out looking for the best poop spot.'),
        ]},
}


LANDSCAPE = {'family-lawn', 'pair-kennel-home', 'pair-walk-family'}  # 나머지 사진은 세로 — 원본 비율 그대로, 폭만 좁게


def post_head(meta, title, art):
    return f'<p class="post-meta">{meta}</p><h1 class="post-h1">{title}</h1>{art}'


def story_list(lang):
    s = STORY[lang]
    c = {'ko': ('이야기', '응가메이트를 만든 가족이 겪은 이야기를 모아요', '이야기 — 응가메이트를 만든 가족 이야기', '응가메이트를 만든 가족과 우리 집 강아지 이야기. “응댕이 똥 쌌어?” 전화가 버튼 하나가 되기까지를 기록해요.',
                ['전체', '우리 강아지 이야기', '만드는 이야기', '보호자 이야기'],
                [('우리 강아지 이야기', '[다음 글] 분홍이가 우리 가족이 되기까지', '밭 옆 견사에서 우리 집 거실까지. 실외배변 루틴이 생긴 이야기.', 'photo:kennel-house'),
                 ('만드는 이야기', '[다음 글] 가족이 같이 기록하면 무엇이 달라질까', '초기 사용자 기록을 보고 가족 초대를 먼저 고친 과정.', 'emoji')], '준비 중'),
         'en': ('Stories', 'Notes from the family behind POOPIEMATE', 'Stories — The family behind POOPIEMATE', 'Stories from the family and the dog behind POOPIEMATE.',
                ['All', 'Our dog', 'Making the app', 'Owner stories'],
                [('Our dog', '[Coming up] How Bunhong-i became family', 'From a farm-side kennel to our living room, and how her outdoor potty routine began.', 'photo:kennel-house'),
                 ('Making the app', '[Coming up] What changes when a family logs together', 'What early users’ logs taught us, and why we fixed family invites first.', 'emoji')], 'Coming soon')}[lang]
    cats = c[4]
    chips = ''.join(f'<button type="button" data-cat="{"all" if i == 0 else i}" aria-pressed="{"true" if i == 0 else "false"}">{x}</button>' for i, x in enumerate(cats))
    first = (f'<a class="post-card" data-cat="1" href="{url("why", lang)}"><span class="thumb"><img src="/assets/img/photo/family-lawn-900.webp" alt="" loading="lazy">{new_badge("2026-10-07")}</span>'
             f'<span class="cat">{cats[1]}</span><b>{s["title"]}</b><span class="ex">{sb(s["excerpt"])}</span><time datetime="2026-10-07">{s["date"]}</time></a>')
    soon = ''
    for cat, t, ex, art in c[5]:
        thumb = (f'<img src="/assets/img/photo/{art[6:]}-900.webp" alt="" loading="lazy">' if art.startswith('photo:')
                 else '<span class="emoji-tile"><img src="/assets/img/emoji/house.webp" alt=""><img src="/assets/img/emoji/growing_heart.webp" alt=""></span>')
        soon += (f'<div class="post-card soon" data-cat="{cats.index(cat)}" aria-disabled="true"><span class="thumb">{thumb}</span>'
                 f'<span class="cat">{cat}</span><b>{t}</b><span class="ex">{sb(ex)}</span><span class="date">{c[6]}</span></div>')
    body = f'''
<section class="list-page"><div class="wrap-list">
{list_head('love_letter', c[0], c[1])}
<div class="chips" data-filter role="group" aria-label="{c[0]}">{chips}</div>
<div class="post-grid">{first}{soon}</div>
{empty_state(lang, 'story')}
</div></section>
'''
    write(url('story', lang), page(lang, 'story', c[2] + (' | 응가메이트' if lang == 'ko' else ''), c[3], body, f'/assets/og/poopiemate-{lang}.jpg', active='story'))


def story_why(lang):
    s = STORY[lang]
    out = []
    for b in s['blocks']:
        if b[0] == 'p':
            out.append(f'<p>{b[1]}</p>')
        elif b[0] == 'quote':
            out.append(f'<blockquote>{b[1]}</blockquote>')
        elif b[0] == 'img':
            o = 'l' if b[1] in LANDSCAPE else 'p'
            out.append(f'<figure class="fig {o}"><img src="/assets/img/photo/{b[1]}-1600.webp" srcset="/assets/img/photo/{b[1]}-900.webp 900w, /assets/img/photo/{b[1]}-1600.webp 1600w" '
                       f'sizes="{"(min-width: 1100px) 1040px, 96vw" if o == "l" else "(min-width: 600px) 480px, 92vw"}" alt="{escape(b[2])}" loading="lazy"><figcaption>{b[2]}</figcaption></figure>')
        elif b[0] == 'h2':
            out.append(f'<h2>{b[1]}</h2>')
    art = art_card('pooping', [('house', 'left:5%;top:30px', 86, -10), ('growing_heart', 'left:24%;top:120px', 49, 10), ('love_letter', 'left:6%;top:196px', 71, 8),
                               ('paw_prints', 'right:31%;top:23px', 53, 16), ('sparkles', 'right:8%;top:38px', 75, 10), ('bone', 'right:21%;top:162px', 56, -22),
                               ('green_heart', 'right:6%;top:199px', 75, -8)])
    body = f'''
<article class="post"><div class="wrap-post">
{post_head(f'<time datetime="2026-10-07">{s["date"]}</time> · {s["by"]}', s['title'], art)}
<div class="prose">{''.join(out)}</div>
<div class="post-end"><a class="btn-block btn-grey" href="{url('story', lang)}">{T[lang]['back']}</a></div>
</div></article>
'''
    ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': s['title'], 'description': s['excerpt'], 'datePublished': '2026-10-07', 'inLanguage': lang,
          'image': f'{SITE}/assets/og/poopiemate-{lang}.jpg', 'author': {'@type': 'Organization', 'name': '응가메이트' if lang == 'ko' else 'POOPIEMATE'},
          'publisher': org_ld(lang)}
    title = s['title'] + (' | 응가메이트 이야기' if lang == 'ko' else ' | POOPIEMATE')
    write(url('why', lang), page(lang, 'why', title, s['excerpt'], body, f'/assets/og/poopiemate-{lang}.jpg', active='story', og_type='article', ld=[ld]))


# ═════════════════════════════════════════════════════════ 공지사항 (캔버스 「v2 공지사항」)
NOTICE = {
    'ko': {'title': '응가메이트 유저 인터뷰에 초대해요', 'date': '2026.10.05', 'by': '응가메이트 팀', 'sub': '보호자님 이야기를 들려주세요. 참여하면 폴 바셋 아이스크림 라떼를 드려요.',
           'body': ['안녕하세요, 응가메이트 팀이에요.<br>매일 강아지의 응가·쉬·산책을 기록해 주셔서 정말 고마워요.',
                    '더 쓰기 편한 응가메이트를 만들고 싶어서, 보호자님의 이야기를 직접 듣고 싶어요.',
                    '<ul><li>앱을 어떻게 쓰고 계신지</li><li>어떤 점이 좋았고, 어떤 점이 아쉬웠는지</li><li>가족과 함께 기록할 때는 어땠는지</li></ul>',
                    '정답은 없어요. 편하게 이야기 나눠 주시면 돼요.', '참여해 주신 분께는 폴 바셋 아이스크림 라떼 기프티콘을 보내드려요.',
                    '원하는 날짜와 시간을 골라 신청해 주세요. 일정이 확정되면 남겨 주신 번호로 연락드릴게요.'],
           'apply': '인터뷰 신청하기', 'pinned': '고정'},
    'en': {'title': 'Join a POOPIEMATE user interview', 'date': 'Oct 5, 2026', 'by': 'POOPIEMATE team', 'sub': 'Tell us how you use POOPIEMATE. Interviews are in English and take about 30 minutes.',
           'body': ['Hi from the POOPIEMATE team.<br>Thank you for logging your dog’s poops, pees and walks every day.',
                    'We want to make POOPIEMATE easier to use, so we’d love to hear from you directly.',
                    '<ul><li>How you use the app</li><li>What you like and what could be better</li><li>What logging with your family is like</li></ul>',
                    'There are no right answers — just chat with us.',
                    'Interviews are in English and take about 30 minutes online.',
                    'Pick a date and a time in your own time zone. We’ll contact you once the schedule is confirmed.'],
           'apply': 'Apply for an interview', 'pinned': 'Pinned'},
}


def notice_list(lang):
    n = NOTICE[lang]
    c = {'ko': ('공지사항', '업데이트와 이벤트 소식을 알려드려요', '공지사항 | 응가메이트', '가족이 함께 보는 강아지 응가 기록 앱, 응가메이트의 업데이트와 이벤트 소식을 알려드려요.'),
         'en': ('Notices', 'Updates and events from POOPIEMATE', 'Notices | POOPIEMATE', 'Updates and events from POOPIEMATE, the dog potty log your whole family shares.')}[lang]
    body = f'''
<section class="list-page"><div class="wrap-list">
{list_head('megaphone', c[0], c[1])}
<div class="post-grid">
<a class="post-card" href="{url('interview_notice', lang)}"><span class="thumb green"><img src="/assets/img/notice-hero.webp" alt="" loading="lazy" width="1038" height="510">{new_badge("2026-10-05")}<span class="pin-ic" role="img" aria-label="{n['pinned']}">{PIN_ICON}</span></span>
<b>{n['title']}</b><span class="ex">{sb(n['sub'])}</span><time datetime="2026-10-05">{n['date']}</time></a>
</div>
{empty_state(lang, 'notice')}
</div></section>
'''
    write(url('notice', lang), page(lang, 'notice', c[2], c[3], body, f'/assets/og/poopiemate-{lang}.jpg', active='notice'))


def notice_interview(lang):
    n = NOTICE[lang]
    art = '<img class="notice-hero" src="/assets/img/notice-hero.webp" alt="" width="1038" height="510">'
    body = f'''
<article class="post"><div class="wrap-post">
{post_head(f'<time datetime="2026-10-05">{n["date"]}</time> · {n["by"]}', n['title'], art)}
<div class="prose">{''.join(b if b.startswith('<ul') else f'<p>{sb(b)}</p>' for b in n['body'])}</div>
<div class="post-end two"><a class="btn-block btn-grey" href="{url('notice', lang)}">{T[lang]['back']}</a><a class="btn-block btn-dark" href="{'/interview/' if lang == 'ko' else '/en/interview/'}">{n['apply']}{EXT_ICON}</a></div>
</div></article>
'''
    write(url('interview_notice', lang), page(lang, 'interview_notice', n['title'] + (' | 응가메이트' if lang == 'ko' else ' | POOPIEMATE'), n['sub'], body,
                                              f'/assets/og/poopiemate-{lang}.jpg', active='notice', og_type='article'))


# ═════════════════════════════════════════════════════════ 정책 (옛 poopiemate-legal에서 옮겨 옴 — 본문은 그대로, 겉모양만)
LEGAL_DESC = {
    'privacy': ('응가메이트가 어떤 개인정보를 왜 모으고 어떻게 지키는지 알려드려요. 수집 항목, 이용 목적, 보관 기간, 이용자의 권리를 담았어요.',
                'What personal data POOPIEMATE collects, why, how long we keep it and how we protect it, plus your rights under Korean, UK and EU law.'),
    'terms': ('응가메이트를 쓸 때 지켜야 할 약속과 서비스 이용 조건을 담은 이용약관이에요. 금지 콘텐츠 신고 방법도 안내해요.',
              'The terms for using POOPIEMATE: your account, family sharing, prohibited content and how to report it, and our responsibilities.'),
    'support': ('응가메이트를 쓰다 궁금한 점이 생기면 이메일로 물어봐 주세요. 자주 묻는 질문과 계정 삭제 방법도 안내해요.',
                'Questions about POOPIEMATE? Email us. Answers to common questions and how to delete your account.'),
    'licenses': ('응가메이트 앱에 쓰인 오픈소스 소프트웨어와 각 라이선스 전문을 모았어요.',
                 'Open-source software used in the POOPIEMATE app, with the full text of each license.'),
}


def legal(name, lang):
    src = (SRC / f'legal/{name}-{lang}.html').read_text(encoding='utf-8')
    title = html_mod.unescape(re.search(r'<title>(.*?)</title>', src, re.S).group(1)).strip()
    m = re.search(r'<div class="container">(.*)</div>\s*(<script>.*?</script>)?\s*</body>', src, re.S)
    inner, script = m.group(1), m.group(2) or ''
    inner = re.sub(r'\s*<footer>.*?</footer>', '', inner, flags=re.S)
    inner = re.sub(r'\s*<div class="app-name">.*?</div>', '', inner, flags=re.S)
    inner = re.sub(r'\s*<div class="lang-switch">.*?</div>', '', inner, flags=re.S)
    inner = inner.replace('<header>', '<div class="legal-head">', 1).replace('</header>', '</div>', 1)
    inner = inner.replace('<h1>', '<h1 class="post-h1">', 1)
    inner = re.sub(r'href="\./(privacy|terms|support|licenses)-(ko|en)(#[^"]*)?"', lambda m: f'href="{url(m.group(1), m.group(2))}{m.group(3) or ""}"', inner)
    if name == 'support':  # 문의 메일은 응가메이트 대표 메일로
        inner = inner.replace('jin@pixelberry.io', EMAIL)
    body = f'<article class="post legal"><div class="wrap-post"><div class="prose">{inner}</div></div></article>\n{script}'
    write(url(name, lang), page(lang, name, title, LEGAL_DESC[name][0 if lang == 'ko' else 1], body, f'/assets/og/poopiemate-{lang}.jpg', active=None))


# ═════════════════════════════════════════════════════════ 검색 가이드 (옛 글 — 새 디자인으로)
def guides():
    for f in sorted((SRC / 'legacy/guides').glob('*.json')):
        g = json.loads(f.read_text(encoding='utf-8'))
        main = g['main']
        main = re.sub(r'<h1>(.*?)</h1>', r'<h1 class="h1">\1</h1>', main, count=1, flags=re.S)
        main = main.replace(' style="margin-top:8px;"', '').replace(' style="margin:0;"', '')
        h1 = re.search(r'<h1 class="h1">(.*?)</h1>', main, re.S)
        rest = main[h1.end():] if h1 else main
        body = f'''
<article class="post"><div class="wrap-post">
<p class="post-meta"><a href="/">응가메이트</a> › 강아지 배변 가이드</p>{h1.group(0).replace('class="h1"', 'class="post-h1"') if h1 else ''}
<div class="prose">{rest}</div></div></article>
{cta_band('ko')}
'''
        write(f'/{g["slug"]}/', page('ko', None, g['title'], g['description'], body, '/assets/og/poopiemate-ko.jpg', ko_path=f'/{g["slug"]}/', en_path=None,
                                     og_type='article', ld=g['ld'], keywords=g['keywords']))


# ═════════════════════════════════════════════════════════ 인터뷰 신청 (폼·스크립트는 그대로, 겉모양만)
def interview(lang):
    """인터뷰 신청 — 한국어는 /interview/, 영어는 /en/interview/ (폼·전송 스크립트는 옛 페이지 그대로, 겉모양만 사이트 디자인)."""
    ko = lang == 'ko'
    s = (SRC / f'legacy/interview{"" if ko else "-en"}.html').read_text(encoding='utf-8')
    s = re.sub(r'\n\s*@font-face \{ font-family:"NanumSquareNeo";[^}]*\}', '', s)
    # 옛 헤더·푸터 규칙은 새 헤더·푸터와 겹치지 않게 본문(main)에만
    s = re.sub(r'header, main, footer \{', 'main.iv {', s, count=1)
    s = re.sub(r'\n\s*header \{ padding-top: 28px; padding-bottom: 8px; \}', '', s)
    s = re.sub(r'\n\s*footer \{[^}]*\}\n\s*footer a \{[^}]*\}', '', s)
    s = s.replace('진도믹스 메로나 보호자예요.', '하얀 진도믹스를 키우는 보호자예요.')  # 공개 문구에 실제 이름은 쓰지 않는다
    s = s.replace('--bg: #ebf7f2;', '--bg: #F2F4F6;').replace('--ink: #1d1f1f;', '--ink: #191F28;').replace('--muted: #56655c;', '--muted: #4E5968;').replace('--line: #d8ebe3;', '--line: #E5E8EB;')
    s = re.sub(r'\n\s*h1 \{', '\n    main.iv h1 {', s, count=1)
    s = re.sub(r'\n\s*h2 \{', '\n    main.iv h2 {', s, count=1)
    s = s.replace('font-family: "NanumSquareNeo", -apple-system', 'font-family: "Pretendard Variable", Pretendard, -apple-system', 1)
    s = s.replace('  <link rel="icon" type="image/png" href="https://poopiemate.com/assets/favicon.png">\n', '')
    s = s.replace('  <link rel="apple-touch-icon" href="https://poopiemate.com/assets/favicon.png">\n', '')
    path = '/interview/' if ko else '/en/interview/'
    og = ('응가메이트', '응가메이트 유저 인터뷰 신청', '보호자님 이야기를 들려주세요. 참여하면 폴 바셋 아이스크림 라떼를 드려요.') if ko else \
         ('POOPIEMATE', 'POOPIEMATE user interview', 'Tell us how you use POOPIEMATE. Interviews are in English and take about 30 minutes.')
    head_add = (PRETENDARD + '\n<link rel="stylesheet" href="/assets/css/site.css?v=' + ASSET_V + '">\n'
                '<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">\n'
                f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="{og[0]}">\n<meta property="og:title" content="{og[1]}">\n'
                f'<meta property="og:description" content="{og[2]}">\n<meta property="og:url" content="{SITE}{path}">\n'
                f'<meta property="og:image" content="{SITE}/assets/og/poopiemate-{lang}.jpg">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="robots" content="noindex, follow">\n'
                f'<link rel="alternate" hreflang="ko" href="{SITE}/interview/">\n<link rel="alternate" hreflang="en" href="{SITE}/en/interview/">\n'
                '<style>:root{--pink-dark:#A2479A}</style>\n')
    s = s.replace('</head>', head_add + '</head>', 1)
    s = re.sub(r'<header>.*?</header>', header(lang, 'notice', '/interview/', '/en/interview/'), s, count=1, flags=re.S)
    s = s.replace('<main>', '<main class="iv" id="main">', 1)
    s = s.replace('<body>', '<body class="iv-page">', 1)
    s = s.replace('꾸준히 응가메이트를 사용해주신 분들께 보내는 인터뷰 신청 페이지입니다.', '응가메이트를 쓰는 보호자님의 이야기를 듣고 싶어요. 원하는 날짜와 시간을 골라 인터뷰를 신청해 주세요.')
    # <p> 안에 목록(ul)은 들어갈 수 없다 — 안내 문단을 div로 (웹표준)
    s = re.sub(r'<p class="hint">(\s*[^<]*<ul>.*?</ul>\s*)</p>', r'<div class="hint">\1</div>', s, flags=re.S)
    s = re.sub(r'<footer>.*?</footer>', footer(lang, '/interview/', '/en/interview/'), s, count=1, flags=re.S)
    s = s.replace('</body>', f'<script src="/assets/js/store-region.js?v={ASSET_V}" defer></script>\n<script src="/assets/js/site.js?v={ASSET_V}" defer></script>\n</body>', 1)
    out = ROOT / path.strip('/') / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding='utf-8')


# ═════════════════════════════════════════════════════════ 다운로드 (스토어로 바로 보내기)
def download():
    html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>응가메이트 다운로드 — iOS·Android 앱 받기</title>
<meta name="description" content="응가메이트를 App Store 또는 Google Play에서 무료로 받으세요. 가족이 함께 강아지 응가·산책을 기록하는 앱이에요.">
<link rel="canonical" href="{SITE}/download/">
<meta name="theme-color" content="#18955A">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/icons/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="응가메이트">
<meta property="og:title" content="응가메이트 무료 다운로드">
<meta property="og:description" content="기록하면 가족 모두에게 바로 알림! 댕댕이 응가·산책을 함께 챙겨요.">
<meta property="og:url" content="{SITE}/download/">
<meta property="og:image" content="{SITE}/assets/og/poopiemate-ko.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/og/poopiemate-ko.jpg">
{PRETENDARD}
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
<script src="/assets/js/store-region.js?v={ASSET_V}"></script>
<script>
  (function () {{
    var ua = navigator.userAgent || navigator.vendor || '';
    var ios = /iPhone|iPad|iPod|Macintosh|Mac OS X/.test(ua);
    var en = /[?&]lang=en/.test(location.search) || (!/[?&]lang=ko/.test(location.search) && !/^ko/i.test(navigator.language || 'ko'));
    var apple = en ? (window.pmAppStoreUrl ? window.pmAppStoreUrl('{APPSTORE['en']}') : '{APPSTORE['en']}') : '{APPSTORE['ko']}';
    location.replace(ios ? apple : (en ? '{PLAY['en']}' : '{PLAY['ko']}'));
  }})();
</script>
</head>
<body>
<main class="wrap" style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:20px">
<img src="/assets/brand/wordmark-ko-green.svg" alt="응가메이트" width="150" height="40">
<p class="lede">앱 스토어로 이동하고 있어요. 바로 열리지 않으면 아래에서 골라 주세요.</p>
{stores('ko')}
</main>
</body>
</html>
'''
    (ROOT / 'download/index.html').write_text(html, encoding='utf-8')


# ═════════════════════════════════════════════════════════ 404 · sitemap
def not_found():
    body = '''
<section class="nf"><div class="wrap"><img src="/assets/img/mascot/scratch.webp" alt="" width="200">
<h1 class="h1">페이지를 찾지 못했어요</h1><p class="lead">주소가 바뀌었거나 없는 페이지예요. <span lang="en">Page not found.</span></p>
<div class="nf-btns"><a class="btn-block btn-dark" href="/">홈으로</a><a class="btn-block btn-grey" href="/en/">English</a></div></div></section>
'''
    (ROOT / '404.html').write_text(page('ko', 'home', '페이지를 찾지 못했어요 | 응가메이트', '찾는 페이지가 없어요. 응가메이트 홈에서 가족이 함께 보는 강아지 응가 기록을 만나 보세요.', body, '/assets/og/poopiemate-ko.jpg', noindex=True), encoding='utf-8')


def sitemap():
    rows = []
    for key, (ko, en) in PATHS.items():
        pr = '1.0' if key == 'home' else '0.8'
        for loc in (ko, en):
            rows.append(f'''  <url><loc>{SITE}{loc}</loc><lastmod>{UPDATED}</lastmod><priority>{pr}</priority>
    <xhtml:link rel="alternate" hreflang="ko" href="{SITE}{ko}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{ko}"/></url>''')
    rows.append(f'  <url><loc>{SITE}/download/</loc><lastmod>{UPDATED}</lastmod><priority>0.6</priority></url>')
    for f in sorted((SRC / 'legacy/guides').glob('*.json')):
        rows.append(f'  <url><loc>{SITE}/{f.stem}/</loc><lastmod>{UPDATED}</lastmod><priority>0.6</priority></url>')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                                      + '\n'.join(rows) + '\n</urlset>\n', encoding='utf-8')


if __name__ == '__main__':
    for lang in ('ko', 'en'):
        home(lang); how(lang); story_list(lang); story_why(lang); notice_list(lang); notice_interview(lang)
        for n in ('privacy', 'terms', 'support', 'licenses'):
            legal(n, lang)
    guides(); interview('ko'); interview('en'); download(); not_found(); sitemap()
    print('built')
