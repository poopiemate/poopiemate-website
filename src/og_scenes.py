"""페이지별 OG 그림 — 오른쪽 무대에 응댕이 포즈 + 글 주제 소품(앱 응가 그림, 동네 손그림 레이어, 3D 이모지, 실제 사진)을 놓는다.

같은 응댕이가 반복돼 보이지 않게 페이지마다 포즈·소품·바탕색을 다르게 고른다. 3D 이모지는 뜻이 있을 때만(산책 날씨·공지) 쓴다. 영어 페이지는 같은 주제의 한국어 장면을 쓴다(글자가 달라 그림은 겹쳐도 된다).
좌표는 1200×630 캔버스 기준: x = 가운데 x, b = 바닥에서 띄운 높이, h = 높이(px), r = 기울기(deg).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYER = Path.home() / 'Desktop/응가메이트/홈페이지_v3_레이어'
POSE = LAYER / '응댕이/포즈'
POOP = ROOT / 'assets/img/poop'
EMOJI = Path.home() / 'project/poopiemate/assets/emoji'  # 앱 3D 이모지(Fluent)
WEB_EMOJI = ROOT / 'assets/img/emoji'
PHOTO = ROOT / 'assets/img/photo'


NEW = ROOT / 'src/art/poses-new'  # 2026-10-30 새로 만든 주제별 포즈 (돋보기·배아픔·밥그릇·자명종·뒷발차기·산책줄·폰·노트북·마이크·편지·트로피·문 앞·애기 응댕이·엄마와 애기)


def dog(pose, x, h, b=34, r=0, flip=False):
    src = NEW / f'{pose}.png' if (NEW / f'{pose}.png').exists() else POSE / f'{pose}.png'
    return {'src': src, 'x': x, 'b': b, 'h': h, 'r': r, 'flip': flip, 'z': 5, 'shadow': True}


def lay(rel, x, h, b=34, r=0, z=2, flip=False):
    return {'src': LAYER / rel, 'x': x, 'b': b, 'h': h, 'r': r, 'flip': flip, 'z': z}


def poop(name, x, h, b=34, r=0, z=6):  # 응가 그림은 480×360 캔버스에 여백·그림자가 있어 1.35배로 키워 놓는다
    return {'src': POOP / f'{name}.webp', 'x': x, 'b': b - 12, 'h': round(h * 1.35), 'r': r, 'z': z}


def emo(name, x, h, b, r=0, z=7):
    p = EMOJI / f'{name}.png'
    return {'src': p if p.exists() else WEB_EMOJI / f'{name}.webp', 'x': x, 'b': b, 'h': h, 'r': r, 'z': z, 'float': True}


def photo(name, x, b, w, r, cap='', z=4):
    return {'photo': PHOTO / f'{name}-900.webp', 'x': x, 'b': b, 'w': w, 'r': r, 'cap': cap, 'z': z}


# 바탕 (배경, 칩 글자색, 땅 그림자색) — 앱 파스텔 틴트에서
BG = {
    'cream': ('#FFF4D1', '#8A5E0A', '#F3DFA0'), 'gold': ('#FFE9A6', '#8A5E0A', '#F0CF6A'), 'peach': ('#FFE7D6', '#B5531F', '#F6C9A9'),
    'mint': ('#DDF3E6', '#127F4A', '#B5E2C6'), 'sky': ('#DCEEFB', '#1E6FA8', '#B3D6F0'), 'lilac': ('#ECE5FF', '#6B4BC2', '#CFC2F5'),
    'pink': ('#FFE6EE', '#B03A64', '#F6C2D3'), 'lemon': ('#F6F4D8', '#6F6A12', '#E2DDA4'), 'stone': ('#EEF0F3', '#4E5968', '#D3D8DF'),
    'green': ('#18955A', '#FFE27A', '#127F4A'), 'sage': ('#E6F0E1', '#4A7A2C', '#C6DDB9'),
}

SCENES = {
    # ── 무료 도구 (초록)
    'poop-condition-guide': ('green', [dog('magnify', 980, 330, b=50), poop('color-yellow', 720, 92, b=46, r=-6), poop('color-green', 800, 74, b=30, r=5),
                                       poop('color-gray', 1150, 78, b=40, r=-4)]),
    'walk-safety-index': ('green', [lay('나무/나무_05.png', 760, 260, b=110, z=1), lay('나무/나무_02.png', 1120, 230, b=130, z=1), dog('leash', 930, 300, b=46),
                                    emo('sun_behind_small_cloud', 1100, 110, 450)]),
    # ── 배변 가이드
    'dog-diarrhea-causes': ('peach', [dog('tummy', 960, 340, b=46), poop('firm-6', 760, 120, b=40, r=-3), poop('firm-7', 1140, 96, b=30)]),
    'dog-constipation-causes': ('lemon', [lay('나무/나무_08.png', 1120, 220, b=100, z=1), lay('나무/덤불_02.png', 760, 90, b=40, z=3), dog('응가전', 930, 280, b=56), poop('firm-1', 1090, 66, b=40, z=7)]),
    'how-to-get-golden-poop': ('gold', [dog('trophy', 1040, 330, b=44), poop('firm-2', 780, 170, b=50, r=-4)]),
    'yellow-gray-dog-poop': ('stone', [dog('귀쫑긋', 1060, 330, b=40), poop('color-yellow', 770, 130, b=56, r=-5), poop('color-gray', 880, 104, b=34, r=4)]),
    'kibble-vs-cooked-vs-raw-poop': ('mint', [dog('bowl', 1000, 330, b=44), poop('firm-3', 760, 90, b=44)]),
    'puppy-potty-count-by-size': ('pink', [dog('family', 1010, 320, b=40), dog('baby-ball', 700, 150, b=40)]),
    'dog-outdoor-potty-why': ('sky', [lay('나무/나무_01.png', 1110, 300, b=110, z=1), lay('나무/덤불_01.png', 720, 100, b=40, z=3), lay('장소/똥스팟.png', 920, 130, b=26, z=1),
                                      dog('응가중', 920, 300, b=64)]),
    'outdoor-potty-holding-risks': ('lilac', [dog('door', 980, 340, b=40)]),
    'why-dogs-kick-after-pooping': ('sage', [lay('장소/똥스팟.png', 900, 120, b=24, z=1), dog('kick', 930, 260, b=60), lay('소품/나뭇잎.png', 700, 64, b=330, r=-30, z=7),
                                             lay('소품/단풍잎.png', 790, 50, b=430, r=20, z=7), lay('소품/나뭇잎.png', 1150, 56, b=400, r=40, z=7)]),
    'potty-interval': ('cream', [lay('광장/시계탑.png', 1130, 420, b=40, z=1), dog('clock', 880, 320, b=40), poop('color-brown', 700, 80, b=40)]),
    'outdoor-potty-dog-tracking': ('sky', [lay('나무/나무_11.png', 800, 230, b=110, z=1), lay('나무/나무_06.png', 1140, 250, b=100, z=1), dog('phone', 960, 320, b=40)]),
    'jindo-mix-potty-training': ('peach', [dog('baby', 760, 180, b=40), dog('귀쫑긋', 1020, 330, b=40)]),
    # ── 산책·가족 가이드
    'multi-dog-household-tracking': ('pink', [dog('배보여주기', 1040, 250, b=40), dog('baby-walk', 790, 200, b=40)]),
    'share-dog-potty-log-with-family': ('cream', [lay('건물/우리집.png', 1080, 300, b=56, z=1), dog('letter', 820, 320, b=34)]),
    'dual-income-dog-walk-schedule': ('sky', [lay('건물/카페.png', 1090, 300, b=56, z=1), dog('laptop', 830, 300, b=38)]),
    # ── 목록 · 브랜드
    'guide': ('mint', [lay('광장/게시판.png', 1110, 260, b=56, z=1), lay('나무/나무_09.png', 790, 210, b=100, z=1), dog('안녕', 930, 320, b=34)]),
    'how-it-works': ('green', [dog('phone', 950, 340, b=44)]),
    'download': ('green', [dog('애교', 1000, 340, b=40), {'src': Path.home() / 'project/poopiemate/assets/icon.png', 'x': 780, 'b': 250, 'h': 150, 'r': -8, 'z': 6, 'icon': True}]),
    # ── 이야기 (실제 사진)
    'story': ('peach', [photo('kennel', 820, 120, 240, -6, '분홍이 시절'), photo('home-now', 1030, 140, 240, 5, '지금 우리 집')]),
    'story-why-i-built-poopiemate': ('cream', [photo('first-paws', 820, 120, 240, -5, '처음 만난 날'), photo('lawn-walk', 1030, 140, 240, 6, '같이 걷는 길')]),
    'story-developer-to-solo-builder': ('sky', [photo('solo-app-ko', 820, 130, 240, -5), photo('solo-trip-dog-sofa', 1030, 140, 240, 6)]),
    # ── 공지 · 인터뷰
    'notice': ('lilac', [lay('광장/게시판.png', 1080, 290, b=56, z=1), dog('귀쫑긋', 820, 320, b=34), emo('megaphone', 1150, 84, 440, r=12)]),
    'notice-interview': ('lilac', [dog('mic', 980, 340, b=40)]),
    'interview': ('mint', [lay('건물/카페.png', 1100, 300, b=56, z=1), dog('mic', 840, 320, b=34)]),
    # ── 이용 안내
    'privacy': ('stone', [lay('건물/우리집.png', 1080, 290, b=56, z=1), dog('앉아있기', 830, 290, b=34)]),
    'terms': ('stone', [lay('광장/게시판.png', 1090, 260, b=56, z=1), dog('애교', 850, 310, b=34)]),
    'licenses': ('sage', [lay('나무/나무_07.png', 1110, 270, b=90, z=1), lay('나무/덤불_02.png', 700, 90, b=40, z=3), dog('배보여주기', 900, 240, b=40)]),
    'support': ('pink', [dog('letter', 960, 340, b=40)]),
    '404': ('lemon', [lay('장소/사다리.png', 1120, 290, b=40, r=8, z=1), lay('소품/비둘기_1.png', 720, 80, b=40, z=6), dog('긁기', 910, 320, b=40)]),
}


def stage(slug):
    base = slug[3:] if slug.startswith('en-') else slug
    return SCENES.get(base)


def item_html(it):
    z = it.get('z', 2)
    if 'photo' in it:
        cap = f'<figcaption>{it["cap"]}</figcaption>' if it['cap'] else ''
        return (f'<figure class="ph" style="left:{it["x"] - it["w"] / 2}px;bottom:{it["b"]}px;width:{it["w"]}px;transform:rotate({it["r"]}deg);z-index:{z}">'
                f'<img src="file://{it["photo"]}">{cap}</figure>')
    tf = f'rotate({it["r"]}deg)' + (' scaleX(-1)' if it.get('flip') else '')
    cls = 'it' + (' sh' if it.get('shadow') else '') + (' fl' if it.get('float') else '') + (' ic' if it.get('icon') else '')
    return (f'<img class="{cls}" src="file://{it["src"]}" style="left:{it["x"]}px;bottom:{it["b"]}px;height:{it["h"]}px;'
            f'transform:translateX(-50%) {tf};z-index:{z}">')


EN_CAP = {'분홍이 시절': 'Bunhong days', '지금 우리 집': 'Home now', '처음 만난 날': 'The day we met', '같이 걷는 길': 'Our walks'}


def stage_html(slug):
    sc = stage(slug)
    if not sc:
        return None
    bg, items = sc
    if slug.startswith('en-'):
        items = [dict(it, cap=EN_CAP.get(it['cap'], it['cap'])) if it.get('cap') else it for it in items]
    return BG[bg], ''.join(item_html(it) for it in items)
