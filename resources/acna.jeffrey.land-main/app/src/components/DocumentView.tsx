import { sections } from '../content'
import { Block } from './Block'

export function DocumentView() {
  return (
    <div className="document">
      {sections.map((section) => (
        <section className="doc-section" id={`section-${section.id}`} key={section.id}>
          {section.blocks.map((block, i) =>
            block.type === 'heading' ? (
              <div id={`h-${section.id}-${i}`} className="heading-anchor" key={i}>
                <Block block={block} />
              </div>
            ) : (
              <Block block={block} key={i} />
            ),
          )}
        </section>
      ))}
      <div className="document-end">
        <p>End of selection.</p>
      </div>
    </div>
  )
}
