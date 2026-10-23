import { findBook, type BibleData } from './bibleData'

export interface ResolvedReading {
  citation: string
  paragraphs: string[]
}

function lastVerseNumber(chapter: Record<string, unknown>): number {
  return Math.max(...Object.keys(chapter).map(Number))
}

/** Concatenates verse text for a book across [startCh:startV, endCh:endV] into paragraphs split on embedded newlines. */
function collectText(
  book: Record<string, Record<string, string>>,
  startCh: number,
  startV: number | null,
  endCh: number,
  endV: number | 'end' | null,
): string[] {
  const parts: string[] = []
  for (let ch = startCh; ch <= endCh; ch++) {
    const chapter = book[String(ch)]
    if (!chapter) continue
    const from = ch === startCh && startV != null ? startV : 1
    const lastV = lastVerseNumber(chapter)
    const to = ch === endCh && endV != null ? (endV === 'end' ? lastV : endV) : lastV
    for (let v = from; v <= to; v++) {
      const text = chapter[String(v)]
      if (text) parts.push(text)
    }
  }
  const joined = parts.join('')
  return joined
    .split('\n')
    .map((p) => p.trim())
    .filter(Boolean)
}

interface RangeSpec {
  chapter: number
  verseStart: number | null
  endChapter: number
  verseEnd: number | 'end' | null
}

function parseRangeSpec(spec: string): RangeSpec | null {
  const s = spec.trim().replace(/v$/, '') // trailing "v" = Coverdale-Psalter verse-numbering note; irrelevant for RSV-UE lookup
  let m: RegExpMatchArray | null

  // chapter:verse-chapter:verse  (e.g. "1:1-2:11", "21:15-22:5")
  m = s.match(/^(\d+):(\d+)-(\d+):(\d+)$/)
  if (m) return { chapter: +m[1], verseStart: +m[2], endChapter: +m[3], verseEnd: +m[4] }

  // chapter:verse-end
  m = s.match(/^(\d+):(\d+)-end$/)
  if (m) return { chapter: +m[1], verseStart: +m[2], endChapter: +m[1], verseEnd: 'end' }

  // chapter:verse-verse
  m = s.match(/^(\d+):(\d+)-(\d+)$/)
  if (m) return { chapter: +m[1], verseStart: +m[2], endChapter: +m[1], verseEnd: +m[3] }

  // chapter:verse
  m = s.match(/^(\d+):(\d+)$/)
  if (m) return { chapter: +m[1], verseStart: +m[2], endChapter: +m[1], verseEnd: +m[2] }

  // bare chapter number (whole chapter)
  m = s.match(/^(\d+)$/)
  if (m) return { chapter: +m[1], verseStart: null, endChapter: +m[1], verseEnd: null }

  return null
}

/** Splits "Book Name" off the front of a citation like "Genesis 1" or "Philemon" (no chapter) or "1 Corinthians 9:24-27". */
function splitBookAndRest(citation: string): { book: string; rest: string | null } {
  // The "rest" (chapter/verse reference) always starts with a digit, so anchoring the
  // split there avoids a non-greedy book match cutting multi-word names short, e.g.
  // "Song Of Songs 4" mis-splitting into book="Song", rest="Of Songs 4".
  const m = citation.trim().match(/^((?:[1-4]\s+)?[A-Za-z][A-Za-z ]*?)(?:\s+(\d.*))?$/)
  if (!m) return { book: citation.trim(), rest: null }
  return { book: m[1].trim(), rest: m[2]?.trim() ?? null }
}

/** Resolves a single lesson citation (e.g. "Genesis 1", "John 7:53-8:30", "Job 25 & 26") to Bible text. */
export function resolveLessonReading(citation: string, bible: BibleData): ResolvedReading | null {
  const { book: bookName, rest } = splitBookAndRest(citation)
  const book = findBook(bible, bookName)
  if (!book) return null

  const paragraphs: string[] = []
  if (!rest) {
    // whole (single-chapter) book, e.g. "Philemon"
    paragraphs.push(...collectText(book, 1, null, 1, null))
  } else {
    for (const part of rest.split('&').map((p) => p.trim())) {
      const range = parseRangeSpec(part)
      if (!range) continue
      paragraphs.push(...collectText(book, range.chapter, range.verseStart, range.endChapter, range.verseEnd))
    }
  }

  return { citation, paragraphs }
}

/** Resolves a comma-separated psalm citation list (e.g. "1, 2, 3, 4, 5" or "119:1-32") to one reading per psalm. */
export function resolvePsalmReadings(citationList: string, bible: BibleData): ResolvedReading[] {
  const book = findBook(bible, 'Psalm')
  if (!book) return []

  const readings: ResolvedReading[] = []
  for (const rawToken of citationList.split(',').map((t) => t.trim()).filter(Boolean)) {
    const token = rawToken.replace(/v$/, '')
    const range = parseRangeSpec(token)
    if (!range) continue
    const paragraphs = collectText(book, range.chapter, range.verseStart, range.endChapter, range.verseEnd)
    const label = range.verseStart != null ? `Psalm ${range.chapter}:${token.split(':')[1]}` : `Psalm ${range.chapter}`
    readings.push({ citation: label, paragraphs })
  }
  return readings
}
