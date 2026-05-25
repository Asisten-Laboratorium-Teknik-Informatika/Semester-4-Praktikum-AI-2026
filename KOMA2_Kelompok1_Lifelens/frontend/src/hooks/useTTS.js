import { useCallback, useEffect, useRef } from 'react'
import useUserStore from '../store/userStore'
import useChatStore from '../store/chatStore'
import useLipSync from './useLipSync'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function makeTraceId(prefix) {
  const suffix = crypto.randomUUID?.().slice(0, 8) || Math.random().toString(36).slice(2, 10)
  return `${prefix}-${Date.now().toString(36)}-${suffix}`
}

/**
 * useTTS — Hook untuk Text-to-Speech RINA
 * 
 * Memanggil POST /api/voice/tts di backend,
 * menerima audio bytes, dan play via Web Audio API.
 * 
 * Fitur:
 * - Auto-play setiap pesan RINA
 * - Queue system (antri jika ada beberapa bubble)
 * - Bisa di-mute via ttsEnabled state
 * - Bersihkan ||| separator sebelum kirim ke TTS
 */
export default function useTTS() {
  const voiceLang = useUserStore((s) => s.voiceLang)
  const setGlobalMouthOpen = useChatStore((s) => s.setMouthOpen)
  const setEmotion = useChatStore((s) => s.setEmotion)
  const { mouthOpen, isPlaying, playWithLipSync, stop: stopLipSync, unlock } = useLipSync()
  const queueRef = useRef([])
  const playingRef = useRef(false)

  useEffect(() => {
    setGlobalMouthOpen(mouthOpen)
  }, [mouthOpen, setGlobalMouthOpen])

  useEffect(() => {
    let unlocked = false
    const handleUserGesture = () => {
      if (unlocked) return
      unlocked = true
      unlock().catch(() => {
        unlocked = false
      })
    }

    window.addEventListener('pointerdown', handleUserGesture, { passive: true })
    window.addEventListener('keydown', handleUserGesture)
    window.addEventListener('touchstart', handleUserGesture, { passive: true })

    return () => {
      window.removeEventListener('pointerdown', handleUserGesture)
      window.removeEventListener('keydown', handleUserGesture)
      window.removeEventListener('touchstart', handleUserGesture)
    }
  }, [unlock])

  const processQueue = useCallback(async () => {
    if (playingRef.current || queueRef.current.length === 0) return
    playingRef.current = true

    const { text, emotion, traceId = makeTraceId('auto') } = queueRef.current.shift()
    const cleanText = text.replace(/\|\|\|/g, '. ').slice(0, 500)
    const started = performance.now()
    console.info('[TTS UI]', traceId, 'queue start', {
      voiceLang,
      emotion: emotion || 'neutral',
      chars: cleanText.length,
      queueRemaining: queueRef.current.length,
    })

    try {
      const fetchStart = performance.now()
      const res = await fetch(`${API_BASE}/api/voice/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: cleanText,
          emotion: emotion || 'neutral',
          voice_lang: voiceLang || 'id',
          require_clone: true,
          client_trace_id: traceId,
        }),
      })
      console.info('[TTS UI]', traceId, 'fetch done', {
        ok: res.ok,
        status: res.status,
        ms: Math.round(performance.now() - fetchStart),
        engine: res.headers.get('x-tts-engine'),
        clone: res.headers.get('x-tts-clone'),
        cache: res.headers.get('x-tts-cache'),
        backendMs: res.headers.get('x-tts-elapsed-ms'),
        sourceVoice: res.headers.get('x-tts-source-voice'),
      })

      const contentType = res.headers.get('content-type') || ''
      if (!res.ok) {
        let payload = null
        try {
          payload = contentType.includes('application/json') ? await res.json() : await res.text()
        } catch {
          payload = null
        }
        console.warn('[TTS UI]', traceId, 'server error', { status: res.status, payload })
        playingRef.current = false
        processQueue()
        return
      }

      if (contentType.includes('application/json')) {
        // Error response as JSON
        const err = await res.json()
        console.warn('[TTS UI]', traceId, 'backend json error', err)
        playingRef.current = false
        processQueue()
        return
      }

      const blob = await res.blob()
      console.info('[TTS UI]', traceId, 'audio blob ready', {
        bytes: blob.size,
        type: blob.type,
        totalBeforePlayMs: Math.round(performance.now() - started),
      })
      setEmotion(emotion || 'talking')
      const playStart = performance.now()
      await playWithLipSync(blob)
      console.info('[TTS UI]', traceId, 'playback ended', {
        playMs: Math.round(performance.now() - playStart),
        totalMs: Math.round(performance.now() - started),
      })
      playingRef.current = false
      processQueue()
    } catch (err) {
      console.warn('[TTS UI]', traceId, 'fetch/play error', err)
      playingRef.current = false
      setGlobalMouthOpen(0)
      processQueue()
    }
  }, [playWithLipSync, setEmotion, setGlobalMouthOpen, voiceLang])

  const speak = useCallback((text, emotion = 'neutral') => {
    if (!text || text.trim().length === 0) return
    const traceId = makeTraceId('auto')
    queueRef.current.push({ text, emotion, traceId })
    console.info('[TTS UI]', traceId, 'queued', { emotion, chars: text.length, queueSize: queueRef.current.length })
    processQueue()
  }, [processQueue])

  const stop = useCallback(() => {
    queueRef.current = []
    playingRef.current = false
    stopLipSync()
    setGlobalMouthOpen(0)
  }, [setGlobalMouthOpen, stopLipSync])

  return { speak, stop, isPlaying }
}
