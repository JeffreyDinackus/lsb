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

const DAY_MS = 24 * 60 * 60 * 1000

/** Whole days from a to b, ignoring time of day and DST shifts. */
function daysBetween(a: Date, b: Date): number {
  const utcA = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate())
  const utcB = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate())
  return Math.round((utcB - utcA) / DAY_MS)
}

export interface ChurchYearDay {
  /** Lectionary key, e.g. "lent2:3"; null once the calendar portion (after Holy Trinity) applies. */
  key: string | null
  /** Human label, e.g. "Wednesday after Lent 2". */
  label: string | null
}

const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

const WEEK_NAMES: Record<string, string> = {
  holyweek: 'Palm Sunday',
  easter1: 'Easter',
  pentecost: 'Pentecost',
  trinity: 'Holy Trinity',
}

function weekName(week: string): string {
  if (WEEK_NAMES[week]) return WEEK_NAMES[week]
  const m = week.match(/^(lent|easter)(\d)$/)
  if (m) return `${m[1] === 'lent' ? 'Lent' : 'Easter'} ${m[2]}`
  return week
}

function label(week: string, dow: number): string {
  if (week === 'ashwed') return dow === 3 ? 'Ash Wednesday' : `${WEEKDAYS[dow]} after Ash Wednesday`
  if (week === 'holyweek') {
    return ['Palm Sunday', 'Monday of Holy Week', 'Tuesday of Holy Week', 'Wednesday of Holy Week',
      'Maundy Thursday', 'Good Friday', 'Holy Saturday'][dow]
  }
  if (week === 'easter1' && dow === 0) return 'Easter Day'
  if (dow === 0) return weekName(week)
  return `${WEEKDAYS[dow]} after ${weekName(week)}`
}

/**
 * Locates a date within the movable portion of the LSB Daily Lectionary, which "begins with Ash
 * Wednesday" and follows the Church Year through Holy Trinity; after that the calendar is followed.
 */
export function getChurchYearDay(date: Date): ChurchYearDay {
  const easter = getEasterDate(date.getFullYear())
  const offset = daysBetween(easter, date) // negative before Easter
  const dow = date.getDay()

  let week: string | null = null
  if (offset >= -46 && offset <= -43) week = 'ashwed'
  else if (offset >= -42 && offset <= -8) week = `lent${Math.floor((offset + 42) / 7) + 1}`
  else if (offset >= -7 && offset <= -1) week = 'holyweek'
  else if (offset >= 0 && offset <= 48) week = `easter${Math.floor(offset / 7) + 1}`
  else if (offset >= 49 && offset <= 55) week = 'pentecost'
  else if (offset === 56) week = 'trinity'

  if (!week) return { key: null, label: null }
  return { key: `${week}:${dow}`, label: label(week, dow) }
}
