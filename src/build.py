"""응가메이트 웹사이트 빌드 — 한국어(/)·영어(/en/) 페이지를 같은 틀로 만든다.

python3 src/build.py          # 페이지 HTML + sitemap.xml
에셋 준비는 src/prepare_assets.py, OG 이미지는 src/og.py.
"""
import html as html_mod, json, re, subprocess
from html import escape
from pathlib import Path
from PIL import Image

import tools

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
SITE = 'https://poopiemate.com'
UPDATED = '2026-10-30'
ASSET_V = '51'  # css·js 캐시 갱신용 — 바꿀 때마다 올린다

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
SHARE_ICON = CHEV.replace('m{d}', 'M12 15V3M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6')
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
        'name': '응가메이트', 'nav': [('how', '이렇게 써요'), ('story', '이야기'), ('guide', '가이드'), ('notice', '공지사항')], 'cta': '앱 다운로드', 'cta_short': '앱 받기',
        'menu': '메뉴 열기', 'close': '메뉴 닫기', 'skip': '본문으로 건너뛰기', 'get': '지금 다운로드', 'lang_label': '언어',
        'f_links': [('고객 지원', '/support/'), ('개인정보 처리방침', '/privacy/'), ('이용약관', '/terms/'), ('오픈소스 라이선스', '/licenses/')],
        'operator': f'운영 픽셀베리 · 문의 <a href="mailto:{EMAIL}">{EMAIL}</a>', 'copy': '© 2026 픽셀베리 · 응가메이트',
        'play': '영상 재생', 'more': '자세히 보기', 'back': '목록으로', 'share': '공유하기', 'copied': '링크를 복사했어요', 'next': '다음 글', 'read': '이야기 읽기',
    },
    'en': {
        'name': 'POOPIEMATE', 'nav': [('how', 'How it works'), ('story', 'Stories'), ('guide', 'Guides'), ('notice', 'Notices')], 'cta': 'Get the app', 'cta_short': 'Get the app',
        'menu': 'Open menu', 'close': 'Close menu', 'skip': 'Skip to content', 'get': 'Download on the', 'lang_label': 'Language',
        'f_links': [('Support', '/en/support/'), ('Privacy Policy', '/en/privacy/'), ('Terms of Service', '/en/terms/'), ('Open-source licenses', '/en/licenses/')],
        'operator': f'Operated by Pixelberry · <a href="mailto:{EMAIL}">{EMAIL}</a>', 'copy': '© 2026 Pixelberry · POOPIEMATE',
        'play': 'Play video', 'more': 'Learn more', 'back': 'Back to list', 'share': 'Share', 'copied': 'Link copied', 'next': 'Next story', 'read': 'Read the story',
    },
}
# 페이지 키 → (한국어 경로, 영어 경로)
PATHS = {
    'home': ('/', '/en/'), 'how': ('/how-it-works/', '/en/how-it-works/'), 'story': ('/story/', '/en/story/'),
    'why': ('/story/why-i-built-poopiemate/', '/en/story/why-i-built-poopiemate/'),
    'solo': ('/story/developer-to-solo-builder/', '/en/story/developer-to-solo-builder/'), 'guide': ('/guide/', '/en/guide/'), 'notice': ('/notice/', '/en/notice/'),
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
            f'<div class="sheet" id="menu" tabindex="-1" role="dialog" aria-modal="true" aria-label="{t["name"]}" aria-hidden="true">'
            f'<div class="sheet-top"><a href="{url("home", lang)}">{logo}</a><button type="button" class="gnb-menu" aria-label="{t["close"]}" data-menu-close>{CLOSE_ICON}</button></div>'
            f'<nav aria-label="{"모바일 메뉴" if lang == "ko" else "Mobile menu"}">{nav}<a href="/download/?lang={lang}">{t["cta"]}</a></nav>'
            f'<div class="sheet-lang">{lang_links(lang, ko_path, en_path, "sheet")}</div>{sns_links(lang)}</div>')


def footer(lang, ko_path, en_path):
    t = T[lang]
    links = [(label, url(k, lang)) for k, label in t['nav']] + t['f_links']
    priv = next(label for label, h in t['f_links'] if 'privacy' in h)
    nav = ''.join(f'<a href="{h}"{" class=" + chr(34) + "strong" + chr(34) if label == priv else ""}>{label}</a>' for label, h in links)
    return (f'<footer class="footer"><div class="wrap">'
            f'<div class="f-row"><img src="/assets/brand/wordmark-{lang}-green.svg" alt="{t["name"]}" width="{"105" if lang == "ko" else "140"}" height="28">{sns_links(lang)}</div>'
            f'<div class="f-mid"><nav class="f-links" aria-label="{"사이트 링크" if lang == "ko" else "Site links"}">{nav}</nav>'
            f'<span class="lang-switch">{lang_links(lang, ko_path, en_path, "foot")}</span></div>'
            f'<div class="f-bottom"><span>{t["operator"]}</span><span>{t["copy"]}</span></div>'
            f'</div></footer>')


# ═════════════════════════════════════════════════════════ 페이지별 공유 이미지(OG)
# 페이지마다 다른 OG 이미지 — 응댕이 포즈 + 페이지 제목을 src/og.py가 1200×630으로 그린다 (assets/og/p/<slug>.jpg).
# 홈만 브랜드 이미지(poopiemate-{ko,en}.jpg). 빌드가 그릴 목록을 .cache/og/pages.json에 남긴다.
OG_PAGES = {}
OG_CHIP = {'ko': {'poop': '강아지 가이드', 'walk': '강아지 가이드', 'tool': '무료 도구', 'story': '이야기', 'notice': '공지사항', 'brand': '응가메이트', 'plain': '응가메이트'},
           'en': {'poop': 'Dog guide', 'walk': 'Dog guide', 'tool': 'Free tool', 'story': 'Stories', 'notice': 'Notices', 'brand': 'POOPIEMATE', 'plain': 'POOPIEMATE'}}
# 「응가메이트」 칩은 바로 위 로고와 겹쳐서 — 페이지 성격으로
OG_CHIP_SLUG = {s: {'ko': '이용 안내', 'en': 'Policies'} for s in ('privacy', 'terms', 'licenses')}
OG_CHIP_SLUG.update({'support': {'ko': '고객 지원', 'en': 'Support'}, 'how-it-works': {'ko': '이렇게 써요', 'en': 'How it works'},
                     'interview': {'ko': '유저 인터뷰', 'en': 'User interview'}, 'download': {'ko': '무료 앱', 'en': 'Free app'}, '404': {'ko': '길을 잃었어요', 'en': 'Lost'}})
# 응댕이 포즈 — 승인된 9개 중에서 (~/Desktop/응가메이트/홈페이지_v3_레이어/응댕이/포즈/)
OG_POSE = {'poop': '응가중', 'walk': '안녕', 'tool': '응가중', 'story': '배보여주기', 'notice': '귀쫑긋', 'brand': '안녕', 'plain': '앉아있기'}
OG_POSE_SLUG = {  # 가이드 글 머리 포즈 — OG 장면(src/og_scenes.py)과 같은 포즈. 2026-10-30에 만든 주제별 포즈(src/art/poses-new) 포함
    'walk-safety-index': 'leash', 'dog-diarrhea-causes': 'tummy', 'dog-constipation-causes': '응가전', 'yellow-gray-dog-poop': '귀쫑긋', 'how-to-get-golden-poop': 'trophy',
    'kibble-vs-cooked-vs-raw-poop': 'bowl', 'puppy-potty-count-by-size': 'family', 'dog-outdoor-potty-why': '응가중', 'outdoor-potty-holding-risks': 'door',
    'why-dogs-kick-after-pooping': 'kick', 'potty-interval': 'clock', 'jindo-mix-potty-training': '귀쫑긋', 'outdoor-potty-dog-tracking': 'phone',
    'dual-income-dog-walk-schedule': 'laptop', 'share-dog-potty-log-with-family': 'letter', 'multi-dog-household-tracking': 'baby-walk', 'poop-condition-guide': 'magnify',
    'guide': '안녕', 'notice': '귀쫑긋', 'interview': 'mic', 'support': 'letter', 'how-it-works': 'phone', 'download': '애교', '404': '긁기',
}


# 포즈 → 사이트에 올린 웹용 이미지 (assets/img/mascot/)
POSE_WEB = {'응가중': 'pooping', '응가전': 'squat', '귀쫑긋': 'ears', '긁기': 'scratch', '배보여주기': 'belly', '안녕': 'hello', '앉아있기': 'sit', '애교': 'beg',
            **{k: k for k in ('magnify', 'tummy', 'bowl', 'clock', 'kick', 'leash', 'phone', 'laptop', 'mic', 'letter', 'trophy', 'door', 'baby', 'baby-ball', 'family', 'baby-walk')}}


def og_image_for(path, lang, title, body, kind, desc=''):
    """이 페이지만의 OG 이미지 주소를 정하고, 그릴 내용(제목·부제·포즈·바탕)을 OG_PAGES에 남긴다."""
    slug = path.strip('/').replace('/', '-') or 'home'
    m = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    head = m.group(1) if m else re.split(r' [|—] ', title)[0]
    sub = ''
    sm = re.search(r'<span>(.*?)</span>', head, re.S)  # 가이드 글 제목은 <span>에 부제가 들어 있다
    if sm:
        sub, head = html_mod.unescape(sm.group(1)).strip(), head.replace(sm.group(0), '')
    head = html_mod.unescape(re.sub(r'<(?!br)[^>]+>', '', re.sub(r'<br\s*/?>', '<br>', head))).strip()
    # 「제목, 부제」「제목? 부제」는 두 줄로 — 큰 제목은 짧게
    if '<br>' not in head:
        parts = re.split(r'(?<=[?？])\s+|,\s+', head, maxsplit=1)
        if len(parts) == 2 and len(parts[0]) >= 6:
            head, sub = parts[0], parts[1]
    # 「이야기」「공지사항」처럼 짧은 제목은 설명 첫 문장을 부제로
    if not sub and '<br>' not in head and len(head) < 12 and desc:
        sub = re.split(r'(?<=[.!?])\s', desc)[0].rstrip('.')
    base = slug[3:] if slug.startswith('en-') else slug
    chip = OG_CHIP_SLUG.get(base, {}).get(lang) or OG_CHIP[lang][kind]
    OG_PAGES[slug] = {'lang': lang, 'head': head, 'sub': sub, 'chip': chip, 'kind': kind,
                      'pose': OG_POSE_SLUG.get(base, OG_POSE[kind])}
    return f'/assets/og/p/{slug}.jpg'


def og_kind(path, active):
    slug = path.strip('/').split('/')[-1]
    if slug in tools.TOOL_SLUGS and not path.startswith('/en/'):
        return 'tool'
    if slug in GUIDE_CARDS:
        return 'poop' if GUIDE_CARDS[slug] == 1 else 'walk'
    return {'guide': 'poop', 'story': 'story', 'notice': 'notice', 'how': 'brand'}.get(active, 'plain')


def page(lang, key, title, desc, body, og_image, active=None, ko_path=None, en_path=None, og_type='website', ld=(), extra_head='', noindex=False, keywords='', intro=False, snap=False):
    ko_path = ko_path or url(key, 'ko')
    en_path = en_path or (url(key, 'en') if key in PATHS else None)
    path = ko_path if lang == 'ko' else en_path
    if key != 'home' or noindex:
        og_image = og_image_for('/404/' if noindex and key == 'home' else path, lang, title, body, og_kind(path, active), desc)
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
{alt}<link rel="alternate" type="application/rss+xml" title="{t['name']}" href="{SITE}{'/rss.xml' if lang == 'ko' else '/en/rss.xml'}">
<meta name="theme-color" content="#18955A">
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
    return (f'<video data-step muted loop playsinline preload="none" controlslist="nodownload noremoteplayback" disablepictureinpicture poster="/assets/video/{key}-{lang}.webp?v={ASSET_V}" aria-label="{escape(label)}">'
            f'<source src="/assets/video/{key}-{lang}.mp4?v={ASSET_V}" type="video/mp4"></video>')


SOUND_OFF = '<svg class="i-off" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="m22 9-6 6M16 9l6 6"/></svg>'
SOUND_ON = '<svg class="i-on" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg>'


def intro_film(lang, label):
    """첫 화면 — 서비스 소개 영상(우리 사이트에 올린 mp4)이 화면 가득 바로 재생. 유튜브 버튼 없이, 소리는 버튼으로."""
    on, off = {'ko': ('소리 켜기', '소리 끄기'), 'en': ('Sound on', 'Sound off')}[lang]
    return (f'<section class="film" data-film aria-label="{escape(label)}">'
            f'<video data-film-video muted loop playsinline autoplay preload="auto" controlslist="nodownload noremoteplayback" disablepictureinpicture aria-label="{escape(label)}"'
            f' data-land="/assets/video/intro-{lang}.mp4?v={ASSET_V}" data-port="/assets/video/intro-{lang}-v.mp4?v={ASSET_V}" data-land-poster="/assets/video/intro-{lang}.webp?v={ASSET_V}" data-port-poster="/assets/video/intro-{lang}-v.webp?v={ASSET_V}">'
            f'<source src="/assets/video/intro-{lang}-v.mp4?v={ASSET_V}" type="video/mp4" media="(max-aspect-ratio: 1/1)">'
            f'<source src="/assets/video/intro-{lang}.mp4?v={ASSET_V}" type="video/mp4"></video>'
            f'<button class="film-sound" type="button" data-sound data-on="{on}" data-off="{off}" aria-pressed="false">{SOUND_OFF}{SOUND_ON}<span>{on}</span></button>'
            f'<a class="film-down" href="#start" aria-label="{"아래로" if lang == "ko" else "Scroll down"}">{CHEV_D}</a></section>')


def waver():
    return ('<div class="waver" aria-hidden="true"><img class="tail" src="/assets/img/mascot/wave-tail.webp" alt="">'
            '<img class="sh" src="/assets/img/mascot/wave-shoulder.webp" alt=""><img class="arm" src="/assets/img/mascot/wave-arm.webp" alt="">'
            '<img src="/assets/img/mascot/wave-body.webp" alt=""></div>')


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


def cta_band(lang, cls=''):
    """다운로드 — 초록 카드, 왼쪽 글·스토어 버튼, 오른쪽 손 흔드는 응댕이 (v3 지도 아래)."""
    c = {'ko': ('둘이 같이 키운다면,<br>둘이 같이 써보세요', '가족 초대도 기록도 알림도 무료예요',
                [('응댕이가 응가를 했어요', '엄마가 방금 기록했어요'), ('아빠가 산책 다녀왔어요', '32분 산책 기록'), ('언니가 가족이 되었어요', '초대를 받았어요')]),
         'en': ('Raising your dog together?<br>Log it together.', 'Family invites, logs and alerts are all free.',
                [('Poochie just pooped', 'Mom logged it just now'), ('Dad finished a walk', '32-minute walk logged'), ('Sis joined the family', 'Invite accepted')])}[lang]
    # 응댕이 둘레에 떠 있는 앱 알림 세 장 (넓은 화면에서만)
    floats = ''.join(f'<div class="cf cf{i}"><img src="/assets/icons/apple-touch-icon.png" alt="" width="34" height="34"><span><b>{b}</b><i>{t}</i></span></div>'
                     for i, (b, t) in enumerate(c[2], 1))
    return (f'<section class="sec-cta {cls}"><div class="wrap"><div class="cta-card rise">'
            f'<div class="cta-text"><h2 class="h2" data-mo>{c[0]}</h2><p>{sb(c[1])}</p></div>{stores(lang)}{waver()}'
            f'<div class="cta-float" aria-hidden="true">{floats}</div></div></div></section>')


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
            'thumbnailUrl': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg', 'uploadDate': '2026-10-09T12:00:00+09:00',  # 시간대까지 — 날짜만 있으면 구글이 잘못됨으로 본다
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



# 홈 「강아지 가이드」 — 이렇게 같이 돌봐요 위에 가이드 여섯 개 (도구 둘 먼저)
HOME_GUIDES = {
    'ko': [('poop-condition-guide', '오늘 응가, 괜찮을까? 강아지 똥 상태 체크'), ('walk-safety-index', '오늘 산책해도 될까? 강아지 산책 안전도 계산기'),
           ('dog-diarrhea-causes', None), ('how-to-get-golden-poop', None), ('outdoor-potty-holding-risks', None), ('potty-interval', None)],
    'en': [('poop-condition-guide', None), ('walk-safety-index', None), ('potty-interval', None),
           ('jindo-mix-potty-training', None), ('dual-income-dog-walk-schedule', None), ('multi-dog-household-tracking', None)],
}


def home_guides(lang):
    cards = ''
    for slug, title in HOME_GUIDES[lang]:
        g = guide_json(slug, lang)
        cards += (f'<a class="post-card" href="{"" if lang == "ko" else "/en"}/{slug}/"><span class="thumb og">'
                  f'<img src="/assets/og/p/{slug if lang == "ko" else "en-" + slug}.jpg" alt="" width="1200" height="630" loading="lazy"></span>'
                  f'<b>{escape(title or g["og_title"])}</b></a>')
    tag, h, more = (('강아지 가이드', '같이 돌볼 때 알아 두면 좋은 것들', '가이드 전체 보기') if lang == 'ko' else
                    ('Dog guides', 'Good to know when you share one dog', 'See all guides'))
    return (f'<section class="sec-guides"><div class="wrap"><div class="guides-head"><div>{label(tag)}<h2 class="h2" data-mo>{h}</h2></div>'
            f'<a class="more-link" href="{url("guide", lang)}">{more}{ARROW_R}</a></div><div class="post-grid">{cards}</div></div></section>')


def home(lang):
    c = {
        'ko': {'title': '응가메이트 — 가족이 함께 보는 강아지 응가·산책 기록',
               'desc': '강아지 응가·쉬·산책을 한 명이 기록하면 가족 모두가 바로 알아요. “응댕이 똥 쌌어?” 이제 안 물어봐도 돼요. 초대·기록·알림 모두 무료예요.',
               'h1': '“응댕이 똥 쌌어?”<br><span class="hl">이제 안 물어봐도 돼요</span>',
               'lead': '강아지를 여럿이 같이 돌보는 집을 위한 앱. <br>한 사람이 응가·쉬를 기록하면 가족 모두가 바로 알아요.',
               'v_label': '응가메이트 서비스 소개 영상 (1분)',
               'b_tag': '이렇게 같이 돌봐요', 'b_h': '가족이 함께 쓰는 여섯 가지', 'f_more': '이렇게 써요 자세히 보기',
               's_tag': '응가메이트 이야기', 's_h': '“응댕이 똥 쌌어?”<br>그 전화에서 시작됐어요', 's_cap': ('분홍이 시절', '지금 우리 집'),
               's_p': '구조 단체 인스타그램에서 ‘분홍이’로 처음 만난 진도믹스는 이제 우리 가족이에요. 집에서는 절대 안 싸서 하루 세 번 똥책을 나가요. 맞벌이 엄마아빠는 매번 전화로 “응댕이 똥 쌌어?”를 물어야 했죠. 그래서 버튼 하나로 가족 모두가 아는 앱을 만들었어요.',
               's_btn': '이야기 더 보기'},
        'en': {'title': 'POOPIEMATE — Your dog’s potty & walk log, shared with family',
               'desc': 'When one of you logs it, everyone knows. No more “Did Poochie poop?” texts. Invites, logs and alerts are free.',
               'h1': '“Did Poochie poop?”<br><span class="hl">No need to ask anymore</span>',
               'lead': 'An app for families who look after one dog together. <br>When one person logs a poop or pee, everyone knows right away.',
               'v_label': 'POOPIEMATE intro video (1 min)',
               'b_tag': 'Care together', 'b_h': 'Six things families share', 'f_more': 'See how it works',
               's_tag': 'Our story', 's_h': '“Did she poop?”<br>It started with that call', 's_cap': ('Rescue days', 'Home with us now'),
               's_p': 'We first saw our white Jindo mix as “Bunhong” on a rescue group’s Instagram. Now she’s family. She never goes indoors, so she walks three times a day. As a working couple, we kept calling to ask “Did Poochie poop?” So we built an app where one tap tells the whole family.',
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

{home_guides(lang)}

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


# ── 앱 홈 게이지(FillGauge·GaugeJelly·GaugeFace)를 웹 SVG로 — 모양·물결·얼굴 좌표는 앱 값 그대로
SHAPE_VB_W, SHAPE_VB_H = 94.46, 97.05
POOP_OUTER = ('M85.45,63.64c4.04-7.85,1.59-20.37-8.66-22.29,1.53-6.86-2.08-15.66-10.68-16.58,4.09-11.71-9.8-22.06-17.32-23.58-5.4-.57.17,11.38-4.24,16.58-3.75,6.32-9.39,7.7,'
              '-15.66,7-8.04-.41-12.3,9.04-10.68,16.58-9.45,1.18-13.17,14.06-9.03,22.29-13.8,5.61,-11.28,32.01,5.34,32.24h65.76c7.74,0,13.82-6.26,13.82-13.45.54-7.14-.72-15.01,-8.66-18.79h0Z')
DROP_OUTER = ('M47.58,97.05c-22.57,0-38.49-16.75-38.49-37.8,0-13.29,10.38-27.83,19.66-39.04L45.78.83c.42-.42,1.11-.83,1.8-.83s1.38.28,1.8.83l16.47,19.38c9.28,11.35,19.52,'
              '25.75,19.52,38.9-.14,20.49-15.23,37.93-37.8,37.93Z')
GAUGE_SHINE = {'poop': 'M14.5 70 Q15.5 64.5 20 62.5', 'pee': 'M22 58 Q22.5 47 30 37.5'}
SHAPE_K = min(115 / SHAPE_VB_W, 118 / SHAPE_VB_H)


def wave_path(length, amp, start, width, bottom=112):
    """수면(y=0)이 물결치는 채움 — 앱 staticWavePath와 같은 모양, x=start부터."""
    d, x = f'M{start} 0', start
    while x < start + width:
        d += f' Q{x + length / 4:g} {-amp} {x + length / 2:g} 0 T{x + length:g} 0'
        x += length
    return d + f' L{x:g} {bottom} L{start} {bottom} Z'


def gauge_card(kind, mood):
    """카드 169×196pt(앱 크기). 모양 무대 115×118은 가운데 위 34pt. 얼굴·숫자·말풍선은 앱 좌표."""
    outer = POOP_OUTER if kind == 'poop' else DROP_OUTER
    ink = '#A2479A' if kind == 'poop' else '#1F6F5B'
    blush = 'rgba(200,101,188,.45)' if kind == 'poop' else 'rgba(31,111,91,.28)'
    ey, by = (46, 58) if kind == 'poop' else (44, 56)

    def eyes(d_l, d_r=None):
        return ''.join(f'<path d="{d}" transform="translate({x} {ey})"/>' for x, d in ((34.5, d_l), (68.5, d_r or d_l)))
    cheeks = f'<rect x="26.5" y="{by}" width="11" height="6" rx="3"/><rect x="77.5" y="{by}" width="11" height="6" rx="3"/>'
    faces = {'now': eyes('M2.5 1.5L9.5 5L2.5 8.5', 'M9.5 1.5L2.5 5L9.5 8.5'), 'relief': eyes('M1.5 2.5Q6 9 10.5 2.5'), 'calm': eyes('M1.5 7.5Q6 1 10.5 7.5')}
    shown = ('now', 'relief', 'calm') if kind == 'poop' else ('calm',)
    face = ''.join(f'<g class="f f-{f}">{faces[f]}</g>' for f in shown)
    # 움직이는 건 안쪽 path(CSS transform), 자리는 바깥 g(transform 속성) — CSS transform이 속성 transform을 덮어쓰지 않게
    stink = ''.join(f'<g transform="translate({27 + x} 48)"><path class="st" style="--o:{o}" d="M6 26c-3-4 3-6 0-10s3-6 0-10"/></g>' for x, o in ((76, 0), (88, .33), (100, .66))) if kind == 'poop' else ''
    sparks = ''.join(f'<g transform="translate({27 + x} {34 + y}) scale({sz / 10})"><path class="sp" style="--o:{o}" d="M5 0L6.2 3.8L10 5L6.2 6.2L5 10L3.8 6.2L0 5L3.8 3.8Z"/></g>'
                     for x, y, sz, o in ((8, 26, 14, 0), (94, 40, 11, .14), (100, 16, 8, .26))) if kind == 'poop' else ''
    dots = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in ((20.5, 24.5, 4.5), (34, 46, 2), (15, 121, 3), (151, 169, 5), (142, 122, 2)))
    level = 100 if kind == 'poop' else 36
    fill_y = SHAPE_VB_H * (1 - level / 100)
    svg = (f'<svg viewBox="0 0 169 196" aria-hidden="true"><defs><clipPath id="hh-clip-{kind}"><path d="{outer}"/></clipPath></defs>'
           f'<g class="dots">{dots}</g>'
           f'<g transform="translate(27 34) scale({SHAPE_K:.4f})"><path d="{outer}" fill="rgba(255,255,255,.32)"/>'
           f'<g clip-path="url(#hh-clip-{kind})"><g class="lvl" style="transform:translateY({fill_y:.2f}px)"><g class="slosh">'
           f'<g class="wb"><path d="{wave_path(60, 2.2, -120, SHAPE_VB_W + 180)}" transform="translate(0 1.5)" fill="rgba(255,255,255,.6)"/></g>'
           f'<g class="wf"><path d="{wave_path(48, 2.8, -48, SHAPE_VB_W + 144)}" fill="#fff"/></g></g></g></g>'
           f'<path d="{GAUGE_SHINE[kind]}" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="3.4" stroke-linecap="round"/></g>'
           f'<g transform="translate(27 34)"><g class="face" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{face}</g>'
           f'<g class="cheek" fill="{blush}">{cheeks}</g></g>'
           f'<g class="stink" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round">{stink}</g><g class="sparks" fill="#fff">{sparks}</g></svg>')
    if kind == 'poop':
        bubble = (f'<span class="mood m-now">{mood["now"]}</span><span class="mood m-relief">{mood["relief"]}</span>'
                  f'<span class="mood m-calm">{mood["calm"]}</span><span class="puff">{mood["puff"]}</span>')
    else:
        bubble = f'<span class="mood m-calm">{mood["calm"]}</span>'
    return (f'<div class="hh-g g-{kind}">{svg}<span class="num"><b></b>%</span>{bubble}'
            f'<span class="plus"><svg viewBox="0 0 14 14"><path d="M7 2v10M2 7h10"/></svg></span>'
            f'{"<span class=tap></span>" if kind == "poop" else ""}</div>')


ROW_ICON = {
    'poop': '<img src="/assets/img/emoji/pile_of_poo.webp" alt="">',
    'walk': '<img src="/assets/img/emoji/paw_prints.webp" alt="">',
}


def how(lang):
    c = {
        'ko': {'title': '이렇게 써요 — 가족이 같이 쓰는 법 | 응가메이트', 'desc': '초대 → 기록 → 알림, 세 단계면 끝. 돌봄 부탁·하트·산책 안전도까지 영상으로 보세요.',
               'h': '산책하다 응가하면<br><em>응가 게이지를 톡.</em>', 'lede': '게이지가 비워지고, 가족 모두의 폰에 바로 알림이 가요.',
               'dog': '응댕이',
               'route': [('가족 초대', '카톡으로 코드만 보내요'), ('게이지 톡', '응가·쉬 게이지를 눌러요'), ('모두에게 알림', '가족 폰이 바로 울려요')],
               'mood': {'now': '지금 나가야 해요!', 'relief': '개운해요!', 'calm': '여유 있어요', 'puff': '휴~'},
               'push': ('응가메이트', '지금', '응가 게이지가 비워졌어요', '방금 응가 기록을 남겼어요'),
               'rows': [('08:40', '나', 'poop', '응가', '개운해요'), ('08:12', '나', 'walk', '산책', '충분해요 · 32분')],
               'cap': '엄마·아빠 폰에도 같은 알림이 가요',
               'steps': [('코드 하나면<br><em>가족 모두 함께</em>', '마이 탭에서 초대 코드를 보내면 같은 강아지를 함께 기록해요.', 'invite', 'house', 'purple'),
                         ('<em>가족 모두의 기록</em>을<br>한눈에', '누가 언제 산책하고 치웠는지 하루 타임라인으로 모아 보여줘요.', 'record', 'pile_of_poo', 'pink'),
                         ('배변 신호·산책 루틴을<br><em>미리 챙겨요</em>', '게이지가 차거나 산책 시간이 되면 알려주고, 산책 시간에 비가 오면 먼저 알려줘요.', 'alerts', 'mobile_phone', 'green'),
                         ('<em>가족과 함께</em> 돌봐요', '고마운 기록엔 하트가 날아오고, 바쁠 땐 가족에게 돌봄을 부탁해요.', 'family', 'love_letter', 'peach'),
                         ('댕댕이 맞춤<br><em>산책 안전도</em>', '체형·털에 날씨를 더해 계산하고, 시간별 안전도와 다음 산책까지 알려줘요.', 'walk', 'sun_behind_small_cloud', 'sky')],
               'labels': {'invite': '가족 초대하는 법 모션그래픽', 'record': '기록과 가족 알림 모션그래픽', 'alerts': '배변 신호 모션그래픽', 'family': '돌봄 부탁과 하트 모션그래픽', 'walk': '산책 루틴과 안전도 모션그래픽'},
               'more_tag': '더 함께 돌보는 기능', 'more_h': '산책은 나눠서 해도,<br>기록은 <em>가족 모두가</em> 함께 봐요',
               'b1': ('가족 기록 공유', '한 명이 누르면<br>가족 폰이 울려요', '“응댕이 똥 쌌어?” 대신 알림 하나. 누가 언제 산책하고 치웠는지 하루 타임라인으로 모아 봐요.'),
               'toasts': [('응댕이가 응가를 했어요 💩', '엄마가 방금 기록했어요', '방금'), ('아빠가 하트를 보냈어요 💜', '아침 산책 기록에', '1분 전')],
               'b2': ('돌봄 부탁 · 하트', '바쁜 날엔 부탁,<br>다녀오면 하트', '“저녁 산책 부탁해!” 전화 대신 버튼 하나로.'),
               'b3': ('가족 초대', '가족 초대는<br>코드 하나면 끝', '카톡으로 코드만 보내면 같은 강아지를 함께 기록해요.'),
               'b4': ('산책 루틴 · 안전도', '오늘 언제 나가면<br>좋을까요?', '산책 시간이 되면 가족 모두에게 알려줘요. 날씨와 우리 강아지 몸에 맞춘 산책 안전도도 보여줘요.')},
        'en': {'title': 'How it works — Sharing dog care with family | POOPIEMATE', 'desc': 'Invite, log, get alerts — three steps. Watch how help requests, hearts and walk safety work.',
               'h': 'Pooped on the walk?<br><em>Tap the poop gauge.</em>', 'lede': 'It empties, and everyone’s phone gets the alert right away.',
               'dog': 'Poochie',
               'route': [('Invite family', 'Send one code by message'), ('Tap the gauge', 'Tap it when they go'), ('Everyone knows', 'Every phone buzzes')],
               'mood': {'now': 'Time to go!', 'relief': 'All clear!', 'calm': 'All good', 'puff': 'Phew~'},
               'push': ('POOPIEMATE', 'now', 'Poopie Gauge is empty', 'A poop was just logged'),
               'rows': [('8:40', 'Me', 'poop', 'Poop', 'All clear'), ('8:12', 'Me', 'walk', 'Walk', 'Plenty · 32 min')],
               'cap': 'Mom and Dad get the same alert',
               'steps': [('One code brings<br><em>everyone in</em>', 'Send an invite code from the My tab and log the same dog together.', 'invite', 'house', 'purple'),
                         ('<em>Every family log</em><br>at a glance', 'See who walked and cleaned up, and when — all in one daily timeline.', 'record', 'pile_of_poo', 'pink'),
                         ('Stay ahead of<br><em>potty & walks</em>', 'Alerts when a gauge fills or it’s walk time, plus a heads-up when rain is coming.', 'alerts', 'mobile_phone', 'green'),
                         ('<em>Care together</em><br>as a family', 'Hearts fly in for your care logs, and family can lend a hand when you’re busy.', 'family', 'love_letter', 'peach'),
                         ('Walk safety made<br><em>for your dog</em>', 'Scored from body type, coat and weather, with hourly safety and your next walks.', 'walk', 'sun_behind_small_cloud', 'sky')],
               'labels': {'invite': 'How to invite your family, motion graphic', 'record': 'Logging and family alerts, motion graphic', 'alerts': 'Potty signals, motion graphic', 'family': 'Help requests and hearts, motion graphic', 'walk': 'Walk routine and safety, motion graphic'},
               'more_tag': 'More ways to care together', 'more_h': 'Split the walks,<br>share the log with <em>everyone</em>',
               'b1': ('Shared family log', 'One tap,<br>every phone buzzes', '“Did Poochie poop?” becomes one alert. See who walked and cleaned up on one timeline.'),
               'toasts': [('Poochie just pooped 💩', 'Mom logged it just now', 'now'), ('Dad sent a heart 💜', 'On the morning walk', '1m ago')],
               'b2': ('Requests · Hearts', 'Ask on busy days,<br>thank with a heart', 'Ask for the evening walk with one button. No phone call needed.'),
               'b3': ('Family invites', 'One code<br>brings them in', 'Send a code by message. Then log the same dog together.'),
               'b4': ('Walk routine · Safety', 'When should<br>we head out?', 'Everyone gets the walk reminder. Plus a safety score for the weather and your dog.')},
    }[lang]
    steps = ''
    for i, (h, p, key, _, tone) in enumerate(c['steps'], 1):
        steps += (f'<section class="how-step snap-sec t-{tone}" id="step-{i}" data-live><div class="wrap-mid step-grid">'
                  f'<div class="step-text"><span class="step-num">{i:02d}<i>/ {len(c['steps']):02d}</i></span><h2 class="h2" data-mo>{h}</h2><p class="mo-fade">{sb(p)}</p></div>'
                  f'<div class="step-media">'
                  f'<div class="step-phone">{reel(key, lang, c["labels"][key])}</div></div></div></section>')
    toasts = ''.join(f'<div class="toast"><img src="/assets/icons/apple-touch-icon.png" alt="" width="36" height="36"><span><b>{b}</b><i>{sub}</i></span><time>{t}</time></div>'
                     for b, sub, t in c['toasts'])
    # 첫 화면 — 앱 홈의 응가·쉬 게이지 그대로. 꽉 찬 응가 게이지를 톡 → 쏴아 비워지고 → 알림이 내려오고 기록이 한 줄 생긴다 (한 바퀴 10초)
    route = ''.join(f'<li><a href="#step-{i}"><b>{i:02d}</b><strong>{h}</strong><span>{d}</span></a></li>' for i, (h, d) in enumerate(c['route'], 1))
    app, now, title, sub = c['push']
    m = c['mood']
    rows = ''.join(f'<div class="hh-row r-{kind}{" new" if i == 0 else ""}"><div class="hh-row-in"><span class="tm"><b>{tm}</b><i>{who}</i></span><span class="av">{who[0]}</span>'
                   f'<span class="pill"><span class="ic">{ROW_ICON[kind]}</span><span class="tx"><b>{name}</b><i>{note}</i></span></span></div></div>'
                   for i, (tm, who, kind, name, note) in enumerate(c['rows']))
    fam = ''.join(f'<i>{x}</i>' for x in (('엄', '아') if lang == 'ko' else ('M', 'D')))
    scene = (f'<figure class="hh-scene"><div class="hh-app" aria-hidden="true">'
             f'<div class="hh-push"><img src="/assets/icons/apple-touch-icon.png" alt="" width="36" height="36"><div><p><b>{app}</b><time>{now}</time></p><strong>{title}</strong><span>{sub}</span></div></div>'
             f'<div class="hh-head"><span class="pic"><img src="/assets/img/mascot/sit.webp" alt="" width="480" height="522"></span><b>{c["dog"]}</b></div>'
             f'<div class="hh-gauges">{gauge_card("poop", m)}{gauge_card("pee", m)}</div>'
             f'<div class="hh-rows">{rows}</div></div>'
             f'<figcaption class="hh-cap"><span class="fam">{fam}</span>{c["cap"]}</figcaption></figure>')
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
<section class="how-hero snap-sec"><div class="wrap hh-grid">
<div class="hh-text"><h1 class="h1" data-mo>{c['h']}</h1><p class="lead mo-fade">{c['lede']}</p>
</div>
{scene}
<ol class="hh-steps">{route}</ol>
</div></section>
{steps}
<section class="sec-more snap-sec"><div class="wrap"><div class="center-head rise"><span class="pill-tag">{c['more_tag']}</span><h2 class="h2">{c['more_h']}</h2></div>{bento}</div></section>
{cta_soft(lang)}
'''
    write(url('how', lang), page(lang, 'how', c['title'], c['desc'], body, f'/assets/og/poopiemate-{lang}.jpg', active='how'))


# ═════════════════════════════════════════════════════════ 이야기 (캔버스 「v2 이야기」)
STORY = {
    'ko': {
        'title': '응가메이트를 만든 이유', 'cat': '우리 강아지 이야기', 'date': '2026.10.07', 'by': '응가메이트를 만든 개발자, 진',
        'excerpt': '구조 단체 인스타그램에서 처음 만난 우리 집 강아지, 그리고 하루에도 몇 번씩 하던 “우리 강아지 똥 쌌어?” 전화 이야기.',
        'blocks': [
            ('p', '안녕하세요, 응가메이트를 만든 개발자, 진입니다. 앱을 만들게 된 이야기를 처음부터 차근차근 해 볼게요. 조금 길어요.'),
            ('h2', '인스타그램에서 만난 분홍이'),
            ('p', '우리 집 강아지의 이름은 메로나예요. 이제 네 살, 13kg의 하얀 진도믹스예요. 진돗개에 비숑이 섞여서 털이 살짝 곱슬거려요.'),
            ('p', '이 아이의 엄마는 시골에서 짧은 목줄에 묶여 살던 강아지였어요. 원래 서울에서 키우던 강아지였는데, 주인이 시골에 버려두고 떠나 버렸대요. 그곳에서 들개와의 사이에 새끼들이 태어났고, 우리 집 강아지는 그중 한 마리예요.'),
            ('p', '어디론가 팔려 갈 뻔했던 그때, 동물 구조 단체 WithAllAnimals(WAA)가 이 새끼들을 구조했어요. 저는 WAA 인스타그램에 올라온 사진에서 이 아이를 처음 봤어요. 그때 이름은 ‘분홍이’였어요.'),
            ('img', 'pair-rescue', 'WAA 인스타그램에서 처음 본 분홍이'),
            ('p', '처음엔 임시보호를 하겠다고 연락했어요. 그런데 막상 한 생명을 맡는다고 생각하니 겁이 나서, 못 하겠다고 말씀드렸어요. 그러다 다음 날, 다시 연락했어요. “제가 임시보호 할게요.” 그렇게 이 아이는 우리 집에 오게 됐어요.'),
            ('h2', '무서워하면서도, 엄마인 걸 아는 것처럼'),
            ('p', '우리 집에 처음 온 날, 이 아이는 저를 무서워하면서도 제가 엄마라는 걸 직감적으로 아는 것 같았어요. 잔뜩 겁먹은 얼굴로 제 손 냄새를 맡더니, 쓰다듬는 손길을 피하지 않고 가만히 저를 올려다봤어요.'),
            ('clips', [('first-meet', '처음 만난 날 밤'), ('first-lick', '바로 다음날!')], '우리 집에 온 첫날과 그다음 날'),
            ('p', '겁이 정말 많았어요. 사람 손길조차 무서워했어요. 가까이 다가가면 눈치를 살피며 한참을 저를 쳐다봤어요.'),
            ('row', ['first-lap-eyes', 'first-paws'], '아직은 조심스럽던 눈빛'),
            ('p', '그런데, 정말 너무 귀여웠어요. 그렇게 겁을 내던 아이가 집에 온 다음 날부터 제 무릎 위에서 잠들기 시작했어요. 잠든 얼굴을 보고 있으면 시간 가는 줄 몰랐어요.'),
            ('row', ['first-lap-sleep', 'first-pink-sleep'], '무릎 위에서, 이불 속에서'),
            ('p', '처음 산책을 나갔을 때는 목줄을 하고 걷는 것조차 못 했어요. 어떻게 해야 할지 몰라서 저도 한참 헤맸어요. 하네스를 채우는 것부터 하나씩 같이 연습했어요.'),
            ('row', ['first-harness', 'first-selfie'], '산책 연습을 하던 겨울'),
            ('h2', '이 아이 없이는 못 살겠다'),
            ('p', '임시보호를 할 때는 한국보다 조금 더 펫 프렌들리한 해외로 입양을 보내고 싶었어요. 그래서 ‘로나’라는 영어 이름을 지어 주고, 성은 ‘메’로 붙였어요. 그렇게 메로나가 됐어요.'),
            ('p', '그러다 남편이 먼저 말했어요. 이 아이 없이는 못 살겠다고, 우리가 입양하자고요. 그렇게 임시보호는 입양이 됐어요.'),
            ('p', '지금도 낯선 사람과 큰 소리, 트럭과 움직이는 사다리를 무서워하는 겁쟁이예요. 그래도 먹을 것 앞에서는 누구보다 용감한 먹보예요. 당근과 닭가슴살을 제일 좋아하고, 배가 고프면 앞발을 공손하게 내밀어요. 그리고 이제는 엄마아빠를 제일 좋아해요.'),
            ('mix', ['park-run', 'clip:paw'], '운동장에서 뛰놀고, 배고프면 공손하게 앞발'),
            ('h2', '집에서는 절대 안 싸는 아이'),
            ('p', '우리 집 강아지는 응가도 쉬도 꼭 밖에서만 해요. 패드를 깔아 줘도, 아무리 오래 참아도 꼭 밖에 나가야 해요. 나가고 싶을 때는 현관에서 신발을 물어 와요.'),
            ('p', '한국 토종개인 진돗개는 열에 아홉이 실외배변을 한다고 할 만큼, 집 안에서는 볼일을 보지 않는 견종으로 알려져 있어요. 진돗개와 비숑이 섞인 우리 집 강아지도 그 습관을 그대로 물려받았어요.'),
            ('p', '그래서 비가 오나 눈이 오나 하루 세 번, 꼭 산책을 나가요. 산책에서 하는 일은 하나예요. 최고의 똥 스팟 찾기. 바싹 마른 낙엽, 폭신한 흙바닥, 솔방울이 잔뜩 떨어진 곳이면 합격이에요.'),
            ('clips', [('potty-morning', '아침 산책에서도'), ('potty-pee', '쉬도 꼭 밖에서')], '오늘의 똥 스팟을 찾아서'),
            ('h2', '하루에도 몇 번씩 하던 전화'),
            ('p', '저희 부부는 둘 다 일을 해서 산책을 나눠서 해요. 문제는 그다음이었어요. 아침에 몇 시에 나가서 산책을 얼마나 했는지, 응가는 했는지, 쉬는 몇 번 했는지. 매번 전화해서 확인해야 했거든요.'),
            ('quote', ['로나 똥 쌌어?', '아침 산책에 몇 번 똥 쌌어?', '저녁엔 누가 나갈래?'], '하루에도 몇 번씩 오가던 전화'),
            ('p', '외출했다가 집에 들어오는 시간도 늘 서로 알려 줘야 했어요. 누가 언제 산책을 나갈지 매번 전화로 스케줄을 맞추는 게 생각보다 쉽지 않았어요. 실외배변만 하는 아이라 응가를 언제 했는지는 건강과도 바로 이어지는 문제였어요. 하루 종일 참고 있는 건 아닌지, 마지막 응가가 몇 시간 전이었는지 늘 마음이 쓰였어요.'),
            ('p', '결국 엄마인 저는 재택근무를 할 수 있는 일을 하게 됐어요. 그리고 생각했어요. 매번 이렇게 연락하는 것보다, 차라리 앱을 만들자.'),
            ('h2', '그 전화를 버튼 하나로'),
            ('p', '한 사람이 응가·쉬를 기록하면 가족 모두의 폰에 바로 알림이 가는 앱이에요. 누가 언제 산책하고 치웠는지는 하루 타임라인으로 모아 보고, 바쁜 날엔 산책을 부탁하고, 다녀오면 고맙다고 하트를 보내요.'),
            ('p', '한여름에는 언제 나가야 발바닥이 뜨겁지 않을지가 늘 고민이었어요. 그래서 우리 강아지의 체형과 털, 나이에 날씨를 더한 산책 안전도를 넣었어요. 배변 텀으로 차오르는 응가·쉬 게이지는 “오늘은 좀 오래 참고 있네”를 가족 모두가 같이 알아차리게 해 줘요.'),
            ('img', 'pair-wedding', '셋이 함께 찍은 웨딩 사진'),
            ('h2', '응댕이는 우리 집 강아지를 닮았어요'),
            ('p', '응가메이트의 캐릭터 응댕이는 우리 집 강아지에서 왔어요. 똥 모양 얼굴에 축 처진 큰 귀, 먹보에 겁쟁이, 배고프면 앞발을 내미는 것까지요. 앱을 켤 때마다 손을 흔드는 응댕이를 보면, 현관에서 신발을 물고 기다리는 우리 집 강아지가 떠올라요.'),
            ('h2', '결혼식 화견, 그리고 매년 찍는 가족사진'),
            ('p', '우리 집 강아지는 저희 결혼식에서 화견도 했어요. 웨딩 사진도 셋이 함께 찍었어요. 그리고 그 뒤로 매년, 가족사진을 같이 찍고 있어요.'),
            ('img', 'pair-family', '2025년 가족사진'),
            ('p', '강아지를 여럿이 같이 돌보는 집이라면, 응가메이트가 “우리 강아지 똥 쌌어?” 전화를 조금이라도 줄여 주면 좋겠어요. 오늘도 우리 집 강아지는 최고의 똥 스팟을 찾아 산책을 나가요.'),
        ]},
    'en': {
        'title': 'Why I built POOPIEMATE', 'cat': 'Our dog', 'date': 'Oct 7, 2026', 'by': 'Jin, developer of POOPIEMATE',
        'excerpt': 'The dog we first saw on a rescue group’s Instagram, and the “Did she poop?” calls we made every single day.',
        'blocks': [
            ('p', 'Hi, I’m Jin, the developer behind POOPIEMATE. Here’s how the app came to be, from the very beginning. It’s a bit of a long one.'),
            ('h2', 'Bunhong, from an Instagram post'),
            ('p', 'Our dog’s name is Melona. She’s now four, a 13 kg white Jindo mix — part Jindo, part Bichon, which is why her fur curls slightly.'),
            ('p', 'Her mother lived on a short chain in the countryside. She had been someone’s dog in Seoul, until her owner abandoned her out there and left. She had puppies with a stray dog, and our dog is one of them.'),
            ('p', 'They were about to be sold off to who knows where when the animal rescue group WithAllAnimals (WAA) rescued them. I first saw her in a photo on WAA’s Instagram. Back then she was called “Bunhong” — little pinky.'),
            ('img', 'pair-rescue', 'Bunhong, as I first saw her on WAA’s Instagram'),
            ('p', 'At first I offered to foster her. Then the idea of being responsible for a life scared me, and I said I couldn’t. The next day I got back in touch: “I’ll foster her.” That’s how she came home with us.'),
            ('h2', 'Scared, yet somehow she knew I was Mom'),
            ('p', 'On her first day with us, she was scared of me — and yet she seemed to sense that I was her mom. Looking terrified, she sniffed my hand — then stood still, let me pet her, and looked up at me.'),
            ('clips', [('first-meet', 'The night we first met'), ('first-lick', 'The very next day!')], 'Her first night with us, and the day after'),
            ('p', 'She was so timid. Even a person’s touch frightened her. When I came close, she would study me for a long time, unsure.'),
            ('row', ['first-lap-eyes', 'first-paws'], 'Still wary in those first days'),
            ('p', 'But oh, she was so, so cute. This scared little dog started falling asleep on my lap from her very second day. I could watch her sleeping face for hours.'),
            ('row', ['first-lap-sleep', 'first-pink-sleep'], 'Asleep on my lap, and under the blanket'),
            ('p', 'On our first walk, she couldn’t even walk on a leash. I didn’t know what to do either. We practiced together, one step at a time, starting with just putting on her harness.'),
            ('row', ['first-harness', 'first-selfie'], 'That winter of walk practice'),
            ('h2', 'We couldn’t live without her'),
            ('p', 'While fostering, I hoped to find her a home abroad, somewhere a little more pet-friendly than Korea. So I gave her an English name, Lona, and the family name Me. That’s how she became Melona.'),
            ('p', 'Then my husband said it first: we can’t live without her, let’s adopt her. And so fostering turned into adoption.'),
            ('p', 'She’s still a scaredy-cat around strangers, loud voices, trucks and moving ladders — but the bravest of us all in front of food. She loves carrots and chicken breast, and when she’s hungry she politely offers a paw. And now her favorite people are Mom and Dad.'),
            ('mix', ['park-run', 'clip:paw'], 'Running at the dog park, and a polite paw when she’s hungry'),
            ('h2', 'A dog who never goes indoors'),
            ('p', 'Our dog only poops and pees outside. Not on a pad, not even when she’s been holding it for hours. When she wants to go out, she brings us a shoe from the doorway.'),
            ('p', 'The Jindo, Korea’s native breed, is known for refusing to go indoors — it’s often said nine in ten Jindos only go outside. Our Jindo-Bichon mix inherited that habit, all of it.'),
            ('p', 'So rain or snow, she goes out three times a day. On every walk she has one mission: find the best poop spot. Crunchy dry leaves, soft dirt, or a patch covered in pinecones all pass the test.'),
            ('clips', [('potty-morning', 'On the morning walk'), ('potty-pee', 'Pees outside too')], 'Searching for today’s poop spot'),
            ('h2', 'The calls we made every day'),
            ('p', 'We both work, so we split the walks. The trouble came after. What time did she go out this morning, and how long was the walk? Did she poop? How many pees? We had to call and check every time.'),
            ('quote', ['Did Lona poop?', 'How many poops on the morning walk?', 'Who’s going out tonight?'], 'The calls we traded every single day'),
            ('p', 'We always had to tell each other when we’d be back home. Lining up who walks her when, one phone call after another, was harder than it sounds. For a dog who only goes outside, when she last pooped is a health question too. We always wondered whether she’d been holding it all day.'),
            ('p', 'In the end, I — Mom — found work I could do from home. And I thought: rather than calling like this every time, why not build an app?'),
            ('h2', 'Turning that call into a button'),
            ('p', 'One person logs a poop or pee and everyone in the family gets an alert right away. A daily timeline shows who walked and cleaned up, you can ask someone else to take the walk on a busy day, and send a heart when they’re back.'),
            ('p', 'In summer we always worried about hot pavement, so we added a walk safety score that combines her body type, coat and age with the weather. The potty gauges, filling up with her rhythm, let the whole family notice when she’s been holding it a little too long.'),
            ('img', 'pair-wedding', 'Our wedding photos, the three of us'),
            ('h2', 'Poochie looks just like her'),
            ('p', 'Our mascot Poochie comes straight from our dog: a poop-shaped face, big floppy ears, a foodie and a scaredy-cat who offers a paw when she’s hungry. Every time Poochie waves on the app’s screen, we think of her waiting at the door with a shoe in her mouth.'),
            ('h2', 'Flower dog at our wedding, and a family photo every year'),
            ('p', 'Our dog was even the flower dog at our wedding, and she’s in our wedding photos too. Ever since, we’ve taken a family photo together every year.'),
            ('img', 'pair-family', 'Our 2025 family photo'),
            ('p', 'If your family shares one dog, we hope POOPIEMATE cuts down on the “Did our dog poop?” texts, even a little. And today, as always, our dog is out looking for the best poop spot.'),
        ]},
}


# 링크드인에 올린 글(2026.10.24)을 옮긴 것 — 사진은 src/prepare_assets.py solo
SOLO = {
    'ko': {
        'title': '개발자에서 1인 빌더로, 응가메이트 이야기', 'cat': '만드는 이야기', 'date': '2026.10.28', 'by': '응가메이트를 만든 개발자, 진',
        'excerpt': 'ComfyUI를 나와 기획, 디자인, 개발, 영상, 스토어 심사, 마케팅까지 혼자 해 온 이야기. 첫 버전 120명에서 가족 돌봄 앱 2.0.0까지.',
        'blocks': [
            ('h2', 'AI가 개발자의 일을 대신하기 시작했을 때'),
            ('p', '실리콘밸리 AI 스타트업 ComfyUI에서 원격 개발자로 일하면서 뛰어난 동료들에게 많이 배우고 성장했어요. 그런데 프론트엔드 개발자의 많은 일이 AI로 대체되는 걸 보면서 제 직업에 대해 다시 생각해 보게 됐어요.'),
            ('p', '항상 ‘AI가 개발자를 대체할 테니 그 전까지 한탕 벌고 은퇴하겠다’는 말을 농담처럼 했는데, 정말 그 시기가 눈앞에 다가오니 고민이 많아졌어요. 그래서 ComfyUI를 나와 제 서비스를 만들어 보기로 했어요.'),
            ('p', '3월에 수원창업지원센터 입주기업으로 선정됐고, 4월에 퇴사했어요. 그렇게 1인 빌더로 응가메이트를 만들었어요. 기획, 디자인, 개발, 영상 제작, 스토어 심사, 마케팅까지 전부 다요!'),
            ('h2', '응가메이트는 이런 앱이에요'),
            ('p', '응가메이트는 실외배변 강아지의 배변을 기록하고 실시간 알림을 주는 앱이에요. 가족 중 한 사람이 기록하면 모두에게 바로 알림이 가고, 누가 언제 산책하고 기록했는지 하루 타임라인으로 모아 봐요. 바쁜 날엔 다른 가족에게 산책을 부탁할 수 있어요.'),
            ('p', '강아지 체형 같은 자세한 정보를 바탕으로 산책 안전도를 알려 주고, 산책 루틴 시간에 비 소식이 있으면 미리 알림을 보내서 비 오기 전에 산책을 다녀올 수 있게 해 줘요.'),
            ('img', 'solo-app-ko', '가족과 함께 챙기는 댕댕이 응가·산책'),
            ('h2', '시작은 우리 집 강아지 메로나'),
            ('p', '시작은 우리 집 강아지 메로나였어요. 학대받던 곳에서 WAA가 구조한 진도믹스인데, 진돗개가 대부분 그렇듯 응가도 쉬도 밖에서만 해요. 그래서 비가 오나 눈이 오나 하루 세 번은 나가야 해요.'),
            ('p', f'맞벌이라 산책을 나눠 하다 보니 “로나 똥 쌌어?” 하는 전화를 하루에도 몇 번씩 했어요. 그 전화를 버튼 하나로 바꾸고 싶었어요. 메로나 이야기는 <a href="{PATHS["why"][0]}">응가메이트를 만든 이유</a>에 더 자세히 적어 두었어요.'),
            ('h2', '첫 버전, 그리고 데이터가 알려 준 것'),
            ('p', '전에 네이버 클로바X 해커톤에서 젤리레터로 우수 프로젝트에 선정된 적이 있어요. 응가메이트는 처음에 젤리레터의 디자인과 개발 소스를 이용해 빠르게 만들었고, 첫 버전으로 유저 120명을 모았어요.'),
            ('row', ['solo-jelly-letter', 'solo-jelly-app'], '세상을 떠난 반려동물이 보호자에게 편지를 보내 주는 젤리레터'),
            ('p', '그런데 데이터를 보니 혼자 강아지를 돌보는 유저는 거의 다 떠났어요. 남은 건 강아지를 여러 마리 키우는 집과, 한 마리를 가족이 같이 돌보는 집이었어요. 그래서 다견 기능을 먼저 냈어요.'),
            ('h2', '노트북 없이 떠난 3주'),
            ('p', '그동안 쉴 새 없이 달리며 일했어요. 번아웃에서 좀 회복하고 싶어서 혼자 3주 동안 유럽 여행을 다녀왔어요. 노트북도 두고 가서 강제로 디지털 디톡스를 했는데, 그동안 ‘돌아가면 응가메이트 디자인을 다시 하고 꼭 잘 만들어야지’ 하는 생각을 했어요.'),
            ('mix', ['solo-trip-cliffs', 'solo-trip-italy', 'solo-trip-dog-sofa'], '노트북 없이 떠난 3주, 그리고 머물던 에어비앤비의 강아지'),
            ('p', '마침 그 3주 사이에 좋은 AI 모델들이 나와서 개발도, 디자인도, 모션그래픽도 훨씬 쉬워져 있었어요. 돌아와서 응가메이트를 가족 돌봄 앱으로 바꿨고, 일주일 만에 2.0.0을 직접 다시 디자인하고 개발하고, Claude로 모션그래픽까지 만들어 SNS 계정도 열었어요.'),
            ('h2', '물어볼 필요 없어요, 응가메이트가 알려줘요'),
            ('p', '처음 문구는 “비가 오나 눈이 오나, 실외배변 루틴을 지켜요”였어요. 지금은 응댕이라는 캐릭터를 만들고 이렇게 바꿨어요.'),
            ('quote', ['“응댕이 아침에 똥 쌌어?”', '물어볼 필요 없어요.', '응가메이트가 알려줘요.'], '지금의 응가메이트 문구'),
            ('p', '기록하는 과정에는 게이미피케이션을 넣었어요. 온보딩에서 입력한 산책 루틴을 기준으로 응가 게이지와 쉬야 게이지의 표정이 바뀌어서 ‘오늘 좀 오래 참고 있네’를 가족이 같이 알아채고, 산책을 다녀온 가족에게는 고맙다고 하트를 보내요. 곧 나올 2.1.0에서는 산책 부탁이 종이비행기로 날아가고, 받은 하트가 분홍 편지에서 쏟아져요.'),
            ('p', '지금 유저는 150명 정도예요. 매일 기록하는 사람이 10명, 일주일에 4일 이상 기록하는 사람이 30명쯤 돼요. 작은 숫자지만 저한테는 아주 큰 힘이 돼요.'),
            ('h2', '응가메이트로 하고 싶은 일'),
            ('p', '응가메이트는 실외배변을 하는 중대형견의 돌봄 난이도를 낮추려고 만든 서비스예요. 돌보는 일이 쉬워지면 진돗개와 진도믹스를 가족으로 맞는 집도 늘어날 거라고 믿어요. 저를 아는 분들은 다 아시겠지만, 저는 WAA 구조단체 스태프로도 일했고 강아지에 진심이에요.'),
            ('img', 'park-run', '운동장에서 뛰노는 우리 집 진도믹스, 메로나'),
            ('p', 'AI 시대에는 목표와 가치를 스스로 만드는 사람이 되는 게 중요하다고 생각해요. 제 목표는 우리나라 토종견들이 보호소에서 안락사당하지 않게 하는 것이고, 제 가치는 중대형견이 가정 안에서 사랑받으며 행복한 산책을 하도록 돕는 거예요.'),
        ]},
    'en': {
        'title': 'From developer to solo builder: the POOPIEMATE story', 'cat': 'Making the app', 'date': 'Oct 28, 2026', 'by': 'Jin, developer of POOPIEMATE',
        'excerpt': 'Leaving ComfyUI and building POOPIEMATE alone, from design and code to store reviews and marketing: 120 first users, then the 2.0.0 family care app.',
        'blocks': [
            ('h2', 'When AI started doing a developer’s job'),
            ('p', 'Working remotely as a developer at ComfyUI, a Silicon Valley AI startup, I learned a lot from brilliant teammates and grew. But as AI took over more and more of a frontend developer’s work, I started rethinking my job.'),
            ('p', 'I used to joke that AI would replace developers someday and that I’d cash in and retire before then. Now that the moment is actually here, I’ve had a lot to think about. So I decided to leave ComfyUI and build my own product.'),
            ('p', 'In March, the Suwon Startup Support Center selected me as a resident company, and in April I left. I built POOPIEMATE as a solo builder. Planning, design, development, video, store reviews, marketing: all of it!'),
            ('h2', 'What POOPIEMATE does'),
            ('p', 'POOPIEMATE is an app that logs an outdoor-only dog’s poops and pees and sends real-time alerts. When one family member logs one, everyone gets a notification right away, and a daily timeline shows who walked and logged, and when. On a busy day you can ask someone else to walk.'),
            ('p', 'It scores walk safety from details like your dog’s build, and if rain is forecast for your walk time, it alerts you early so you can walk before it.'),
            ('img', 'solo-app-en', 'POOPIEMATE today'),
            ('h2', 'It started with our dog Melona'),
            ('p', 'It started with our dog Melona, a Jindo mix WAA rescued from abuse. Like most Jindos, she only goes outside, so rain or snow, she needs three walks a day.'),
            ('p', f'We both work and split the walks, so we kept calling each other to ask, “Did Lona poop?” I wanted to turn that call into one tap. I wrote more about Melona in <a href="{PATHS["why"][1]}">Why I built POOPIEMATE</a>.'),
            ('h2', 'The first version, and what the data said'),
            ('p', 'My JellyLetter was picked as an outstanding project at a Naver CLOVA X hackathon. I built POOPIEMATE’s first version quickly on top of JellyLetter’s design and code, and it reached 120 users.'),
            ('row', ['solo-jelly-letter', 'solo-jelly-app'], 'JellyLetter, where a pet who has passed away sends letters to their family'),
            ('p', 'Then the data showed that people caring for a dog alone almost all left. Multi-dog homes and families sharing one dog stayed. So I shipped multi-dog support first.'),
            ('h2', 'Three weeks without a laptop'),
            ('p', 'After running nonstop, I went to Europe alone for three weeks to recover from burnout. I left my laptop at home, a forced digital detox, and kept thinking: when I get back, I’ll redesign POOPIEMATE and build it properly.'),
            ('mix', ['solo-trip-cliffs', 'solo-trip-italy', 'solo-trip-dog-sofa'], 'Three weeks without a laptop, and the dog at the Airbnb where I stayed'),
            ('p', 'Better AI models came out in those three weeks, and development, design and even motion graphics got much easier. When I got back, I turned POOPIEMATE into a family care app. In one week I redesigned and built 2.0.0 myself, made motion graphics with Claude and set up our social accounts.'),
            ('h2', 'No need to ask. POOPIEMATE tells you'),
            ('p', 'The first tagline was “Keep the outdoor potty routine, rain or snow.” Now we have a character, Poochie, and a new line.'),
            ('quote', ['“Did Poochie poop this morning?”', 'No need to ask.', 'POOPIEMATE tells you.'], 'Our tagline today'),
            ('p', 'Logging is gamified. The poop and pee gauges change their faces based on the walk routine you set during onboarding, so the family can see when she’s been holding it, and you send a thank-you heart to whoever walked her. In 2.1.0, coming soon, walk requests fly off as paper planes and hearts pour out of a pink letter.'),
            ('p', 'About 150 people use it now. Around 10 log every day, and about 30 log four or more days a week. Small numbers, but they keep me going.'),
            ('h2', 'What I want POOPIEMATE to do'),
            ('p', 'POOPIEMATE exists to make caring for medium and large outdoor-only dogs easier. I believe that when care gets easier, more families will welcome Jindos and Jindo mixes. As most people who know me probably know, I’ve also worked as staff at the rescue group WAA, and I’m all in when it comes to dogs.'),
            ('img', 'park-run', 'Our Jindo mix Melona, running at the dog park'),
            ('p', 'In the age of AI, I think it matters to be someone who creates their own goals and values. My goal is that Korea’s native dogs are no longer euthanized in shelters. The value I want to create is helping medium and large dogs be loved at home and go on happy walks.'),
        ]},
}
# 글 키 → (본문, 올린 날, 고친 날, 분류 번호, 목록 썸네일·글 머리, 공유 이미지) — 목록에는 새 글이 먼저
POSTS = {
    'solo': (SOLO, '2026-10-28', '2026-10-28', 2, '/assets/img/story-solo-thumb.webp', '/assets/og/story-solo.jpg'),
    'why': (STORY, '2026-10-07', '2026-10-10', 1, '/assets/img/story-thumb-{lang}.webp', '/assets/og/story-{lang}.jpg'),
}


THUMB_POS = {'park-run': '50% 60%'}  # 썸네일에서 강아지가 가운데 오게 — 사진마다 잘라 보일 위치
LANDSCAPE = {'pair-rescue', 'pair-wedding', 'pair-family', 'solo-app-ko', 'solo-app-en'}  # 나머지 사진은 세로 — 원본 비율 그대로, 폭만 좁게


def post_head(meta, title, art):
    return f'<p class="post-meta">{meta}</p><h1 class="post-h1">{title}</h1>{art}'


def story_list(lang):
    c = {'ko': ('이야기', '응가메이트를 만든 가족이 겪은 이야기를 모아요', '이야기 — 응가메이트를 만든 가족 이야기', '응가메이트를 만든 가족과 우리 집 강아지 이야기. “우리 강아지 똥 쌌어?” 전화가 버튼 하나가 되기까지를 기록해요.',
                ['전체', '우리 강아지 이야기', '만드는 이야기', '보호자 이야기'],
                [('우리 강아지 이야기', '[다음 글] 비가 오나 눈이 오나, 똥책 사계절', '밖에서만 싸는 강아지와 보내는 사계절. 날씨 따라 달라지는 산책 루틴 이야기.', 'photo:park-run'),
                 ('만드는 이야기', '[다음 글] 가족이 같이 기록하면 무엇이 달라질까', '초기 사용자 기록을 보고 가족 초대를 먼저 고친 과정.', 'emoji')], '준비 중'),
         'en': ('Stories', 'Notes from the family behind POOPIEMATE', 'Stories — The family behind POOPIEMATE', 'Stories from the family and the rescued Jindo mix behind POOPIEMATE, and how “Did she poop?” calls turned into one tap.',
                ['All', 'Our dog', 'Making the app', 'Owner stories'],
                [('Our dog', '[Coming up] Rain or snow: a year of potty walks', 'Four seasons with a dog who only goes outside, and how the walk routine changes with the weather.', 'photo:park-run'),
                 ('Making the app', '[Coming up] What changes when a family logs together', 'What early users’ logs taught us, and why we fixed family invites first.', 'emoji')], 'Coming soon')}[lang]
    cats = c[4]
    chips = ''.join(f'<button type="button" data-cat="{"all" if i == 0 else i}" aria-pressed="{"true" if i == 0 else "false"}">{x}</button>' for i, x in enumerate(cats))
    first = ''
    for key, (src, date, _, cat, thumb, _) in POSTS.items():
        s = src[lang]
        first += (f'<a class="post-card" data-cat="{cat}" href="{url(key, lang)}"><span class="thumb"><img src="{thumb.format(lang=lang)}" alt="" loading="lazy" width="1600" height="1000">{new_badge(date)}</span>'
                  f'<span class="cat">{cats[cat]}</span><b>{s["title"]}</b><span class="ex">{sb(s["excerpt"])}</span><time datetime="{date}">{s["date"]}</time></a>')
    soon = ''
    for cat, t, ex, art in c[5]:
        pos = THUMB_POS.get(art[6:])
        thumb = (f'<img src="/assets/img/photo/{art[6:]}-900.webp" alt="" loading="lazy"{f" style={chr(34)}object-position:{pos}{chr(34)}" if pos else ""}>' if art.startswith('photo:')
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
    write(url('story', lang), page(lang, 'story', c[2] + (' | 응가메이트' if lang == 'ko' else ''), c[3], body, f'/assets/og/story-{lang}.jpg', active='story'))


def photo_size(name):
    from PIL import Image
    with Image.open(ROOT / f'assets/img/photo/{name}-1600.webp') as im:
        return im.size


def photo_img(name, sizes, alt=''):
    w, h = photo_size(name)
    return (f'<img src="/assets/img/photo/{name}-1600.webp" srcset="/assets/img/photo/{name}-900.webp 900w, /assets/img/photo/{name}-1600.webp 1600w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{escape(alt)}" loading="lazy">')


def clip_size(name):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                          str(ROOT / f'assets/video/story-{name}.mp4')], capture_output=True, text=True).stdout
    return tuple(int(x) for x in re.findall(r'\d+', out)[:2])  # 새 ffprobe는 값 사이에 빈 줄을 넣기도 한다


def story_clip(name, label, lang, cap=True):
    """글 사이 세로 영상 — 화면에 들어오면 소리 없이 돌고, 버튼으로 원본 소리를 켠다 (site.js)."""
    on, off = {'ko': ('소리 켜기', '소리 끄기'), 'en': ('Sound on', 'Sound off')}[lang]
    has_sound = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0',
                                str(ROOT / f'assets/video/story-{name}.mp4')], capture_output=True, text=True).stdout.strip()
    sound = (f'<button class="clip-sound" type="button" data-clip-sound data-on="{on}" data-off="{off}" aria-pressed="false" aria-label="{on}">{SOUND_OFF}{SOUND_ON}</button>'
             if has_sound else '')
    w, h = clip_size(name)
    ratio = '' if (w, h) == (720, 1280) else f' style="aspect-ratio:{w} / {h}"'  # 기본은 9:16 (css), 잘라 낸 영상만 제 비율로
    return (f'<div class="clip" data-clip><div class="clip-box"{ratio}><video muted loop playsinline preload="none" controlslist="nodownload noremoteplayback" disablepictureinpicture '
            f'poster="/assets/video/story-{name}.webp?v={ASSET_V}" width="{w}" height="{h}" aria-label="{escape(label)}"><source src="/assets/video/story-{name}.mp4?v={ASSET_V}" type="video/mp4"></video>'
            f'{sound}</div>'
            f'{f"<span class=\"clip-cap\">{label}</span>" if cap else ""}</div>')


def next_post(lang, key):
    """글 끝의 다음 글 — 홈의 이야기 카드(크림 바탕, 그림 + 라벨·제목·요약·더 보기)와 같은 모양.
    목록 순서(새 글 먼저)로 다음 것, 마지막 글이면 맨 앞 글로."""
    keys = list(POSTS)
    nxt = keys[(keys.index(key) + 1) % len(keys)]
    src, _, _, _, thumb, _ = POSTS[nxt]
    s = src[lang]
    # 카드 전체가 링크 — 그림·제목·요약 어디를 눌러도 다음 글로
    return (f'<a class="story-card next-card" href="{url(nxt, lang)}"><span class="next-art"><img src="{thumb.format(lang=lang)}" alt="" width="1600" height="1000" loading="lazy"></span>'
            f'<div class="story-text">{label(T[lang]["next"], "gold")}<h2 class="h2">{s["title"]}</h2><p>{s["excerpt"]}</p>'
            f'<span class="more-link">{T[lang]["read"]}{ARROW_R}</span></div></a>')


def story_post(lang, key):
    src, date, modified, _, thumb, og = POSTS[key]
    s = src[lang]
    out = []
    for b in s['blocks']:
        if b[0] == 'p':
            out.append(f'<p>{b[1]}</p>')
        elif b[0] == 'quote':
            lines = ''.join(f'<p>{x}</p>' for x in b[1])
            out.append(f'<blockquote class="pull">{lines}<cite>{b[2]}</cite></blockquote>')
        elif b[0] == 'img':
            o = 'l' if b[1] in LANDSCAPE else 'p'
            out.append(f'<figure class="fig {o}">{photo_img(b[1], "(min-width: 1100px) 1040px, 96vw" if o == "l" else "(min-width: 600px) 480px, 92vw", b[2])}<figcaption>{b[2]}</figcaption></figure>')
        elif b[0] == 'clips':
            out.append(f'<figure class="fig clips"><div class="clip-row">{"".join(story_clip(n, lab, lang) for n, lab in b[1])}</div><figcaption>{b[2]}</figcaption></figure>')
        elif b[0] == 'row':
            # 같은 높이로 나란히 — 사진 비율만큼 폭을 나눠 가진다
            imgs = ''.join(f'<span style="flex:{photo_size(n)[0] / photo_size(n)[1]:.3f}">{photo_img(n, "(min-width: 800px) 360px, 46vw")}</span>' for n in b[1])
            out.append(f'<figure class="fig row"><div class="row-in">{imgs}</div><figcaption>{b[2]}</figcaption></figure>')
        elif b[0] == 'mix':
            # 사진과 세로 영상을 같은 높이로 나란히 — 'clip:이름'은 영상
            cells = []
            for n in b[1]:
                if n.startswith('clip:'):
                    cells.append(f'<div style="flex:{clip_size(n[5:])[0] / clip_size(n[5:])[1]:.3f}">{story_clip(n[5:], b[2], lang, cap=False)}</div>')  # 영상 칸은 div — span 안에 div를 넣을 수 없다
                else:
                    cells.append(f'<span style="flex:{photo_size(n)[0] / photo_size(n)[1]:.3f}">{photo_img(n, "(min-width: 1100px) 600px, 54vw")}</span>')
            out.append(f'<figure class="fig l row mix"><div class="row-in">{"".join(cells)}</div><figcaption>{b[2]}</figcaption></figure>')
        elif b[0] == 'h2':
            out.append(f'<h2>{b[1]}</h2>')
    # 목록 썸네일과 같은 그림(홈의 폴라로이드 두 장, src/og.py)을 글 머리에 — 목록에서 누른 그 그림으로 글이 열리게
    art = f'<div class="post-hero"><img src="{thumb.format(lang=lang)}" alt="{escape(s["title"])}" width="1600" height="1000"></div>'
    body = f'''
<article class="post"><div class="wrap-post">
{post_head(f'<time datetime="{date}">{s["date"]}</time> · {s["by"]}', s['title'], art)}
<div class="prose">{''.join(out)}</div>
{next_post(lang, key)}
<div class="post-end two"><button class="btn-block btn-dark" type="button" data-share data-title="{escape(s['title'])}" data-copied="{T[lang]['copied']}">{SHARE_ICON}<span aria-live="polite">{T[lang]['share']}</span></button><a class="btn-block btn-grey" href="{url('story', lang)}">{T[lang]['back']}</a></div>
</div></article>
{cta_band(lang)}
'''
    ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': s['title'], 'description': s['excerpt'], 'datePublished': date, 'dateModified': modified, 'inLanguage': lang,
          'image': SITE + og.format(lang=lang), 'author': {'@type': 'Organization', 'name': '응가메이트' if lang == 'ko' else 'POOPIEMATE'},
          'publisher': org_ld(lang)}
    title = s['title'] + (' | 응가메이트 이야기' if lang == 'ko' else ' | POOPIEMATE')
    write(url(key, lang), page(lang, key, title, s['excerpt'], body, og.format(lang=lang), active='story', og_type='article', ld=[ld]))


# ═════════════════════════════════════════════════════════ 공지사항 (캔버스 「v2 공지사항」)
NOTICE = {
    'ko': {'title': '응가메이트 유저 인터뷰에 초대해요', 'date': '2026.10.05', 'by': '응가메이트 팀', 'sub': '보호자님 이야기를 들려주세요. 참여하면 폴 바셋 아이스크림 라떼를 드려요.',
           'body': ['안녕하세요, 응가메이트 팀이에요.<br>매일 강아지의 응가·쉬·산책을 기록해 주셔서 정말 고마워요.',
                    '더 쓰기 편한 응가메이트를 만들고 싶어서, 보호자님의 이야기를 직접 듣고 싶어요.',
                    '<ul><li>앱을 어떻게 쓰고 계신지</li><li>어떤 점이 좋았고, 어떤 점이 아쉬웠는지</li><li>가족과 함께 기록할 때는 어땠는지</li></ul>',
                    '정답은 없어요. 편하게 이야기 나눠 주시면 돼요.', '참여해 주신 분께는 폴 바셋 아이스크림 라떼 기프티콘을 보내드려요.',
                    '원하는 날짜와 시간을 골라 신청해 주세요. 일정이 확정되면 남겨 주신 번호로 연락드릴게요.'],
           'apply': '인터뷰 신청하기'},
    'en': {'title': 'Join a POOPIEMATE user interview', 'date': 'Oct 5, 2026', 'by': 'POOPIEMATE team', 'sub': 'Tell us how you use POOPIEMATE. Interviews are in English and take about 30 minutes.',
           'body': ['Hi from the POOPIEMATE team.<br>Thank you for logging your dog’s poops, pees and walks every day.',
                    'We want to make POOPIEMATE easier to use, so we’d love to hear from you directly.',
                    '<ul><li>How you use the app</li><li>What you like and what could be better</li><li>What logging with your family is like</li></ul>',
                    'There are no right answers — just chat with us.',
                    'Interviews are in English and take about 30 minutes online.',
                    'Pick a date and a time in your own time zone. We’ll contact you once the schedule is confirmed.'],
           'apply': 'Apply for an interview'},
}


def notice_list(lang):
    n = NOTICE[lang]
    c = {'ko': ('공지사항', '업데이트와 이벤트 소식을 알려드려요', '공지사항 | 응가메이트', '가족이 함께 보는 강아지 응가 기록 앱, 응가메이트의 업데이트와 이벤트 소식을 알려드려요.'),
         'en': ('Notices', 'Updates and events from POOPIEMATE', 'Notices | POOPIEMATE', 'Updates and events from POOPIEMATE, the dog potty log your whole family shares.')}[lang]
    body = f'''
<section class="list-page"><div class="wrap-list">
{list_head('megaphone', c[0], c[1])}
<div class="post-grid">
<a class="post-card" href="{url('interview_notice', lang)}"><span class="thumb green"><img src="/assets/img/notice-hero.webp" alt="" loading="lazy" width="1038" height="510">{new_badge("2026-10-05")}</span>
<b>{n['title']}</b><span class="ex">{sb(n['sub'])}</span><time datetime="2026-10-05">{n['date']}</time></a>
</div>
{empty_state(lang, 'notice')}
</div></section>
'''
    write(url('notice', lang), page(lang, 'notice', c[2], c[3], body, '/assets/og/notice.jpg', active='notice'))


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
                                              '/assets/og/notice.jpg', active='notice', og_type='article'))


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
def guide_json(slug, lang):
    f = SRC / f'legacy/guides/{"en/" if lang == "en" else ""}{slug}.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else None


GUIDE_COPY = {
    'ko': {'list': '강아지 가이드', 'toc': '이 글의 순서', 'read': '{n}분 읽기', 'updated': '업데이트', 'related': '같이 보면 좋은 글',
           'app_h': '응가메이트로 같이 기록해요', 'app_p': '응가·산책을 가족과 한 화면에서 봐요.<br>평소와 달라진 날을 바로 알 수 있어요.', 'app_btn': '무료로 시작하기', 'faq': '자주 묻는 질문', 'warn': '알아 두세요'},
    'en': {'list': 'Dog guides', 'toc': 'In this guide', 'read': '{n} min read', 'updated': 'Updated', 'related': 'Keep reading',
           'app_h': 'Log it together with POOPIEMATE', 'app_p': 'See potty and walks with your family on one screen.<br>Spot an off day right away.', 'app_btn': 'Start free', 'faq': 'Frequently asked questions', 'warn': 'Good to know'},
}
WARN_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>'


def _text(h):
    return html_mod.unescape(re.sub(r'<[^>]+>', '', h)).strip()


def guide_article(slug, lang, g):
    """가이드 글 — 옛 글 HTML(src/legacy/guides)을 받아 히어로·목차·카드형 표·앱 카드·FAQ·관련 글 카드로 다시 짠다."""
    c = GUIDE_COPY[lang]
    main = re.sub(r'\s(style|class)="(margin[^"]*)"', '', g['main'])
    main = re.sub(r'href="https://poopiemate\.com/', 'href="/', main)
    h1 = _text(re.search(r'<h1[^>]*>(.*?)</h1>', main, re.S).group(1))
    main = re.sub(r'<h1[^>]*>.*?</h1>', '', main, count=1, flags=re.S)
    lede_m = re.search(r'<p class="lede">(.*?)</p>', main, re.S) or re.search(r'<p>(.*?)</p>', main, re.S)
    lede = lede_m.group(1).strip()
    main = main.replace(lede_m.group(0), '', 1)
    # FAQ — 아래 사이트 공통 아코디언으로 따로 그린다
    faqs = [(_text(q), _text(a)) for q, a in re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*<p[^>]*>(.*?)</p>\s*</details>', main, re.S)]
    main = re.sub(r'<h2>[^<]*(자주 묻는 질문|Frequently Asked Questions|FAQ)[^<]*</h2>', '', main, flags=re.I)
    main = re.sub(r'\s*<details class="faq-item">.*?</details>', '', main, flags=re.S)
    # 관련 글 — 썸네일 카드로
    rel = []
    rm = re.search(r'<p class="related">(.*?)</p>', main, re.S)
    if rm:
        for href, label in re.findall(r'<a href="([^"]+)">(.*?)</a>', rm.group(1)):
            rs = href.strip('/').split('/')[-1]
            if rs and rs != slug:
                rel.append((href, _text(label), (f'en-{rs}' if lang == 'en' else rs)))
        main = main.replace(rm.group(0), '')
    # 앱 카드 — 「응가메이트로…」 소제목 + 카드 + 버튼을 한 장으로
    app_text, app_href = '', '/download/'
    am = re.search(r'(?:<h2>[^<]*</h2>\s*)?<div class="card">\s*(?:<p>)?(.*?)(?:</p>)?\s*</div>\s*(?:<a class="cta" href="([^"]+)">[^<]*</a>)?', main, re.S)
    if am:
        app_text = am.group(1).strip()
        main = main.replace(am.group(0), '')
    main = re.sub(r'\s*<a class="cta" href="[^"]*">[^<]*</a>', '', main)
    # 안내 상자 · 표 · 소제목
    main = re.sub(r'<div class="warn">(.*?)</div>', lambda m: f'<aside class="g-warn">{WARN_ICON}<div><b>{c["warn"]}</b><p>{m.group(1).strip()}</p></div></aside>', main, flags=re.S)
    main = re.sub(r'<table>(.*?)</table>', r'<div class="g-table"><table>\1</table></div>', main, flags=re.S)
    toc = []

    def h2(m):
        i = len(toc) + 1
        inner = re.sub(r'^\s*\d+\.\s*', '', m.group(1))  # 옛 글의 「1. 」 번호는 빼고 순서 번호만
        toc.append(_text(inner))
        return f'<h2 id="s{i}"><span class="g-num">{i:02d}</span>{inner}</h2>'
    main = re.sub(r'<h2>(.*?)</h2>', h2, main, flags=re.S)

    kind = 'poop' if GUIDE_CARDS.get(slug, 1) == 1 else 'walk'
    pose = OG_POSE_SLUG.get(slug, OG_POSE[kind])
    pw, ph = Image.open(ROOT / f'assets/img/mascot/{POSE_WEB[pose]}.webp').size
    head, sub = h1, ''
    parts = re.split(r'(?<=[?？])\s+|,\s+', h1, maxsplit=1)
    if len(parts) == 2 and len(parts[0]) >= 6:
        head, sub = parts
    minutes = max(2, round(len(_text(g['main'])) / (500 if lang == 'ko' else 1100)))
    base = '' if lang == 'ko' else '/en'
    toc_html = ''.join(f'<li><a href="#s{i + 1}">{escape(t)}</a></li>' for i, t in enumerate(toc))
    # 글마다 있던 긴 앱 소개 대신 짧은 두 줄 — 글 안에 앱 카드가 있을 때만 단다
    app = (f'<section class="g-app"><div><h2>{c["app_h"]}</h2><p>{c["app_p"]}</p>'
           f'<a class="g-app-btn" href="{app_href}">{c["app_btn"]} {ARROW_R}</a></div>'
           f'<img src="/assets/img/mascot/pooping.webp" alt="" width="240" height="240" loading="lazy"></section>') if app_text else ''
    rel_html = ''
    if rel:
        rel_html = ('<section class="g-rel"><div class="wrap-list"><h2 class="h3">' + c['related'] + '</h2><div class="post-grid">' + ''.join(
            f'<a class="post-card" href="{h}"><span class="thumb og"><img src="/assets/og/p/{o}.jpg" alt="" width="1200" height="630" loading="lazy"></span><b>{escape(t)}</b></a>'
            for h, t, o in rel[:3]) + '</div></div></section>')
    return f'''
<section class="g-hero k-{kind}"><div class="wrap-g">
<p class="post-meta"><a href="{url("home", lang)}">{T[lang]["name"]}</a> › <a href="{url("guide", lang)}">{c["list"]}</a></p>
<div class="g-hero-grid"><div>
<h1 class="g-h1">{escape(head)}{f'<span>{escape(sub)}</span>' if sub else ''}</h1>
<p class="g-lede">{lede}</p>
<p class="g-meta"><span>{c["read"].format(n=minutes)}</span><span>{c["updated"]} {UPDATED.replace("-", ".")}</span></p>
</div><div class="g-art"><img class="g-pose" src="/assets/img/mascot/{POSE_WEB[pose]}.webp" alt="" width="{pw}" height="{ph}"></div></div>
</div></section>
<div class="wrap-g g-body">
<aside class="g-toc" aria-label="{c["toc"]}"><b>{c["toc"]}</b><ol>{toc_html}</ol></aside>
<article class="g-article prose">{main.strip()}{app}</article>
</div>
<div class="g-faq">{faq_block(lang, faqs) if faqs else ''}</div>
{rel_html}
<div class="g-end"></div>
<script src="/assets/js/guide.js?v={ASSET_V}" defer></script>
'''


def guides():
    for f in sorted((SRC / 'legacy/guides').glob('*.json')):
        slug = f.stem
        has_en = guide_json(slug, 'en') is not None
        for lang in ('ko', 'en') if has_en else ('ko',):
            if lang == 'ko' and slug in tools.TOOL_SLUGS:  # 한국어는 도구 페이지가 같은 주소를 쓴다 (src/tools.py)
                continue
            g = guide_json(slug, lang)
            path = f'/{slug}/' if lang == 'ko' else f'/en/{slug}/'
            write(path, page(lang, None, g['title'], g['description'], guide_article(slug, lang, g), None, ko_path=f'/{slug}/', en_path=f'/en/{slug}/' if has_en else None,
                             active='guide', og_type='article', ld=g['ld'], keywords=g['keywords'],
                             extra_head=f'<link rel="stylesheet" href="/assets/css/tools.css?v={ASSET_V}">\n'))


# 가이드 목록 — 분류 번호(1 배변, 2 산책·가족). 카드 썸네일은 그 글의 OG 이미지(응댕이 + 제목)
GUIDE_CARDS = {
    'poop-condition-guide': 1,
    'potty-interval': 1,
    'outdoor-potty-dog-tracking': 1,
    'jindo-mix-potty-training': 1,
    'dog-diarrhea-causes': 1,
    'dog-constipation-causes': 1,
    'how-to-get-golden-poop': 1,
    'yellow-gray-dog-poop': 1,
    'kibble-vs-cooked-vs-raw-poop': 1,
    'puppy-potty-count-by-size': 1,
    'dog-outdoor-potty-why': 1,
    'outdoor-potty-holding-risks': 1,
    'why-dogs-kick-after-pooping': 1,
    'walk-safety-index': 2,
    'dual-income-dog-walk-schedule': 2,
    'share-dog-potty-log-with-family': 2,
    'multi-dog-household-tracking': 2,
}


def guide_list(lang):
    c = {'ko': ('강아지 가이드', '배변 상태부터 산책 당번까지, 강아지를 같이 돌볼 때 알아 두면 좋은 것들을 모아요', ['전체', '배변', '산책·가족'], '강아지 가이드 | 응가메이트',
                '강아지 응가 상태, 배변 텀, 실외배변, 산책 안전, 맞벌이 산책 당번, 다견가정 기록까지. 가족이 같이 강아지를 돌볼 때 알아 두면 좋은 가이드를 모았어요.'),
         'en': ('Dog guides', 'From poop checks to walk duty: what helps when a family looks after one dog together', ['All', 'Potty', 'Walks & family'], 'Dog guides | POOPIEMATE',
                'Poop color and texture, potty intervals, outdoor-only dogs, walk safety, walk duty for working parents and multi-dog homes, for families who share one dog.')}[lang]
    cats = c[2]
    chips = ''.join(f'<button type="button" data-cat="{"all" if i == 0 else i}" aria-pressed="{"true" if i == 0 else "false"}">{x}</button>' for i, x in enumerate(cats))
    cards = ''
    for slug, cat in GUIDE_CARDS.items():
        g = guide_json(slug, lang)
        if not g:
            continue
        og_slug = slug if lang == 'ko' else f'en-{slug}'
        if og_slug in OG_PAGES and lang == 'ko' and slug in tools.TOOL_SLUGS:  # 한국어 도구 페이지는 도구 제목으로
            h1 = OG_PAGES[og_slug]['head'].replace('<br>', ' ')
        else:
            h1 = html_mod.unescape(re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', g['main'], re.S).group(1))).strip()
        cards += (f'<a class="post-card" data-cat="{cat}" href="{"" if lang == "ko" else "/en"}/{slug}/"><span class="thumb og">'
                  f'<img src="/assets/og/p/{og_slug}.jpg" alt="" width="1200" height="630" loading="lazy"></span>'
                  f'<span class="cat">{cats[cat]}</span><b>{escape(h1)}</b><span class="ex">{sb(escape(g["description"]))}</span></a>')
    body = f'''
<section class="list-page"><div class="wrap-list">
{list_head('paw_prints', c[0], c[1])}
<div class="chips" data-filter role="group" aria-label="{c[0]}">{chips}</div>
<div class="post-grid">{cards}</div>
{empty_state(lang, 'story')}
</div></section>
'''
    write(url('guide', lang), page(lang, 'guide', c[3], c[4], body, f'/assets/og/poopiemate-{lang}.jpg', active='guide'))


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
                f'<meta property="og:image" content="{SITE}{og_image_for(path, lang, og[1], f"<h1>{og[1]}</h1>", "plain")}">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="robots" content="noindex, follow">\n'
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
    og = og_image_for('/download/', 'ko', '', '<h1>응가메이트<br>무료 다운로드</h1>', 'brand')
    html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>응가메이트 다운로드 — iOS·Android 앱 받기</title>
<meta name="description" content="응가메이트를 App Store 또는 Google Play에서 무료로 받으세요. 가족이 함께 강아지 응가·산책을 기록하는 앱이에요.">
<link rel="canonical" href="{SITE}/download/">
<meta name="robots" content="noindex, follow">
<meta name="theme-color" content="#18955A">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/icons/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="응가메이트">
<meta property="og:title" content="응가메이트 무료 다운로드">
<meta property="og:description" content="기록하면 가족 모두에게 바로 알림! 댕댕이 응가·산책을 함께 챙겨요.">
<meta property="og:url" content="{SITE}/download/">
<meta property="og:image" content="{SITE}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}{og}">
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


# ═════════════════════════════════════════════════════════ 옮긴 주소 · 404 · sitemap
# 예전 주소 → 새 주소. 이미 공유된 링크가 끊기지 않게 예전 자리에 바로 넘어가는 작은 페이지를 둔다
MOVED = {'/story/why-we-built/': url('why', 'ko'), '/en/story/why-we-built/': url('why', 'en'),
         '/dog-walk-schedule-sharing/': '/dual-income-dog-walk-schedule/'}  # 산책 당번 가이드는 맞벌이 산책 가이드에 합쳤다


def moved():
    for old, new in MOVED.items():
        write(old, f'''<!doctype html><html lang="{'en' if old.startswith('/en/') else 'ko'}"><head><meta charset="utf-8"><title>{SITE}{new}</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{new}"><meta http-equiv="refresh" content="0; url={new}">
<script>location.replace({json.dumps(new)} + location.search + location.hash)</script></head>
<body><a href="{new}">{SITE}{new}</a></body></html>
''')


def not_found():
    body = '''
<section class="nf"><div class="wrap"><img src="/assets/img/mascot/scratch.webp" alt="" width="200">
<h1 class="h1">페이지를 찾지 못했어요</h1><p class="lead">주소가 바뀌었거나 없는 페이지예요. <span lang="en">Page not found.</span></p>
<div class="nf-btns"><a class="btn-block btn-dark" href="/">홈으로</a><a class="btn-block btn-grey" href="/en/">English</a></div></div></section>
'''
    (ROOT / '404.html').write_text(page('ko', 'home', '페이지를 찾지 못했어요 | 응가메이트', '찾는 페이지가 없어요. 응가메이트 홈에서 가족이 함께 보는 강아지 응가 기록을 만나 보세요.', body, '/assets/og/poopiemate-ko.jpg', noindex=True), encoding='utf-8')


def rss(lang):
    """새 글 알림용 RSS — 이야기와 가이드. 네이버 서치어드바이저에 /rss.xml을 등록해 두면 새 글을 바로 가져간다."""
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    kst = timezone(timedelta(hours=9))
    items = []
    for key, (src, date, _, _, thumb, _) in POSTS.items():
        s = src[lang]
        items.append((datetime.fromisoformat(date).replace(hour=9, tzinfo=kst), s['title'], SITE + url(key, lang), s['excerpt'], T[lang]['nav'][1][1]))
    for f in sorted((SRC / 'legacy/guides').glob('*.json')):
        g = guide_json(f.stem, lang)
        if not g:
            continue
        src_file = f if lang == 'ko' else SRC / f'legacy/guides/en/{f.stem}.json'
        # 가이드는 날짜가 없어서 원본 파일이 저장소에 처음 들어온 날을 쓴다
        added = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%aI', '--', str(src_file)], capture_output=True, text=True, cwd=ROOT).stdout.split()
        when = datetime.fromisoformat(added[-1]) if added else datetime.now(kst)
        h1 = html_mod.unescape(re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', g['main'], re.S).group(1))).strip()
        items.append((when, h1, f'{SITE}{"" if lang == "ko" else "/en"}/{f.stem}/', g['description'], T[lang]['nav'][2][1]))
    items.sort(key=lambda x: x[0], reverse=True)
    home = SITE + url('home', lang)
    title, desc = {'ko': ('응가메이트 이야기·가이드', '가족이 함께 보는 강아지 응가·산책 기록 앱, 응가메이트의 이야기와 강아지 가이드'),
                   'en': ('POOPIEMATE stories and guides', 'Stories and dog guides from POOPIEMATE, the dog potty log your whole family shares')}[lang]
    feed = url('home', lang) + 'rss.xml'
    body = ''.join(f'''
  <item>
    <title>{escape(t_)}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <description>{escape(d)}</description>
    <category>{escape(cat)}</category>
    <pubDate>{format_datetime(when)}</pubDate>
  </item>''' for when, t_, link, d, cat in items)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{title}</title>
  <link>{home}</link>
  <description>{desc}</description>
  <language>{lang}</language>
  <atom:link href="{SITE}{feed}" rel="self" type="application/rss+xml"/>
  <lastBuildDate>{format_datetime(items[0][0])}</lastBuildDate>{body}
</channel>
</rss>
'''
    (ROOT / feed.lstrip('/')).write_text(xml, encoding='utf-8')


def sitemap():
    rows = []
    for key, (ko, en) in PATHS.items():
        pr = '1.0' if key == 'home' else '0.8'
        for loc in (ko, en):
            rows.append(f'''  <url><loc>{SITE}{loc}</loc><lastmod>{UPDATED}</lastmod><priority>{pr}</priority>
    <xhtml:link rel="alternate" hreflang="ko" href="{SITE}{ko}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{ko}"/></url>''')
    for f in sorted((SRC / 'legacy/guides').glob('*.json')):
        ko, en = f'/{f.stem}/', f'/en/{f.stem}/'
        if guide_json(f.stem, 'en') is None:
            rows.append(f'  <url><loc>{SITE}{ko}</loc><lastmod>{UPDATED}</lastmod><priority>0.6</priority></url>')
            continue
        for loc in (ko, en):
            rows.append(f'''  <url><loc>{SITE}{loc}</loc><lastmod>{UPDATED}</lastmod><priority>0.6</priority>
    <xhtml:link rel="alternate" hreflang="ko" href="{SITE}{ko}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{ko}"/></url>''')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                                      + '\n'.join(rows) + '\n</urlset>\n', encoding='utf-8')


if __name__ == '__main__':
    for lang in ('ko', 'en'):
        home(lang); how(lang); story_list(lang); story_post(lang, 'why'); story_post(lang, 'solo'); notice_list(lang); notice_interview(lang)
        for n in ('privacy', 'terms', 'support', 'licenses'):
            legal(n, lang)
    guides()
    write('/poop-condition-guide/', tools.poop_tool(page, faq_block, faq_ld, cta_band, ASSET_V))
    write('/walk-safety-index/', tools.walk_tool(page, faq_block, faq_ld, cta_band, ASSET_V))
    guide_list('ko'); guide_list('en'); interview('ko'); interview('en'); download(); moved(); not_found(); sitemap(); rss('ko'); rss('en')
    (ROOT / '.cache/og').mkdir(parents=True, exist_ok=True)
    (ROOT / '.cache/og/pages.json').write_text(json.dumps(OG_PAGES, ensure_ascii=False, indent=1), encoding='utf-8')
    print('built', len(OG_PAGES), 'og pages')
