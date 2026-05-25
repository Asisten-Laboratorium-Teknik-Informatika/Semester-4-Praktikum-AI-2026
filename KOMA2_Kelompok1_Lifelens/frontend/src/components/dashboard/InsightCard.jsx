import { motion } from 'framer-motion'
import { Lightbulb } from 'lucide-react'
import useChatStore from '../../store/chatStore'

const staggerItem = { initial: { opacity: 0, x: -10 }, animate: { opacity: 1, x: 0 } }

export default function InsightCard() {
  const recommendations = useChatStore((s) => s.recommendations)

  if (!recommendations || recommendations.length === 0) return null

  return (
    <motion.div
      layout
      className="rounded-2xl p-5"
      style={{ background: 'var(--color-surface)', boxShadow: 'var(--shadow-sm)', border: '1px solid var(--color-border-soft)' }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb size={16} style={{ color: 'var(--color-accent)' }} />
        <span className="text-sm font-semibold font-display" style={{ color: 'var(--color-text-secondary)' }}>
          Saran untuk Kamu
        </span>
      </div>

      <motion.div
        initial="initial"
        animate="animate"
        transition={{ staggerChildren: 0.08 }}
        className="space-y-3"
      >
        {recommendations.map((rec, i) => (
          <motion.div
            key={i}
            variants={staggerItem}
            className="rounded-xl p-3"
            style={{ background: 'var(--color-primary-subtle)' }}
          >
            <p className="text-sm font-semibold font-display mb-1" style={{ color: 'var(--color-primary)' }}>
              {rec.title}
            </p>
            <p className="text-xs" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {rec.tip}
            </p>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  )
}
