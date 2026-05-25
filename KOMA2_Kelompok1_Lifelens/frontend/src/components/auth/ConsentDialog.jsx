/**
 * ConsentDialog — Dialog consent via RINA.
 *
 * Sesuai spec 09_ethics_safety.md:
 *   RINA meminta izin untuk simpan percakapan (terenkripsi).
 *   User bisa pilih "Boleh" atau "Tidak dulu".
 *   Jika tidak → hanya data statistik yang disimpan.
 */
import { motion, AnimatePresence } from 'framer-motion'
import { Lock, Heart } from 'lucide-react'
import useUserStore from '../../store/userStore'
import api from '../../services/api'

export default function ConsentDialog({ onComplete }) {
  const setConsent = useUserStore((s) => s.setConsent)
  const userId = useUserStore((s) => s.userId)

  const handleConsent = async (given) => {
    setConsent(given)
    // Kirim ke backend untuk enforce encryption policy
    try {
      await api.post('/consent', { user_id: userId, consent_given: given })
    } catch (err) {
      console.warn('[Consent] API call failed, saved locally only:', err.message)
    }
    if (onComplete) onComplete(given)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      style={{
        maxWidth: 420,
        margin: '0 auto',
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      {/* RINA bubble 1 */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border-soft)',
          borderRadius: '18px 18px 18px 4px',
          padding: '14px 18px',
          fontSize: 14,
          lineHeight: 1.7,
          color: 'var(--color-text)',
        }}
      >
        Eh, sebelum kita mulai — aku mau nanya sesuatu dulu.
      </motion.div>

      {/* RINA bubble 2 */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.8 }}
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border-soft)',
          borderRadius: '18px 18px 18px 4px',
          padding: '14px 18px',
          fontSize: 14,
          lineHeight: 1.7,
          color: 'var(--color-text)',
        }}
      >
        Percakapan kita ini bisa aku simpan untuk belajar jadi lebih baik — supaya aku bisa lebih ngerti orang-orang seperti kamu di masa depan. Tapi ini <strong>pilihan kamu</strong>.
      </motion.div>

      {/* RINA bubble 3 */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.6 }}
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border-soft)',
          borderRadius: '18px 18px 18px 4px',
          padding: '14px 18px',
          fontSize: 14,
          lineHeight: 1.7,
          color: 'var(--color-text)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <Lock size={14} style={{ color: 'var(--color-primary)' }} />
          <span style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>Terenkripsi AES-256</span>
        </div>
        Kalau kamu bilang boleh, percakapannya akan <strong>dienkripsi dan disimpan aman</strong>. Tidak ada yang bisa baca namamu.
        Kalau tidak mau, oke banget — kita tetap ngobrol seperti biasa, hanya data statistiknya saja yang aku simpan.
      </motion.div>

      {/* Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2.2 }}
        style={{ display: 'flex', gap: 10, marginTop: 8 }}
      >
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => handleConsent(true)}
          style={{
            flex: 1,
            padding: '12px 16px',
            borderRadius: 14,
            border: 'none',
            background: 'var(--color-primary)',
            color: 'white',
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
          }}
        >
          <Heart size={15} />
          Boleh, dengan senang hati
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => handleConsent(false)}
          style={{
            flex: 1,
            padding: '12px 16px',
            borderRadius: 14,
            border: '1px solid var(--color-border)',
            background: 'var(--color-surface)',
            color: 'var(--color-text-secondary)',
            fontSize: 14,
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          Tidak dulu
        </motion.button>
      </motion.div>
    </motion.div>
  )
}
