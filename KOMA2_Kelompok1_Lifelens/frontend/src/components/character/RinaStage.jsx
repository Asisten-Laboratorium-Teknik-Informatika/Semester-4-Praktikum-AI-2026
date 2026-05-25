import { motion } from 'framer-motion'
import { useEffect, useState, useRef } from 'react'
import useChatStore from '../../store/chatStore'

const MOODS = {
  idle: 'Menunggu ceritamu...',
  happy: 'Senang mendengarnya!',
  empathy: 'Aku ikut merasakan...',
  thinking: 'Sedang memproses...',
  surprised: 'Wah, serius?',
  talking: 'Sedang menjawab...',
  listening: 'Mendengarkan...',
  concerned: 'Aku peduli...',
  encouraging: 'Kamu hebat!',
  neutral: 'Ada di sini untukmu',
}

const EMOTION_TO_IMAGE = {
  idle: '1.png',
  happy: '2.png',
  empathy: '3.png',
  thinking: '4.png',
  surprised: '5.png',
  talking: '6.png',
  listening: '7.png',
  concerned: '8.png',
  encouraging: '9.png',
  neutral: '10.png',
}

export default function RinaStage() {
  const { currentEmotion, isTyping, messages, mouthOpen, _streamBubbles } = useChatStore()
  const emotion = isTyping ? 'thinking' : currentEmotion
  
  // Ambil dialog RINA terakhir dari chatStore (type: 'rina' atau 'crisis', propertinya 'text')
  const lastRinaMsg = messages.slice().reverse().find(m => m.type === 'rina' || m.type === 'crisis')
  const activeStream = (_streamBubbles || []).filter(b => b && b.trim().length > 0).at(-1)
  const dialogueText = activeStream || (isTyping ? '...' : (lastRinaMsg ? lastRinaMsg.text : 'Halo! Ada yang mau diceritain hari ini?'))

  // Animasi Typewriter
  const [displayedText, setDisplayedText] = useState('')
  useEffect(() => {
    if (activeStream) {
      setDisplayedText(dialogueText)
      return
    }

    let i = 0
    setDisplayedText('')
    if (!dialogueText) return
    const interval = setInterval(() => {
      setDisplayedText(dialogueText.substring(0, i + 1))
      i++
      if (i >= dialogueText.length) clearInterval(interval)
    }, 30) // kecepatan ngetik
    return () => clearInterval(interval)
  }, [dialogueText, activeStream])

  // PNGTuber style bouncing saat suara dimainkan (isTalking dinamis)
  const isTalking = mouthOpen > 0.05
  const imgFile = EMOTION_TO_IMAGE[emotion] || '1.png'

  // Logika Bounce: hanya di awal ngomong atau saat ganti emosi
  const [bounceKey, setBounceKey] = useState(0)
  const prevTalking = useRef(isTalking)
  const prevEmotion = useRef(emotion)

  useEffect(() => {
    if (isTalking && !prevTalking.current) {
      setBounceKey(k => k + 1)
    }
    prevTalking.current = isTalking
  }, [isTalking])

  useEffect(() => {
    if (emotion !== prevEmotion.current) {
      setBounceKey(k => k + 1)
    }
    prevEmotion.current = emotion
  }, [emotion])

  return (
    <section className="rina-stage" style={{ position: 'relative', overflow: 'hidden', width: '100%', height: '100%' }}>
      {/* Animated gradient background */}
      <div className="rina-stage__bg" />

      {/* Floating orbs */}
      <div className="rina-stage__orb rina-stage__orb--1" />
      <div className="rina-stage__orb rina-stage__orb--2" />
      <div className="rina-stage__orb rina-stage__orb--3" />

      {/* Visual Novel Background Dialogue Box */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '10%',
        right: '10%',
        background: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '16px',
        padding: '20px',
        color: '#fff',
        zIndex: 20,
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        minHeight: '80px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <div style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--color-primary-light, #ffccb3)', marginBottom: '6px' }}>RINA</div>
        <div style={{ fontSize: '15px', lineHeight: '1.5', fontFamily: 'sans-serif' }}>
          {displayedText}
        </div>
      </div>

      {/* Character container */}
      <motion.div
        className="rina-stage__character"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        style={{ 
          zIndex: 10, 
          position: 'absolute', 
          top: 0,
          bottom: 0, 
          left: 0, 
          right: 0, 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'flex-end',
        }}
      >
        {/* Avatar Image (PNGTuber) */}
        <motion.div
          key={`bounce-${bounceKey}`}
          animate={{
            y: [0, -15, 0], // Bounce effect
            scale: [1, 1.03, 1], // Squish effect
          }}
          transition={{ 
            duration: 0.4, 
            ease: "easeInOut"
          }}
          style={{
            height: '100%', // Full height dari container parent agar kaki mentok bawah
            width: '100%',
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'center',
            filter: 'drop-shadow(0px 10px 20px rgba(0,0,0,0.2))'
          }}
        >
          <img 
            src={`/assets/rina/${imgFile}?v=6`} 
            alt={`Rina ${emotion}`} 
            style={{
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
              objectPosition: 'center bottom',
              display: 'block'
            }}
          />
        </motion.div>

      </motion.div>
    </section>
  )
}
