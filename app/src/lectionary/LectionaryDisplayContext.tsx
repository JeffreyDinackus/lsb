import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export type LectionaryDisplayMode = 'text' | 'citation'

const STORAGE_KEY = 'lutheran-lectionary-display-mode'
const DUAL_MODE_STORAGE_KEY = 'lutheran-lectionary-dual-mode'

const LectionaryDisplayContext = createContext<{
  mode: LectionaryDisplayMode
  toggleMode: () => void
  dualMode: boolean
  toggleDualMode: () => void
}>({
  mode: 'text',
  toggleMode: () => {},
  dualMode: false,
  toggleDualMode: () => {},
})

export function LectionaryDisplayProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<LectionaryDisplayMode>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === 'citation' ? 'citation' : 'text'
  })
  const [dualMode, setDualMode] = useState<boolean>(() => {
    return localStorage.getItem(DUAL_MODE_STORAGE_KEY) === 'true'
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, mode)
  }, [mode])

  useEffect(() => {
    localStorage.setItem(DUAL_MODE_STORAGE_KEY, String(dualMode))
  }, [dualMode])

  const toggleMode = () => setMode((m) => (m === 'text' ? 'citation' : 'text'))
  const toggleDualMode = () => setDualMode((d) => !d)

  return (
    <LectionaryDisplayContext.Provider value={{ mode, toggleMode, dualMode, toggleDualMode }}>
      {children}
    </LectionaryDisplayContext.Provider>
  )
}

export function useLectionaryDisplay() {
  return useContext(LectionaryDisplayContext)
}
