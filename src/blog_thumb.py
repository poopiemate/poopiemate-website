"""네이버 블로그 썸네일 1080×1080 — 응댕이 주제 포즈 + 큰 제목 두 줄. 시리즈가 한눈에 같은 브랜드로 보이게 틀은 하나로 고정한다.

검색 결과에선 썸네일이 손톱만 하게 보여서 제목은 한 줄 6~8자, 두 줄까지만. 응댕이는 오른쪽 아래에 크게.
python3 src/blog_thumb.py → ~/Desktop/응가메이트/블로그/썸네일/<key>.jpg
"""
from pathlib import Path

from og import TMP, shot
from og_scenes import BG, EMOJI, NEW, POSE, WEB_EMOJI

ROOT = Path(__file__).resolve().parent.parent
OUT = Path.home() / 'Desktop/응가메이트/블로그/썸네일'

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


def html(bg_key, chip, head, sub, pose, emo):
    a = ROOT / 'assets'
    bg, accent, ground = BG[bg_key]
    lines = head.split('<br>')
    size = 118 if max(len(x) for x in lines) <= 6 else 104 if max(len(x) for x in lines) <= 8 else 92
    e = (f'<img class="emo" src="file://{_emoji(emo)}">' if emo else '')
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
</style></head><body><div class="c"><span class="glow"></span><span class="ground"></span>
<img class="mark" src="file://{a}/brand/wordmark-ko-green.svg"><span class="chip">{chip}</span>
<h1>{head}</h1><p class="sub">{sub}</p>{e}<img class="dog" src="file://{_src(pose)}"></div></body></html>'''


def main(only=None):
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for key, spec in THUMBS.items():
        if only and key not in only:
            continue
        shot(html(*spec), TMP / f'blog-{key}.png', 1080, 1080).save(OUT / f'{key}.jpg', quality=90, optimize=True, progressive=True)
        print('blog thumb', OUT / f'{key}.jpg')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
