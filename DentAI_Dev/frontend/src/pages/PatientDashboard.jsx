import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

const CONDITION_STYLE = {
  cavity:    { color: '#92400e', bg: '#fffbeb', border: '#fde68a', dot: '#f59e0b' },
  healthy:   { color: '#065f46', bg: '#ecfdf5', border: '#6ee7b7', dot: '#10b981' },
  impacted:  { color: '#9a3412', bg: '#fff7ed', border: '#fdba74', dot: '#f97316' },
  infection: { color: '#991b1b', bg: '#fef2f2', border: '#fca5a5', dot: '#ef4444' },
  other:     { color: '#334155', bg: '#f8fafc', border: '#cbd5e1', dot: '#64748b' },
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function PatientDashboard() {
  const { user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client.get('/predict/history')
      .then(res => setHistory(res.data))
      .catch(() => setHistory([]))
      .finally(() => setLoading(false))
  }, [])

  const total = history.length
  const avgConf = total ? Math.round(history.reduce((a, p) => a + p.confidence, 0) / total * 100) : 0
  const latest = history[0]

  return (
    <div style={{ minHeight: '100vh', background: '#eef2f7', paddingTop: '88px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '0 24px' }}>

        {/* Header */}
        <div className="anim-fade-up" style={{ marginBottom: '32px' }}>
          <p style={{ color: '#0d9488', fontWeight: 700, fontSize: '0.7rem', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: '8px' }}>
            Patient Dashboard
          </p>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.03em', marginBottom: '6px' }}>
            Welcome back, {user?.name}
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>Here's your dental diagnosis history.</p>
        </div>

        {/* Stats row */}
        <div className="anim-fade-up" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '28px' }}>
          {[
            { label: 'Total Diagnoses', value: total, icon: '🦷', color: '#0d9488' },
            { label: 'Avg Confidence',  value: total ? `${avgConf}%` : '—', icon: '📊', color: '#0891b2' },
            { label: 'Latest Result',   value: latest ? latest.final_diagnosis : '—', icon: '✅', color: '#6366f1', capitalize: true },
          ].map((s, i) => (
            <div key={i} style={{
              background: '#fff', border: '1px solid #e2e8f0', borderRadius: '16px',
              padding: '22px 24px', boxShadow: '0 4px 16px rgba(15,23,42,0.05)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <span style={{ fontSize: '1.3rem' }}>{s.icon}</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{s.label}</span>
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 900, color: s.color, letterSpacing: '-0.02em', textTransform: s.capitalize ? 'capitalize' : 'none' }}>
                {s.value}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="anim-fade-up" style={{ marginBottom: '28px' }}>
          <Link to="/predict" className="btn-primary" style={{ fontSize: '0.9rem', padding: '12px 28px' }}>
            + New Diagnosis
          </Link>
        </div>

        {/* History list */}
        <div className="anim-fade-up">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f172a', marginBottom: '16px', letterSpacing: '-0.01em' }}>
            Diagnosis History
          </h2>

          {loading && (
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '50%', margin: '0 auto 12px', border: '3px solid #e2e8f0', borderTopColor: '#0d9488', animation: 'spin 0.8s linear infinite' }} />
              <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Loading history...</p>
            </div>
          )}

          {!loading && history.length === 0 && (
            <div style={{
              background: '#fff', border: '1px solid #e2e8f0', borderRadius: '16px',
              padding: '60px 24px', textAlign: 'center',
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🦷</div>
              <p style={{ fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>No diagnoses yet</p>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '24px' }}>Run your first diagnosis to see results here.</p>
              <Link to="/predict" className="btn-primary" style={{ fontSize: '0.9rem', padding: '12px 28px' }}>Start Diagnosis</Link>
            </div>
          )}

          {!loading && history.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {history.map((p, i) => {
                const c = CONDITION_STYLE[p.final_diagnosis] || CONDITION_STYLE.other
                const conf = Math.round(p.confidence * 100)
                return (
                  <div key={p.id} className="anim-fade-up" style={{
                    animationDelay: `${i * 0.05}s`,
                    background: '#fff', border: '1px solid #e2e8f0', borderRadius: '16px',
                    padding: '20px 24px',
                    transition: 'box-shadow 0.2s, border-color 0.2s',
                  }}
                    onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 8px 28px rgba(15,23,42,0.09)'; e.currentTarget.style.borderColor = c.border }}
                    onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.borderColor = '#e2e8f0' }}
                  >
                    {/* Flex row: thumbnail + info + action */}
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                      {/* Thumbnail */}
                      <div style={{
                        width: '72px', height: '72px', borderRadius: '12px', flexShrink: 0, overflow: 'hidden',
                        background: '#f8fafc', border: '1px solid #e2e8f0',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        {p.image_url
                          ? <img src={p.image_url} alt="xray" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          : <span style={{ fontSize: '1.8rem' }}>💬</span>
                        }
                      </div>

                      {/* Info */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
                          <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '6px',
                            padding: '4px 12px', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 700,
                            background: c.bg, border: `1px solid ${c.border}`, color: c.color, textTransform: 'capitalize',
                          }}>
                            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: c.dot }} />
                            {p.final_diagnosis}
                          </span>
                          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>{formatDate(p.created_at)}</span>
                        </div>

                        {p.symptoms && (
                          <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5, marginBottom: '8px',
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '500px' }}>
                            "{p.symptoms}"
                          </p>
                        )}

                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <div style={{ flex: 1, maxWidth: '200px', background: '#f1f5f9', borderRadius: '999px', height: '5px', overflow: 'hidden' }}>
                            <div style={{ height: '100%', background: c.dot, width: `${conf}%`, borderRadius: '999px' }} />
                          </div>
                          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#475569' }}>{conf}% confidence</span>
                        </div>
                      </div>

                      {/* Action */}
                      <Link to={`/treatments/${p.final_diagnosis}`} style={{
                        flexShrink: 0, padding: '8px 16px', borderRadius: '10px',
                        border: '1.5px solid #e2e8f0', color: '#64748b', fontSize: '0.8rem',
                        fontWeight: 600, textDecoration: 'none', transition: 'all 0.2s',
                        alignSelf: 'center',
                      }}
                        onMouseEnter={e => { e.currentTarget.style.borderColor = '#99f6e4'; e.currentTarget.style.color = '#0d9488' }}
                        onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }}
                      >
                        Treatment →
                      </Link>
                    </div>

                    {/* Doctor Note — inside the card */}
                    {p.doctor_note && (
                      <div style={{
                        marginTop: '14px', padding: '14px 16px', borderRadius: '12px',
                        background: '#f0fdfa', border: '1.5px solid #99f6e4',
                        display: 'flex', gap: '12px', alignItems: 'flex-start',
                      }}>
                        <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>👨‍⚕️</span>
                        <div>
                          <p style={{ fontSize: '0.72rem', fontWeight: 800, color: '#0d9488', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '5px' }}>
                            Doctor's Note
                            {p.reviewed_at && (
                              <span style={{ fontWeight: 500, color: '#94a3b8', marginLeft: '8px', textTransform: 'none', letterSpacing: 0 }}>
                                · {formatDate(p.reviewed_at)}
                              </span>
                            )}
                          </p>
                          <p style={{ fontSize: '0.875rem', color: '#0f172a', lineHeight: 1.65 }}>
                            {p.doctor_note}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
