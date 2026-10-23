export type TimeOfDaySection = 'matins' | 'daily-prayer-noon' | 'vespers' | 'compline'

/**
 * Maps the device's local clock time to the office that would normally be prayed then:
 *   Matins 4:00am-10:45am, Noon 10:46am-3:15pm, Vespers 3:16pm-9:45pm, Compline 9:46pm-3:59am.
 * Uses Date's local getHours/getMinutes, so this follows the device's own timezone with no
 * explicit timezone handling.
 */
export function getSectionForTime(date: Date): TimeOfDaySection {
  const minutes = date.getHours() * 60 + date.getMinutes()
  if (minutes >= 4 * 60 && minutes <= 10 * 60 + 45) return 'matins'
  if (minutes >= 10 * 60 + 46 && minutes <= 15 * 60 + 15) return 'daily-prayer-noon'
  if (minutes >= 15 * 60 + 16 && minutes <= 21 * 60 + 45) return 'vespers'
  return 'compline'
}
