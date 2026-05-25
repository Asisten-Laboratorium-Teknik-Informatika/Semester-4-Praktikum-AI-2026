import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000, // Diperpanjang jadi 3 menit buat ngasih waktu AI mikir & loading suara
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('[API Error]', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export const chatApi = {
  send: (message, userId) =>
    api.post('/chat/', { message, user_id: userId }),

  tts: async (text, emotion, voiceLang = 'id', options = {}) => {
    return api.post('/voice/tts', {
      text,
      emotion,
      voice_lang: voiceLang,
      require_clone: options.requireClone ?? true,
      client_trace_id: options.traceId,
    }, { responseType: 'blob', timeout: 180000 })
  },
}

export const voiceApi = {
  /** Get available voice options */
  getVoices: () => api.get('/voice/voices'),

  /** Check if server-side STT is available */
  sttStatus: () => api.get('/voice/stt/status'),

  /** Send audio blob for server-side STT */
  stt: (audioBlob) => {
    const form = new FormData()
    form.append('audio', audioBlob, 'recording.wav')
    return api.post('/voice/stt', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    })
  },
}

export const dashboardApi = {
  get: (userId) => api.get(`/dashboard/${userId}`),
}

export const statusApi = {
  check: () => api.get('/health'),
}

export default api
