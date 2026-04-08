const CONDITIONS = {
  cavity:    { color: '#92400e', bg: '#fffbeb', border: '#fde68a', bar: '#f59e0b', icon: '🦷' },
  healthy:   { color: '#065f46', bg: '#ecfdf5', border: '#6ee7b7', bar: '#10b981', icon: '✅' },
  impacted:  { color: '#9a3412', bg: '#fff7ed', border: '#fdba74', bar: '#f97316', icon: '😬' },
  infection: { color: '#991b1b', bg: '#fef2f2', border: '#fca5a5', bar: '#ef4444', icon: '⚠️' },
  other:     { color: '#334155', bg: '#f8fafc', border: '#cbd5e1', bar: '#64748b', icon: '❓' },
}

const ALL_BAR_COLORS = {
  cavity: '#f59e0b', healthy: '#10b981', impacted: '#f97316', infection: '#ef4444', other: '#64748b',
}

export default function PredictionResult({ result }) {
  if (!result) return null

  const diagnosis = result.final_diagnosis || result.diagnosis
  const c = CONDITIONS[diagnosis] || CONDITIONS.other
  const confidence = Math.round((result.confidence || 0) * 100)
  const probabilities = result.probabilities || {}
  const mode = result.mode || 'image'

  return (
    <div style={{
      background: '#fff', border: `1.5px solid ${c.border}`,
      borderRadius: '20px', overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(15,23,42,0.08)',
    }}>
      {/* Top banner */}
      <div style={{ background: c.bg, padding: '24px 28px', borderBottom: `1px solid ${c.border}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '64px', height: '64px', borderRadius: '18px', fontSize: '2rem',
            background: '#fff', border: `1.5px solid ${c.border}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.06)', flexShrink: 0,
          }}>
            {c.icon}
          </div>
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '4px' }}>
              Diagnosis Result
            </p>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 900, color: c.color, letterSpacing: '-0.02em', textTransform: 'capitalize', marginBottom: '6px' }}>
              {diagnosis}
            </h2>
            <span style={{
              display: 'inline-block', padding: '3px 12px', borderRadius: '999px', fontSize: '0.72rem',
              fontWeight: 700, letterSpacing: '0.06em', textTransform: 'capitalize',
              background: '#fff', border: `1px solid ${c.border}`, color: c.color,
            }}>
              {mode.replace('_', ' ')} prediction
            </span>
          </div>
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '2px' }}>
              Confidence
            </p>
            <p style={{ fontSize: '2.4rem', fontWeight: 900, color: c.color, lineHeight: 1, letterSpacing: '-0.03em' }}>
              {confidence}%
            </p>
          </div>
        </div>

        {/* Confidence bar */}
        <div style={{ marginTop: '18px' }}>
          <div style={{ background: '#e2e8f0', borderRadius: '999px', height: '6px', overflow: 'hidden' }}>
            <div style={{
              height: '100%', borderRadius: '999px', background: c.bar,
              width: `${confidence}%`, transition: 'width 1s cubic-bezier(0.22,1,0.36,1)',
            }} />
          </div>
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: '24px 28px' }}>

        {/* Model breakdown (combined) */}
        {result.image_diagnosis && result.text_diagnosis && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '24px' }}>
            {[
              { label: 'Image Model', value: result.image_diagnosis, icon: '🦷' },
              { label: 'Symptom Model', value: Array.isArray(result.text_diagnosis) ? result.text_diagnosis[0] : result.text_diagnosis, icon: '💬' },
            ].map((m, i) => (
              <div key={i} style={{
                background: '#f8fafc', border: '1px solid #e2e8f0',
                borderRadius: '12px', padding: '14px 16px',
              }}>
                <p style={{ fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '6px' }}>
                  {m.icon} {m.label}
                </p>
                <p style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a', textTransform: 'capitalize' }}>
                  {m.value}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Probability bars */}
        <div>
          <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '14px' }}>
            All Probabilities
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(probabilities)
              .sort(([, a], [, b]) => b - a)
              .map(([cls, prob]) => {
                const pct = Math.round(prob * 100)
                const barColor = ALL_BAR_COLORS[cls] || '#64748b'
                return (
                  <div key={cls} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ width: '72px', fontSize: '0.82rem', fontWeight: 600, color: '#475569', textTransform: 'capitalize', flexShrink: 0 }}>
                      {cls}
                    </span>
                    <div style={{ flex: 1, background: '#f1f5f9', borderRadius: '999px', height: '6px', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%', borderRadius: '999px', background: barColor,
                        width: `${pct}%`, transition: 'width 0.8s ease',
                      }} />
                    </div>
                    <span style={{ width: '36px', textAlign: 'right', fontSize: '0.82rem', fontWeight: 700, color: '#475569', flexShrink: 0 }}>
                      {pct}%
                    </span>
                  </div>
                )
              })}
          </div>
        </div>

        {/* Disclaimer */}
        <div style={{
          marginTop: '20px', padding: '12px 16px', borderRadius: '10px',
          background: '#f8fafc', border: '1px solid #e2e8f0',
          display: 'flex', gap: '10px', alignItems: 'flex-start',
        }}>
          <span style={{ fontSize: '1rem', flexShrink: 0 }}>ℹ️</span>
          <p style={{ fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.6 }}>
            This AI result is for informational purposes only. Always consult a qualified dentist for professional diagnosis and treatment.
          </p>
        </div>
      </div>
    </div>
  )
}
