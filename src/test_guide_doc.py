"""앱의 가이드 상세(응가메이트 가이드)가 받는 글 JSON — guide_doc.py. 실행: python3 -m pytest src/test_guide_doc.py"""
from guide_doc import guide_blocks, spans_of

MAIN = '''<h1>강아지가 설사를 하는 이유, 집에서 볼 때</h1>
<p class="lede">가벼운 이유가 <b>가장</b> 흔해요.</p>
<h2>1. 흔한 원인</h2>
<table>
  <tr><th>원인</th><th>이럴 때</th></tr>
  <tr><td>사료 급변</td><td>하루아침에 <b>바꿨을</b> 때</td></tr>
</table>
<p>원인은 <a href="/poop-condition-guide/">똥 상태 체크</a>로 봐요.</p>
<div class="warn">이 글은 진단이 아니에요.</div>
<ul>
  <li><b>물은 충분히:</b> 깨끗한 물을</li>
  <li>둘째</li>
</ul>
<ol><li>설치해요</li></ol>
<div class="method-card">
  <b>① 단톡방</b>
  <p style="margin:6px 0 0;">스크롤로 찾아야 해요.</p>
</div>
<h2>응가메이트로 변화 알아채기</h2>
<div class="card"><p style="margin:0;">앱 소개</p></div>
<a class="cta" href="/download/">기록하기</a>
<h2>참고 자료</h2>
<ul class="refs"><li><a href="https://news.example/a" rel="noopener" target="_blank">신문, 기사</a></li></ul>
<h2>자주 묻는 질문</h2>
<details class="faq-item">
  <summary>한 번 했는데 병원?</summary>
  <p style="margin-top:8px;">하루 지켜봐요.</p>
</details>
<p class="related">관련 글: <a href="/dog-constipation-causes/">변비 원인</a> · <a href="/yellow-gray-dog-poop/">노란 똥</a></p>
'''


def test_spans_keep_bold_and_links():
    assert spans_of('가벼운 이유가 <b>가장</b> 흔해요.') == [{'text': '가벼운 이유가 '}, {'text': '가장', 'bold': True}, {'text': ' 흔해요.'}]
    assert spans_of('<a href="/x/">글</a> 봐요') == [{'text': '글', 'href': '/x/'}, {'text': ' 봐요'}]
    assert spans_of('줄\n   바꿈') == [{'text': '줄 바꿈'}]


def test_doc_head():
    d = guide_blocks(MAIN, 'dog-diarrhea-causes')
    assert d['title'] == '강아지가 설사를 하는 이유, 집에서 볼 때'
    assert d['lede'] == [{'text': '가벼운 이유가 '}, {'text': '가장', 'bold': True}, {'text': ' 흔해요.'}]


def test_blocks_in_order_without_app_card_faq_related():
    b = guide_blocks(MAIN, 'dog-diarrhea-causes')['blocks']
    assert [x['type'] for x in b] == ['h2', 'table', 'p', 'warn', 'list', 'list', 'card', 'h2', 'list']
    assert b[0] == {'type': 'h2', 'text': '흔한 원인'}  # 옛 「1. 」 번호는 뺀다
    assert b[1]['head'] == ['원인', '이럴 때']
    assert b[1]['rows'] == [[[{'text': '사료 급변'}], [{'text': '하루아침에 '}, {'text': '바꿨을', 'bold': True}, {'text': ' 때'}]]]
    assert b[2]['spans'][1] == {'text': '똥 상태 체크', 'href': '/poop-condition-guide/'}
    assert b[3] == {'type': 'warn', 'spans': [{'text': '이 글은 진단이 아니에요.'}]}
    assert b[4] == {'type': 'list', 'ordered': False, 'items': [[{'text': '물은 충분히:', 'bold': True}, {'text': ' 깨끗한 물을'}], [{'text': '둘째'}]]}
    assert b[5] == {'type': 'list', 'ordered': True, 'items': [[{'text': '설치해요'}]]}
    assert b[6] == {'type': 'card', 'title': '① 단톡방', 'spans': [{'text': '스크롤로 찾아야 해요.'}]}
    assert b[7] == {'type': 'h2', 'text': '참고 자료'}
    assert b[8]['items'] == [[{'text': '신문, 기사', 'href': 'https://news.example/a'}]]


def test_faq_and_related():
    d = guide_blocks(MAIN, 'dog-diarrhea-causes')
    assert d['faqs'] == [{'q': '한 번 했는데 병원?', 'a': '하루 지켜봐요.'}]
    assert d['related'] == [{'slug': 'dog-constipation-causes', 'title': '변비 원인'}, {'slug': 'yellow-gray-dog-poop', 'title': '노란 똥'}]


def test_every_real_guide_converts():
    import json, pathlib
    root = pathlib.Path(__file__).parent / 'legacy/guides'
    files = list(root.glob('*.json')) + list((root / 'en').glob('*.json'))
    assert len(files) >= 30
    for f in files:
        d = guide_blocks(json.loads(f.read_text(encoding='utf-8'))['main'], f.stem)
        assert d['title'] and d['lede'] and d['blocks'], f
        assert d['blocks'][0]['type'] in ('h2', 'p', 'table', 'list', 'card'), f


def test_upsert_sql_quotes_and_prunes():
    from guide_doc import guides_upsert_sql
    rows = [{'slug': 'a', 'lang': 'ko', 'cat': 'poop', 'title': "강아지's 똥", 'summary': '요약', 'image': 'x.webp', 'thumbnail': 't.jpg', 'published_on': '2026-10-30',
             'minutes': 3, 'lede': [{'text': "it's"}], 'blocks': [], 'faqs': [], 'related': []}]
    sql = guides_upsert_sql(rows)
    assert "insert into public.guides" in sql
    assert "'강아지''s 똥'" in sql
    assert "'[{\"text\": \"it''s\"}]'::jsonb" in sql
    assert 'on conflict (slug, lang) do update set' in sql
    assert "delete from public.guides where (slug, lang) not in (('a', 'ko'))" in sql
    assert sql.startswith('begin;') and sql.rstrip().endswith('commit;')


def test_macrons_become_plain_letters_for_the_app_font():
    # 앱 글꼴에 ō·ū 같은 장음 글자가 없어 다른 글꼴로 대신 그려져 튄다 — 앱 글에는 장음 부호를 뺀다(dōkō → doko)
    assert spans_of('"<b>dōkō hinan</b>" and dōhan') == [{'text': '"'}, {'text': 'doko hinan', 'bold': True}, {'text': '" and dohan'}]
    d = guide_blocks('<h1>Dōkō</h1><p class="lede">x</p><h2>Rūru</h2>', 's')
    assert d['title'] == 'Doko' and d['blocks'][0]['text'] == 'Ruru'
