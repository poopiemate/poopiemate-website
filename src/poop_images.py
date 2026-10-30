"""똥 상태 체크 그림 — 앱의 응가 이미지(poopiemate 앱 assets/mascot/pooping/poop.png)를 색깔·굳기별로 바꿔 만든다.

python3 src/poop_images.py   # assets/img/poop/*.webp
색깔은 원본의 명암을 그대로 두고 색만 바꾸고, 굳기는 같은 똥을 눌러 납작하게 하거나(무른 변·설사) 작게 여러 개(딱딱한 알갱이)로 만든다.
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src/art/poop.png'  # 앱 assets/mascot/pooping/poop.png 복사본
OUT = ROOT / 'assets/img/poop'
W, H = 240, 180  # 2배 해상도 캔버스 — 화면에선 120×90 안쪽으로 쓴다


def base():
    im = Image.open(SRC).convert('RGBA')
    k = 140 / im.height  # 캔버스(높이 180)에 위아래 여유를 두고 들어가게
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)


def recolor(im, rgb, gloss=1.0):
    """원본 밝기(평균 대비)를 새 색에 곱한다 — 클레이 명암은 그대로, 색만 바뀐다."""
    r, g, b, a = im.split()
    lum = Image.merge('RGB', (r, g, b)).convert('L')
    px = [p for p, al in zip(lum.getdata(), a.getdata()) if al > 200]
    mean = sum(px) / len(px)
    out = Image.new('RGBA', im.size)
    data = []
    for l, al in zip(lum.getdata(), a.getdata()):
        k = (l / mean) ** gloss
        data.append(tuple(min(255, int(c * k)) for c in rgb) + (al,))
    out.putdata(data)
    return out


def squash(im, sx, sy):
    return im.resize((max(1, int(im.width * sx)), max(1, int(im.height * sy))), Image.LANCZOS)


def place(*items):
    """(그림, 가운데 x, 바닥 y) 들을 캔버스에 놓고, 바닥에 옅은 그림자를 깐다."""
    c = Image.new('RGBA', (W, H))
    sh = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(sh)
    for im, cx, by in items:
        d.ellipse((cx - im.width * .46, by - 7, cx + im.width * .46, by + 5), fill=(25, 31, 40, 34))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    for im, cx, by in items:
        c.alpha_composite(im, (int(cx - im.width / 2), int(by - im.height)))
    return c


def puddle(src):
    """물설사 — 모양 없이 퍼진 웅덩이 (원본 똥 색으로 칠하고 윗면에 반사광)."""
    c = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(c)
    col = src.getpixel((src.width // 2, int(src.height * .7)))[:3]
    for x0, y0, x1, y1 in ((20, H - 44, 212, H - 14), (150, H - 56, 226, H - 28), (8, H - 34, 70, H - 16)):
        d.ellipse((x0, y0, x1, y1), fill=col + (235,))
    d.ellipse((24, H - 52, 34, H - 44), fill=col + (220,))
    d.ellipse((60, H - 38, 130, H - 32), fill=(255, 255, 255, 70))
    return c.filter(ImageFilter.GaussianBlur(.6))


def masked(overlay, shape):
    """그림 위에만 보이게 — 똥 모양(알파) 밖은 지운다."""
    o = overlay.copy()
    o.putalpha(ImageChops.multiply(overlay.getchannel('A'), shape.getchannel('A')))
    return o


def deco(im, kind):
    o = Image.new('RGBA', im.size)
    d = ImageDraw.Draw(o)
    w, h = im.size
    if kind == 'red':  # 선홍색 피 줄
        for y, x0, x1 in ((.42, .22, .62), (.62, .35, .86), (.80, .12, .5)):
            d.arc((w * x0, h * y - 14, w * x1, h * y + 14), 200, 340, fill=(214, 46, 40, 235), width=6)
    elif kind == 'specks':  # 흰 쌀알 알갱이
        for x, y in ((.3, .5), (.55, .36), (.68, .62), (.4, .78), (.78, .82), (.5, .58)):
            d.ellipse((w * x - 7, h * y - 4, w * x + 7, h * y + 4), fill=(255, 252, 238, 255), outline=(200, 190, 170, 255), width=1)
    elif kind == 'mucus':  # 젤리 같은 점액 막
        glaze = Image.new('RGBA', im.size, (226, 238, 232, 70))
        o = masked(glaze, im)
        d = ImageDraw.Draw(o)
        d.arc((w * .18, h * .3, w * .82, h * 1.05), 200, 320, fill=(255, 255, 255, 210), width=5)
        return Image.alpha_composite(im, o)
    return Image.alpha_composite(im, masked(o, im))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    src = base()
    brown = src  # 원본이 갈색(황금똥)
    colors = {
        'brown': brown,
        'yellow': recolor(src, (232, 168, 64)),
        'green': recolor(src, (118, 140, 56)),
        'black': recolor(src, (54, 44, 40), gloss=1.9),
        'gray': recolor(src, (190, 182, 170)),
        'red': deco(brown, 'red'),
        'mucus': deco(brown, 'mucus'),
        'specks': deco(brown, 'specks'),
    }
    for k, im in colors.items():
        place((im, W / 2, H - 14)).save(OUT / f'color-{k}.webp', quality=90, method=6)

    small = squash(brown, .42, .42)
    firm = {
        1: place((squash(small, 1, .92), 78, H - 22), (small, 122, H - 16), (squash(small, .9, .85), 164, H - 24), (squash(small, .8, .8), 104, H - 50)),
        2: place((brown, W / 2, H - 14)),
        3: place((squash(brown, 1.18, .74), W / 2, H - 14)),
        4: place((squash(brown, 1.34, .52), W / 2, H - 14)),
        5: place((squash(brown, .82, .4), 86, H - 14), (squash(brown, .7, .34), 158, H - 16)),
        6: place((squash(brown, 1.5, .36), W / 2, H - 14)),
        7: puddle(src),
    }
    for s, im in firm.items():
        im.save(OUT / f'firm-{s}.webp', quality=90, method=6)
    print('poop images →', OUT)


if __name__ == '__main__':
    build()
