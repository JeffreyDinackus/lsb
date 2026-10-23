export type ChapterData = Record<string, string> // verse number -> verse text
export type BookData = Record<string, ChapterData> // chapter number -> chapter
export type TestamentData = Record<string, BookData> // book name -> book
export type BibleData = Record<string, TestamentData> // "Old Testament" | "New Testament" | "Apocrypha" -> book

let bibleCache: Promise<BibleData> | null = null

/** Lazily fetches the (large) RSV-UE Bible JSON exactly once, cached for the app's lifetime. */
export function loadBible(): Promise<BibleData> {
  if (!bibleCache) {
    bibleCache = fetch('/bibles/rsvue-bible.json').then((res) => {
      if (!res.ok) throw new Error(`Failed to load Bible text (${res.status})`)
      return res.json() as Promise<BibleData>
    })
  }
  return bibleCache
}

export function findBook(bible: BibleData, bookName: string): BookData | null {
  for (const testament of Object.values(bible)) {
    if (testament[bookName]) return testament[bookName]
  }
  return null
}
