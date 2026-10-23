import lsbRaw from '../data/lsbLectionary.json'
import psalterRaw from '../data/psalter30Day.json'

/** One day of the LSB Daily Lectionary. */
export interface LsbEntry {
  ot: string
  nt: string
  /** Additional reading from the Apocrypha, the Lutheran Confessions, or the Catalog of Testimonies. */
  additional: string
  additionalKind: 'scripture' | 'confessions'
}

export interface LsbLectionary {
  /** Ash Wednesday through Holy Trinity, keyed "<week>:<weekday>" (see churchYear.ts). */
  churchYear: Record<string, LsbEntry>
  /** After Holy Trinity until Lent, keyed "MM-DD". */
  byDate: Record<string, LsbEntry>
}

export const lsbLectionary = lsbRaw as unknown as LsbLectionary

/**
 * Psalms by day of the month, morning and evening (the 30-day psalter carried over from the ACNA
 * project). TODO: replace with the LSB Table of Psalms for Daily Prayer (p. 304) when available.
 */
export const psalter30Day = (psalterRaw as unknown as {
  psalms30Day: Record<string, { morning: string; evening: string }>
}).psalms30Day
