import { lectionary, type MovableEntry } from './data'

/** Anonymous Gregorian algorithm (Meeus/Jones/Butcher) for the date of Easter Day. */
export function getEasterDate(year: number): Date {
  const a = year % 19
  const b = Math.floor(year / 100)
  const c = year % 100
  const d = Math.floor(b / 4)
  const e = b % 4
  const f = Math.floor((b + 8) / 25)
  const g = Math.floor((b - f + 1) / 3)
  const h = (19 * a + b - d - g + 15) % 30
  const i = Math.floor(c / 4)
  const k = c % 4
  const l = (32 + 2 * e + 2 * i - h - k) % 7
  const m = Math.floor((a + 11 * h + 22 * l) / 451)
  const month = Math.floor((h + l - 7 * m + 114) / 31) // 3 = March, 4 = April
  const day = ((h + l - 7 * m + 114) % 31) + 1
  return new Date(year, month - 1, day)
}

function addDays(date: Date, days: number): Date {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}

function sameCalendarDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

type LectionaryShape = typeof lectionary
export type MovableKey = keyof LectionaryShape['movable']

const MOVABLE_OFFSETS: [MovableKey, number][] = [
  ['ashWednesday', -46],
  ['maundyThursday', -3],
  ['goodFriday', -2],
  ['holySaturday', -1],
  ['easterDay', 0],
  ['ascensionDay', 39],
  ['pentecost', 49],
]

/** Returns the movable-feast key that overrides the fixed calendar-date reading for this date, if any. */
export function getMovableKeyForDate(date: Date): MovableKey | null {
  const easter = getEasterDate(date.getFullYear())
  for (const [key, offset] of MOVABLE_OFFSETS) {
    if (sameCalendarDay(date, addDays(easter, offset))) return key
  }
  return null
}

/** Per user instruction: calendar year even => lectionary Year I, odd => Year II. */
export function getLectionaryYear(date: Date): 'yearI' | 'yearII' {
  return date.getFullYear() % 2 === 0 ? 'yearI' : 'yearII'
}

function pad2(n: number): string {
  return n < 10 ? `0${n}` : `${n}`
}

export interface DailyReading {
  morningPsalms: string
  eveningPsalms: string
  morningLesson: string | null
  eveningLesson: string | null
}

export function getDailyReading(date: Date): DailyReading {
  const day = date.getDate()
  const psalms = lectionary.psalms30Day[String(day)] ?? { morning: '', evening: '' }

  const movableKey = getMovableKeyForDate(date)
  if (movableKey) {
    // Movable feasts (unlike the regular calendar table) appoint their own complete
    // OT+NT pair for morning and a separate complete pair for evening -- not one pair
    // split across offices. We only have a single reading slot per office, so we show
    // each office's own first lesson rather than crossing lesson1/lesson2 between them.
    const entry: MovableEntry = lectionary.movable[movableKey]
    return {
      morningPsalms: entry.morningPsalm,
      eveningPsalms: entry.eveningPsalm,
      morningLesson: entry.morningLesson1,
      eveningLesson: entry.eveningLesson1,
    }
  }

  const dateKey = `${pad2(date.getMonth() + 1)}-${pad2(day)}`
  const dateEntry = lectionary.byDate[dateKey]
  const yearKey = getLectionaryYear(date)
  const pair = dateEntry?.[yearKey]

  return {
    morningPsalms: psalms.morning,
    eveningPsalms: psalms.evening,
    morningLesson: pair?.lesson1 ?? null,
    eveningLesson: pair?.lesson2 ?? null,
  }
}
