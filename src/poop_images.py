"""똥 상태 체크 그림 — ChatGPT로 만든 응가 시트 두 장(src/art/poop-new/*-sheet.png)을 한 개씩 잘라낸다.

python3 src/poop_images.py   # assets/img/poop/*.webp (+ src/art/poop-new/<이름>.png)
흰 바탕에서 응가만 떼어 내고, 땅 그림자는 새로 그려 모든 그림이 같은 바닥에 앉게 한다.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'src/art/poop-new'
OUT = ROOT / 'assets/img/poop'
W, H, PAD = 480, 360, 26  # 2배 해상도 캔버스 — 화면에선 120×90 안쪽으로 쓴다
COLORS = ['brown', 'yellow', 'green', 'red', 'black', 'gray', 'mucus', 'specks']  # 시트 4×2 순서


def cut(sheet, boxes):
    im = np.array(Image.open(ART / sheet).convert('RGB'))
    for x0, y0, x1, y1 in boxes:
        a = im[y0:y1, x0:x1]
        lo, hi = a.min(2).astype(int), a.max(2).astype(int)
        m = nd.binary_opening(((255 - lo) > 70) | ((hi - lo) > 38))
        lab, k = nd.label(m)
        sizes = nd.sum(m, lab, range(1, k + 1))
        keep = nd.binary_fill_holes(np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > max(60, sizes.max() * 0.004)]))
        keep = nd.binary_erosion(keep, iterations=2)  # 가장자리에 섞인 흰 바탕을 덜어 낸다
        alpha = np.array(Image.fromarray((keep * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)
        rgb = a.astype(float)
        # 바닥의 흰 바탕 그림자(밝은 띠)는 아래 20% 안에서 지운다 — 그림자는 place()가 새로 그린다
        ys = np.where(keep.any(1))[0]
        band = np.zeros_like(keep)
        band[int(ys.max() - (ys.max() - ys.min()) * .2):] = True
        lum = rgb.mean(2)
        pale = band & keep & (lum > 135) & (((hi - lo) < 60) | (lum > 165))
        lab_p, k_p = nd.label(pale)  # 바깥 테두리에 닿은 덩어리만 — 안쪽의 흰 알갱이·밝은 물은 그대로
        edge = nd.binary_dilation(~keep, iterations=2)
        pale = np.isin(lab_p, [i for i in range(1, k_p + 1) if (edge & (lab_p == i)).any()])
        alpha[nd.binary_dilation(pale, iterations=1) & band] = 0
        alpha = np.array(Image.fromarray(alpha.astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))).astype(float)
        out = np.dstack([rgb, alpha]).clip(0, 255).astype('uint8')
        rgba = Image.fromarray(out)
        yield rgba.crop(rgba.getbbox())


def place(items, names):
    items = list(items)
    s = min((W - 2 * PAD) / max(i.width for i in items), (H - 2 * PAD - 20) / max(i.height for i in items))
    for name, i in zip(names, items):
        i = i.resize((round(i.width * s), round(i.height * s)), Image.LANCZOS)
        base = H - PAD - 6
        shadow = Image.new('L', (W, H), 0)
        ImageDraw.Draw(shadow).ellipse((W / 2 - i.width * .46, base - 10, W / 2 + i.width * .46, base + 10), fill=70)
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        c.paste(Image.new('RGBA', (W, H), (70, 45, 20, 255)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(9)))
        c.alpha_composite(i, ((W - i.width) // 2, base - i.height + 4))
        c.save(ART / f'{name}.png')
        c.save(OUT / f'{name}.webp', quality=88, method=6)


if __name__ == '__main__':
    xs = [0, 300, 590, 890, 1200, 1510, 1830, 2172]
    place(cut('firm-sheet.png', [(xs[j], 180, xs[j + 1], 540) for j in range(7)]), [f'firm-{j + 1}' for j in range(7)])
    cols, rows = [0, 384, 768, 1152, 1536], [40, 520, 1000]
    place(cut('color-sheet.png', [(cols[c] + 10, rows[r], cols[c + 1] - 10, rows[r + 1]) for r in range(2) for c in range(4)]),
          [f'color-{c}' for c in COLORS])
