"""가이드 글(옛 글 HTML, src/legacy/guides)을 앱이 직접 그리는 글 JSON으로 바꾼다.

앱의 「응가메이트 가이드」 상세는 웹뷰가 아니라 앱 화면이라, 글을 블록으로 받는다:
  h2(소제목) · h3(작은 소제목) · p(문단) · list(점·번호 목록) · table(표) · warn(알아 두세요 상자) · card(비교 카드) · img(강아지 사진)
읽기 쉽게(11-08): 긴 문단은 두 문장씩 나누고, 「굵은 말: 설명」 목록은 작은 소제목 + 문단으로 풀고, 소제목 사이사이에 사진을 넣는다.
글 안 글자는 spans — [{text, bold?, href?}]. 앱 소개 카드·버튼·FAQ·관련 글 줄은 본문에서 빼고 faqs·related로 따로 준다.
"""
import html
import re
import unicodedata
from html.parser import HTMLParser


class _Node:
    def __init__(self, tag, attrs):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    @property
    def cls(self):
        return self.attrs.get('class') or ''


class _Tree(HTMLParser):
    VOID = {'br', 'img', 'hr', 'meta', 'link', 'input'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node('root', [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _parse(fragment):
    t = _Tree()
    t.feed(fragment)
    t.close()
    return t.root


def _plain(text):
    """장음 부호(ō·ū·ā)를 뺀다 — 앱 글꼴에 없는 글자라 다른 글꼴로 그려져 튀니까"""
    return unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', text) if c != '\u0304'))


def _inline(node, bold=False, href=None, out=None):
    out = [] if out is None else out
    for c in node.children:
        if isinstance(c, str):
            text = _plain(re.sub(r'\s+', ' ', c))
            if not text:
                continue
            span = {'text': text}
            if bold:
                span['bold'] = True
            if href:
                span['href'] = href
            if out and {k: v for k, v in out[-1].items() if k != 'text'} == {k: v for k, v in span.items() if k != 'text'}:
                out[-1]['text'] += text
            else:
                out.append(span)
        elif c.tag == 'br':
            if out:
                out[-1]['text'] += '\n'
        else:
            _inline(c, bold or c.tag in ('b', 'strong'), c.attrs.get('href') if c.tag == 'a' else href, out)
    return out


def _trim(spans):
    spans = [dict(s) for s in spans]
    while spans and not spans[0]['text'].strip():
        spans.pop(0)
    while spans and not spans[-1]['text'].strip():
        spans.pop()
    if spans:
        spans[0]['text'] = spans[0]['text'].lstrip()
        spans[-1]['text'] = spans[-1]['text'].rstrip()
    return spans


def spans_of(fragment):
    return _trim(_inline(_parse(fragment)))


def _text(node):
    return ''.join(s['text'] for s in _trim(_inline(node))).strip()


def _elements(node):
    return [c for c in node.children if not isinstance(c, str)]


FAQ_H2 = re.compile(r'자주 묻는 질문|Frequently Asked Questions|FAQ', re.I)


SENT_END = re.compile(r'(?<=[.!?])\s+(?=\S)')


def _split_para(spans, per=2, min_len=90):
    """긴 문단을 두 문장씩 여러 문단으로 — 굵게·링크(spans)는 그대로 둔다"""
    if sum(len(x['text']) for x in spans) < min_len:
        return [spans]
    paras, cur, n = [], [], 0
    for sp in spans:
        parts = SENT_END.split(sp['text'])
        for i, part in enumerate(parts):
            last = i == len(parts) - 1
            piece = part if last else part + ' '
            if piece:
                cur.append({**sp, 'text': piece})
            if not last:
                n += 1
                if n >= per:
                    paras.append(_trim(cur)); cur, n = [], 0
    if cur and _trim(cur):
        paras.append(_trim(cur))
    return [p for p in paras if p] or [spans]


def _lead_item(item):
    """「굵은 말: 설명」 목록 줄 → (소제목, 설명 spans) — 아니면 None"""
    if len(item) < 2 or not item[0].get('bold') or item[0].get('href'):
        return None
    head = item[0]['text'].strip()
    if not head.endswith(':') or len(head) > 40:
        return None
    rest = _trim(item[1:])
    if sum(len(x['text']) for x in rest) < 30:
        return None
    return head.rstrip(':').strip(), rest


def _readable(blocks, photos):
    out = []
    for b in blocks:
        if b['type'] == 'p':
            out += [{'type': 'p', 'spans': x} for x in _split_para(b['spans'])]
        elif b['type'] == 'list' and not b['ordered'] and b['items'] and all(_lead_item(i) for i in b['items']):
            for i in b['items']:
                head, rest = _lead_item(i)
                out.append({'type': 'h3', 'text': head})
                out += [{'type': 'p', 'spans': x} for x in _split_para(rest)]
        else:
            out.append(b)
    # 사진 — 둘째·넷째·여섯째 소제목 앞에 한 장씩(글이 짧으면 있는 만큼)
    if photos:
        h2s = [i for i, b in enumerate(out) if b['type'] == 'h2']
        spots = [h2s[k] for k in (1, 3, 5) if k < len(h2s)][:len(photos)]
        for i, idx in sorted(zip(range(len(spots)), spots), key=lambda x: -x[1]):
            out.insert(idx, {'type': 'img', **photos[i]})
    return out


def guide_blocks(main, slug, photos=None):
    root = _parse(main)
    title, lede, blocks, faqs, related = '', [], [], [], []
    for el in _elements(root):
        tag, cls = el.tag, el.cls
        if tag == 'h1':
            title = _text(el)
        elif tag == 'p' and 'lede' in cls and not lede:
            lede = _trim(_inline(el))
        elif tag == 'p' and 'related' in cls:
            for a in (c for c in _elements(el) if c.tag == 'a'):
                rs = a.attrs.get('href', '').strip('/').split('/')[-1]
                if rs and rs != slug:
                    related.append({'slug': rs, 'title': _text(a)})
        elif tag == 'details':
            q = next((c for c in _elements(el) if c.tag == 'summary'), None)
            a = next((c for c in _elements(el) if c.tag == 'p'), None)
            if q is not None and a is not None:
                faqs.append({'q': _text(q), 'a': _text(a)})
        elif tag == 'h2':
            text = re.sub(r'^\s*\d+\.\s*', '', _text(el))
            if not FAQ_H2.search(text):
                blocks.append({'type': 'h2', 'text': text})
        elif tag == 'h3':
            blocks.append({'type': 'h3', 'text': _text(el)})
        elif tag == 'div' and cls == 'card':
            # 앱 소개 카드 — 바로 앞 소제목과 함께 뺀다(앱 안이니까)
            if blocks and blocks[-1]['type'] == 'h2':
                blocks.pop()
        elif tag == 'a' and 'cta' in cls:
            continue
        elif tag == 'p':
            spans = _trim(_inline(el))
            if not lede:
                lede = spans
            elif spans:
                blocks.append({'type': 'p', 'spans': spans})
        elif tag in ('ul', 'ol'):
            items = [_trim(_inline(li)) for li in _elements(el) if li.tag == 'li']
            blocks.append({'type': 'list', 'ordered': tag == 'ol', 'items': items})
        elif tag == 'table':
            rows = [r for r in _walk(el) if r.tag == 'tr']
            head, body = [], []
            for r in rows:
                cells = [c for c in _elements(r) if c.tag in ('th', 'td')]
                if cells and all(c.tag == 'th' for c in cells) and not head and not body:
                    head = [_text(c) for c in cells]
                else:
                    body.append([_trim(_inline(c)) for c in cells])
            blocks.append({'type': 'table', 'head': head, 'rows': body})
        elif tag == 'div' and 'warn' in cls:
            blocks.append({'type': 'warn', 'spans': _trim(_inline(el))})
        elif tag == 'div' and 'method-card' in cls:
            b = next((c for c in _elements(el) if c.tag == 'b'), None)
            p = next((c for c in _elements(el) if c.tag == 'p'), None)
            blocks.append({'type': 'card', 'title': _text(b) if b is not None else '', 'spans': _trim(_inline(p)) if p is not None else []})
    return {'title': html.unescape(title), 'lede': lede, 'blocks': _readable(blocks, photos), 'faqs': faqs, 'related': related}


def _walk(node):
    for c in _elements(node):
        yield c
        yield from _walk(c)


def _q(v):
    if v is None:
        return 'null'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


GUIDE_COLUMNS = ('slug', 'lang', 'cat', 'title', 'summary', 'image', 'thumbnail', 'published_on', 'minutes', 'lede', 'blocks', 'faqs', 'related')
JSON_COLUMNS = {'lede', 'blocks', 'faqs', 'related'}


def guides_upsert_sql(rows):
    """앱 가이드 표(public.guides)를 홈페이지 글과 똑같이 맞추는 SQL — 있는 글은 고치고, 없는 글은 넣고, 사라진 글은 지운다."""
    import json
    values = []
    for r in rows:
        cells = [(_q(json.dumps(r[c], ensure_ascii=False)) + '::jsonb') if c in JSON_COLUMNS else _q(r[c]) for c in GUIDE_COLUMNS]
        values.append('(' + ', '.join(cells) + ')')
    updates = ', '.join(f'{c} = excluded.{c}' for c in GUIDE_COLUMNS if c not in ('slug', 'lang'))
    keep = ', '.join(f"({_q(r['slug'])}, {_q(r['lang'])})" for r in rows)
    return ('begin;\n'
            f'insert into public.guides ({", ".join(GUIDE_COLUMNS)}) values\n  ' + ',\n  '.join(values) + '\n'
            f'on conflict (slug, lang) do update set {updates}, updated_at = now();\n'
            f'delete from public.guides where (slug, lang) not in ({keep});\n'
            'commit;\n')
