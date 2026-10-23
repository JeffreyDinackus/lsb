import raw from './data/content.json'
import type { Section } from './types'

export const sections = raw as unknown as Section[]

export interface HeadingEntry {
  id: string
  text: string
  sectionId: string
  sectionTitle: string
}

export const headingIndex: HeadingEntry[] = []

sections.forEach((section) => {
  section.blocks.forEach((block, i) => {
    if (block.type === 'heading') {
      headingIndex.push({
        id: `h-${section.id}-${i}`,
        text: block.text,
        sectionId: section.id,
        sectionTitle: section.title,
      })
    }
  })
})
