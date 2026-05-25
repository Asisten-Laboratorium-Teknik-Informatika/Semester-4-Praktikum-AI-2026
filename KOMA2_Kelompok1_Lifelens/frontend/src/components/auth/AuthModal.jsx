import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Mail, User } from 'lucide-react'
import { signInWithGoogle, signInWithEmail, isAuthEnabled } from '../../services/supabase'
import Button from '../shared/Button'

export default function AuthModal({ onClose, onAnonymous }) {
  const [mode, setMode] = useState('main') // main | email
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const authReady = isAuthEnabled()

  const handleGoogle = async () => {
    const { error } = await signInWithGoogle()
    if (error) setError('Gagal login dengan Google')
  }

  const handleEmail = async () => {
    if (!email || !password) { setError('Email dan password wajib diisi'); return }
    const { error } = await signInWithEmail(email, password)
    if (error) setError(error.message || 'Login gagal')
    else onClose()
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.4)' }}
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-md rounded-3xl p-8"
        style={{ background: 'var(--color-surface)', boxShadow: 'var(--shadow-lg)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start mb-2">
          <h2 className="text-2xl font-bold font-display" style={{ color: 'var(--color-text)' }}>
            Selamat Datang
          </h2>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center cursor-pointer"
            style={{ background: 'var(--color-surface-raised)', color: 'var(--color-text-secondary)', border: 'none' }}>
            <X size={16} />
          </button>
        </div>

        <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>
          Simpan progress-mu dengan login, atau langsung mulai tanpa akun.
        </p>

        {error && (
          <div className="mb-4 p-3 rounded-xl text-sm" style={{ background: 'var(--color-risk-high-soft)', color: 'var(--color-risk-high)' }}>
            {error}
          </div>
        )}

        {mode === 'main' && (
          <>
            {/* Google Login */}
            {authReady && (
              <button
                onClick={handleGoogle}
                className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-2xl font-medium mb-3 cursor-pointer transition-colors"
                style={{
                  border: '2px solid var(--color-border)',
                  background: 'var(--color-surface)',
                  color: 'var(--color-text)',
                }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Lanjut dengan Google
              </button>
            )}

            {/* Email option */}
            {authReady && (
              <button
                onClick={() => setMode('email')}
                className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-2xl text-sm cursor-pointer mb-3"
                style={{
                  border: '1px solid var(--color-border-soft)',
                  background: 'transparent',
                  color: 'var(--color-text-secondary)',
                }}
              >
                <Mail size={16} />
                Pakai email & password
              </button>
            )}

            {!authReady && (
              <p className="text-sm text-center mb-4" style={{ color: 'var(--color-text-tertiary)' }}>
                Auth belum dikonfigurasi. Gunakan mode anonymous.
              </p>
            )}

            {/* Anonymous */}
            <button
              onClick={onAnonymous}
              className="w-full py-3 text-sm cursor-pointer bg-transparent border-none"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              <User size={14} className="inline mr-1" />
              Lanjut tanpa akun
            </button>
          </>
        )}

        {mode === 'email' && (
          <>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full py-3 px-4 rounded-xl mb-3 outline-none"
              style={{ border: '1.5px solid var(--color-border)', background: 'var(--color-bg)', color: 'var(--color-text)' }}
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full py-3 px-4 rounded-xl mb-4 outline-none"
              style={{ border: '1.5px solid var(--color-border)', background: 'var(--color-bg)', color: 'var(--color-text)' }}
              onKeyDown={(e) => e.key === 'Enter' && handleEmail()}
            />
            <Button onClick={handleEmail} fullWidth>Login</Button>
            <button onClick={() => setMode('main')}
              className="w-full mt-3 text-sm cursor-pointer bg-transparent border-none"
              style={{ color: 'var(--color-text-tertiary)' }}>
              Kembali
            </button>
          </>
        )}

        <p className="text-xs text-center mt-6" style={{ color: 'var(--color-text-tertiary)' }}>
          Data kamu dienkripsi dan tidak dibagikan ke siapapun.
        </p>
      </motion.div>
    </motion.div>
  )
}
