/**
 * useVoice — STT hook.
 *
 * Strategy:
 *   1. Web Speech API (browser-native, MVP, default)
 *   2. faster-whisper via server (V2 upgrade, jika tersedia)
 *
 * Web Speech API digunakan kalau tersedia di browser.
 * Jika tidak (Firefox/Safari), fallback ke server STT.
 */
import { useState, useRef, useCallback, useEffect } from 'react'
import { voiceApi } from '../services/api'

export default function useVoice(onTranscript) {
  const [isRecording, setIsRecording] = useState(false)
  const [isSupported, setIsSupported] = useState(true)
  const [sttEngine, setSttEngine] = useState('web_speech_api') // web_speech_api | faster_whisper | none
  const recognizerRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  // Stable ref for callback — prevents re-creating SpeechRecognition on every render
  const onTranscriptRef = useRef(onTranscript)
  useEffect(() => { onTranscriptRef.current = onTranscript }, [onTranscript])

  // Check STT support (run once)
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SR) {
      // Web Speech API available
      const recognition = new SR()
      recognition.lang = 'id-ID'
      recognition.interimResults = true
      recognition.continuous = false

      recognition.onresult = (e) => {
        let transcript = ''
        for (let i = 0; i < e.results.length; i++) {
          transcript += e.results[i][0].transcript
        }
        if (onTranscriptRef.current) onTranscriptRef.current(transcript, e.results[0]?.isFinal)
      }

      recognition.onend = () => setIsRecording(false)
      recognition.onerror = () => setIsRecording(false)

      recognizerRef.current = recognition
      setSttEngine('web_speech_api')
    } else {
      // No Web Speech API — check server STT
      voiceApi.sttStatus()
        .then(({ data }) => {
          if (data.available) {
            setSttEngine('faster_whisper')
            setIsSupported(true)
          } else {
            setSttEngine('none')
            setIsSupported(false)
          }
        })
        .catch(() => {
          setSttEngine('none')
          setIsSupported(false)
        })
    }
  }, []) // Run once — onTranscript accessed via ref

  // Start recording (Web Speech API)
  const startWebSpeech = useCallback(() => {
    if (!recognizerRef.current || isRecording) return
    setIsRecording(true)
    try { recognizerRef.current.start() } catch { /* already started */ }
  }, [isRecording])

  // Start recording (MediaRecorder for server STT)
  const startMediaRecorder = useCallback(async () => {
    if (isRecording) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })

        try {
          const { data } = await voiceApi.stt(blob)
          if (data.transcript && onTranscriptRef.current) {
            onTranscriptRef.current(data.transcript, true)
          }
        } catch (err) {
          console.error('[STT server]', err)
        }
      }

      mediaRecorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error('[Mic]', err)
      setIsRecording(false)
    }
  }, [isRecording])

  // Unified start/stop
  const startRecording = useCallback(() => {
    if (sttEngine === 'web_speech_api') {
      startWebSpeech()
    } else if (sttEngine === 'faster_whisper') {
      startMediaRecorder()
    }
  }, [sttEngine, startWebSpeech, startMediaRecorder])

  const stopRecording = useCallback(() => {
    if (sttEngine === 'web_speech_api' && recognizerRef.current) {
      recognizerRef.current.stop()
    } else if (sttEngine === 'faster_whisper' && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }, [sttEngine, isRecording])

  return { isRecording, isSupported, sttEngine, startRecording, stopRecording }
}
