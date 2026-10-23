"""Extracts the LSB Daily Lectionary table into app/src/data/lsbLectionary.json.

Usage: python build_lectionary.py <LSB-Daily-Lectionary.pdf>   (needs PyMuPDF: pip install pymupdf)

Source: "Daily Lectionary -- from rough draft of Lutheran Service Book with Additional Readings
from the Apocrypha, the Lutheran Confessions, and the Catalog of Testimonies". Each row is
Day/Date, Old Testament, New Testament, Additional Reading, laid out as columns separated by runs
of spaces.

The church-year portion (Ash Wednesday -> Holy Trinity) is keyed "<week>:<weekday>", where
weekday is 0=Sunday..6=Saturday and week is "ashwed", "lent1".."lent5", "holyweek",
"easter1".."easter7", "pentecost", "trinity". The calendar portion ("The Time of the Church"
and "The Time of Christmas") is keyed "MM-DD".
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz

WEEKDAYS = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
MONTHS = {m: i + 1 for i, m in enumerate(
    ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}

# Additional readings drawn from the Book of Concord rather than Scripture.
CONFESSIONS_RE = re.compile(r'^(AC\b|Ap\.|SA\b|Tr\.|FC\b|Cat\. Test\.|Apocr\.|Triglotta|Pref\. to Book of Concord)')

# Book names in the table that the Bible JSON spells differently.
ADDITIONAL_FIXES = [
    (re.compile(r'^Prayer of Mann?asseh'), 'Prayer Of Manasseh'),
    (re.compile(r'^Song of the 3 Child\.'), 'Prayer Of Azariah'),
    (re.compile(r'^Baruch 6:'), 'Letter Of Jeremiah 1:'),  # the RSV-UE prints Baruch 6 as its own book
]


def weekday_of(label: str):
    key = label.strip().lower()[:3]
    return WEEKDAYS.get(key)


def church_year_key(label: str, week: str | None):
    """Returns (week, key) for a church-year label, carrying the current week for bare weekdays."""
    s = label.strip()
    if s == 'Ash Wednesday':
        return 'ashwed', 'ashwed:3'
    m = re.match(r'^(Lent|Easter) (\d)$', s)
    if m:
        w = f'{m.group(1).lower()}{m.group(2)}'
        return w, f'{w}:0'
    holy_week = {'Palm Sunday': 0, 'Maundy Thursday': 4, 'Good Friday': 5, 'Holy Saturday': 6}
    if s in holy_week:
        return 'holyweek', f'holyweek:{holy_week[s]}'
    m = re.match(r'^(Easter|Pentecost) (\w+)\.$', s)
    if m:
        w = 'easter1' if m.group(1) == 'Easter' else 'pentecost'
        return w, f'{w}:{weekday_of(m.group(2))}'
    if s.startswith('Holy Trinity'):
        return 'trinity', 'trinity:0'
    if s == 'Ascension Day':
        return week, f'{week}:4'
    dow = weekday_of(s)
    if dow is not None and week:
        return week, f'{week}:{dow}'
    return week, None


def date_key(label: str):
    m = re.match(r'^(\d{1,2}) ([A-Za-z]{3})', label.strip())
    if not m or m.group(2).lower() not in MONTHS:
        return None
    return f'{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}'


def clean_additional(text: str):
    text = text.strip()
    kind = 'confessions' if CONFESSIONS_RE.match(text) else 'scripture'
    if kind == 'scripture':
        for pattern, replacement in ADDITIONAL_FIXES:
            text = pattern.sub(replacement, text)
        # "Lam 4:1–22 (Psalm 31)" -> two readings; "(Psalm 118)" alone -> "Psalm 118"
        text = re.sub(r'\s*\((Psalm [^)]+)\)', r' and \1', text).strip()
        text = re.sub(r'^and ', '', text)
    return text, kind


def main(pdf_path: str):
    doc = fitz.open(pdf_path)
    text = '\n'.join(page.get_text() for page in doc)

    church_year: dict = {}
    by_date: dict = {}
    week = None

    for line in text.split('\n'):
        cols = [c.strip() for c in re.split(r'\s{2,}', line.strip()) if c.strip()]
        if len(cols) == 5:  # an OT citation wrapped onto two columns ("Ex 38:21—39:8,", "22–23, 27–31")
            cols = [cols[0], f'{cols[1]} {cols[2]}', cols[3], cols[4]]
        if len(cols) != 4 or cols[0].startswith('Day/Date'):
            continue
        label, ot, nt, additional = cols
        additional, kind = clean_additional(additional)
        entry = {'ot': ot, 'nt': nt, 'additional': additional, 'additionalKind': kind}

        dk = date_key(label)
        if dk:
            by_date[dk] = entry
            continue
        week, key = church_year_key(label, week)
        if key is None:
            print(f'skipped row: {cols}', file=sys.stderr)
            continue
        church_year[key] = entry

    out = Path(__file__).resolve().parent.parent / 'app/src/data/lsbLectionary.json'
    out.write_text(json.dumps({'churchYear': church_year, 'byDate': by_date}, ensure_ascii=False, indent=1),
                   encoding='utf-8')
    print(f'church-year entries: {len(church_year)}, calendar entries: {len(by_date)} -> {out}')


if __name__ == '__main__':
    main(sys.argv[1])
