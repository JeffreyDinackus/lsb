import { sections } from '../content'
import { useTheme } from '../theme'
import { useLectionaryDisplay } from '../lectionary/LectionaryDisplayContext'

interface TocProps {
  onSelect: (sectionId: string) => void
  onBack: () => void
}

export function TableOfContents({ onSelect, onBack }: TocProps) {
  const { theme, toggleTheme } = useTheme()
  const { mode, toggleMode, dualMode, toggleDualMode } = useLectionaryDisplay()

  return (
    <div className="toc-screen">
      <div className="toc-topbar">
        <button type="button" className="toc-back" onClick={onBack} aria-label="Back">
          <span className="toc-back-arrow">‹</span>
          <span>Back</span>
        </button>
        <button
          type="button"
          className="toc-theme-toggle"
          onClick={toggleTheme}
          aria-label="Toggle light and dark mode"
          aria-pressed={theme === 'dark'}
        >
          <span className="toc-theme-icon">{theme === 'dark' ? '☾' : '☀'}</span>
          <span className="toc-theme-track">
            <span className="toc-theme-thumb" />
          </span>
        </button>
      </div>

      <div className="toc-body">
        <div className="toc-group-label toc-attribution">Anglican Church in North America 2019</div>
        <h1 className="toc-page-title">Book of Common Prayer</h1>
        <p className="toc-page-subtitle">Daily Office &amp; Family Prayer</p>

        <div className="toc-group-label">Daily Readings</div>
        <button
          type="button"
          className={'toc-setting-row' + (mode === 'citation' ? ' is-on' : '')}
          onClick={toggleMode}
          aria-label="Toggle between Bible text and lectionary citations"
          aria-pressed={mode === 'citation'}
        >
          <span className="toc-setting-text">
            <span className="toc-setting-title">{mode === 'text' ? 'Bible Text (RSVUE)' : 'Lectionary Numbers'}</span>
            <span className="toc-setting-sub">
              {mode === 'text'
                ? 'Showing the full Scripture text for each lesson'
                : 'Showing chapter & verse citations only'}
            </span>
          </span>
          <span className="toc-lect-track">
            <span className="toc-lect-thumb" />
          </span>
        </button>

        <button
          type="button"
          className={'toc-setting-row' + (dualMode ? ' is-on' : '')}
          onClick={toggleDualMode}
          aria-label="Toggle Dual Mode, showing both morning and evening scripture together"
          aria-pressed={dualMode}
        >
          <span className="toc-setting-text">
            <span className="toc-setting-title">Dual Mode</span>
            <span className="toc-setting-sub">
              {dualMode
                ? 'Showing both morning and evening scripture at each office'
                : 'Show both morning and evening scripture at each office'}
            </span>
          </span>
          <span className="toc-lect-track">
            <span className="toc-lect-thumb" />
          </span>
        </button>

        <div className="toc-group-label">Daily Office</div>
        <nav className="toc-list">
          {sections.map((section) => (
            <button
              type="button"
              className="toc-entry"
              key={section.id}
              onClick={() => onSelect(section.id)}
            >
              <span className="toc-entry-title">{section.title}</span>
              <span className="toc-entry-leader" aria-hidden="true" />
              <span className="toc-entry-page">{section.printedPage}</span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  )
}
