import { useCallback, useRef } from 'react'
import useChatStore from '../store/chatStore'

const MIN_SEND_INTERVAL_MS = 1500 // Minimal 1.5 detik antar pesan

export default function useChat() {
  const { addMessage, setTyping, ws, isConnected } = useChatStore()
  const lastSentRef = useRef(0)

  const sendMessage = useCallback((text) => {
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
      addMessage({
        type: 'rina',
        text: 'Maaf, koneksi terputus. Coba tunggu sebentar, aku sedang mencoba menyambung kembali...',
      })
    }
  }, [ws, isConnected, addMessage, setTyping])

  return { sendMessage }
}
