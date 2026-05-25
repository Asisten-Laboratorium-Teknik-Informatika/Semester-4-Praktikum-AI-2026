import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'

export default function OnboardingFlow({ onComplete }) {
  const [name, setName] = useState('')

  const handleStart = () => onComplete(name.trim() || 'teman')
  const handleSkip = () => onComplete('teman')

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        background: 'rgba(59,46,34,0.35)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
      }}
    >
      <motion.div
        initial={{ scale: 0.92, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 280, damping: 24, delay: 0.1 }}
        style={{
          width: '100%',
          maxWidth: '420px',
          borderRadius: '24px',
          padding: '44px 36px 36px',
          textAlign: 'center',
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border-soft)',
          boxShadow: '0 24px 60px rgba(59,46,34,0.18), 0 8px 20px rgba(59,46,34,0.08)',
        }}
      >
        {/* Icon */}
        <motion.div
          initial={{ scale: 0, rotate: -10 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 350, damping: 18, delay: 0.25 }}
          style={{
            width: '80px',
            height: '80px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px',
          }}
        >
          <img src="/assets/logo.png" alt="LifeLens Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ y: 16, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.35 }}
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.5rem',
            fontWeight: 800,
            color: 'var(--color-text)',
            marginBottom: '10px',
            letterSpacing: '-0.01em',
          }}
        >
          Selamat Datang
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ y: 12, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.42 }}
          style={{
            fontSize: '0.875rem',
            color: 'var(--color-text-secondary)',
            lineHeight: 1.7,
            marginBottom: '28px',
            fontFamily: 'var(--font-body)',
          }}
        >
          Hai! Aku <strong style={{ color: 'var(--color-primary)', fontWeight: 600 }}>RINA</strong>.
          <br />
          Cerita apa aja, aku dengerin pelan-pelan.
        </motion.p>

        {/* Name Input */}
        <motion.div
          initial={{ y: 12, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          style={{ marginBottom: '16px' }}
        >
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleStart()}
            placeholder="Nama panggilanmu"
            autoFocus
            style={{
              width: '100%',
              padding: '13px 20px',
              borderRadius: '9999px',
              textAlign: 'center',
              outline: 'none',
              border: '1.5px solid var(--color-border)',
              background: 'var(--color-bg)',
              fontFamily: 'var(--font-body)',
              fontSize: '0.9375rem',
              color: 'var(--color-text)',
              transition: 'border-color 0.2s, box-shadow 0.2s',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--color-primary)'
              e.target.style.boxShadow = '0 0 0 3px rgba(196,149,106,0.15)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--color-border)'
              e.target.style.boxShadow = 'none'
            }}
          />
        </motion.div>

        {/* Start Button */}
        <motion.button
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.58 }}
          whileHover={{ scale: 1.02, boxShadow: '0 8px 28px rgba(196,149,106,0.35)' }}
          whileTap={{ scale: 0.97 }}
          onClick={handleStart}
          style={{
            width: '100%',
            padding: '14px',
            borderRadius: '9999px',
            border: 'none',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-hover))',
            color: 'white',
            fontFamily: 'var(--font-display)',
            fontWeight: 700,
            fontSize: '0.9375rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            boxShadow: '0 4px 16px rgba(196,149,106,0.3)',
            letterSpacing: '0.02em',
          }}
        >
          Mulai Ngobrol
          <ArrowRight size={16} />
        </motion.button>

        {/* Skip */}
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          transition={{ delay: 0.65 }}
          whileHover={{ opacity: 1 }}
          onClick={handleSkip}
          style={{
            marginTop: '14px',
            fontSize: '0.75rem',
            cursor: 'pointer',
            background: 'transparent',
            border: 'none',
            color: 'var(--color-text-tertiary)',
            fontFamily: 'var(--font-body)',
          }}
        >
          Lanjut tanpa nama
        </motion.button>

        {/* Disclaimer — sesuai spec 09_ethics_safety.md */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.75 }}
          style={{
            marginTop: '24px',
            padding: '14px 16px',
            borderRadius: '12px',
            background: 'var(--color-primary-subtle)',
            border: '1px solid var(--color-border-soft)',
            textAlign: 'left',
          }}
        >
          <p style={{
            fontSize: '0.6875rem',
            lineHeight: 1.7,
            color: 'var(--color-text-secondary)',
            fontFamily: 'var(--font-body)',
            marginBottom: 8,
          }}>
            LifeLens adalah alat bantu refleksi diri, <strong>BUKAN pengganti konsultasi dengan psikolog atau tenaga kesehatan profesional</strong>.
          </p>
          <p style={{
            fontSize: '0.625rem',
            lineHeight: 1.7,
            color: 'var(--color-text-tertiary)',
            fontFamily: 'var(--font-body)',
          }}>
            Jika kamu merasa membutuhkan bantuan profesional, hubungi:
            <br />
            Psikolog / konselor kampus &bull; Puskesmas / klinik kesehatan jiwa
            <br />
            Hotline Into The Light: <strong>119 ext 8</strong>
            <br /><br />
            Data kamu dienkripsi AES-256 dan tidak dibagikan ke siapapun.
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
