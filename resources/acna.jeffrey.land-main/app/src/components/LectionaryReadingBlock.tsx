import {
  useLectionaryReading,
  type LectionaryOffice,
  type LectionaryReadingState,
  type LectionaryRole,
} from '../lectionary/useLectionaryReading'
import { useLectionaryDisplay } from '../lectionary/LectionaryDisplayContext'

function SingleReading({ state, role }: { state: LectionaryReadingState; role: LectionaryRole }) {
  const { citation, mode, status, readings } = state

  if (!citation) return null

  if (mode === 'citation') {
    return (
      <p className="lect-citation-only">
        <span className="lect-citation-only-label">{role === 'psalm' ? 'Psalm(s)' : 'Reading'}</span>
        <span className="lect-citation-only-text">{citation}</span>
      </p>
    )
  }

  if (status === 'loading') {
    return <p className="lect-loading">Loading {citation}&hellip;</p>
  }

  if (status === 'error' || readings.length === 0) {
    return (
      <p className="lect-citation-only">
        <span className="lect-citation-only-label">{role === 'psalm' ? 'Psalm(s)' : 'Reading'}</span>
        <span className="lect-citation-only-text">{citation}</span>
      </p>
    )
  }

  return (
    <div className="lect-reading">
      {readings.map((r, i) => (
        <div className="b-verse-block lect-passage" key={i}>
          <cite className="lect-passage-citation">{r.citation}</cite>
          {r.paragraphs.map((p, pi) => (
            <p className="b-paragraph lect-paragraph" key={pi}>
              {p}
            </p>
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

  if (!dualMode) {
    return <SingleReading state={office === 'morning' ? morning : evening} role={role} />
  }

  // Dual Mode: morning always shown first, regardless of which office section this block sits in.
  return (
    <div className="lect-dual">
      <p className="b-small-heading">Morning</p>
      <SingleReading state={morning} role={role} />
      <p className="b-small-heading">Evening</p>
      <SingleReading state={evening} role={role} />
    </div>
  )
}
