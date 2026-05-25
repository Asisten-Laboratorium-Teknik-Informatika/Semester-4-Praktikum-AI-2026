import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

// Demo data — will be replaced by real API data
const DEMO_DATA = [
  { day: 'Sen', mood: 6, sleep: 7 },
  { day: 'Sel', mood: 5, sleep: 6 },
  { day: 'Rab', mood: 4, sleep: 5 },
  { day: 'Kam', mood: 5, sleep: 6 },
  { day: 'Jum', mood: 6, sleep: 7 },
  { day: 'Sab', mood: 7, sleep: 8 },
  { day: 'Min', mood: 6, sleep: 7 },
]

export default function MoodTrendChart({ data }) {
  const chartData = data && data.length > 0 ? data : DEMO_DATA
  const hasRealData = data && data.length > 0

  return (
    <div className="rounded-2xl p-5"
      style={{ background: 'var(--color-surface)', boxShadow: 'var(--shadow-sm)', border: '1px solid var(--color-border-soft)' }}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-semibold font-display" style={{ color: 'var(--color-text-secondary)' }}>
          Tren 7 Hari
        </span>
        {!hasRealData && (
          <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--color-accent-soft)', color: 'var(--color-accent)' }}>
            Demo
          </span>
        )}
      </div>

      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-soft)" />
          <XAxis
            dataKey="day"
            tick={{ fill: 'var(--color-text-tertiary)', fontSize: 12 }}
            axisLine={{ stroke: 'var(--color-border)' }}
          />
          <YAxis
            domain={[0, 10]}
            tick={{ fill: 'var(--color-text-tertiary)', fontSize: 12 }}
            axisLine={{ stroke: 'var(--color-border)' }}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 12,
              fontSize: 13,
            }}
          />
          <Line
            type="monotone"
            dataKey="mood"
            stroke="var(--color-primary)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: 'var(--color-primary)' }}
            activeDot={{ r: 6, fill: 'var(--color-primary)' }}
            name="Mood"
          />
          <Line
            type="monotone"
            dataKey="sleep"
            stroke="var(--color-accent)"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3, fill: 'var(--color-accent)' }}
            name="Tidur (jam)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
