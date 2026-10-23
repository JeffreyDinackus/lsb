import re, json, sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

SECTIONS = [
    ("morning-prayer", "Daily Morning Prayer", 21, 42),
    ("midday-prayer", "Daily Midday Prayer", 43, 50),
    ("evening-prayer", "Daily Evening Prayer", 51, 66),
    ("compline", "Compline", 67, 76),
    ("family-prayer", "Family Prayer", 77, 88),
    ("supplemental-canticles", "Supplemental Canticles for Worship", 89, 100),
]

tree = ET.parse('scratch/office.xml')
root = tree.getroot()

pages = {}
for page in root.findall('page'):
    num = int(page.get('number'))
    elems = []
    for t in page.findall('text'):
        top = int(t.get('top'))
        left = int(t.get('left'))
        width = int(t.get('width'))
        if top >= 735:
            continue  # running footer / page number
        # determine style from nested tags
        b = t.find('.//b')
        i = t.find('.//i')
        is_bold = b is not None
        is_italic = i is not None
        # get text content stripping tags
        text = ''.join(t.itertext())
        if text.strip() == '' and not text:
            continue
        size = None
        fid = t.get('font')
        elems.append(dict(top=top, left=left, width=width, text=text, bold=is_bold, italic=is_italic, font=fid))
    elems.sort(key=lambda e: (e['top'], e['left']))
    pages[num] = elems

# fontspec ids are declared once globally in document order and reused
# across pages without being redeclared, so accumulate into one global map
global_fontsizes = {}
for page in root.findall('page'):
    for fs in page.findall('fontspec'):
        global_fontsizes[fs.get('id')] = int(fs.get('size'))
fontsizes = {}
for page in root.findall('page'):
    num = int(page.get('number'))
    fontsizes[num] = global_fontsizes

def line_cluster(elems):
    lines = []
    cur = []
    cur_top = None
    for e in elems:
        if cur_top is None or abs(e['top'] - cur_top) <= 4:
            cur.append(e)
            cur_top = e['top'] if cur_top is None else cur_top
        else:
            lines.append(cur)
            cur = [e]
            cur_top = e['top']
    if cur:
        lines.append(cur)
    return lines

out_pages = {}
for num, elems in pages.items():
    lines = line_cluster(elems)
    line_objs = []
    for ln in lines:
        ln_sorted = sorted(ln, key=lambda e: e['left'])
        text = ''
        last_right = None
        runs = []
        for e in ln_sorted:
            t = e['text']
            runs.append(dict(left=e['left'], width=e['width'], text=t, bold=e['bold'], italic=e['italic'], size=fontsizes[num].get(e['font'])))
        # weighted dominant style/size by text length
        def wmode(key):
            counts = {}
            for r in runs:
                k = r[key]
                counts[k] = counts.get(k, 0) + max(len(r['text'].strip()), 1)
            return max(counts.items(), key=lambda kv: kv[1])[0] if counts else None
        dom_bold = wmode('bold')
        dom_italic = wmode('italic')
        dom_size = wmode('size')
        full_text = ''.join(r['text'] for r in runs)
        min_left = min(r['left'] for r in runs)
        line_objs.append(dict(top=ln_sorted[0]['top'], left=min_left, text=full_text, bold=dom_bold,
                               italic=dom_italic, size=dom_size, runs=runs))
    out_pages[num] = line_objs

with open('scratch/lines.json', 'w') as f:
    json.dump(out_pages, f, indent=1)

print("done", len(out_pages))
