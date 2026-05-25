import { motion } from 'framer-motion'

const VARIANTS = {
  primary: {
    background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-hover))',
    color: 'white',
    border: 'none',
  },
  secondary: {
    background: 'var(--color-surface-raised)',
    color: 'var(--color-text)',
    border: '1px solid var(--color-border)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--color-text-secondary)',
    border: 'none',
  },
  danger: {
    background: 'transparent',
    color: 'var(--color-risk-high)',
    border: '1.5px solid var(--color-risk-high)',
  },
}

const SIZES = {
  sm: { padding: '8px 16px', fontSize: '0.75rem' },
  md: { padding: '10px 20px', fontSize: '0.8125rem' },
  lg: { padding: '12px 24px', fontSize: '0.875rem' },
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  onClick,
  style: customStyle,
  ...props
}) {
  const variantStyle = VARIANTS[variant] || VARIANTS.primary
  const sizeStyle = SIZES[size] || SIZES.md

  return (
    <motion.button
      whileHover={disabled ? {} : { scale: 1.02 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      onClick={onClick}
      disabled={disabled}
      style={{
        ...variantStyle,
        ...sizeStyle,
        width: fullWidth ? '100%' : 'auto',
        borderRadius: 'var(--radius-sm)',
        fontFamily: 'var(--font-display)',
        fontWeight: 600,
        letterSpacing: '0.02em',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.4 : 1,
        transition: 'opacity 0.15s, background 0.15s',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        ...customStyle,
      }}
      {...props}
    >
      {children}
    </motion.button>
  )
}
