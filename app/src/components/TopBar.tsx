interface TopBarProps {
  visible: boolean
  title: string
  subtitle?: string
  onOpenToc: () => void
}

export function TopBar({ visible, title, subtitle, onOpenToc }: TopBarProps) {
  return (
    <button
      type="button"
      className={'top-bar' + (visible ? ' is-visible' : '')}
      onClick={onOpenToc}
      aria-label="Open table of contents"
    >
      <span className="top-bar-inner">
        <span className="top-bar-title">{title}</span>
        {subtitle && <span className="top-bar-subtitle"> › {subtitle}</span>}
      </span>
      <span className="top-bar-chevron" aria-hidden="true">
        ⌄
      </span>
    </button>
  )
}
