"""공유 미리보기(OG) 이미지 1200×630 — 인스타 GridA 톤: 초록 바탕, 위에 큰 흰 워드마크, 굵은 제목 + 노랑 알약, 오른쪽에 큰 응댕이.
제목 글꼴은 영상·SNS와 같은 Pretendard(OFL). 크롬 headless로 그려 JPG로 저장한다.

python3 src/og.py
"""
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / '.cache/og'
FONTS = Path.home() / 'Desktop/응가메이트/서비스 소개 영상/v10_최종/_source/assets'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# 이름: (제목 줄, 알약, 아래 한 줄, 그림)
OG = {
    'home-ko': ('“응댕이 똥 쌌어?”', '이제 안 물어봐도 돼요', '가족과 함께 챙기는 댕댕이 응가·산책', 'dog:hello'),
    'home-en': ('“Did Poochie poop?”', 'No need to ask anymore', 'Potty & walks, shared with family', 'dog:hello'),
    'how-ko': ('가족이 같이 쓰는 법', '초대 → 기록 → 알림', '세 단계면 가족 모두가 바로 알아요', 'dog:sit'),
    'how-en': ('How families use it', 'Invite → Log → Alert', 'Three steps and everyone knows', 'dog:sit'),
    'story-ko': ('응가메이트 이야기', '우리 집 강아지에서 시작했어요', '앱을 만든 가족의 이야기를 모아요', 'photo:family-lawn'),
    'story-en': ('Our story', 'It started with our dog', 'Notes from the family behind the app', 'photo:family-lawn'),
    'why-ko': ('응가메이트를 만든 이유', '“똥 쌌어?” 그 전화에서', '버튼 하나로 가족 모두가 알게 되기까지', 'photo:kennel'),
    'why-en': ('Why we built PoopieMate', 'It started with one call', 'From “Did she poop?” to a single button', 'photo:kennel'),
    'notice-ko': ('공지사항', '업데이트 · 이벤트 소식', '응가메이트 새 소식을 알려드려요', 'dog:ears'),
    'notice-en': ('Notices', 'Updates & events', 'What’s new at PoopieMate', 'dog:ears'),
    'interview-ko': ('유저 인터뷰에 초대해요', '참여하면 라떼 기프티콘을 드려요', '보호자님 이야기를 들려주세요', 'dog:ears'),
    'interview-en': ('Join a user interview', 'Tell us how you use it', 'Interviews are in Korean for now', 'dog:ears'),
    'download-ko': ('응가메이트 무료 다운로드', '가족 모두에게 바로 알림', 'App Store · Google Play', 'dog:pooping'),
}
# 응댕이 양옆 3D 아이콘 — X 헤더에서 고른 배치 (왼쪽: 분홍 하트·응가·발자국 / 오른쪽: 반짝이·초록 하트·뼈다귀)
ICONS = [('growing_heart', 640, 120, 62, -12), ('pile_of_poo', 610, 300, 66, -8), ('paw_prints', 650, 470, 56, 10),
         ('sparkles', 1110, 110, 58, 8), ('green_heart', 1124, 290, 60, 12), ('bone', 1090, 470, 66, -16)]


def html(name, title, pill, sub, art):
    lang = name.rsplit('-', 1)[1]
    hs = 62 if len(title) <= (11 if lang == 'ko' else 15) else (56 if lang == 'ko' else 50)
    a = ROOT / 'assets'
    if art.startswith('dog:'):
        icons = ''.join(f'<img src="file://{a}/img/emoji/{i}.webp" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)">' for i, x, y, w, r in ICONS)
        visual = f'{icons}<img src="file://{a}/img/mascot/{art[4:]}.webp" style="position:absolute;left:{870 - 200}px;top:110px;width:400px;height:430px;object-fit:contain;object-position:50% 100%">'
    else:
        visual = (f'<div style="position:absolute;left:700px;top:96px;width:400px;padding:16px 16px 0;background:#fff;border-radius:14px;transform:rotate(3deg);box-shadow:0 24px 48px rgba(0,40,20,.28)">'
                  f'<img src="file://{a}/img/photo/{art[6:]}-800.webp" style="display:block;width:368px;height:300px;object-fit:cover;border-radius:8px">'
                  f'<div style="height:70px"></div></div>'
                  f'<img src="file://{a}/img/mascot/beg.webp" style="position:absolute;left:600px;top:360px;width:190px">')
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url("file://{FONTS}/Pretendard-ExtraBold.otf");font-weight:800}}
@font-face{{font-family:P;src:url("file://{FONTS}/Pretendard-SemiBold.otf");font-weight:600}}
html,body{{margin:0}}
.c{{position:relative;width:1200px;height:630px;overflow:hidden;background:#18955A;font-family:P,sans-serif;color:#fff;word-break:keep-all}}
.glow{{position:absolute;left:870px;top:330px;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.16),rgba(255,255,255,0) 62%)}}
.logo{{position:absolute;left:80px;top:70px;height:{78 if lang == 'ko' else 64}px}}
.t{{position:absolute;left:80px;top:{214 if lang == 'ko' else 206}px;width:560px}}
.h{{font-size:{hs}px;line-height:1.18;font-weight:800;letter-spacing:-.02em}}
.pill{{display:inline-block;margin-top:14px;padding:6px 22px 10px;border-radius:999px;background:#FFE27A;color:#191F28;font-size:{40 if len(pill) < 16 else 34}px;font-weight:800;letter-spacing:-.02em}}
.s{{margin-top:26px;font-size:26px;font-weight:600;opacity:.88}}
</style></head><body><div class="c"><span class="glow"></span>
<img class="logo" src="file://{a}/brand/wordmark-{lang}-white.svg">
<div class="t"><div class="h">{title}</div><div class="pill">{pill}</div><div class="s">{sub}</div></div>
{visual}</div></body></html>'''


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    out = ROOT / 'assets/og'
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in OG.items():
        h = TMP / f'{name}.html'
        h.write_text(html(name, *spec), encoding='utf-8')
        png = TMP / f'{name}.png'
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files', '--window-size=1200,630',
                        '--virtual-time-budget=2000', f'--screenshot={png}', f'file://{h}'], check=True, capture_output=True)
        Image.open(png).convert('RGB').save(out / f'{name}.jpg', quality=88, optimize=True, progressive=True)
        print(name)
    # 예전 주소로 공유된 링크도 새 이미지를 보게
    for lang in ('ko', 'en'):
        Image.open(out / f'home-{lang}.jpg').save(ROOT / f'assets/og-image-{lang}.jpg', quality=88, optimize=True, progressive=True)


if __name__ == '__main__':
    main()
