/**
 * VoiceSelector — Pilih suara RINA (ID / JP / EN / KR).
 * Dengan preview button untuk dengarkan sample sebelum pilih.
 */
import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Volume2, Check, Loader, Globe } from 'lucide-react'
import { chatApi } from '../../services/api'
import useUserStore from '../../store/userStore'

const VOICE_OPTIONS = [
  {
    lang: 'id',
    label: 'Indonesia',
    flag: 'ID',
    description: 'Clone referensi Indonesia',
    sample: 'Hai, aku Rina. Hari ini rasanya gimana?',
  },
  {
    lang: 'ja',
    label: 'Japanese',
    flag: 'JP',
    description: 'Clone referensi Hu Tao Jepang',
    sample: 'Konnichiwa, Rina desu. Kyou wa donna ichinichi datta?',
  },
  // Bahasa EN dan KO disembunyikan sementara sesuai request
]

export default function VoiceSelector({ compact = false }) {
  const voiceLang = useUserStore((s) => s.voiceLang)
  const setVoiceLang = useUserStore((s) => s.setVoiceLang)
  const [previewing, setPreviewing] = useState(null) // lang being previewed
  const audioRef = useRef(null)

  const handlePreview = async (lang, sampleText) => {
    if (previewing === lang) return

    // Stop current audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    setPreviewing(lang)
    try {
      const { data: blob } = await chatApi.tts(sampleText, 'neutral', lang)
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)

      audio.onended = () => {
        setPreviewing(null)
        URL.revokeObjectURL(url)
      }
      audio.onerror = () => {
        setPreviewing(null)
        URL.revokeObjectURL(url)
      }

      audioRef.current = audio
      await audio.play()
    } catch {
      setPreviewing(null)
    }
  }

  const handleSelect = (lang) => {
    setVoiceLang(lang)
  }

  if (compact) {
    return (
      <div style={{ display: 'flex', gap: 8 }}>
        {VOICE_OPTIONS.map((opt) => (
          <motion.button
            key={opt.lang}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSelect(opt.lang)}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              border: voiceLang === opt.lang ? '2px solid var(--color-primary)' : '1px solid var(--color-border)',
              background: voiceLang === opt.lang ? 'var(--color-primary-soft)' : 'var(--color-surface)',
              color: voiceLang === opt.lang ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: voiceLang === opt.lang ? 600 : 400,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <span style={{ fontSize: 11, opacity: 0.7 }}>{opt.flag}</span>
            {opt.label}
            {voiceLang === opt.lang && <Check size={12} />}
          </motion.button>
        ))}
      </div>
    )
  }

  return (
    <div className="voice-selector" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        marginBottom: 4, color: 'var(--color-text-secondary)', fontSize: 13
      }}>
        <Globe size={15} />
        <span>Suara RINA</span>
      </div>

      {VOICE_OPTIONS.map((opt) => {
        const isSelected = voiceLang === opt.lang
        const isPreviewing = previewing === opt.lang

        return (
          <motion.div
            key={opt.lang}
            whileHover={{ scale: 1.01 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '12px 16px',
              borderRadius: 12,
              border: isSelected
                ? '2px solid var(--color-primary)'
                : '1px solid var(--color-border)',
              background: isSelected
                ? 'var(--color-primary-soft)'
                : 'var(--color-surface)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onClick={() => handleSelect(opt.lang)}
          >
            {/* Radio indicator */}
            <div style={{
              width: 18, height: 18, borderRadius: '50%',
              border: isSelected ? '2px solid var(--color-primary)' : '2px solid var(--color-border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <AnimatePresence>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    style={{
                      width: 10, height: 10, borderRadius: '50%',
                      background: 'var(--color-primary)',
                    }}
                  />
                )}
              </AnimatePresence>
            </div>

            {/* Label */}
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: 14, fontWeight: isSelected ? 600 : 400,
                color: 'var(--color-text-primary)',
                display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <span style={{ fontSize: 11, opacity: 0.6 }}>{opt.flag}</span>
                {opt.label}
                {opt.lang === 'id' && (
                  <span style={{
                    fontSize: 10, padding: '1px 6px', borderRadius: 8,
                    background: 'var(--color-primary-soft)', color: 'var(--color-primary)',
                  }}>
                    default
                  </span>
                )}
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)', marginTop: 2 }}>
                {opt.description}
              </div>
            </div>

            {/* Preview button */}
            <motion.button
              whileTap={{ scale: 0.85 }}
              onClick={(e) => {
                e.stopPropagation()
                handlePreview(opt.lang, opt.sample)
              }}
              style={{
                width: 32, height: 32, borderRadius: '50%',
                border: '1px solid var(--color-border)',
                background: isPreviewing ? 'var(--color-primary-soft)' : 'var(--color-surface)',
                color: isPreviewing ? 'var(--color-primary)' : 'var(--color-text-tertiary)',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}
              title={`Preview suara ${opt.label}`}
            >
              {isPreviewing ? <Loader size={14} className="animate-spin" /> : <Volume2 size={14} />}
            </motion.button>
          </motion.div>
        )
      })}

      <div style={{
        fontSize: 11, color: 'var(--color-text-tertiary)',
        padding: '4px 0', marginTop: 4,
      }}>
        Teks percakapan tetap dalam Bahasa Indonesia. Hanya suara yang berubah.
      </div>
    </div>
  )
}
