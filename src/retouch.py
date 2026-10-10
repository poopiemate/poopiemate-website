"""가족사진 보정 — 얼굴을 살짝 바꾸고(눈 키우기·턱선 갸름·코 좁히기), 엄마 얼굴은 환하게, 팔뚝은 얇게.
얼굴 위치는 원본 옆 family-landmarks.json (mediapipe FaceLandmarker로 뽑은 478점, 원본 px)."""
import json
import numpy as np
import cv2
from PIL import Image

# mediapipe 얼굴 점 번호
IRIS = (468, 473)
JAW_L = (172, 136, 150, 149)
JAW_R = (397, 365, 379, 378)
CHIN = 152
NOSE = 4
MOUTH = (61, 291)
CHEEKS = (234, 454)
FACE_OVAL = (10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109)

# 사진마다 — 턱이 강아지에 가린 얼굴은 턱선을 건드리지 않는다. 팔뚝: 바깥 윤곽 점(원본 px)과 미는 방향
EDIT = {
    'family-2025-a': {'jaw': {'man': 'LR', 'woman': 'LR'}, 'arms': [((3120, 2450), (-55, 0)), ((3150, 2700), (-60, 0)), ((3160, 2950), (-55, 0)), ((3150, 3200), (-40, 0))], 'arm_r': 230},
    # b: 엄마 오른쪽 턱·아빠 턱은 강아지 귀·몸에 닿아 있어 밀면 강아지가 휜다. 팔뚝 점도 강아지 앞발(x 1650~1880)은 피한다
    'family-2025-b': {'jaw': {'woman': 'L'}, 'arms': [((1100, 3220), (0, 40)), ((1400, 3290), (0, 45)), ((2000, 3400), (0, 50)), ((2250, 3430), (0, 50)), ((2450, 3480), (0, 35))], 'arm_r': 200},
}


def _grid(shape):
    h, w = shape[:2]
    return np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))


def _falloff(gx, gy, c, r):
    d2 = (gx - c[0]) ** 2 + (gy - c[1]) ** 2
    return np.clip(1 - d2 / (r * r), 0, 1) ** 2


def push(a, c, v, r):
    """앞으로 밀기 — c 둘레 반지름 r 안을 v만큼 밀어낸다 (포토샵 뒤틀기 도구처럼)."""
    gx, gy = _grid(a.shape)
    w = _falloff(gx, gy, c, r)
    return cv2.remap(a, gx - w * v[0], gy - w * v[1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def scale(a, c, r, s):
    """부풀리기(s>0) · 오므리기(s<0)."""
    gx, gy = _grid(a.shape)
    f = 1 - s * _falloff(gx, gy, c, r)
    return cv2.remap(a, c[0] + (gx - c[0]) * f, c[1] + (gy - c[1]) * f, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def retouch(name, src, landmarks_json, work=1800):
    im = src.resize((work, round(src.height * work / src.width)), Image.LANCZOS)
    k = work / src.width
    a = np.array(im.convert('RGB'))
    faces = {who: np.array(pts) * k for who, pts in json.load(open(landmarks_json))[name].items()}
    ed = EDIT[name]

    # 엄마 얼굴 — 밝기만 살짝 올린다 (목까지 부드럽게 이어지게 아래로 길게 번지는 마스크)
    if 'woman' in faces:
        p = faces['woman']
        oval = p[list(FACE_OVAL)].astype(np.int32)
        fh = oval[:, 1].max() - oval[:, 1].min()
        mask = np.zeros(a.shape[:2], np.float32)
        cv2.fillConvexPoly(mask, cv2.convexHull(oval), 1)
        neck = oval.copy(); neck[:, 1] = np.where(neck[:, 1] > p[NOSE][1], neck[:, 1] + fh * 0.35, neck[:, 1])
        cv2.fillConvexPoly(mask, cv2.convexHull(neck.astype(np.int32)), 1)
        mask = cv2.GaussianBlur(mask, (0, 0), fh * 0.12)
        lab = cv2.cvtColor(a, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[..., 0] += mask * 11
        lab[..., 1] -= mask * 2  # 붉은 기를 조금 덜어 맑게
        a = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)

    # 얼굴 모양 — 눈은 조금 크게, 코는 조금 좁게, 턱선은 안쪽으로
    for who, p in faces.items():
        fw = np.linalg.norm(p[CHEEKS[0]] - p[CHEEKS[1]])
        for i in IRIS:
            a = scale(a, p[i], fw * 0.17, 0.3)
        a = scale(a, p[NOSE], fw * 0.14, -0.22)
        # 입꼬리를 살짝 올리고 인중을 짧게
        a = push(a, p[MOUTH[0]], (0, -fw * 0.02), fw * 0.1)
        a = push(a, p[MOUTH[1]], (0, -fw * 0.02), fw * 0.1)
        sides = ed['jaw'].get(who, '')
        cx = (p[CHEEKS[0]][0] + p[CHEEKS[1]][0]) / 2
        for j in (JAW_L if 'L' in sides else ()) + (JAW_R if 'R' in sides else ()):
            v = np.array([(cx - p[j][0]) * 0.13, -fw * 0.015])
            a = push(a, p[j], v, fw * 0.22)
        if sides == 'LR':
            a = push(a, p[CHIN], (0, -fw * 0.04), fw * 0.2)

    # 팔뚝 — 소매 바깥 윤곽을 안쪽으로
    for c, v in ed['arms']:
        a = push(a, np.array(c) * k, np.array(v) * k, ed['arm_r'] * k)
    return Image.fromarray(a)
