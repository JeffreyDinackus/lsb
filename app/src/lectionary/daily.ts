import { lsbLectionary, psalter30Day } from './data'
import { getChurchYearDay } from './churchYear'

function pad2(n: number): string {
  return n < 10 ? `0${n}` : `${n}`
}

export interface DailyReading {
  /** e.g. "Wednesday after Lent 2", or the calendar date once the calendar portion applies. */
  dayLabel: string
  morningPsalms: string
  eveningPsalms: string
  /** "NT at Morning Prayer, Additional Reading at Mid-day Prayer, and OT at Evening Prayer." */
  morningLesson: string | null
  middayLesson: string | null
  middayKind: 'scripture' | 'confessions'
  eveningLesson: string | null
}

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
  'October', 'November', 'December']
const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

export function getDailyReading(date: Date): DailyReading {
  const day = date.getDate()
  const churchDay = getChurchYearDay(date)
  const dayLabel = churchDay.label ?? `${WEEKDAYS[date.getDay()]}, ${MONTHS[date.getMonth()]} ${day}`
  const psalms = psalter30Day[String(day)] ?? { morning: '', evening: '' }

  // The lectionary follows the Church Year from Ash Wednesday through Holy Trinity, and the
  // calendar from then until Lent; between them the two tables cover every day of the year.
  const entry = churchDay.key
    ? lsbLectionary.churchYear[churchDay.key]
    : lsbLectionary.byDate[`${pad2(date.getMonth() + 1)}-${pad2(day)}`]

  return {
    dayLabel,
    morningPsalms: psalms.morning,
    eveningPsalms: psalms.evening,
    morningLesson: entry?.nt ?? null,
    middayLesson: entry?.additional ?? null,
    middayKind: entry?.additionalKind ?? 'scripture',
    eveningLesson: entry?.ot ?? null,
  }
}
