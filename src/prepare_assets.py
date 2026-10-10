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


def web_video(src, dst, width, crf=27, audio=False, t0=0, dur=None, frames=False):
    """웹 영상 — H.264 8비트, BT.709·제한 범위(tv)로 맞춰 꼬리표를 단다. 사파리는 꼬리표 없는 영상이나 카톡·폰의
    전체 범위(yuvj) 영상을 페이지 흰색과 다르게 그려서 영상 상자가 회색으로 비친다. 아이폰 HDR(HLG)은 SDR로 톤매핑."""
    info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'csv=p=0', str(src)],
                          capture_output=True, text=True).stdout if not frames else ''
    hdr = 'arib-std-b67' in info or 'smpte2084' in info
    tone = 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,' if hdr else ''
    vf = f'{tone}scale={width}:-2:out_range=tv:out_color_matrix=bt709,fps=30,format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709'
    cut = (['-ss', str(t0)] if t0 else []) + (['-t', str(dur)] if dur else [])
    inp = ['-framerate', '30', '-i', str(src)] if frames else [*cut, '-i', str(src)]
    a = ['-map', '0:a:0?', '-c:a', 'aac', '-b:a', '128k'] if audio else ['-an']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-vf', vf, '-map', '0:v:0', *a, '-c:v', 'libx264', '-profile:v', 'high', '-crf', str(crf), '-preset', 'slow',
                    '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart', str(dst)], check=True)
    return dst


def web_poster(video, dst, width, at=0.4):
    """포스터는 다시 인코딩한 웹 영상에서 뽑는다 — 영상과 포스터 색이 똑같게."""
    png = ROOT / '.cache' / (Path(dst).stem + '.png')
    png.parent.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(at), '-i', str(video), '-frames:v', '1', str(png)], check=True)
    webp(png, dst, width=width, q=80)


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


def arm_root(arm, body, reach=0.05):
    """팔 뿌리를 몸 안쪽으로 늘려 그린다 — 팔은 몸 뒤에 깔리므로(site.css) 늘린 부분은 가만히 있을 땐 몸에 가려지고,
    팔을 흔들어도 어깨에 잘린 단면이나 틈이 보이지 않는다."""
    import numpy as np
    from scipy import ndimage
    a = np.array(arm.convert('RGBA')).astype(np.float64)
    b = np.array(body.convert('RGBA').resize(arm.size))[..., 3] > 200
    solid = a[..., 3] >= 245
    dist, idx = ndimage.distance_transform_edt(~solid, return_indices=True)
    below_face = np.arange(arm.size[1])[:, None] >= 0.52 * arm.size[1]  # 얼굴 쪽으로는 늘리지 않는다 (흔들 때 얼굴 옆으로 삐져나오지 않게)
    grow = (~solid) & b & below_face & (dist <= reach * arm.size[0])
    for ch in range(3):
        a[..., ch] = np.where(grow, a[..., ch][idx[0], idx[1]], a[..., ch])
    a[..., 3] = np.where(grow, 255, a[..., 3])
    return Image.fromarray(a.astype(np.uint8))


# ── 응댕이 — 앱 원본 (손 흔드는 3장, 응가하는 3장, 정지 포즈)
def mascot():
    # 손 흔드는 응댕이 — 소개 영상(v10)에서 가장자리를 다듬은 판: 팔·꼬리 테두리 정리 + 팔 들 때 틈을 메우는 어깨
    rig = DESK / '서비스 소개 영상/v10_최종/_source/assets'
    for n in ('wave-body', 'wave-tail', 'wave-shoulder'):
        webp(rig / f'{n}.png', f'img/mascot/{n}.webp', q=92, fn=clean_edge)
    body = clean_edge(ImageOps.exif_transpose(Image.open(rig / 'wave-body.png')))
    webp(rig / 'wave-arm.png', 'img/mascot/wave-arm.webp', q=92, fn=lambda im: arm_root(clean_edge(im), body))
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


PAIRS = {'pair-rescue': ('kennel', 'kennel-house'), 'pair-wedding': ('wedding-jump', 'wedding-kiss'), 'pair-family': ('family-2025-a', 'family-2025-b')}


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


def erase(box):
    """이름표 글자를 판 색으로 덮기 — 글자(밝은 픽셀)를 뺀 판의 중간 색으로 채우고 가장자리만 살짝 흐리게."""
    from PIL import ImageFilter, ImageDraw
    import numpy as np

    def fn(im):
        part = np.array(im.crop(box).convert('RGB'))
        plate = part[part.sum(axis=2) < 560]
        fill = tuple(int(v) for v in np.median(plate, axis=0))
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(box, radius=24, fill=255)
        im.paste(Image.new('RGB', im.size, fill), (0, 0), mask.filter(ImageFilter.GaussianBlur(6)))
        return im
    return fn


# ── 「응가메이트를 만든 이유」 사진·영상 — 사진 앱에서 꺼내 바탕화면 메로나/웹스토리에 모아 둔 원본
STORY_SRC = PHOTOS / '웹스토리'
STORY_PHOTO = [  # 파일, 출력 이름, 가릴 이름표(원본 px) — 뭉개기 / 판 색으로 덮기
    ('01-lap-sleep.jpeg', 'first-lap-sleep', [], []), ('02-lap-eyes.jpeg', 'first-lap-eyes', [], []),
    ('03-paws.jpeg', 'first-paws', [(1240, 2400, 1400, 2580)], []), ('06-pink-sleep.jpeg', 'first-pink-sleep', [], []),
    ('08-harness.jpeg', 'first-harness', [], []), ('10-selfie.jpeg', 'first-selfie', [], []),
    ('11-park-friends.jpeg', 'park-friends', [], [(2725, 2450, 3085, 2610)]), ('12-park-smile.jpeg', 'park-smile', [], []),
    ('13-park-run.jpeg', 'park-run', [], []),
    ('wedding-jump.jpg', 'wedding-jump', [], []), ('wedding-kiss.jpg', 'wedding-kiss', [], []),
    ('family-2025-a.jpeg', 'family-2025-a', [], []), ('family-2025-b.jpeg', 'family-2025-b', [], []),
]
STORY_CLIP = [  # 원본, 출력 이름, 시작(초), 길이(초), 소리 — 소리는 원본 그대로 (바스락 잡음뿐인 영상만 소리 없이)
    (STORY_SRC / 'first-meet.MOV', 'first-meet', 0, None, True), (STORY_SRC / 'first-lick.mp4', 'first-lick', 0, None, False),
    (STORY_SRC / 'snow-potty.MOV', 'potty-snow', 2.0, 14.0, True),
    (DESK / '응가메이트_틱톡/소스추가/DJI_20260727073257_0095_D.MP4', 'potty-summer', 0, None, True),
]


def story():
    for src, name, boxes, plates in STORY_PHOTO:
        def fn(im, boxes=boxes, plates=plates):
            for p in plates:
                im = erase(p)(im)
            return hide(boxes)(im)
        for size in (1600, 900):
            dim = webp(STORY_SRC / src, f'img/photo/{name}-{size}.webp', width=size, height=size, q=82, fn=fn)
        print('photo', name, dim)
    for src, name, t0, dur, sound in STORY_CLIP:
        dst = web_video(src, out(f'video/story-{name}.mp4'), 720, crf=26, audio=sound, t0=t0, dur=dur)
        web_poster(dst, f'video/story-{name}.webp', 720)
        print('clip', name, dst.stat().st_size // 1024, 'KB')


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
            dst = web_video(src, out(f'video/{key}-{lang}.mp4'), 720)
            web_poster(dst, f'video/{key}-{lang}.webp', 540, at=2.5)
            print('reel', key, lang, dst.stat().st_size // 1024, 'KB')


# ── 「가족을 초대해요」 릴스 — 다른 기능 릴스와 같은 틀로 새로 그린 것 (src/render/render.js가 프레임을 찍는다)
def invite():
    for lang in ('ko', 'en'):
        frames = ROOT / f'.cache/invite-{lang}'
        dst = web_video(frames / '%03d.png', out(f'video/invite-{lang}.mp4'), 720, frames=True)
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
        dst = web_video(src, out(f'video/intro-{lang}.mp4'), 1600, crf=28, audio=True)
        web_poster(dst, f'video/intro-{lang}.webp', 1600, at=0.6)
        print('intro', lang, dst.stat().st_size // 1024, 'KB')
    # 모바일(세로 화면)용 — 같은 영상의 숏폼 세로판
    d = DESK / '서비스 소개 영상/v10_최종/숏폼'
    files = {unicodedata.normalize('NFC', f.name): f for f in d.glob('*.mp4')}
    for lang, name in INTRO_V.items():
        src = files[name]
        dst = web_video(src, out(f'video/intro-{lang}-v.mp4'), 720, crf=28, audio=True)
        web_poster(dst, f'video/intro-{lang}-v.webp', 720, at=0.6)
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


STEPS = {'fonts': fonts, 'invite': invite, 'notice_hero': notice_hero, 'intro': intro, 'brand': brand, 'mascot': mascot, 'emoji': emoji, 'story': story, 'photos': photos, 'reels': reels, 'thumbs': thumbs, 'favicon': favicon}
if __name__ == '__main__':
    for k in (sys.argv[1:] or STEPS):
        print('==', k)
        STEPS[k]()
