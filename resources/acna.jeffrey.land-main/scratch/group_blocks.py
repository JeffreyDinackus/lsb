import json, re

SECTIONS = [
    ("morning-prayer", "Daily Morning Prayer", 11, 21, 42),
    ("midday-prayer", "Daily Midday Prayer", 33, 43, 50),
    ("evening-prayer", "Daily Evening Prayer", 41, 51, 66),
    ("compline", "Compline", 57, 67, 76),
    ("family-prayer", "Family Prayer", 67, 77, 88),
    # pages 99-100 are just the blank/divider pages leading into the next
    # major section (The Great Litany & Decalogue), not part of this content
    ("supplemental-canticles", "Supplemental Canticles for Worship", 79, 89, 98),
]

tokens_by_page = json.load(open('scratch/tokens.json'))


def all_tokens_for_range(p_start, p_end):
    toks = []
    for p in range(p_start, p_end + 1):
        for t in tokens_by_page.get(str(p), []):
            t = dict(t)
            t['page'] = p
            toks.append(t)
    return toks


def same_flow(a, b):
    # true if token b is a wrapped continuation of the same paragraph/verse
    # as token a, rather than a new paragraph after a blank-line gap. normal
    # line-to-line spacing is ~19-20pt; a blank line before the next
    # paragraph shows up as roughly double that.
    if a['page'] != b['page']:
        return True
    return (b['top'] - a['top']) <= 26


def group_section(toks):
    blocks = []
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        kind = t['kind']

        if kind == 'citation-only':
            if blocks and blocks[-1].get('type') in ('paragraph', 'dialogue'):
                blocks[-1]['citation'] = t.get('citation')
            i += 1
            continue

        if kind == 'heading':
            # large titles can wrap across two closely-stacked physical
            # lines (bigger type means bigger natural line spacing than
            # the ~26pt gap threshold used for ordinary paragraph text)
            texts = [t['text']]
            j = i + 1
            while (j < n and toks[j]['kind'] == 'heading' and toks[j]['page'] == toks[j - 1]['page']
                   and (toks[j]['top'] - toks[j - 1]['top']) <= 35):
                texts.append(toks[j]['text'])
                j += 1
            blocks.append(dict(type='heading', text=' '.join(texts)))
            i = j
            continue

        if kind == 'subtitle':
            blocks.append(dict(type='subtitle', text=t['text']))
            i += 1
            continue

        if kind == 'small-heading':
            blocks.append(dict(type='small-heading', text=t['text']))
            i += 1
            continue

        if t.get('columns'):
            rows = [t['columns']]
            j = i + 1
            while j < n and toks[j].get('columns'):
                rows.append(toks[j]['columns'])
                j += 1
            blocks.append(dict(type='columns', rows=rows))
            i = j
            continue

        if t.get('label'):
            texts = [t['text']]
            citation = t.get('citation')
            j = i + 1
            # a wrapped second physical line of the same spoken line has no
            # label of its own; absorb it as a continuation rather than
            # letting it spawn a stray paragraph/verse block
            while (j < n and toks[j]['kind'] in ('body', 'strong')
                   and not toks[j].get('label') and not toks[j].get('columns')
                   and toks[j].get('verse_num') is None and same_flow(toks[j - 1], toks[j])):
                texts.append(toks[j]['text'])
                if toks[j].get('citation'):
                    citation = toks[j]['citation']
                j += 1
            block = dict(type='dialogue', label=t['label'], text=' '.join(texts), strong=t['bold'])
            if citation:
                block['citation'] = citation
            blocks.append(block)
            i = j
            continue

        if kind == 'rubric':
            texts = [t['text']]
            j = i + 1
            while (j < n and toks[j]['kind'] == 'rubric' and not toks[j].get('label')
                   and not toks[j].get('columns') and same_flow(toks[j - 1], toks[j])):
                texts.append(toks[j]['text'])
                j += 1
            blocks.append(dict(type='rubric', text=' '.join(texts)))
            i = j
            continue

        if kind == 'body':
            texts = [t['text']]
            citation = t.get('citation')
            j = i + 1
            while (j < n and toks[j]['kind'] == 'body' and not toks[j].get('label') and not toks[j].get('columns')
                   and not toks[j].get('verse_num') and same_flow(toks[j - 1], toks[j])):
                texts.append(toks[j]['text'])
                if toks[j].get('citation'):
                    citation = toks[j]['citation']
                j += 1
            # a short standalone bold line right after a plain paragraph is
            # normally just that paragraph's congregational "Amen." printed
            # on its own typeset line - fold it in as trailing emphasis
            # instead of letting it spawn an orphan one-line verse-block
            if (j < n and toks[j]['kind'] == 'strong' and not toks[j].get('label')
                    and not toks[j].get('columns') and toks[j].get('verse_num') is None
                    and len(toks[j]['text'].strip(' .')) <= 12 and same_flow(toks[j - 1], toks[j])):
                texts.append(f"**{toks[j]['text'].strip()}**")
                if toks[j].get('citation'):
                    citation = toks[j]['citation']
                j += 1
            block = dict(type='paragraph', text=' '.join(texts))
            if citation:
                block['citation'] = citation
            blocks.append(block)
            i = j
            continue

        if kind == 'strong':
            # group into one or more verses; a verse_num starts a new verse,
            # otherwise all consecutive strong lines (no label/columns) form
            # one running verse-block preserving individual poetic lines
            verses = []
            cur_lines = []
            cur_num = t.get('verse_num')
            cur_citation = None

            def flush():
                if cur_lines:
                    v = dict(number=cur_num, lines=list(cur_lines))
                    if cur_citation:
                        v['citation'] = cur_citation
                    verses.append(v)

            j = i
            while (j < n and toks[j]['kind'] == 'strong' and not toks[j].get('label') and not toks[j].get('columns')
                   and (j == i or same_flow(toks[j - 1], toks[j]))):
                tk = toks[j]
                if tk.get('verse_num') is not None and cur_lines:
                    flush()
                    cur_lines = []
                    cur_num = tk.get('verse_num')
                    cur_citation = None
                elif tk.get('verse_num') is not None:
                    cur_num = tk.get('verse_num')
                cur_lines.append(tk['text'])
                if tk.get('citation'):
                    cur_citation = tk['citation']
                j += 1
            flush()
            blocks.append(dict(type='verse-block', verses=verses))
            i = j
            continue

        i += 1

    return blocks


sections_out = []
for sid, title, printed_page, p_start, p_end in SECTIONS:
    toks = all_tokens_for_range(p_start, p_end)
    blocks = group_section(toks)
    sections_out.append(dict(id=sid, title=title, printedPage=printed_page, blocks=blocks))

with open('scratch/content.json', 'w') as f:
    json.dump(sections_out, f, indent=1, ensure_ascii=False)

# print quick stats
for s in sections_out:
    from collections import Counter
    c = Counter(b['type'] for b in s['blocks'])
    print(s['id'], len(s['blocks']), dict(c))
