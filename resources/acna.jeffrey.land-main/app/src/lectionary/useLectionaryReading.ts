import { useEffect, useMemo, useState } from 'react'
import { useLectionaryDisplay } from './LectionaryDisplayContext'
import { getDailyReading } from './dates'
import { loadBible } from './bibleData'
import { resolveLessonReading, resolvePsalmReadings, type ResolvedReading } from './reference'

export type LectionaryOffice = 'morning' | 'evening'
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
    if (role === 'psalm') return office === 'morning' ? daily.morningPsalms : daily.eveningPsalms
    return office === 'morning' ? daily.morningLesson : daily.eveningLesson
  }, [office, role])

  const [state, setState] = useState<LectionaryReadingState>({
    citation,
    mode,
    status: 'ready',
    readings: [],
  })

  useEffect(() => {
    if (mode === 'citation' || !citation) {
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
            : [resolveLessonReading(citation, bible)].filter((r): r is ResolvedReading => r !== null)
        setState({ citation, mode, status: 'ready', readings })
      })
      .catch(() => {
        if (!cancelled) setState({ citation, mode, status: 'error', readings: [] })
      })

    return () => {
      cancelled = true
    }
  }, [mode, citation, role])

  return state
}
