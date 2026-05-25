import { motion } from 'framer-motion'
import { ArrowLeft, Moon, Sun, Trash2, LogOut } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import useUserStore from '../store/userStore'
import useChatStore from '../store/chatStore'
import Button from '../components/shared/Button'
import VoiceSelector from '../components/settings/VoiceSelector'

export default function Settings() {
  const { userName, theme, toggleTheme, logout } = useUserStore()
  const clearMessages = useChatStore((s) => s.clearMessages)
  const navigate = useNavigate()

  const handleLogout = () => {
    clearMessages()
    logout()
    navigate('/')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="settings-page"
    >
      <div className="settings-container">

        {/* Header */}
        <div className="settings-header">
          <Link to="/" className="settings-back-btn" aria-label="Kembali">
            <ArrowLeft size={18} />
          </Link>
          <h1 className="settings-title">Pengaturan</h1>
        </div>

        {/* Profile section */}
        <div className="settings-card">
          <h2>Profil</h2>
          <div className="settings-profile">
            <div className="settings-profile__avatar">
              {(userName || 'T')[0].toUpperCase()}
            </div>
            <div>
              <p className="settings-profile__name">{userName || 'Teman'}</p>
              <p className="settings-profile__sub">Anonymous user</p>
            </div>
          </div>
        </div>

        {/* Theme */}
        <div className="settings-card">
          <h2>Tampilan</h2>
          <button className="settings-toggle" onClick={toggleTheme} type="button">
            <div className="settings-toggle__label">
              {theme === 'dark' ? <Moon size={18} /> : <Sun size={18} />}
              <span>Dark Mode</span>
            </div>
            <div className={`settings-toggle__switch ${theme === 'dark' ? 'active' : ''}`}>
              <div className="settings-toggle__knob" />
            </div>
          </button>
        </div>

        {/* Voice */}
        <div className="settings-card">
          <h2>Suara RINA</h2>
          <VoiceSelector />
        </div>

        {/* Data */}
        <div className="settings-card">
          <h2>Data</h2>
          <div className="settings-actions">
            <Button variant="danger" size="sm" onClick={() => { clearMessages(); window.location.href = '/' }}>
              <Trash2 size={14} style={{ marginRight: 8, verticalAlign: 'middle' }} />
              Hapus Riwayat Chat
            </Button>
          </div>
        </div>

        {/* Logout */}
        <div className="settings-card">
          <h2>Akun</h2>
          <button className="settings-logout-btn" onClick={handleLogout} type="button">
            <LogOut size={16} />
            <span>Keluar / Ganti Akun</span>
          </button>
        </div>

        {/* Disclaimer */}
        <p className="settings-disclaimer">
          LifeLens v1.0.0 — AI Burnout Screening Tool<br/>
          Bukan pengganti diagnosis medis. Darurat: 119 ext 8
        </p>
      </div>
    </motion.div>
  )
}
