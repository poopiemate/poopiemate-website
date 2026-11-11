"""네이버 블로그 썸네일 1080×1080 — 응댕이 주제 포즈 + 큰 제목 두 줄. 시리즈가 한눈에 같은 브랜드로 보이게 틀은 하나로 고정한다.

검색 결과에선 썸네일이 손톱만 하게 보여서 제목은 한 줄 6~8자, 두 줄까지만. 응댕이는 오른쪽 아래에 크게.
그림은 ChatGPT로 만든다(응댕이 포즈 PNG를 첨부해 장면을 그리게 하고 글자는 넣지 않게) → 썸네일/chatgpt/<key>.png.
그 그림이 있으면 바탕으로 깔고 제목만 앱 글꼴로 얹는다(ChatGPT는 한글을 자주 틀려서). 없으면 포즈 PNG 한 장으로 그린다.
python3 src/blog_thumb.py → ~/Desktop/응가메이트/블로그/썸네일/<key>.jpg
"""
from pathlib import Path

from og import TMP, shot
from og_scenes import BG, EMOJI, NEW, POSE, WEB_EMOJI

ROOT = Path(__file__).resolve().parent.parent
OUT = Path.home() / 'Desktop/응가메이트/블로그/썸네일'
ART = OUT / 'chatgpt'
# ChatGPT 그림을 얼마나 아래로 내릴지(px, 1080 기준) — 제목과 응댕이가 겹치지 않게. 빈 위쪽은 그림 맨 위 색으로 채운다
ART_SHIFT = {'winter-walk-temperature': 230, 'puppy-2-month-potty': 230, 'dog-winter-clothes-warmth': 230}

# key: (바탕, 칩, 제목(<br>로 두 줄), 부제, 포즈, 곁들일 3D 이모지)
THUMBS = {
    'winter-walk-temperature': ('sky', '겨울 산책', '겨울 산책<br>몇 도까지?', '체감온도·크기별 기준표', 'leash', 'snowflake'),
    'puppy-2-month-potty': ('peach', '아기 강아지', '2개월 강아지<br>배변 횟수', '하루 몇 번이 정상일까', 'baby', None),
    'dog-winter-clothes-warmth': ('lilac', '겨울 옷', '강아지 옷<br>뭐가 제일 따뜻해?', '패딩·플리스·니트·김장조끼', 'coat', None),
}


def _src(pose):
    p = NEW / f'{pose}.png'
    return p if p.exists() else POSE / f'{pose}.png'


def _emoji(name):
    p = EMOJI / f'{name}.png'
    return p if p.exists() else WEB_EMOJI / f'{name}.webp'


def html(bg_key, chip, head, sub, pose, emo, key=''):
    a = ROOT / 'assets'
    art = ART / f'{key}.png'
    bg, accent, ground = BG[bg_key]
    lines = head.split('<br>')
    size = 118 if max(len(x) for x in lines) <= 6 else 104 if max(len(x) for x in lines) <= 8 else 92
    e = (f'<img class="emo" src="file://{_emoji(emo)}">' if emo else '')
    dog = f'<img class="dog" src="file://{_src(pose)}">'
    art_css = ''
    if art.exists():
        from PIL import Image
        im = Image.open(art).convert('RGB')
        top = im.resize((1, 1), box=(0, 0, im.width, 8)).getpixel((0, 0))  # 그림 맨 위 줄 평균색
        bg = '#%02x%02x%02x' % top
        shift = ART_SHIFT.get(key, 200)
        e, dog = '', f'<img class="art" src="file://{art}">'
        art_css = (f'.art{{position:absolute;left:0;top:{shift}px;width:1080px;height:1080px}}'
                   f'.fade{{position:absolute;left:0;right:0;top:{shift}px;height:160px;background:linear-gradient({bg},rgba(0,0,0,0));z-index:1}}'
                   '.glow,.ground{display:none}.mark,.chip,h1,.sub{z-index:2}')
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
@font-face{{font-family:N;src:url("file://{a}/fonts/NanumSquareNeo-dEb.woff2");font-weight:800}}
@font-face{{font-family:N;src:url("file://{a}/fonts/NanumSquareNeo-cBd.woff2");font-weight:700}}
html,body{{margin:0}}
.c{{position:relative;width:1080px;height:1080px;overflow:hidden;background:{bg};font-family:N,sans-serif;color:#191F28;word-break:keep-all}}
.glow{{position:absolute;right:-260px;bottom:-200px;width:1100px;height:1100px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.65),rgba(255,255,255,0) 62%)}}
.ground{{position:absolute;left:280px;right:-120px;bottom:-190px;height:330px;border-radius:50%;background:{ground};opacity:.55}}
.mark{{position:absolute;left:84px;top:84px;height:52px}}
.chip{{position:absolute;left:84px;top:196px;padding:12px 26px;border-radius:999px;background:rgba(255,255,255,.9);color:{accent};font-size:34px;font-weight:800}}
h1{{position:absolute;left:84px;right:60px;top:290px;margin:0;font-size:{size}px;line-height:1.18;font-weight:800;letter-spacing:-.045em}}
.sub{{position:absolute;left:88px;top:{290 + round(size * 1.18 * len(lines)) + 26}px;margin:0;font-size:40px;font-weight:700;color:#4E5968;letter-spacing:-.02em}}
.dog{{position:absolute;right:40px;bottom:30px;height:470px;filter:drop-shadow(0 22px 30px rgba(25,31,40,.16))}}
.emo{{position:absolute;right:70px;top:80px;height:150px;transform:rotate(10deg);filter:drop-shadow(0 12px 16px rgba(25,31,40,.16))}}
{art_css}</style></head><body><div class="c"><span class="glow"></span><span class="ground"></span>
<img class="mark" src="file://{a}/brand/wordmark-ko-green.svg"><span class="chip">{chip}</span>
{dog}{'<span class="fade"></span>' if art_css else ''}<h1>{head}</h1><p class="sub">{sub}</p>{e}</div></body></html>'''


def main(only=None):
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for key, spec in THUMBS.items():
        if only and key not in only:
            continue
        shot(html(*spec, key=key), TMP / f'blog-{key}.png', 1080, 1080).save(OUT / f'{key}.jpg', quality=90, optimize=True, progressive=True)
        print('blog thumb', OUT / f'{key}.jpg')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
