import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' }

const Button: React.FC<Props> = ({ variant = 'primary', className = '', ...rest }) => {
  const base = 'px-3 py-1 rounded text-sm'
  const styles = variant === 'primary' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
  return <button className={`${base} ${styles} ${className}`} {...rest} />
}

export default Button