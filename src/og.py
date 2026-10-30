"""공유 미리보기(OG) 이미지 1200×630 — 캔버스 「OG A」: 초록 바탕 가운데 은은한 빛, 위에 응댕이 얼굴, 아래 흰 워드마크. 글은 넣지 않는다.
대부분의 페이지가 언어별로 한 장을 같이 쓴다 (assets/og/poopiemate-{ko,en}.jpg). 이야기·공지는 따로 (story-{ko,en}.jpg, notice.jpg).
크롬 headless로 그려 JPG로 저장한다.

python3 src/og.py
"""
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / '.cache/og'
FACE = Path.home() / 'Desktop/응가메이트/홈페이지_v3_레이어/응댕이/포즈/얼굴.png'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
# 워드마크 폭·위치 — 한국어 500px(위 398), 영어 560px(위 404)
LOGO = {'ko': (500, 398), 'en': (560, 404)}


def html(lang):
    w, top = LOGO[lang]
    a = ROOT / 'assets'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0}}
.c{{position:relative;width:1200px;height:630px;overflow:hidden;background:#18955A}}
.glow{{position:absolute;left:50%;top:50%;width:1000px;height:1000px;margin:-500px 0 0 -500px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.15),rgba(255,255,255,0) 60%)}}
.face{{position:absolute;left:50%;top:66px;width:380px;transform:translateX(-50%);filter:drop-shadow(0 22px 36px rgba(6,60,34,.4))}}
.logo{{position:absolute;left:50%;top:{top}px;width:{w}px;transform:translateX(-50%)}}
</style></head><body><div class="c"><span class="glow"></span>
<img class="face" src="file://{FACE}"><img class="logo" src="file://{a}/brand/wordmark-{lang}-white.svg"></div></body></html>'''


# 이야기 — 홈 「응가메이트 이야기」처럼 폴라로이드 두 장을 크림 바탕 가운데에 (지금 우리 집은 웃는 여왕님 사진). 목록 썸네일·글 머리(16:10)와 공유 이미지에 같이 쓴다
STORY_CAP = {'ko': ('분홍이 시절', '우리 집 메로나'), 'en': ('Bunhong days', 'Melona at home')}


def story_html(lang, w, h, zoom):
    a = ROOT / 'assets'
    cap = STORY_CAP[lang]
    fig = lambda name, c, pos: (f'<figure style="{pos}"><img src="file://{a}/img/photo/{name}-900.webp"><figcaption>{c}</figcaption></figure>')
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:N;src:url("file://{a}/fonts/NanumSquareNeo-dEb.woff2");font-weight:800}}
html,body{{margin:0}}
.c{{display:grid;place-items:center;width:{w}px;height:{h}px;overflow:hidden;background:#FFF6D6}}
.p{{position:relative;top:14px;width:384px;height:330px;zoom:{zoom}}}
figure{{position:absolute;margin:0;width:196px;padding:10px 10px 0;box-sizing:border-box;background:#FFFFFF;border-radius:8px;box-shadow:0 12px 26px rgba(25,31,40,.18)}}
img{{display:block;width:176px;height:216px;object-fit:cover;object-position:50% 35%;border-radius:4px}}
figcaption{{padding:10px 0 12px;text-align:center;font:800 16px N,sans-serif;color:#4E5968}}
</style></head><body><div class="c"><div class="p">
{fig('kennel', cap[0], 'left:0;top:18px;transform:rotate(-6deg)')}{fig('home-now', cap[1], 'right:0;top:0;transform:rotate(5deg)')}
</div></div></body></html>'''


# 공지 — 앱 공지 상세의 초록 무대(src/render/notice_hero.html)를 같은 초록 바탕 가운데에 크게
def notice_html():
    app = Path.home() / 'project/poopiemate'
    src = (ROOT / 'src/render/notice_hero.html').read_text(encoding='utf-8').replace('APP/', f'file://{app}/')
    return src.replace('html,body{margin:0;background:transparent}',
                       'html,body{margin:0;background:#18955A}body{display:grid;place-items:center;width:1200px;height:630px;overflow:hidden}.card{zoom:3.468}')


def shot(src, png, w, h):
    h_ = TMP / (png.stem + '.html')
    h_.write_text(src, encoding='utf-8')
    for i in range(3):  # 헤드리스 크롬이 가끔 그냥 실패한다 — 두 번 더. 프로필은 매번 새로(같이 쓰면 잠금 때문에 느려진다)
        with tempfile.TemporaryDirectory(prefix='og-chrome-') as prof:
            r = subprocess.run([CHROME, '--headless=new', f'--user-data-dir={prof}', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files', f'--window-size={w},{h}',
                                '--virtual-time-budget=2000', f'--screenshot={png}', f'file://{h_}'], capture_output=True)
        if r.returncode == 0:
            break
    r.check_returncode()
    return Image.open(png).convert('RGB')


def pages():
    out = ROOT / 'assets/og'
    for lang in ('ko', 'en'):
        shot(story_html(lang, 1200, 630, 2.0), TMP / f'story-{lang}.png', 1200, 630).save(out / f'story-{lang}.jpg', quality=88, optimize=True, progressive=True)
        shot(story_html(lang, 1600, 1000, 3.1), TMP / f'story-thumb-{lang}.png', 1600, 1000).save(ROOT / f'assets/img/story-thumb-{lang}.webp', 'WEBP', quality=84, method=6)
        print('og story', lang)
    shot(notice_html(), TMP / 'notice.png', 1200, 630).save(out / 'notice.jpg', quality=88, optimize=True, progressive=True)
    print('og notice')


# ═════════════════════════════════════════════════════════ 페이지별 OG — 응댕이 포즈 + 페이지 제목 (build.py가 남긴 .cache/og/pages.json)
POSES = Path.home() / 'Desktop/응가메이트/홈페이지_v3_레이어/응댕이/포즈'
# 종류별 바탕 · 강조색 · 글자색 — 앱 토큰 색(브랜드 초록, 파스텔 틴트)에서
THEME = {
    'poop': ('#FFF3CC', '#8A5E0A', '#191F28'), 'walk': ('#DDEFFB', '#1E6FA8', '#191F28'), 'tool': ('#18955A', '#FFE27A', '#FFFFFF'),
    'story': ('#FFE9D6', '#B5531F', '#191F28'), 'notice': ('#EDE3FF', '#6B4BC2', '#191F28'), 'brand': ('#18955A', '#FFE27A', '#FFFFFF'),
    'plain': ('#E8F5EE', '#127F4A', '#191F28'),
}


def head_size(head):
    longest = max(len(x) for x in head.split('<br>'))
    if '<br>' in head:
        return 64 if longest <= 14 else 56
    n = len(head)
    return 84 if n <= 9 else 74 if n <= 14 else 64 if n <= 22 else 54 if n <= 40 else 46


def page_html(p):
    a = ROOT / 'assets'
    bg, accent, fg = THEME[p['kind']]
    dark = fg == '#FFFFFF'
    mark = f'{a}/brand/wordmark-{p["lang"]}-{"white" if dark else "green"}.svg'
    sub = f'<p class="sub">{p["sub"]}</p>' if p['sub'] else ''
    return f'''<!doctype html><html lang="{p['lang']}"><head><meta charset="utf-8"><style>
@font-face{{font-family:N;src:url("file://{a}/fonts/NanumSquareNeo-dEb.woff2");font-weight:800}}
@font-face{{font-family:N;src:url("file://{a}/fonts/NanumSquareNeo-cBd.woff2");font-weight:700}}
html,body{{margin:0}}
.c{{position:relative;width:1200px;height:630px;overflow:hidden;background:{bg};font-family:N,sans-serif;color:{fg};word-break:keep-all}}
.glow{{position:absolute;right:-120px;bottom:-260px;width:820px;height:820px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,{.16 if dark else .7}),rgba(255,255,255,0) 64%)}}
.t{{position:absolute;left:76px;top:70px;bottom:70px;width:{640 if p['sub'] or len(p['head']) > 9 else 600}px;display:flex;flex-direction:column}}
.mark{{height:{46 if p['lang'] == 'ko' else 34}px;width:auto;align-self:flex-start}}
.copy{{margin-top:auto;margin-bottom:auto;padding-top:8px}}
.chip{{display:inline-block;padding:9px 18px;border-radius:999px;background:{'rgba(255,255,255,.16)' if dark else 'rgba(255,255,255,.85)'};color:{accent if not dark else '#FFFFFF'};font-size:24px;font-weight:800}}
h1{{text-wrap:balance;margin:22px 0 0;font-size:{head_size(p['head'])}px;line-height:1.24;font-weight:800;letter-spacing:-.035em}}
.sub{{text-wrap:pretty;margin:20px 0 0;font-size:30px;line-height:1.4;font-weight:700;color:{'rgba(255,255,255,.86)' if dark else '#4E5968'};letter-spacing:-.02em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.dog{{position:absolute;right:56px;bottom:34px;height:{430 if p['pose'] != '배보여주기' else 360}px;width:auto;filter:drop-shadow(0 18px 30px rgba(6,60,34,{.32 if dark else .16}))}}
</style></head><body><div class="c"><span class="glow"></span>
<div class="t"><img class="mark" src="file://{mark}"><div class="copy"><span class="chip">{p['chip']}</span><h1>{p['head']}</h1>{sub}</div></div>
<img class="dog" src="file://{POSES}/{p['pose']}.png"></div></body></html>'''


def page_ogs(only=None):
    """바뀐 페이지만 다시 그린다 — 그린 내용은 .cache/og/done.json에 기억."""
    import hashlib, json
    specs = json.loads((TMP / 'pages.json').read_text(encoding='utf-8'))
    done_f = TMP / 'done.json'
    done = json.loads(done_f.read_text()) if done_f.exists() else {}
    out = ROOT / 'assets/og/p'
    out.mkdir(parents=True, exist_ok=True)
    for slug, p in specs.items():
        if only and slug not in only:
            continue
        src = page_html(p)
        h = hashlib.sha1(src.encode()).hexdigest()
        if done.get(slug) == h and (out / f'{slug}.jpg').exists():
            continue
        shot(src, TMP / f'p-{slug}.png', 1200, 630).save(out / f'{slug}.jpg', quality=86, optimize=True, progressive=True)
        done[slug] = h
        done_f.write_text(json.dumps(done, indent=1))  # 중간에 멈춰도 그린 것과 기록이 어긋나지 않게 한 장마다
        print('og', slug)
    # 더는 없는 페이지의 이미지는 지운다
    for f in out.glob('*.jpg'):
        if f.stem not in specs:
            f.unlink()


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    out = ROOT / 'assets/og'
    out.mkdir(parents=True, exist_ok=True)
    for lang in ('ko', 'en'):
        h = TMP / f'og-{lang}.html'
        h.write_text(html(lang), encoding='utf-8')
        png = TMP / f'og-{lang}.png'
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files', '--window-size=1200,630',
                        '--virtual-time-budget=2000', f'--screenshot={png}', f'file://{h}'], check=True, capture_output=True)
        img = Image.open(png).convert('RGB')
        img.save(out / f'poopiemate-{lang}.jpg', quality=88, optimize=True, progressive=True)
        # 예전 주소로 공유된 링크도 새 이미지를 보게
        img.save(ROOT / f'assets/og-image-{lang}.jpg', quality=88, optimize=True, progressive=True)
        print('og', lang)
    pages()
    page_ogs()


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['pages']:  # 페이지별 OG만: python3 src/og.py pages
        TMP.mkdir(parents=True, exist_ok=True)
        page_ogs()
    else:
        main()
