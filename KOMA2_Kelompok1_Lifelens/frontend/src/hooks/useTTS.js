import { useCallback, useEffect } from 'react'
import useChatStore from '../store/chatStore'

const TTS_DISABLED = true

export default function useTTS() {
  const setGlobalMouthOpen = useChatStore((s) => s.setMouthOpen)

  useEffect(() => {
    if (TTS_DISABLED) {
      setGlobalMouthOpen(0)
    }
  }, [setGlobalMouthOpen])

  const speak = useCallback((text, emotion = 'neutral') => {
    if (!text || text.trim().length === 0) return
    if (TTS_DISABLED) {
      console.info('[TTS UI] disabled, skip autoplay', {
        emotion,
        chars: text.length,
      })
    }
  }, [])

  const stop = useCallback(() => {
    setGlobalMouthOpen(0)
  }, [setGlobalMouthOpen])

  return { speak, stop, isPlaying: false, disabled: TTS_DISABLED }
}
