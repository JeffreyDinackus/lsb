import json, re

SECTIONS = [
    ("morning-prayer", "Daily Morning Prayer", 21, 42),
    ("midday-prayer", "Daily Midday Prayer", 43, 50),
    ("evening-prayer", "Daily Evening Prayer", 51, 66),
    ("compline", "Compline", 67, 76),
    ("family-prayer", "Family Prayer", 77, 88),
    ("supplemental-canticles", "Supplemental Canticles for Worship", 89, 100),
]

lines_by_page = json.load(open('scratch/lines.json'))

WS_RE = re.compile(r'[ \t]+')
def clean(s):
    s = s.replace('­', '')
    s = WS_RE.sub(' ', s)
    return s.strip()

LABELS = {"officiant", "people", "officiant and people", "reader", "deacon",
          "the officiant", "the people", "priest", "all", "leader", "minister",
          "the priest", "the celebrant", "celebrant", "the deacon", "the leader",
          "husband", "wife", "parent", "child", "one voice", "the reader"}

def classify_line(line):
    runs = line['runs']
    clean_runs = []
    for r in runs:
        t = r['text']
        if clean(t) == '':
            continue
        clean_runs.append(r)
    if not clean_runs:
        return None
    # drop stray decorative marker glyphs (e.g. a lone dagger/pilcrow that
    # extracts as a single tiny-font character trailing the real content)
    while len(clean_runs) >= 2:
        last = clean_runs[-1]
        ct = clean(last['text'])
        if len(ct) <= 1 and (last.get('size') or 17) <= 10:
            clean_runs = clean_runs[:-1]
        else:
            break
    if not clean_runs:
        return None
    # detect trailing citation: last run far right, small size
    citation = None
    body_runs = clean_runs
    if len(clean_runs) >= 2:
        last = clean_runs[-1]
        if last['left'] > 300 and (last.get('size') or 17) <= 16 and clean(last['text']):
            citation = clean(last['text'])
            body_runs = clean_runs[:-1]
    if not body_runs:
        return dict(kind='citation-only', citation=citation, top=line['top'])

    # detect label + body on same line (dialogue)
    label = None
    if len(body_runs) >= 2:
        first = body_runs[0]
        low = clean(first['text']).rstrip('.').lower()
        if first['italic'] and low in LABELS and body_runs[1]['left'] - first['left'] < 100:
            label = clean(first['text']).rstrip('.')
            body_runs = body_runs[1:]

    # detect leading verse number (bold small digits)
    verse_num = None
    if len(body_runs) >= 1:
        first = body_runs[0]
        txt = clean(first['text'])
        if txt.isdigit() and (first.get('size') or 17) <= 12:
            verse_num = txt
            body_runs = body_runs[1:]

    if not body_runs:
        return dict(kind='citation-only', citation=citation, top=line['top']) if citation else None

    def weight(pred):
        total = sum(max(len(clean(r['text'])), 1) for r in body_runs) or 1
        matched = sum(max(len(clean(r['text'])), 1) for r in body_runs if pred(r))
        return matched > total / 2
    bold = weight(lambda r: r['bold'])
    italic = weight(lambda r: r['italic'])
    size = body_runs[0].get('size') or 17
    left = body_runs[0]['left']

    def is_substantial(s):
        s = s.strip(' .,;:*')
        return len(s) >= 6 and len(s.split()) >= 2

    # detect two-column "traditional / contemporary" style alternatives:
    # either an explicit lone italic "or" run between two chunks, or a wide
    # real (width-aware) horizontal gap between runs. Short trailing bold
    # interjections (e.g. a congregational "Amen.") are NOT columns - those
    # are handled as inline emphasis below.
    columns = None
    or_idx = None
    heading_sized = size > 17
    if not heading_sized:
        for idx, r in enumerate(body_runs):
            if 0 < idx < len(body_runs) - 1 and r['italic'] and clean(r['text']).lower() == 'or':
                or_idx = idx
                break
    if or_idx is not None:
        colA = clean(''.join(r['text'] for r in body_runs[:or_idx]))
        colB = clean(''.join(r['text'] for r in body_runs[or_idx + 1:]))
        if is_substantial(colA) and is_substantial(colB):
            columns = [colA, colB]
    if columns is None and not heading_sized and len(body_runs) >= 2:
        best_gap = 0
        best_i = None
        for idx in range(1, len(body_runs)):
            prev = body_runs[idx - 1]
            prev_right = prev['left'] + (prev.get('width') or len(prev['text']) * 8)
            gap = body_runs[idx]['left'] - prev_right
            if gap > best_gap:
                best_gap = gap
                best_i = idx
        if best_gap > 40 and best_i is not None:
            colA = clean(''.join(r['text'] for r in body_runs[:best_i]))
            colB = clean(''.join(r['text'] for r in body_runs[best_i:]))
            if is_substantial(colA) and is_substantial(colB):
                columns = [colA, colB]
    if columns is None and not heading_sized:
        joined = ''.join(r['text'] for r in body_runs)
        m = re.search(r'\S {3,}\S', joined)
        if m:
            split_at = joined.index('  ', m.start())
            colA = clean(joined[:split_at])
            colB = clean(joined[split_at:])
            if is_substantial(colA) and is_substantial(colB):
                columns = [colA, colB]

    # build text with inline emphasis markers for runs whose style deviates
    # from the line's dominant style (e.g. a bolded "Amen." inside an
    # otherwise plain sentence, or a lone italic aside inside a bold verse).
    # adjacent runs sharing the same deviation are grouped into a single
    # span first so the source's own literal "_" characters (used as a
    # fill-in-the-blank rule) are never mistaken for marker boundaries.
    groups = []
    for r in body_runs:
        rt = r['text']
        if not rt.strip():
            kind_tag = None
        else:
            rb = r['bold'] and not bold
            ri = r['italic'] and not italic
            kind_tag = 'b' if rb else ('i' if ri else None)
        if groups and groups[-1][0] == kind_tag:
            groups[-1][1] += rt
        else:
            groups.append([kind_tag, rt])
    parts = []
    for kind_tag, seg in groups:
        if kind_tag:
            lead = ' ' if seg[:1] == ' ' else ''
            trail = ' ' if seg[-1:] == ' ' else ''
            mark = '**' if kind_tag == 'b' else ''
            seg = f'{lead}{mark}{seg.strip()}{mark}{trail}'
        parts.append(seg)
    raw_text = ''.join(parts)
    if not bold and not italic and size >= 20:
        # large plain headings are letter-tracked in the source (single
        # spaces between letters, wide gaps between words); reconstruct
        # real word boundaries before collapsing whitespace
        raw_text = re.sub(r' {2,}', '\x00', raw_text)
        raw_text = raw_text.replace(' ', '')
        raw_text = raw_text.replace('\x00', ' ')
    text = clean(raw_text)
    text = text.replace('', '_')
    if not text:
        return None

    is_citation_like = bool(re.fullmatch(r"[a-z0-9][a-z0-9 ,;:.\-']+", text)) and bool(re.search(r'\d', text))

    kind = 'body'
    if not bold and not italic and size >= 18:
        kind = 'heading'
    elif not bold and not italic and size <= 16 and (left > 150 or is_citation_like):
        # centered small citation/heading (e.g. "psalm 121", "Levavi oculos" handled separately by italic check)
        kind = 'small-heading'
    elif italic and not bold:
        kind = 'subtitle' if left > 150 else 'rubric'
    elif bold:
        kind = 'strong'
    else:
        kind = 'body'

    return dict(kind=kind, text=text, columns=columns, label=label, verse_num=verse_num, citation=citation,
                top=line['top'], left=left, bold=bold, italic=italic, size=size)


def build_blocks_for_page(page_num):
    lines = lines_by_page.get(str(page_num), [])
    tokens = []
    for line in lines:
        cl = classify_line(line)
        if cl:
            tokens.append(cl)
    return tokens


all_tokens = {}
for num in range(21, 101):
    all_tokens[num] = build_blocks_for_page(num)

with open('scratch/tokens.json', 'w') as f:
    json.dump(all_tokens, f, indent=1)

print('done')
