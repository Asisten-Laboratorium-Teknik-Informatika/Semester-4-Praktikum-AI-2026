import { useCallback, useRef } from 'react'
import useChatStore from '../store/chatStore'
import { chatApi } from '../services/api'

const MIN_SEND_INTERVAL_MS = 1500 // Minimal 1.5 detik antar pesan

function splitIntoBubbles(text) {
  return String(text || '')
    .split('|||')
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, 3)
}

export default function useChat() {
  const { addMessage, setTyping, updateRecommendations, updateNlp, setDaysTracked, ws, isConnected } = useChatStore()
  const lastSentRef = useRef(0)

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return

    // Rate limit: cegah spam
    const now = Date.now()
    if (now - lastSentRef.current < MIN_SEND_INTERVAL_MS) {
      return // Abaikan pesan terlalu cepat
    }
    lastSentRef.current = now

    // Tampilkan pesan user
    addMessage({ type: 'user', text })

    // Kirim via WebSocket
    if (ws && isConnected) {
      setTyping(true)
      ws.send(JSON.stringify({ message: text }))
    } else {
      console.warn('[WS] not connected, using HTTP chat fallback')
      setTyping(true)
      try {
        const { data } = await chatApi.send(text, 'demo-http-fallback')
        const bubbles = splitIntoBubbles(data.response)
        const emotion = data.emotion || 'neutral'
        if (bubbles.length === 0) {
          addMessage({ type: 'rina', text: 'aku dengerin. coba ulang pelan-pelan ya?', emotion: 'listening' })
        } else {
          addMessage({ type: data.is_crisis ? 'crisis' : 'rina', text: bubbles[0], emotion })
          bubbles.slice(1).forEach((bubbleText, i) => {
            setTimeout(() => addMessage({ type: 'rina', text: bubbleText, emotion }), (i + 1) * 450)
          })
        }
        if (data.extracted_data?.nlp) updateNlp(data.extracted_data.nlp)
        if (data.extracted_data?.features_tracked_days != null) setDaysTracked(data.extracted_data.features_tracked_days)
        updateRecommendations(data.recommendations || [])
      } catch (err) {
        console.error('[HTTP chat fallback] failed', err)
        addMessage({
          type: 'rina',
          text: 'Maaf, koneksi backend belum kebaca. Pastikan backend di 127.0.0.1:8000 sudah jalan, lalu refresh halaman.',
          emotion: 'concerned',
        })
      } finally {
        setTyping(false)
      }
    }
  }, [ws, isConnected, addMessage, setTyping, updateRecommendations, updateNlp, setDaysTracked])

  return { sendMessage }
}
