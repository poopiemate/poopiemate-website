"""사이트 에셋 준비 — 원본(데스크톱·앱 저장소)에서 가져와 웹용으로 줄인다. 한 번 돌리면 assets/ 아래가 채워진다.

python3 src/prepare_assets.py
"""
import os, re, shutil, subprocess, sys, unicodedata
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / 'assets'
HOME = Path.home()
APP = HOME / 'project/poopiemate/assets'
DESK = HOME / 'Desktop/응가메이트'
PHOTOS = HOME / 'Desktop/메로나'


def out(p):
    p = A / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def webp(src, dst, width=None, height=None, q=86, crop=None, fn=None):
    im = ImageOps.exif_transpose(Image.open(src))
    im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    if crop:
        w, h = im.size
        l, t, r, b = crop
        im = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
    if fn:
        im = fn(im)
    if width or height:
        im.thumbnail((width or 10 ** 5, height or 10 ** 5), Image.LANCZOS)
    im.save(out(dst), 'WEBP', quality=q, method=6)
    return im.size


# ── 제목 글꼴 — 앱과 같은 나눔스퀘어 네오 Bold, 메인 제목만 ExtraBold (본문은 Pretendard). woff2로만 바꿈
def fonts():
    from fontTools.ttLib import TTFont
    f = TTFont(APP / 'fonts/NanumSquareNeo-cBd.ttf')
    f.flavor = 'woff2'
    f.save(out('fonts/NanumSquareNeo-cBd.woff2'))
    # 홈 첫 화면 큰 제목만 ExtraBold — 앱에는 없어 네이버 공식 배포본을 받는다
    eb = ROOT / '.cache/NanumSquareNeoTTF-dEb.ttf'
    if not eb.exists():
        subprocess.run(['curl', '-sfL', 'https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareNeo/NanumSquareNeoTTF-dEb.ttf', '-o', str(eb)], check=True)
    f = TTFont(eb)
    f.flavor = 'woff2'
    f.save(out('fonts/NanumSquareNeo-dEb.woff2'))


# ── 워드마크 — 흰색 원본 SVG에서 초록 버전을 만들고 여백을 잘라 viewBox를 맞춘다
def brand():
    src = {'ko': ROOT / 'assets/brand/poopiemate-text.svg', 'en': ROOT / 'assets/brand/poopiemate-text-en.svg'}
    # 글자 실제 범위 (675×150 viewBox 기준) — 렌더해서 잰 값
    vb = {'ko': '0 4 516 140', 'en': '0 4 674 140'}
    for lang, p in src.items():
        s = p.read_text()
        s = re.sub(r'viewBox="[^"]*"', f'viewBox="{vb[lang]}"', s, count=1)
        s = re.sub(r'\s(width|height)="[^"]*"', '', s, count=2)
        out(f'brand/wordmark-{lang}-white.svg').write_text(s)
        out(f'brand/wordmark-{lang}-green.svg').write_text(s.replace('#ffffff', '#18955A'))


def clean_edge(im):
    """반투명 가장자리 픽셀에 남은 옛 배경색(어두운 회색)을 바로 안쪽 몸 색으로 바꿔 — 어떤 바탕에 올려도 회색 테두리가 안 보이게."""
    import numpy as np
    from scipy import ndimage
    a = np.array(im.convert('RGBA')).astype(np.float64)
    opaque = a[..., 3] >= 245
    idx = ndimage.distance_transform_edt(~opaque, return_distances=False, return_indices=True)
    for ch in range(3):
        a[..., ch] = np.where(opaque, a[..., ch], a[..., ch][idx[0], idx[1]])
    a[..., 3] = np.where(a[..., 3] < 24, 0, a[..., 3])
    return Image.fromarray(a.astype(np.uint8))


# ── 응댕이 — 앱 원본 (손 흔드는 3장, 응가하는 3장, 정지 포즈)
def mascot():
    # 손 흔드는 응댕이 — 소개 영상(v10)에서 가장자리를 다듬은 판: 팔·꼬리 테두리 정리 + 팔 들 때 틈을 메우는 어깨
    rig = DESK / '서비스 소개 영상/v10_최종/_source/assets'
    for n in ('wave-body', 'wave-arm', 'wave-tail', 'wave-shoulder'):
        webp(rig / f'{n}.png', f'img/mascot/{n}.webp', q=92, fn=clean_edge)
    lay = DESK / '홈페이지_v3_레이어/응댕이/포즈'
    for n, en in (('귀쫑긋', 'ears'), ('긁기', 'scratch'), ('앉아있기', 'sit'), ('애교', 'beg'), ('안녕', 'hello'), ('응가중', 'pooping'), ('얼굴', 'face')):
        webp(lay / f'{n}.png', f'img/mascot/{en}.webp', width=480, q=88)


# ── Fluent 3D 이모지 (MIT) — 앱 assets/emoji + 모자란 것은 fluentui-emoji 저장소에서
FLUENT = {'alarm_clock': 'Alarm clock', 'mobile_phone': 'Mobile phone'}


def emoji():
    for n in ('house', 'love_letter', 'growing_heart', 'pile_of_poo', 'sun_behind_small_cloud', 'paw_prints', 'sparkles', 'bone',
              'green_heart', 'megaphone', 'speech_balloon'):
        webp(APP / f'emoji/{n}.png', f'img/emoji/{n}.webp', width=160, q=90)
    tmp = ROOT / '.cache/emoji'
    tmp.mkdir(parents=True, exist_ok=True)
    for n, folder in FLUENT.items():
        f = tmp / f'{n}.png'
        if not f.exists():
            url = f'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/{folder.replace(" ", "%20")}/3D/{n}_3d.png'
            subprocess.run(['curl', '-sfL', url, '-o', str(f)], check=True)
        webp(f, f'img/emoji/{n}.webp', width=160, q=90)
    shutil.copy(APP / 'emoji/LICENSE-fluentui-emoji.txt', out('img/emoji/LICENSE.txt'))


# ── 사진 — 얼굴이 나오지 않게 자르고, 색을 살짝 맞춰서 (글 사이 가득 찬 폭)
def photo_tone(im):
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Color(im).enhance(1.06)
    return ImageEnhance.Brightness(im).enhance(1.02)


PHOTO = [  # 파일, 출력 이름, 이름표 전화번호 가릴 곳(원본 px) — 비율은 원본 그대로 (강아지 얼굴이 잘리지 않게)
    ('메로나임보전.jpeg', 'kennel', []),
    ('로나아가시절.jpeg', 'home-first', [(562, 850, 650, 905)]),
    ('분홍이시절.jpeg', 'kennel-house', []),
    ('IMG_6047.jpeg', 'lawn-walk', [(172, 746, 226, 790)]),
    ('IMG_5506.JPG', 'family-lawn', [(1925, 700, 2125, 870)]),
]


PAIRS = {'pair-kennel-home': ('kennel', 'home-first'), 'pair-walk-family': ('lawn-walk', 'family-lawn')}


def hide(boxes):
    """이름표의 전화번호만 뭉개기 — 픽셀을 크게 뭉갠 뒤 흐리게."""
    from PIL import ImageFilter

    def fn(im):
        for box in boxes:
            part = im.crop(box)
            w, h = part.size
            part = part.resize((max(1, w // 10), max(1, h // 10)), Image.BILINEAR).resize((w, h), Image.NEAREST).filter(ImageFilter.GaussianBlur(4))
            im.paste(part, box)
        return photo_tone(im)
    return fn


def photos():
    for src, name, boxes in PHOTO:
        for size in (1600, 900):
            dim = webp(PHOTOS / src, f'img/photo/{name}-{size}.webp', width=size, height=size, q=82, fn=hide(boxes))
        print('photo', name, dim)
    # 글 사이 가득 찬 폭 — 세로 사진 두 장을 같은 높이로 붙여 한 장으로
    for name, parts in PAIRS.items():
        ims = [Image.open(out(f'img/photo/{p}-1600.webp')).convert('RGB') for p in parts]
        h = 1100
        ims = [im.resize((round(im.width * h / im.height), h), Image.LANCZOS) for im in ims]
        gap = 16
        canvas = Image.new('RGB', (sum(im.width for im in ims) + gap * (len(ims) - 1), h), (255, 255, 255))
        x = 0
        for im in ims:
            canvas.paste(im, (x, 0))
            x += im.width + gap
        for w in (1600, 900):
            c = canvas.copy()
            c.thumbnail((w, 10 ** 5), Image.LANCZOS)
            c.save(out(f'img/photo/{name}-{w}.webp'), 'WEBP', quality=82, method=6)
        print('pair', name, canvas.size)


# ── 영상 — 인스타 릴스(기능별, 한/영) 720p로 다시 인코딩 + 첫 장면 포스터
REELS = {'record': '01', 'family': '02', 'alerts': '03', 'walk': '04'}  # 이렇게 써요 2~5단계
REEL_SRC = {'ko': DESK / '응가메이트_인스타그램/한국어/9칸_B_기능별/릴스', 'en': DESK / '응가메이트_인스타그램/영어/Reels'}


def reels():
    for lang, d in REEL_SRC.items():
        files = {unicodedata.normalize('NFC', f.name)[:2]: f for f in d.glob('*.mp4')}
        for key, num in REELS.items():
            src = files[num]
            dst = out(f'video/{key}-{lang}.mp4')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', 'scale=720:-2', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '27',
                            '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', str(dst)], check=True)
            poster = ROOT / '.cache' / f'{key}-{lang}.png'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2.5', '-i', str(src), '-frames:v', '1', str(poster)], check=True)
            webp(poster, f'video/{key}-{lang}.webp', width=540, q=80)
            print('reel', key, lang, dst.stat().st_size // 1024, 'KB')


# ── 「가족을 초대해요」 릴스 — 다른 기능 릴스와 같은 틀로 새로 그린 것 (src/render/render.js가 프레임을 찍는다)
def invite():
    for lang in ('ko', 'en'):
        frames = ROOT / f'.cache/invite-{lang}'
        dst = out(f'video/invite-{lang}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', str(frames / '%03d.png'), '-vf', 'scale=720:-2', '-c:v', 'libx264', '-profile:v', 'high',
                        '-crf', '27', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dst)], check=True)
        webp(frames / '075.png', f'video/invite-{lang}.webp', width=540, q=80)
        print('invite', lang, dst.stat().st_size // 1024, 'KB')


# ── 앱 공지 상세 무대 그림 (src/render/notice_hero.html → .cache/notice-hero.png)
def notice_hero():
    webp(ROOT / '.cache/notice-hero.png', 'img/notice-hero.webp', q=88)


# ── 서비스 소개 롱폼 (1분) — 홈 첫 화면 가득 소리 없이 저절로 재생 (유튜브 버튼 없이 바로)
INTRO = {'ko': '응가메이트_서비스소개_롱폼_KO.mp4', 'en': 'PoopieMate_Intro_Landscape_EN.mp4'}
INTRO_V = {'ko': '응가메이트_서비스소개_숏폼_KO.mp4', 'en': 'PoopieMate_Intro_Vertical_EN.mp4'}


def intro():
    d = DESK / '서비스 소개 영상/v10_최종/롱폼'
    files = {unicodedata.normalize('NFC', f.name): f for f in d.glob('*.mp4')}
    for lang, name in INTRO.items():
        src = files[name]
        dst = out(f'video/intro-{lang}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', 'scale=1600:-2', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '28',
                        '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(dst)], check=True)
        poster = ROOT / '.cache' / f'intro-{lang}.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.6', '-i', str(src), '-frames:v', '1', str(poster)], check=True)
        webp(poster, f'video/intro-{lang}.webp', width=1600, q=80)
        print('intro', lang, dst.stat().st_size // 1024, 'KB')
    # 모바일(세로 화면)용 — 같은 영상의 숏폼 세로판
    d = DESK / '서비스 소개 영상/v10_최종/숏폼'
    files = {unicodedata.normalize('NFC', f.name): f for f in d.glob('*.mp4')}
    for lang, name in INTRO_V.items():
        src = files[name]
        dst = out(f'video/intro-{lang}-v.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', 'scale=720:-2', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '28',
                        '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(dst)], check=True)
        poster = ROOT / '.cache' / f'intro-{lang}-v.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.6', '-i', str(src), '-frames:v', '1', str(poster)], check=True)
        webp(poster, f'video/intro-{lang}-v.webp', width=720, q=80)
        print('intro vertical', lang, dst.stat().st_size // 1024, 'KB')


# ── 유튜브 썸네일 (직접 만든 것) — 클릭 전엔 이미지만, 누르면 영상
def thumbs():
    d = DESK / '서비스 소개 영상/v10_최종/썸네일'
    for f in d.glob('*.jpg'):
        name = unicodedata.normalize('NFC', f.stem)
        if name.startswith('롱폼_service'):  # 사이트에 올린 유튜브 영상은 서비스 소개 롱폼뿐
            webp(f, f'img/yt/{name.replace("롱폼_", "long-")}.webp', width=1280, q=82)


# ── 파비콘 — 바탕화면 favicon 세트 (지금 앱 아이콘)
def favicon():
    d = DESK / 'favicon'
    for f in d.iterdir():
        if f.name.startswith('.'):
            continue
        if f.name == 'site.webmanifest':
            (ROOT / f.name).write_text(f.read_text().replace('/assets/icon-', '/assets/icons/icon-'))
        else:
            shutil.copy(f, ROOT / f.name if f.name == 'favicon.ico' else out(f'icons/{f.name}'))


STEPS = {'fonts': fonts, 'invite': invite, 'notice_hero': notice_hero, 'intro': intro, 'brand': brand, 'mascot': mascot, 'emoji': emoji, 'photos': photos, 'reels': reels, 'thumbs': thumbs, 'favicon': favicon}
if __name__ == '__main__':
    for k in (sys.argv[1:] or STEPS):
        print('==', k)
        STEPS[k]()
