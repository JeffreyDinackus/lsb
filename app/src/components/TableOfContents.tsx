import { sections } from '../content'
import { useTheme } from '../theme'
import { useLectionaryDisplay } from '../lectionary/LectionaryDisplayContext'
import { getDailyReading } from '../lectionary/daily'

interface TocProps {
  onSelect: (sectionId: string) => void
  onBack: () => void
}

export function TableOfContents({ onSelect, onBack }: TocProps) {
  const { theme, toggleTheme } = useTheme()
  const { mode, toggleMode, dualMode, toggleDualMode } = useLectionaryDisplay()
  const today = getDailyReading(new Date())

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
        <div className="toc-ornament" aria-hidden="true">✠</div>
        <h1 className="toc-page-title">Lutheran Prayer Book</h1>
        <p className="toc-page-subtitle">The Daily Office &amp; Daily Prayer</p>

        <div className="toc-group-label">Today</div>
        <div className="toc-today">
          <p className="toc-today-day">{today.dayLabel}</p>
          <dl className="toc-today-list">
            {today.morningLesson && (
              <>
                <dt>Morning</dt>
                <dd>{today.morningLesson}</dd>
              </>
            )}
            {today.middayLesson && (
              <>
                <dt>Midday</dt>
                <dd>{today.middayLesson}</dd>
              </>
            )}
            {today.eveningLesson && (
              <>
                <dt>Evening</dt>
                <dd>{today.eveningLesson}</dd>
              </>
            )}
            <dt>Psalms</dt>
            <dd>
              {today.morningPsalms} <span className="toc-today-sep">(morning)</span> · {today.eveningPsalms}{' '}
              <span className="toc-today-sep">(evening)</span>
            </dd>
          </dl>
        </div>

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

        <div className="toc-group-label">Contents</div>
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

        <footer className="toc-footer">
          <a className="toc-hub-link" href="https://prayernetwork.christ.software">
            <span className="toc-hub-title">More prayer books</span>
            <span className="toc-hub-url">prayernetwork.christ.software ›</span>
          </a>
        </footer>
      </div>
    </div>
  )
}
