# 從「雅思單詞」資料夾的 PDF 抽出小說，輸出 content/storyNNN.md（{英文|中文} 標記）。
# 用法：python extract.py "D:/.../雅思單詞"
# 來源：學習版 PDF（單字後附中文）；以複習版 PDF 與「重點單詞.xlsx」交叉驗證單字序列。
import os, re, sys, glob, html, zipfile, difflib
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')
SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content')
os.makedirs(OUT, exist_ok=True)
W = r"[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ\-'’]*"
CAND = rf"({W}(?:\s+{W})*)\s*（"
TOK = re.compile(CAND + r"([^）]*)）")
RTOK = re.compile(CAND + r"\s*）")
XSET = set()

def norm(c): return re.sub(r'\s+', ' ', c.strip())

def resolve(c):
    """候選字串可能黏著前面的英文（如 AItranslate），用單字表找詞組起點。回傳 (前綴, 單字或詞組)"""
    c = norm(c)
    for i in range(len(c)):
        if c[i:].lower() in XSET: return c[:i], c[i:]
    return '', c

def sj(parts):  # 行與行相接：兩側皆英文字母時補空白（詞組換行）
    out = parts[0]
    for t in parts[1:]:
        out += (' ' if re.search(r'[A-Za-z]$', out) and re.match(r'[A-Za-z]', t) else '') + t
    return out

def rows_of(pdf):
    sp = []
    for b in pymupdf.open(pdf)[0].get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                sp.append((s['origin'][1], s['origin'][0], s['text']))
    sp.sort(); rows, cur = [], []
    for s in sp:
        if cur and s[0] - cur[-1][0] > 4: rows.append(cur); cur = []
        cur.append(s)
    if cur: rows.append(cur)
    return [(r[0][0], ''.join(x[2] for x in sorted(r, key=lambda z: z[1]))) for r in rows]

def story(pdf):
    title, paras, cur, prev = None, [], [], None
    for y, t in rows_of(pdf):
        t = t.strip()
        if t.startswith('Step'): continue
        if re.match(r'Story\d+', t) and title is None: title = t; prev = y; continue
        if re.search(r'Story\d+\s*(學習版|複習版)', t): continue
        if prev is not None and cur and y - prev > 60: paras.append(sj(cur)); cur = []
        cur.append(t); prev = y
    if cur: paras.append(sj(cur))
    return title, paras

def xlsx_words(path):
    s = zipfile.ZipFile(path).read('xl/worksheets/sheet1.xml').decode('utf-8')
    out = []
    for row in re.findall(r'<row [^>]*>(.*?)</row>', s, re.S)[1:]:
        c = [html.unescape(x) for x in re.findall(r'<t[^>]*>([^<]*)</t>', row)]
        if len(c) >= 2: out.append((c[0], c[1]))
    return out

def mark(p):
    res, pos, toks = [], 0, []
    for m in TOK.finditer(p):
        pre, w = resolve(m.group(1)); w = w.replace("'", '’'); zh = m.group(2).strip()
        res.append(re.sub(r'\s+', '', p[pos:m.start()] + pre)); res.append('{%s|%s}' % (w, zh)); toks.append((w, zh)); pos = m.end()
    res.append(re.sub(r'\s+', '', p[pos:]))
    return ''.join(res), toks

dirs = sorted([d for d in os.listdir(SRC) if re.match(r'\d+、', d)], key=lambda d: int(d.split('、')[0]))
bad = 0
for d in dirs:
    n = int(d.split('、')[0]); folder = os.path.join(SRC, d)
    learn = glob.glob(os.path.join(folder, '*學習版.pdf'))[0]; review = glob.glob(os.path.join(folder, '*複習版.pdf'))[0]
    xl = xlsx_words(os.path.join(folder, '重點單詞.xlsx'))
    XSET.clear(); XSET.update(a.lower() for a, _ in xl)
    title, paras = story(learn)
    lines, toks = [], []
    for p in paras:
        m, t = mark(p); lines.append(m); toks += t
    _, rparas = story(review)
    rtok = [resolve(m.group(1))[1] for p in rparas for m in RTOK.finditer(p)]
    issues = []
    ids = [a.replace("'", '’') for a, _ in toks]
    toks = [(a.replace("'", '’'), z) for a, z in toks]
    if ids != rtok:
        sm = difflib.SequenceMatcher(None, ids, rtok)
        issues.append('review-seq(%d vs %d) %s' % (len(ids), len(rtok), [(t, ids[i1:i2], rtok[j1:j2]) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal'][:3]))
    ws = set(a.lower() for a in ids); xw = set(XSET)
    miss = {a for a in ws - xw if '-' not in a}
    if miss or (xw - ws): issues.append('xlsx-diff only-story=%s only-xlsx=%s' % (sorted(miss)[:6], sorted(xw - ws)[:6]))
    odd = [a for a in ids if re.search(r"[\\\"<>{}|]", a)]
    if odd: issues.append('odd-id %s' % odd)
    if any(not zh for _, zh in toks): issues.append('empty-gloss')
    if issues: bad += 1; print('!!', n, d, issues)
    open(os.path.join(OUT, 'story%03d.md' % n), 'w', encoding='utf-8').write(re.sub(r'(?<![標書抽])籤', '簽', '# %s\n\n%s\n' % (title or d, '\n\n'.join(lines))))  # 轉繁體時的 簽/籤 誤字
    print(n, d, len(paras), 'paras', len(toks), 'words')
print('done', len(dirs), 'stories;', bad, 'with issues')
