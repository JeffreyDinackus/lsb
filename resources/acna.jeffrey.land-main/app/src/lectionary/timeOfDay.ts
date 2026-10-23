export type TimeOfDaySection = 'morning-prayer' | 'midday-prayer' | 'evening-prayer' | 'compline'

/**
 * Maps the device's local clock time to the office that would normally be prayed then:
 *   Morning 4:00am-10:45am, Midday 10:46am-3:15pm, Evening 3:16pm-9:45pm, Compline 9:46pm-3:59am.
 * Uses Date's local getHours/getMinutes, so this follows the device's own timezone with no
 * explicit timezone handling.
 */
export function getSectionForTime(date: Date): TimeOfDaySection {
  const minutes = date.getHours() * 60 + date.getMinutes()
  if (minutes >= 4 * 60 && minutes <= 10 * 60 + 45) return 'morning-prayer'
  if (minutes >= 10 * 60 + 46 && minutes <= 15 * 60 + 15) return 'midday-prayer'
  if (minutes >= 15 * 60 + 16 && minutes <= 21 * 60 + 45) return 'evening-prayer'
  return 'compline'
}
