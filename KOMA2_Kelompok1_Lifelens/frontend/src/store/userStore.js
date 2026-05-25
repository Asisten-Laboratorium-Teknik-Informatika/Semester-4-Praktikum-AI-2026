import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useUserStore = create(
  persist(
    (set) => ({
      userId: crypto.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
      }),
      userName: '',
      theme: 'light',
      voiceLang: 'id',
      onboarded: false,
      consentGiven: null,        // null = belum ditanya, true/false = sudah jawab
      consentTimestamp: null,

      setUserName: (name) => set({ userName: name, onboarded: true }),
      setTheme: (theme) => {
        document.documentElement.setAttribute('data-theme', theme)
        set({ theme })
      },
      toggleTheme: () => set((s) => {
        const next = s.theme === 'light' ? 'dark' : 'light'
        document.documentElement.setAttribute('data-theme', next)
        return { theme: next }
      }),
      setVoiceLang: (lang) => set({ voiceLang: lang }),
      setConsent: (given) => set({
        consentGiven: given,
        consentTimestamp: new Date().toISOString(),
      }),
      logout: () => {
        // Hapus chat store juga
        localStorage.removeItem('ll-chat')
        set({
          userId: crypto.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
          }),
          userName: '',
          onboarded: false,
          consentGiven: null,
          consentTimestamp: null,
        })
      },
    }),
    { name: 'll-user' }
  )
)

export default useUserStore
