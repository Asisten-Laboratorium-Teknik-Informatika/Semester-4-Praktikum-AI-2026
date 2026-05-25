import { motion } from 'framer-motion'

export default function LoadingSpinner({ size = 32, color }) {
  return (
    <motion.div
      className="flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke={color || 'var(--color-primary)'}
        strokeWidth="2.5"
        strokeLinecap="round"
      >
        <motion.path
          d="M12 2a10 10 0 0 1 10 10"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '12px 12px' }}
        />
      </svg>
    </motion.div>
  )
}
