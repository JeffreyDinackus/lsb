import { Fragment } from 'react'
import {
  useLectionaryReading,
  type LectionaryOffice,
  type LectionaryReadingState,
  type LectionaryRole,
} from '../lectionary/useLectionaryReading'
import { useLectionaryDisplay } from '../lectionary/LectionaryDisplayContext'
import { getDailyReading } from '../lectionary/daily'
import type { ReadingLine } from '../lectionary/reference'

const CONFESSION_NAMES: [RegExp, string][] = [
  [/^AC\b/, 'Augsburg Confession'],
  [/^Ap\./, 'Apology of the Augsburg Confession'],
  [/^SA\b/, 'Smalcald Articles'],
  [/^Tr\./, 'Treatise on the Power and Primacy of the Pope'],
  [/^FC SD\b/, 'Formula of Concord, Solid Declaration'],
  [/^Cat\. Test\./, 'Catalog of Testimonies'],
]

/** Expands the table's abbreviations for Book of Concord readings, e.g. "SA 3/1-3/2". */
function expandConfession(citation: string): string {
  for (const [re, name] of CONFESSION_NAMES) {
    if (re.test(citation)) return citation.replace(re, name)
  }
  return citation
}

function roleLabel(office: LectionaryOffice, role: LectionaryRole): string {
  if (role === 'psalm') return 'Psalmody'
  if (office === 'midday') return 'Additional Reading'
  return office === 'morning' ? 'New Testament Reading' : 'Old Testament Reading'
}

// RSV-UE text carries its verse numbers as Unicode superscripts; set them off typographically.
const VNUM_RE = /([⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g
const SUPERSCRIPT_DIGITS = '⁰¹²³⁴⁵⁶⁷⁸⁹'

function VerseText({ text }: { text: string }) {
  return (
    <>
      {text.split(VNUM_RE).map((part, i) =>
        i % 2 === 1 ? (
          <sup className="lect-vnum" key={i}>
            {[...part].map((c) => SUPERSCRIPT_DIGITS.indexOf(c)).join('')}
          </sup>
        ) : (
          <Fragment key={i}>{part}</Fragment>
        ),
      )}
    </>
  )
}

function Line({ line }: { line: ReadingLine }) {
  const cls = line.poetry ? 'lect-line is-poetry' + (line.indent ? ' is-indent' : '') : 'b-paragraph lect-paragraph'
  return (
    <p className={cls}>
      <VerseText text={line.text} />
    </p>
  )
}

function CitationOnly({ label, citation }: { label: string; citation: string }) {
  return (
    <p className="lect-citation-only">
      <span className="lect-citation-only-label">{label}</span>
      <span className="lect-citation-only-text">{citation}</span>
    </p>
  )
}

function SingleReading({
  state,
  office,
  role,
}: {
  state: LectionaryReadingState
  office: LectionaryOffice
  role: LectionaryRole
}) {
  const { citation, mode, status, readings } = state
  const label = roleLabel(office, role)

  if (!citation) return null
  if (office === 'midday' && getDailyReading(new Date()).middayKind === 'confessions') {
    return <CitationOnly label="From the Book of Concord" citation={expandConfession(citation)} />
  }
  if (mode === 'citation' || status === 'error' || (status === 'ready' && readings.length === 0)) {
    return <CitationOnly label={label} citation={citation} />
  }
  if (status === 'loading') {
    return <p className="lect-loading">Loading {citation}&hellip;</p>
  }

  return (
    <div className="lect-reading">
      {readings.map((r, i) => (
        <div className="lect-passage" key={i}>
          <cite className="lect-passage-citation">
            {role === 'lesson' && <span className="lect-passage-role">{label} · </span>}
            {r.citation}
          </cite>
          {r.lines.map((line, li) => (
            <Line line={line} key={li} />
          ))}
        </div>
      ))}
    </div>
  )
}

export function LectionaryReadingBlock({ office, role }: { office: LectionaryOffice; role: LectionaryRole }) {
  const { dualMode } = useLectionaryDisplay()
  // Always resolve both offices (rules of hooks forbid skipping one when dualMode toggles).
  const morning = useLectionaryReading('morning', role)
  const evening = useLectionaryReading('evening', role)
  const midday = useLectionaryReading('midday', role)

  if (office === 'midday') return <SingleReading state={midday} office="midday" role={role} />

  if (!dualMode) {
    return <SingleReading state={office === 'morning' ? morning : evening} office={office} role={role} />
  }

  // Dual Mode: morning always shown first, regardless of which office section this block sits in.
  return (
    <div className="lect-dual">
      <p className="b-small-heading">Morning</p>
      <SingleReading state={morning} office="morning" role={role} />
      <p className="b-small-heading">Evening</p>
      <SingleReading state={evening} office="evening" role={role} />
    </div>
  )
}
