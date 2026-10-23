import type { Block as BlockType } from '../types'
import { InlineText } from './InlineText'
import { LectionaryReadingBlock } from './LectionaryReadingBlock'

// keep the mid-verse pause mark glued to the preceding word so it never
// wraps onto a line by itself
function glueAsterisk(text: string) {
  return text.replace(/ \*$/, ' *')
}

export function Block({ block }: { block: BlockType }) {
  switch (block.type) {
    case 'heading':
      return (
        <h2 className="b-heading">
          <InlineText text={block.text} />
        </h2>
      )

    case 'subtitle':
      return (
        <p className="b-subtitle">
          <InlineText text={block.text} />
        </p>
      )

    case 'small-heading':
      return (
        <p className="b-small-heading">
          <InlineText text={block.text} />
        </p>
      )

    case 'rubric':
      return (
        <p className="b-rubric">
          <InlineText text={block.text} />
        </p>
      )

    case 'paragraph':
      return (
        <p className="b-paragraph">
          <InlineText text={block.text} />
          {block.citation && <cite className="b-citation">{block.citation}</cite>}
        </p>
      )

    case 'dialogue':
      return (
        <p className={'b-dialogue' + (block.strong ? ' is-strong' : '')}>
          <span className="b-dialogue-label">{block.label}</span>
          <span className="b-dialogue-text">
            <InlineText text={block.text} />
            {block.citation && <cite className="b-citation">{block.citation}</cite>}
          </span>
        </p>
      )

    case 'columns':
      return (
        <div className="b-columns">
          {block.rows.map((row, i) => (
            <div className="b-columns-row" key={i}>
              <span className="b-columns-col">
                <InlineText text={row[0]} />
              </span>
              <span className="b-columns-col">
                <InlineText text={row[1]} />
              </span>
            </div>
          ))}
        </div>
      )

    case 'verse-block':
      return (
        <div className="b-verse-block">
          {block.verses.map((v, i) => (
            <p className="b-verse" key={i}>
              {v.number && <sup className="b-verse-num">{v.number}</sup>}
              <span className="b-verse-lines">
                {v.lines.map((line, li) => (
                  <span className="b-verse-line" key={li}>
                    <InlineText text={glueAsterisk(line)} />
                  </span>
                ))}
              </span>
              {v.citation && <cite className="b-citation">{v.citation}</cite>}
            </p>
          ))}
        </div>
      )

    case 'lectionary-reading':
      return <LectionaryReadingBlock office={block.office} role={block.role} />

    default:
      return null
  }
}
