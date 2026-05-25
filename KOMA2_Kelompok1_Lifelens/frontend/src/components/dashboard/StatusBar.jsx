import { motion } from 'framer-motion'
import { Activity } from 'lucide-react'
import useChatStore from '../../store/chatStore'

export default function StatusBar() {
  const { riskLevel, factors } = useChatStore()

  const level = riskLevel?.toUpperCase() || null
  const badgeClass = level ? level.toLowerCase() : 'pending'

  return (
    <div className="status-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <Activity size={12} style={{ color: 'var(--color-text-tertiary)' }} />
        <span className="status-bar__label">Status</span>
      </div>

      <div className="status-bar__right">
        {factors.length > 0 && (
          <span style={{
            fontSize: '0.625rem',
            color: 'var(--color-text-tertiary)',
            maxWidth: 120,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontWeight: 500,
          }}>
            {factors[0]}
          </span>
        )}
        <motion.div
          className={`risk-badge ${badgeClass}`}
          layout
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          key={badgeClass}
        >
          <span className="risk-badge__dot" />
          {level || 'Menunggu'}
        </motion.div>
      </div>
    </div>
  )
}
