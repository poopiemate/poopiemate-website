"""공유 미리보기(OG) 이미지 1200×630 — 캔버스 「OG A」: 초록 바탕 가운데 은은한 빛, 위에 응댕이 얼굴, 아래 흰 워드마크. 글은 넣지 않는다.
모든 페이지가 언어별로 한 장을 같이 쓴다 (assets/og/poopiemate-{ko,en}.jpg). 크롬 headless로 그려 JPG로 저장한다.

python3 src/og.py
"""
import subprocess
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


if __name__ == '__main__':
    main()
