import { create } from 'zustand'

/**
 * Memecah respons RINA menjadi 1-3 bubble chat.
 * Gemini mengirim respons dengan pemisah ||| antar bagian.
 * Jika tidak ada |||, tetap tampilkan sebagai 1 bubble.
 */
function splitIntoBubbles(text) {
  if (!text || text.trim().length === 0) return [text]
  
  // Pecah berdasarkan ||| (delimiter dari system prompt Gemini)
  const parts = text
    .split('|||')
    .map(s => s.trim())
    .filter(s => s.length > 0)
  
  // Maksimal 3 bubble
  return parts.slice(0, 3)
}

// ─── LocalStorage helpers ────────────────────────────────────────────────────
const STORAGE_KEY = 'lifelens_chat_messages'
const OLD_JUDGMENT_WORD = 'meng' + 'hakimi'
const OLD_COMPANION_LINE = 'teman bicaramu di ' + 'LifeLens'
const OLD_GREETING_RE = new RegExp(
  `Hai\\s+(.+?)!\\s+Aku RINA,\\s*${OLD_COMPANION_LINE}\\.\\s*` +
  `Aku di sini buat dengerin kamu tanpa ${OLD_JUDGMENT_WORD}\\.\\s*` +
  'Gimana kabarmu hari ini\\?',
  'i'
)
const OLD_COMPANION_RE = new RegExp(`Aku RINA,\\s*${OLD_COMPANION_LINE}\\.\\s*`, 'i')
const OLD_LISTENING_RE = new RegExp(`Aku di sini buat dengerin kamu tanpa ${OLD_JUDGMENT_WORD}\\.\\s*`, 'i')
const OLD_ONBOARDING_RE = new RegExp(`Cerita apa aja,\\s*aku dengerin tanpa ${OLD_JUDGMENT_WORD}\\.`, 'i')
const OLD_JUDGMENT_RE = new RegExp(`\\btanpa ${OLD_JUDGMENT_WORD}\\b`, 'gi')

function sanitizeMessage(msg) {
  if (!msg || typeof msg !== 'object') return msg
  if (msg.type !== 'rina' && msg.type !== 'crisis') return msg
  if (typeof msg.text !== 'string') return msg

  let text = msg.text
    .replace(OLD_GREETING_RE, 'Hai $1, aku Rina. Gimana kabarmu hari ini?')
    .replace(OLD_COMPANION_RE, 'Aku Rina. ')
    .replace(OLD_LISTENING_RE, '')
    .replace(OLD_ONBOARDING_RE, 'Cerita apa aja, aku dengerin pelan-pelan.')
    .replace(OLD_JUDGMENT_RE, 'pelan-pelan')
    .replace(/\s+/g, ' ')
    .trim()

  return { ...msg, text }
}

function loadMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    // Simpan max 100 pesan terakhir
    return Array.isArray(parsed) ? parsed.slice(-100).map(sanitizeMessage) : []
  } catch { return [] }
}

function saveMessages(messages) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-100)))
  } catch { /* quota exceeded, silent fail */ }
}


const useChatStore = create((set, get) => ({
  messages: loadMessages(),
  isTyping: false,
  isConnected: false,
  currentEmotion: 'idle',
  mouthOpen: 0,
  riskLevel: null,
  factors: [],
  recommendations: [],
  nlpData: null,
  daysTracked: 0,

  ws: null,

  setEmotion: (emo) => set({ currentEmotion: emo }),
  setMouthOpen: (val) => set({ mouthOpen: val }),
  addMessage: (msg) => set((s) => {
    const updated = [...s.messages, sanitizeMessage({ ...msg, ts: Date.now() })]
    saveMessages(updated)
    return { messages: updated }
  }),

  setTyping: (v) => set({ isTyping: v }),
  setConnected: (v) => set({ isConnected: v }),

  _reconnectAttempts: 0,
  _reconnectTimer: null,

  connect: (userId) => {
    if (get().ws) return

    const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000'
    const wsUrl = `${wsBase}/api/chat/ws/${userId}`

    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.info('[WS] connected', wsUrl)
      set({ isConnected: true, isTyping: false, _reconnectAttempts: 0 })
      // Clear any pending reconnect timer
      const timer = get()._reconnectTimer
      if (timer) { clearTimeout(timer); set({ _reconnectTimer: null }) }
    }
    ws.onerror = (event) => {
      console.warn('[WS] error', wsUrl, event)
    }
    ws.onclose = (event) => {
      set({ isConnected: false, isTyping: false, ws: null })
      // Auto-reconnect (max 5 attempts, exponential backoff)
      const attempts = get()._reconnectAttempts
      if (attempts < 5 && !event.wasClean) {
        const delay = Math.min(1000 * Math.pow(2, attempts), 8000)
        console.log(`[WS] Reconnecting in ${delay}ms (attempt ${attempts + 1}/5)`)
        const timer = setTimeout(() => {
          set({ _reconnectAttempts: attempts + 1 })
          get().connect(userId)
        }, delay)
        set({ _reconnectTimer: timer })
      }
    }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        // ─── Streaming protocol ───
        if (data.type === 'stream_start') {
          // RINA mulai "mengetik"
          set({ isTyping: true, currentEmotion: 'thinking' })
          // Reset streaming buffer
          set({ _streamBubbles: [''], _streamCurrentBubble: 0 })
          return
        }

        if (data.type === 'chunk') {
          const state = get()
          const bubbles = [...(state._streamBubbles || [''])]

          if (data.is_bubble_break) {
            // Simpan bubble saat ini, mulai bubble baru
            bubbles.push('')
            set({ _streamBubbles: bubbles, _streamCurrentBubble: bubbles.length - 1 })
          } else {
            // Tambah teks ke bubble aktif (backend kirim per-kata dgn spasi)
            const idx = bubbles.length - 1
            bubbles[idx] = (bubbles[idx] || '') + data.text
            set({
              _streamBubbles: bubbles,
              currentEmotion: data.emotion || 'talking',
              isTyping: false, // Hilangkan "typing" indicator — teks sudah muncul langsung
            })
          }
          return
        }

        if (data.type === 'stream_end') {
          set({ isTyping: false })
          const emotion = data.emotion || 'idle'
          const streamBubbles = get()._streamBubbles || []

          // Tampilkan semua bubble yang terkumpul
          const validBubbles = streamBubbles.filter(b => b.trim().length > 0)
          if (validBubbles.length > 0) {
            // Bubble pertama langsung
            set({ currentEmotion: emotion })
            get().addMessage({
              type: data.is_crisis ? 'crisis' : 'rina',
              text: validBubbles[0],
              emotion,
            })

            // Bubble ke-2+ dengan delay
            validBubbles.slice(1).forEach((bubbleText, i) => {
              const delay = (i + 1) * (400 + Math.random() * 400)

              setTimeout(() => { set({ isTyping: true }) }, delay - 300)

              setTimeout(() => {
                set({ isTyping: false })
                get().addMessage({ type: 'rina', text: bubbleText, emotion })
              }, delay)
            })
          }

          // Update metadata
          if (data.extracted_data) {
            const ext = data.extracted_data
            if (ext.nlp) set({ nlpData: ext.nlp })
            if (ext.features_tracked_days != null) set({ daysTracked: ext.features_tracked_days })
          }
          if (data.risk_level) {
            set({
              riskLevel: data.risk_level,
              factors: data.top_factors || [],
              recommendations: data.recommendations || [],
            })
          }

          // Cleanup stream buffer
          set({ _streamBubbles: [''], _streamCurrentBubble: 0 })
          return
        }

        // ─── Legacy protocol (backward compat) ───
        if (data.type === 'message' || data.type === 'crisis') {
          const emotion = data.emotion || 'idle'
          const fullText = data.response || ''
          const bubbles = splitIntoBubbles(fullText)

          set({ isTyping: false, currentEmotion: emotion })
          get().addMessage({
            type: data.type === 'crisis' ? 'crisis' : 'rina',
            text: bubbles[0],
            emotion
          })

          bubbles.slice(1).forEach((bubbleText, i) => {
            const delay = (i + 1) * (400 + Math.random() * 400)
            setTimeout(() => { set({ isTyping: true }) }, delay - 300)
            setTimeout(() => {
              set({ isTyping: false })
              get().addMessage({ type: 'rina', text: bubbleText, emotion })
            }, delay)
          })

          if (data.extracted_data) {
             const ext = data.extracted_data
             if (ext.nlp) set({ nlpData: ext.nlp })
             if (ext.features_tracked_days != null) set({ daysTracked: ext.features_tracked_days })
          }
        }

        if (data.type === 'risk_update') {
          const ext = data.extracted_data || {}
          set({
             riskLevel: data.risk_level || null,
             factors: data.top_factors || [],
             recommendations: data.recommendations || [],
             nlpData: ext.nlp || get().nlpData,
             daysTracked: ext.features_tracked_days ?? get().daysTracked,
          })
        }
      } catch (err) {
        console.error("Failed to parse WS message", err)
      }
    }
    
    set({ ws })
  },
  
  disconnect: () => {
    const { ws, _reconnectTimer } = get()
    // Clear any pending reconnect
    if (_reconnectTimer) clearTimeout(_reconnectTimer)
    if (ws) {
      ws.close()
    }
    set({ ws: null, isConnected: false, _reconnectTimer: null, _reconnectAttempts: 0 })
  },

  updateRisk: (data) => set({
    riskLevel: data.risk_level || null,
    factors: data.factors || [],
  }),

  updateRecommendations: (recs) => set({ recommendations: recs || [] }),
  updateNlp: (nlp) => set({ nlpData: nlp }),
  setDaysTracked: (d) => set({ daysTracked: d }),

  clearMessages: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ messages: [] })
  },
}))

export default useChatStore
