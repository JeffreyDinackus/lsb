import type { BibleData, BookData } from './bibleData'

export interface ReadingLine {
  text: string
  /** Short line of poetry (psalms, prophets) rather than a prose paragraph. */
  poetry: boolean
  /** Indented continuation line of poetry. */
  indent: boolean
}

export interface ResolvedReading {
  citation: string
  lines: ReadingLine[]
}

// Abbreviations used by the LSB lectionary whose prefix match would be ambiguous or wrong.
const BOOK_ALIASES: Record<string, string> = {
  ps: 'Psalm',
  pss: 'Psalm',
  psalms: 'Psalm',
  philem: 'Philemon',
  phlm: 'Philemon',
  song: 'Song Of Songs',
  songofsolomon: 'Song Of Songs',
  jude: 'Jude',
  judg: 'Judges',
  wis: 'Wisdom Of Solomon',
  wisdom: 'Wisdom Of Solomon',
  sir: 'Sirach',
  ecclus: 'Sirach',
  tob: 'Tobit',
  jdt: 'Judith',
  bar: 'Baruch',
  ezek: 'Ezekiel',
  eccl: 'Ecclesiastes',
  ecc: 'Ecclesiastes',
}

const normalize = (s: string) =>
  s
    .toLowerCase()
    .replace(/[.\s]/g, '')
    .replace(/kng$/, 'kings') // the lectionary table abbreviates "1 Kng", "2 Kng"

/** Resolves a full or abbreviated book name ("Gen.", "1 Cor.", "Song Of Songs") to the Bible's own book. */
export function findBookByName(bible: BibleData, name: string): BookData | null {
  const key = normalize(name)
  const alias = BOOK_ALIASES[key]
  const books: [string, BookData][] = Object.values(bible).flatMap((t) => Object.entries(t))
  if (alias) return books.find(([n]) => n === alias)?.[1] ?? null
  const exact = books.find(([n]) => normalize(n) === key)
  if (exact) return exact[1]
  return books.find(([n]) => normalize(n).startsWith(key))?.[1] ?? null
}

interface Range {
  startCh: number
  startV: number | null
  endCh: number
  endV: number | null // null = to end of chapter
}

/**
 * Parses the chapter/verse part of a citation into ranges. Handles both the LSB style
 * ("16:1–9, 15—17:22", "27:30–45; 28:10–22") and the plainer fallback style ("25 & 26", "1:1-2:11").
 * After a semicolon (or "&") a bare number is a chapter; after a comma it is a verse of the
 * current chapter.
 */
export function parseRanges(rest: string): Range[] {
  const s = rest.replace(/[–—]/g, '-').replace(/&/g, ';').replace(/(\d)[a-c]\b/g, '$1')
  const ranges: Range[] = []
  for (const group of s.split(';')) {
    let chapter: number | null = null // set once a chapter:verse has been seen in this group
    for (const raw of group.split(',')) {
      const part = raw.trim()
      if (!part) continue
      const [startRaw, endRaw] = part.split('-').map((p) => p.trim())

      let startCh: number
      let startV: number | null
      if (startRaw.includes(':')) {
        const [c, v] = startRaw.split(':').map(Number)
        startCh = c
        startV = v
        chapter = c
      } else if (chapter != null) {
        startCh = chapter
        startV = Number(startRaw)
      } else {
        startCh = Number(startRaw)
        startV = null
      }

      let endCh = startCh
      let endV: number | null = startV
      if (endRaw !== undefined) {
        if (endRaw === 'end') {
          endV = null
        } else if (endRaw.includes(':')) {
          const [c, v] = endRaw.split(':').map(Number)
          endCh = c
          endV = v
          chapter = c
        } else if (startV == null) {
          endCh = Number(endRaw) // chapter range, e.g. "25-26"
          endV = null
        } else {
          endV = Number(endRaw)
        }
      }
      if (Number.isNaN(startCh) || Number.isNaN(endCh)) continue
      ranges.push({ startCh, startV, endCh, endV })
    }
  }
  return ranges
}

const VERSE_NUM_RE = /^[⁰¹²³⁴⁵⁶⁷⁸⁹]+\s*/

function collectLines(book: BookData, ranges: Range[]): ReadingLine[] {
  const parts: string[] = []
  for (const r of ranges) {
    for (let ch = r.startCh; ch <= r.endCh; ch++) {
      const chapter = book[String(ch)]
      if (!chapter) continue
      const lastV = Math.max(...Object.keys(chapter).map(Number))
      const from = ch === r.startCh && r.startV != null ? r.startV : 1
      const to = ch === r.endCh && r.endV != null ? r.endV : lastV
      for (let v = from; v <= to; v++) {
        const text = chapter[String(v)]
        if (text) parts.push(text)
      }
    }
    parts.push('\n') // break between discontinuous ranges
  }
  return parts
    .join('')
    .split('\n')
    .filter((l) => l.trim())
    .map((l) => {
      const indent = /^\s{2,}/.test(l) || /^[⁰¹²³⁴⁵⁶⁷⁸⁹]+\s{2,}/.test(l)
      const text = l.trim()
      const bare = text.replace(VERSE_NUM_RE, '')
      return { text, indent, poetry: bare.length < 72 }
    })
}

/** Splits "Book Name" off the front of a citation like "Gen. 1:1–19", "1 Cor. 9:24", or "Philemon". */
function splitBookAndRest(citation: string): { book: string; rest: string | null } {
  // The chapter/verse part always starts with a digit, so anchoring the split there keeps
  // multi-word names ("Song Of Songs 4") whole.
  const m = citation.trim().match(/^((?:[1-4]\s*)?[A-Za-z][A-Za-z. ]*?)\.?(?:\s+(\d.*))?$/)
  if (!m) return { book: citation.trim(), rest: null }
  return { book: m[1].trim(), rest: m[2]?.trim() ?? null }
}

/** Resolves a lesson citation (e.g. "Gen. 16:1–9, 15—17:22", "John 7:53-8:30") to Bible text. */
export function resolveLessonReading(citation: string, bible: BibleData): ResolvedReading | null {
  const { book: bookName, rest } = splitBookAndRest(citation)
  const book = findBookByName(bible, bookName)
  if (!book) return null
  // In a one-chapter book (Prayer of Manasseh, Jude) bare numbers are verses: "Prayer Of Azariah 1-27".
  const singleChapter = Object.keys(book).length === 1
  const spec = rest && singleChapter && !rest.includes(':') ? `1:${rest}` : rest
  const ranges: Range[] = spec ? parseRanges(spec) : [{ startCh: 1, startV: null, endCh: 1, endV: null }]
  const lines = collectLines(book, ranges)
  return lines.length ? { citation, lines } : null
}

/** Resolves a comma-separated psalm list (e.g. "1, 2, 3, 4, 5" or "119:1-32") to one reading per psalm. */
export function resolvePsalmReadings(citationList: string, bible: BibleData): ResolvedReading[] {
  const book = findBookByName(bible, 'Psalm')
  if (!book) return []
  const readings: ResolvedReading[] = []
  for (const rawToken of citationList.split(',').map((t) => t.trim()).filter(Boolean)) {
    const token = rawToken.replace(/v$/, '') // trailing "v" = verse-numbering note in the source table
    const [range] = parseRanges(token)
    if (!range) continue
    const label = token.includes(':') ? `Psalm ${token.replace(/-/g, '–')}` : `Psalm ${range.startCh}`
    readings.push({ citation: label, lines: collectLines(book, [range]) })
  }
  return readings
}
