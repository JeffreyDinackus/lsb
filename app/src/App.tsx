import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { DocumentView } from './components/DocumentView'
import { TopBar } from './components/TopBar'
import { TableOfContents } from './components/TableOfContents'
import { headingIndex, sections } from './content'
import { ThemeProvider } from './theme'
import { LectionaryDisplayProvider } from './lectionary/LectionaryDisplayContext'
import { getSectionForTime } from './lectionary/timeOfDay'
import './styles.css'

const TOP_MARGIN = 72

function App() {
  const [view, setView] = useState<'document' | 'toc'>('document')
  const [barVisible, setBarVisible] = useState(true)
  const [currentHeadingIdx, setCurrentHeadingIdx] = useState(0)
  const scrollRestoreY = useRef(0)

  const updateCurrentHeading = useCallback(() => {
    let best = 0
    for (let i = 0; i < headingIndex.length; i++) {
      const el = document.getElementById(headingIndex[i].id)
      if (!el) continue
      const top = el.getBoundingClientRect().top
      if (top <= TOP_MARGIN) {
        best = i
      } else {
        break
      }
    }
    setCurrentHeadingIdx(best)
  }, [])

  // Jump straight to the office matching the device's current local time on first load,
  // before paint, so the page never visibly scrolls there.
  useLayoutEffect(() => {
    const targetId = getSectionForTime(new Date())
    const el = document.getElementById(`section-${targetId}`)
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 8
      window.scrollTo({ top: y })
    }
    updateCurrentHeading()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (view !== 'document') return
    let ticking = false
    const onScroll = () => {
      if (ticking) return
      ticking = true
      requestAnimationFrame(() => {
        updateCurrentHeading()
        ticking = false
      })
    }
    updateCurrentHeading()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [view, updateCurrentHeading])

  const handleContentClick = () => {
    setBarVisible((v) => !v)
  }

  const handleOpenToc = () => {
    scrollRestoreY.current = window.scrollY
    setView('toc')
  }

  const handleBack = () => {
    setView('document')
    requestAnimationFrame(() => {
      window.scrollTo({ top: scrollRestoreY.current })
      updateCurrentHeading()
    })
  }

  const handleSelectSection = (sectionId: string) => {
    setView('document')
    setBarVisible(true)
    requestAnimationFrame(() => {
      const el = document.getElementById(`section-${sectionId}`)
      if (el) {
        const y = el.getBoundingClientRect().top + window.scrollY - 8
        window.scrollTo({ top: y })
      }
      updateCurrentHeading()
    })
  }

  const current = headingIndex[currentHeadingIdx]
  const firstHeadingOfSection =
    current && headingIndex.find((h) => h.sectionId === current.sectionId)
  const isOwnSectionTitle = current && firstHeadingOfSection && firstHeadingOfSection.id === current.id

  return (
    <ThemeProvider>
      <LectionaryDisplayProvider>
        <div className="app-root">
          <TopBar
            visible={view === 'document' && barVisible}
            title={current ? current.sectionTitle : sections[0].title}
            subtitle={current && !isOwnSectionTitle ? current.text : undefined}
            onOpenToc={handleOpenToc}
          />

          <main className="content-click-area" onClick={handleContentClick}>
            <DocumentView />
          </main>

          {view === 'toc' && <TableOfContents onSelect={handleSelectSection} onBack={handleBack} />}
        </div>
      </LectionaryDisplayProvider>
    </ThemeProvider>
  )
}

export default App
