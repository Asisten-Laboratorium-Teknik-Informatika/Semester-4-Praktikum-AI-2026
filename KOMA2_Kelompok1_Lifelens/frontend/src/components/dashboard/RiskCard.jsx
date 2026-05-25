import { motion } from 'framer-motion'
import { Shield, AlertTriangle, TrendingDown } from 'lucide-react'
import useChatStore from '../../store/chatStore'
import clsx from 'clsx'

const staggerItem = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 } }

export default function RiskCard() {
  const riskLevel = useChatStore((s) => s.riskLevel)
  const factors = useChatStore((s) => s.factors)
  const daysTracked = useChatStore((s) => s.daysTracked)

  const level = (riskLevel || 'pending').toLowerCase()
  const labels = { low: 'Kondisi Baik', medium: 'Perlu Perhatian', high: 'Perlu Tindakan', pending: 'Menunggu Data' }
  const icons = { low: Shield, medium: AlertTriangle, high: TrendingDown, pending: Shield }
  const Icon = icons[level] || Shield

  const scorePct = level === 'low' ? 25 : level === 'medium' ? 55 : level === 'high' ? 85 : 0

  return (
    <motion.div
      layout
      className="rounded-2xl p-5"
      style={{ background: 'var(--color-surface)', boxShadow: 'var(--shadow-sm)', border: '1px solid var(--color-border-soft)' }}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold font-display" style={{ color: 'var(--color-text-secondary)' }}>
          Kondisi Saat Ini
        </span>
        <motion.div
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className={clsx('risk-badge', level)}
        >
          <Icon size={14} />
          {labels[level]}
        </motion.div>
      </div>

      {/* Score bar */}
      <div className="w-full h-2 rounded-full mb-4" style={{ background: 'var(--color-surface-raised)' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${scorePct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{
            background: level === 'low' ? 'var(--color-risk-low)'
              : level === 'medium' ? 'var(--color-risk-medium)'
              : level === 'high' ? 'var(--color-risk-high)'
              : 'var(--color-border)',
          }}
        />
      </div>

      {/* Factors */}
      {factors.length > 0 && (
        <motion.div
          initial="initial"
          animate="animate"
          transition={{ staggerChildren: 0.05 }}
          className="space-y-2"
        >
          {factors.map((f, i) => (
            <motion.div key={i} variants={staggerItem} className="flex items-start gap-2 text-sm">
              <span className="w-1.5 h-1.5 mt-1.5 rounded-full shrink-0" style={{ background: 'var(--color-primary)' }} />
              <span style={{ color: 'var(--color-text-secondary)' }}>{f}</span>
            </motion.div>
          ))}
        </motion.div>
      )}

      {factors.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
          Mulai ngobrol untuk melihat analisis
        </p>
      )}

      {daysTracked > 0 && (
        <div className="mt-4 pt-3 text-xs" style={{ borderTop: '1px solid var(--color-border-soft)', color: 'var(--color-text-tertiary)' }}>
          Hari ke-{daysTracked} tracking
        </div>
      )}
    </motion.div>
  )
}
