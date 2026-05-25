import { useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import { Moon, Sun, Settings, BarChart3 } from 'lucide-react'
import { Link } from 'react-router-dom'

import StatusBar from '../components/dashboard/StatusBar'
import ChatArea from '../components/chat/ChatArea'
import InputBar from '../components/chat/InputBar'
import OnboardingFlow from '../components/auth/OnboardingFlow'
import ConsentDialog from '../components/auth/ConsentDialog'
import RinaStage from '../components/character/RinaStage'

import useChat from '../hooks/useChat'
import useChatStore from '../store/chatStore'
import useUserStore from '../store/userStore'

export default function Chat() {
  const { sendMessage } = useChat()
  const { userName, onboarded, setUserName, theme, toggleTheme, consentGiven } = useUserStore()
  const { addMessage, isTyping } = useChatStore()

  // Apply saved theme on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  // Manage WebSocket Connection
  const { connect, disconnect } = useChatStore()
  const { userId } = useUserStore()

  useEffect(() => {
    if (onboarded && userName) {
      connect(userId)
    }
    return () => disconnect()
  }, [onboarded, userName, userId, connect, disconnect])

  const handleOnboardComplete = (name) => {
    setUserName(name)
    addMessage({
      type: 'rina',
      text: `Hai ${name}, aku Rina. Gimana kabarmu hari ini?`,
      emotion: 'listening',
    })
  }

  const handleSend = (text) => {
    sendMessage(text)
  }

  return (
    <>
      {/* Onboarding overlay */}
      <AnimatePresence>
        {!onboarded && <OnboardingFlow onComplete={handleOnboardComplete} />}
      </AnimatePresence>

      {/* Consent dialog — muncul sekali setelah onboarding */}
      <AnimatePresence>
        {onboarded && consentGiven === null && (
          <div style={{
            position: 'fixed', inset: 0, zIndex: 90,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'rgba(59,46,34,0.35)',
            backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
          }}>
            <ConsentDialog />
          </div>
        )}
      </AnimatePresence>

      {/* ═══ MAIN LAYOUT ═══ */}
      <div className="app-layout">

        {/* ─── KIRI 70%: Placeholder untuk background + RINA baru ─── */}
        <div style={{ flex: '0 0 70%', position: 'relative', height: '100%' }}>
          <RinaStage />
        </div>

        {/* ─── KANAN 30%: Chat Panel ─── */}
        <div className="chat-panel">

          {/* Header */}
          <header className="chat-panel__header">
            <div className="chat-panel__header-left">
              <img src="/assets/rina_profile.png" alt="Rina" className="chat-panel__rina-dot" style={{ objectFit: 'cover' }} />
              <div>
                <div className="chat-panel__rina-name">RINA</div>
                <div className="chat-panel__rina-status">
                  <span className="chat-panel__rina-status-dot" />
                  <span>Online</span>
                </div>
              </div>
            </div>

            <div className="chat-panel__header-actions">
              <Link
                to="/dashboard"
                className="chat-panel__icon-btn"
                aria-label="Dashboard"
                style={{ textDecoration: 'none' }}
              >
                <BarChart3 size={15} />
              </Link>
              <Link
                to="/settings"
                className="chat-panel__icon-btn"
                aria-label="Settings"
                style={{ textDecoration: 'none' }}
              >
                <Settings size={15} />
              </Link>
              <button
                className="chat-panel__icon-btn"
                onClick={toggleTheme}
                aria-label="Toggle theme"
                type="button"
              >
                {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
              </button>
            </div>
          </header>

          {/* Status bar — risk level */}
          <StatusBar />

          {/* Chat messages (scrollable) */}
          <ChatArea />

          {/* Input bar (fixed bottom) */}
          <InputBar onSend={handleSend} disabled={isTyping} />
        </div>
      </div>
    </>
  )
}
