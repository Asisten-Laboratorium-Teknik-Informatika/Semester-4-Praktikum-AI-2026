/**
 * Dashboard — Halaman insight & trend burnout user.
 *
 * Menampilkan:
 *   - Risk level saat ini + score bar
 *   - Trend 7 hari (mood + tidur)
 *   - Top factors dari SHAP
 *   - Rekomendasi personal
 *   - Disclaimer etika
 */
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, RefreshCw, Calendar, Activity, Shield, AlertTriangle, TrendingDown, Lightbulb, Info } from 'lucide-react'
import { Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts'
import { dashboardApi } from '../services/api'
import useUserStore from '../store/userStore'

const RISK_CONFIG = {
  LOW: { label: 'Kondisi Baik', icon: Shield, color: 'var(--color-risk-low)', pct: 25 },
  MEDIUM: { label: 'Perlu Perhatian', icon: AlertTriangle, color: 'var(--color-risk-medium)', pct: 55 },
  HIGH: { label: 'Perlu Tindakan', icon: TrendingDown, color: 'var(--color-risk-high)', pct: 85 },
}

export default function Dashboard() {
  const userId = useUserStore((s) => s.userId)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await dashboardApi.get(userId)
      setData(res.data)
    } catch (err) {
      setError('Gagal memuat data dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [userId])

  const riskCfg = data?.risk_level ? RISK_CONFIG[data.risk_level] : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-screen bg-animated"
    >
      <div style={{ maxWidth: 640, margin: '0 auto', padding: 24 }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28 }}>
          <Link to="/"
            style={{
              width: 36, height: 36, borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--color-surface)', color: 'var(--color-text-secondary)',
              textDecoration: 'none', border: '1px solid var(--color-border-soft)',
            }}>
            <ArrowLeft size={18} />
          </Link>
          <h1 style={{
            fontSize: 20, fontWeight: 700, color: 'var(--color-text)',
            fontFamily: 'var(--font-display)', flex: 1,
          }}>
            Dashboard
          </h1>
          <motion.button
            whileTap={{ scale: 0.9, rotate: 180 }}
            onClick={fetchData}
            style={{
              width: 36, height: 36, borderRadius: 10, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--color-surface)', color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-border-soft)',
            }}
          >
            <RefreshCw size={16} />
          </motion.button>
        </div>

        {/* Loading state */}
        {loading && (
          <div style={{
            textAlign: 'center', padding: 60,
            color: 'var(--color-text-tertiary)', fontSize: 14,
          }}>
            <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px' }} />
            Memuat data...
          </div>
        )}

        {/* Error state */}
        {error && (
          <div style={{
            textAlign: 'center', padding: 40,
            color: 'var(--color-risk-high)', fontSize: 14,
          }}>
            {error}
          </div>
        )}

        {/* No data state */}
        {!loading && !error && (!data || data?.status === 'no_data') && (
          <div style={{
            textAlign: 'center', padding: 60,
            color: 'var(--color-text-tertiary)', fontSize: 14,
          }}>
            <Activity size={32} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
            <p style={{ fontWeight: 500, marginBottom: 8 }}>Belum ada data</p>
            <p>Mulai ngobrol dengan RINA dulu untuk melihat insight.</p>
            <Link to="/" style={{
              display: 'inline-block', marginTop: 16, padding: '8px 20px',
              borderRadius: 20, background: 'var(--color-primary)',
              color: 'white', textDecoration: 'none', fontSize: 13, fontWeight: 500,
            }}>
              Mulai Chat
            </Link>
          </div>
        )}

        {/* Dashboard content */}
        {!loading && !error && data?.status === 'ok' && (
          <motion.div
            initial="hidden"
            animate="visible"
            variants={{ visible: { transition: { staggerChildren: 0.08 } } }}
            style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
          >
            {/* Risk Card */}
            <motion.div
              variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}
              style={{
                borderRadius: 16, padding: 20,
                background: 'var(--color-surface)',
                boxShadow: 'var(--shadow-sm)',
                border: '1px solid var(--color-border-soft)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  Kondisi Saat Ini
                </span>
                {riskCfg && (
                  <motion.div
                    animate={{ scale: [1, 1.04, 1] }}
                    transition={{ duration: 2.5, repeat: Infinity }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 6,
                      padding: '4px 12px', borderRadius: 20,
                      background: riskCfg.color + '18', color: riskCfg.color,
                      fontSize: 12, fontWeight: 600,
                    }}
                  >
                    <riskCfg.icon size={13} />
                    {riskCfg.label}
                  </motion.div>
                )}
              </div>

              {/* Score bar */}
              <div style={{
                width: '100%', height: 8, borderRadius: 8,
                background: 'var(--color-surface-raised)', marginBottom: 16,
              }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${riskCfg?.pct || 0}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                  style={{
                    height: '100%', borderRadius: 8,
                    background: riskCfg?.color || 'var(--color-border)',
                  }}
                />
              </div>

              {/* Top factors */}
              {data.top_factors?.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {data.top_factors.map((f, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'start', gap: 8, fontSize: 13 }}>
                      <span style={{
                        width: 6, height: 6, borderRadius: '50%', marginTop: 6, flexShrink: 0,
                        background: 'var(--color-primary)',
                      }} />
                      <span style={{ color: 'var(--color-text-secondary)' }}>{f}</span>
                    </div>
                  ))}
                </div>
              )}

              <div style={{
                marginTop: 16, paddingTop: 12, fontSize: 12,
                borderTop: '1px solid var(--color-border-soft)',
                color: 'var(--color-text-tertiary)',
                display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <Calendar size={13} />
                Hari ke-{data.days_tracked} tracking
              </div>
            </motion.div>

            {/* Mood Trend Chart */}
            <motion.div
              variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}
              style={{
                borderRadius: 16, padding: 20,
                background: 'var(--color-surface)',
                boxShadow: 'var(--shadow-sm)',
                border: '1px solid var(--color-border-soft)',
              }}
            >
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: 16 }}>
                Tren 7 Hari Terakhir
              </span>

              {data.averages ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 16 }}>
                  {[
                    { label: 'Mood', value: data.averages.mood_score, max: 10 },
                    { label: 'Tidur', value: data.averages.sleep_hours, max: 12, unit: 'jam' },
                    { label: 'Beban', value: data.averages.workload_score, max: 10 },
                  ].map((stat) => (
                    <div key={stat.label} style={{
                      padding: '12px 8px', borderRadius: 12, textAlign: 'center',
                      background: 'var(--color-primary-subtle)',
                    }}>
                      <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--color-primary)' }}>
                        {stat.value != null ? Number(stat.value).toFixed(1) : '—'}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)', marginTop: 2 }}>
                        {stat.label}{stat.unit ? ` (${stat.unit})` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: 13, color: 'var(--color-text-tertiary)' }}>
                  Belum cukup data untuk menampilkan tren.
                </p>
              )}
            </motion.div>

            {/* Recommendations */}
            {data.recommendations?.length > 0 && (
              <motion.div
                variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}
                style={{
                  borderRadius: 16, padding: 20,
                  background: 'var(--color-surface)',
                  boxShadow: 'var(--shadow-sm)',
                  border: '1px solid var(--color-border-soft)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                  <Lightbulb size={15} style={{ color: 'var(--color-accent)' }} />
                  <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                    Saran untuk Kamu
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {data.recommendations.map((rec, i) => (
                    <div key={i} style={{
                      padding: 14, borderRadius: 12,
                      background: 'var(--color-primary-subtle)',
                    }}>
                      <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-primary)', marginBottom: 4 }}>
                        {rec.title}
                      </p>
                      <p style={{ fontSize: 12, color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                        {rec.tip}
                      </p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Disclaimer */}
            <motion.div
              variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}
              style={{
                borderRadius: 12, padding: 14,
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border-soft)',
                display: 'flex', alignItems: 'start', gap: 10,
              }}
            >
              <Info size={15} style={{ color: 'var(--color-text-tertiary)', marginTop: 1, flexShrink: 0 }} />
              <p style={{ fontSize: 11, color: 'var(--color-text-tertiary)', lineHeight: 1.6 }}>
                {data.disclaimer || 'Ini adalah estimasi berdasarkan pola percakapan, bukan diagnosis medis. Konsultasikan dengan profesional jika kamu merasa perlu dukungan lebih.'}
              </p>
            </motion.div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
