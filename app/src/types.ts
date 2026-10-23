export type Block =
  | { type: 'heading'; text: string }
  | { type: 'subtitle'; text: string }
  | { type: 'small-heading'; text: string }
  | { type: 'rubric'; text: string }
  | { type: 'paragraph'; text: string; citation?: string }
  | { type: 'dialogue'; label: string; text: string; strong?: boolean; citation?: string }
  | { type: 'columns'; rows: [string, string][] }
  | {
      type: 'verse-block'
      plain?: boolean
      verses: { number?: string | null; lines: string[]; citation?: string }[]
    }
  | { type: 'lectionary-reading'; office: 'morning' | 'midday' | 'evening'; role: 'psalm' | 'lesson' }
  | { type: 'weekday-intention' }

export interface Section {
  id: string
  title: string
  printedPage: number
  blocks: Block[]
}
