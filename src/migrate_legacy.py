"""한 번만 — 옛 정적 페이지(검색 가이드 10개·인터뷰 신청)에서 본문과 메타를 떼어 src/legacy/ 로 옮긴다.
이후로는 build.py가 이 원본으로 새 디자인 페이지를 만든다."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ['share-dog-potty-log-with-family', 'dog-walk-schedule-sharing', 'dual-income-dog-walk-schedule', 'multi-dog-household-tracking',
          'outdoor-potty-dog-tracking', 'jindo-mix-potty-training', 'potty-interval', 'poop-condition-guide', 'walk-safety-index']


def meta(s, name, attr='name'):
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', s)
    return m.group(1) if m else ''


for slug in GUIDES:
    s = (ROOT / slug / 'index.html').read_text(encoding='utf-8')
    main = re.search(r'<main>(.*?)</main>', s, re.S).group(1)
    main = re.sub(r'\s*<nav aria-label="breadcrumb".*?</nav>', '', main, flags=re.S)   # 새 템플릿이 빵부스러기를 그린다
    data = {
        'slug': slug,
        'title': re.search(r'<title>(.*?)</title>', s, re.S).group(1).strip(),
        'description': meta(s, 'description'),
        'keywords': meta(s, 'keywords'),
        'og_title': meta(s, 'og:title', 'property'),
        'ld': re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S),
        'main': main.strip(),
    }
    (ROOT / f'src/legacy/guides/{slug}.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(slug, len(main))

(ROOT / 'src/legacy/interview.html').write_text((ROOT / 'interview/index.html').read_text(encoding='utf-8'), encoding='utf-8')
