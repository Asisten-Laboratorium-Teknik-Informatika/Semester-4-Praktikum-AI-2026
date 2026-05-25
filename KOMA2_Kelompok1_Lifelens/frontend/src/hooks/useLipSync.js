/**
 * useLipSync — Lip sync hook untuk karakter 2D RINA.
 *
 * Menggunakan Web Audio API AnalyserNode untuk mendeteksi
 * amplitude audio real-time dan menggerakkan mulut karakter.
 *
 * Usage:
 *   const { mouthOpen, playWithLipSync, isPlaying } = useLipSync()
 *   // mouthOpen: 0..1 (seberapa buka mulut)
 *   // playWithLipSync(audioBlob) → mulai animasi
 */
import { useState, useRef, useCallback, useEffect } from 'react'

export default function useLipSync() {
  const [mouthOpen, setMouthOpen] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioCtxRef = useRef(null)
  const analyserRef = useRef(null)
  const animFrameRef = useRef(null)
  const sourceRef = useRef(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
      if (audioCtxRef.current) audioCtxRef.current.close()
    }
  }, [])

  const getAudioContext = useCallback(() => {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)()
      analyserRef.current = audioCtxRef.current.createAnalyser()
      analyserRef.current.fftSize = 256
      analyserRef.current.smoothingTimeConstant = 0.7
    }
    return { ctx: audioCtxRef.current, analyser: analyserRef.current }
  }, [])

  const unlock = useCallback(async () => {
    const { ctx } = getAudioContext()
    if (ctx.state === 'suspended') {
      await ctx.resume()
    }
  }, [getAudioContext])

  const startLipSync = useCallback(() => {
    const analyser = analyserRef.current
    if (!analyser) return

    const dataArray = new Uint8Array(analyser.frequencyBinCount)

    const update = () => {
      analyser.getByteFrequencyData(dataArray)

      // Hitung amplitude rata-rata dari frekuensi suara manusia (300Hz - 3kHz)
      // fftSize=256 → 128 bins, sample rate 44100 → each bin ~172Hz
      // Bin 2-17 ≈ 344Hz - 2924Hz (vocal range)
      const vocalBins = dataArray.slice(2, 18)
      const avgAmplitude = vocalBins.reduce((a, b) => a + b, 0) / vocalBins.length

      // Normalize to 0..1 with smoothing
      const normalized = Math.min(avgAmplitude / 128, 1.0)
      // Apply easing — mulut tidak langsung buka penuh
      const eased = Math.pow(normalized, 0.7)

      setMouthOpen(eased)
      animFrameRef.current = requestAnimationFrame(update)
    }

    animFrameRef.current = requestAnimationFrame(update)
  }, [])

  const stopLipSync = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current)
      animFrameRef.current = null
    }
    setMouthOpen(0)
    setIsPlaying(false)
  }, [])

  /**
   * Play audio blob dengan lip sync.
   * @param {Blob} audioBlob - Audio dari TTS
   * @returns {Promise<void>}
   */
  const playWithLipSync = useCallback(async (audioBlob) => {
    const { ctx, analyser } = getAudioContext()

    // Resume context jika suspended (autoplay policy)
    if (ctx.state === 'suspended') await ctx.resume()

    try {
      const arrayBuffer = await audioBlob.arrayBuffer()
      const audioBuffer = await ctx.decodeAudioData(arrayBuffer)

      // Stop previous source
      if (sourceRef.current) {
        try { sourceRef.current.stop() } catch { /* noop */ }
      }

      const source = ctx.createBufferSource()
      source.buffer = audioBuffer
      source.connect(analyser)
      analyser.connect(ctx.destination)
      sourceRef.current = source

      return await new Promise((resolve) => {
        source.onended = () => {
          stopLipSync()
          resolve()
        }
        setIsPlaying(true)
        source.start()
        startLipSync()
      })
    } catch (err) {
      console.error('[LipSync]', err)
      stopLipSync()
      throw err
    }
  }, [getAudioContext, startLipSync, stopLipSync])

  /**
   * Stop current audio + lip sync
   */
  const stop = useCallback(() => {
    if (sourceRef.current) {
      try { sourceRef.current.stop() } catch { /* noop */ }
    }
    stopLipSync()
  }, [stopLipSync])

  return { mouthOpen, isPlaying, playWithLipSync, stop, unlock }
}
