import { useEffect, useMemo, useState } from 'react'
import { useLectionaryDisplay } from './LectionaryDisplayContext'
import { getDailyReading } from './daily'
import { loadBible } from './bibleData'
import { resolveLessonReading, resolvePsalmReadings, type ResolvedReading } from './reference'

export type LectionaryOffice = 'morning' | 'midday' | 'evening'
export type LectionaryRole = 'psalm' | 'lesson'

export interface LectionaryReadingState {
  citation: string | null
  mode: 'text' | 'citation'
  status: 'loading' | 'ready' | 'error'
  readings: ResolvedReading[]
}

export function useLectionaryReading(office: LectionaryOffice, role: LectionaryRole): LectionaryReadingState {
  const { mode } = useLectionaryDisplay()

  const citation = useMemo(() => {
    const daily = getDailyReading(new Date())
    if (role === 'psalm') return office === 'evening' ? daily.eveningPsalms : daily.morningPsalms
    if (office === 'midday') return daily.middayLesson
    return office === 'morning' ? daily.morningLesson : daily.eveningLesson
  }, [office, role])

  // readings from the Book of Concord have no Bible text to load
  const citationOnly = office === 'midday' && getDailyReading(new Date()).middayKind === 'confessions'

  const [state, setState] = useState<LectionaryReadingState>({
    citation,
    mode,
    status: 'ready',
    readings: [],
  })

  useEffect(() => {
    if (mode === 'citation' || citationOnly || !citation) {
      setState({ citation, mode, status: 'ready', readings: [] })
      return
    }

    let cancelled = false
    setState((s) => ({ ...s, citation, mode, status: 'loading' }))

    loadBible()
      .then((bible) => {
        if (cancelled) return
        const readings =
          role === 'psalm'
            ? resolvePsalmReadings(citation, bible)
            : citation
                .split(/\s+and\s+/) // e.g. "Daniel 10:1—12:13 and Isaiah 48:1–22"
                .map((c) => resolveLessonReading(c, bible))
                .filter((r): r is ResolvedReading => r !== null)
        setState({ citation, mode, status: 'ready', readings })
      })
      .catch(() => {
        if (!cancelled) setState({ citation, mode, status: 'error', readings: [] })
      })

    return () => {
      cancelled = true
    }
  }, [mode, citation, role, citationOnly])

  return state
}
