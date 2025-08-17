import React from 'react'

type Props = { title?: string; children: React.ReactNode; className?: string }

const Card: React.FC<Props> = ({ title, children, className='' }) => {
  return (
    <div className={`bg-white border rounded ${className}`}>
      {title && <div className="border-b p-3 font-semibold">{title}</div>}
      <div className="p-3">{children}</div>
    </div>
  )
}

export default Card