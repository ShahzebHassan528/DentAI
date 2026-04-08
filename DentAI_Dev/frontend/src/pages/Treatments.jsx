import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import client from '../api/client'

const CONDITION_STYLE = {
  cavity:    { color: '#92400e', bg: '#fffbeb', border: '#fde68a', bar: '#f59e0b', icon: '🦷', light: '#fef9c3' },
  healthy:   { color: '#065f46', bg: '#ecfdf5', border: '#6ee7b7', bar: '#10b981', icon: '✅', light: '#d1fae5' },
  impacted:  { color: '#9a3412', bg: '#fff7ed', border: '#fdba74', bar: '#f97316', icon: '😬', light: '#ffedd5' },
  infection: { color: '#991b1b', bg: '#fef2f2', border: '#fca5a5', bar: '#ef4444', icon: '⚠️', light: '#fee2e2' },
  other:     { color: '#334155', bg: '#f8fafc', border: '#cbd5e1', bar: '#64748b', icon: '❓', light: '#f1f5f9' },
}

export default function Treatments() {
  const { condition } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const c = CONDITION_STYLE[condition] || CONDITION_STYLE.other

  useEffect(() => {
    setLoading(true)
    setError('')
    client.get(`/treatments/${condition}`)
      .then(res => setData(res.data))
      .catch(() => setError('Treatment data not found for this condition.'))
      .finally(() => setLoading(false))
  }, [condition])

  return (
    <div style={{ minHeight: '100vh', background: '#eef2f7', paddingTop: '88px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '760px', margin: '0 auto', padding: '0 24px' }}>

        {/* Back */}
        <Link to="/predict" style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px',
          color: '#94a3b8', fontSize: '0.85rem', fontWeight: 600,
          textDecoration: 'none', marginBottom: '28px',
          transition: 'color 0.2s',
        }}
          onMouseEnter={e => e.currentTarget.style.color = '#0d9488'}
          onMouseLeave={e => e.currentTarget.style.color = '#94a3b8'}
        >
          ← Back to Diagnosis
        </Link>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <div style={{
              width: '40px', height: '40px', borderRadius: '50%', margin: '0 auto 16px',
              border: '3px solid #e2e8f0', borderTopColor: '#0d9488',
              animation: 'spin 0.8s linear infinite',
            }} />
            <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>Loading treatment guide...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            background: '#fef2f2', border: '1.5px solid #fca5a5', borderRadius: '14px',
            padding: '20px 24px', color: '#b91c1c', fontWeight: 500,
          }}>
            {error}
          </div>
        )}

        {data && (
          <>
            {/* ── Hero Card ── */}
            <div className="anim-fade-up" style={{
              background: c.bg, border: `1.5px solid ${c.border}`,
              borderRadius: '20px', padding: '32px', marginBottom: '20px',
              boxShadow: '0 8px 32px rgba(15,23,42,0.07)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '18px', marginBottom: '16px' }}>
                <div style={{
                  width: '64px', height: '64px', borderRadius: '18px', fontSize: '2rem',
                  background: '#fff', border: `1.5px solid ${c.border}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.06)', flexShrink: 0,
                }}>
                  {c.icon}
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '4px' }}>
                    Treatment Guide
                  </p>
                  <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: c.color, letterSpacing: '-0.025em', lineHeight: 1.1 }}>
                    {data.condition}
                  </h1>
                </div>
              </div>
              <p style={{ color: '#64748b', fontSize: '0.95rem', lineHeight: 1.75, padding: '14px 16px', background: '#fff', borderRadius: '12px', border: `1px solid ${c.border}` }}>
                {data.severity_note}
              </p>
            </div>

            {/* ── Treatments ── */}
            <div className="anim-fade-up" style={{
              background: '#fff', border: '1px solid #e2e8f0',
              borderRadius: '20px', padding: '28px', marginBottom: '20px',
              boxShadow: '0 4px 16px rgba(15,23,42,0.05)',
            }}>
              <SectionLabel icon="💊" label="Treatment Options" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {data.treatments?.map((t, i) => (
                  <div key={i} style={{
                    padding: '18px 20px', borderRadius: '14px',
                    background: '#f8fafc', border: '1px solid #e2e8f0',
                    transition: 'border-color 0.2s',
                  }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = c.bar + '80'}
                    onMouseLeave={e => e.currentTarget.style.borderColor = '#e2e8f0'}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                      <div style={{
                        width: '28px', height: '28px', borderRadius: '8px', flexShrink: 0,
                        background: c.light, border: `1px solid ${c.border}`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.78rem', fontWeight: 800, color: c.color,
                      }}>
                        {i + 1}
                      </div>
                      <div>
                        <p style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a', marginBottom: '4px' }}>
                          {t.name}
                        </p>
                        <p style={{ color: '#64748b', fontSize: '0.875rem', lineHeight: 1.65 }}>
                          {t.description}
                        </p>
                        {t.when && (
                          <p style={{ marginTop: '6px', fontSize: '0.78rem', color: '#94a3b8', fontStyle: 'italic' }}>
                            When: {t.when}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ── Home Care ── */}
            {data.home_care?.length > 0 && (
              <div className="anim-fade-up" style={{
                background: '#fff', border: '1px solid #e2e8f0',
                borderRadius: '20px', padding: '28px', marginBottom: '20px',
                boxShadow: '0 4px 16px rgba(15,23,42,0.05)',
              }}>
                <SectionLabel icon="🏠" label="Home Care Tips" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {data.home_care.map((tip, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '12px 0', borderBottom: i < data.home_care.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                      <span style={{
                        width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0, marginTop: '1px',
                        background: '#f0fdfa', border: '1px solid #99f6e4',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.65rem', fontWeight: 800, color: '#0d9488',
                      }}>✓</span>
                      <p style={{ color: '#475569', fontSize: '0.9rem', lineHeight: 1.65 }}>{tip}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── Prevention ── */}
            {data.prevention?.length > 0 && (
              <div className="anim-fade-up" style={{
                background: '#fff', border: '1px solid #e2e8f0',
                borderRadius: '20px', padding: '28px', marginBottom: '20px',
                boxShadow: '0 4px 16px rgba(15,23,42,0.05)',
              }}>
                <SectionLabel icon="🛡️" label="Prevention" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {data.prevention.map((tip, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '12px 0', borderBottom: i < data.prevention.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                      <span style={{
                        width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0, marginTop: '1px',
                        background: '#eff6ff', border: '1px solid #bfdbfe',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.65rem', fontWeight: 800, color: '#1d4ed8',
                      }}>✓</span>
                      <p style={{ color: '#475569', fontSize: '0.9rem', lineHeight: 1.65 }}>{tip}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── When to see dentist ── */}
            {data.when_to_see_dentist && (
              <div className="anim-fade-up" style={{
                background: '#fffbeb', border: '1.5px solid #fde68a',
                borderRadius: '20px', padding: '24px 28px', marginBottom: '20px',
              }}>
                <SectionLabel icon="🏥" label="When to See a Dentist" color="#92400e" />
                <p style={{ color: '#78350f', fontSize: '0.92rem', lineHeight: 1.75 }}>
                  {data.when_to_see_dentist}
                </p>
              </div>
            )}

            {/* ── CTA ── */}
            <div className="anim-fade-up" style={{
              background: 'linear-gradient(135deg, #f0fdfa, #e0f2fe)',
              border: '1.5px solid #99f6e4', borderRadius: '20px',
              padding: '28px', textAlign: 'center',
              boxShadow: '0 4px 20px rgba(13,148,136,0.08)',
            }}>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>
                Need a second opinion?
              </p>
              <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '20px' }}>
                Run a new diagnosis or consult a dentist for professional advice.
              </p>
              <Link to="/predict" className="btn-primary" style={{ fontSize: '0.9rem', padding: '12px 28px' }}>
                Run Another Diagnosis
              </Link>
            </div>
          </>
        )}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

function SectionLabel({ icon, label, color = '#0d9488' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px' }}>
      <span style={{ fontSize: '1.1rem' }}>{icon}</span>
      <p style={{ fontSize: '0.7rem', fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', color }}>
        {label}
      </p>
    </div>
  )
}
