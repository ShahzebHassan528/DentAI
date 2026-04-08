import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
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

export default function DoctorDashboard() {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [noteModal, setNoteModal] = useState(null) // { predictionId, existingNote }
  const [noteText, setNoteText] = useState('')
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')

  useEffect(() => {
    client.get('/predict/all')
      .then(res => setPredictions(res.data))
      .catch(() => addToast('Failed to load predictions.', 'error'))
      .finally(() => setLoading(false))
  }, [])

  async function saveNote() {
    if (!noteText.trim()) return
    setSaving(true)
    try {
      await client.post('/reports/', { prediction_id: noteModal.predictionId, doctor_notes: noteText })
      addToast('Notes saved successfully.', 'success')
      setNoteModal(null)
      setNoteText('')
    } catch {
      addToast('Failed to save notes.', 'error')
    } finally {
      setSaving(false)
    }
  }

  const filtered = predictions.filter(p =>
    p.patient?.name?.toLowerCase().includes(search.toLowerCase()) ||
    p.final_diagnosis?.toLowerCase().includes(search.toLowerCase())
  )

  const total = predictions.length
  const condCounts = predictions.reduce((acc, p) => { acc[p.final_diagnosis] = (acc[p.final_diagnosis] || 0) + 1; return acc }, {})
  const topCondition = Object.entries(condCounts).sort(([,a],[,b]) => b - a)[0]?.[0] || '—'

  return (
    <div style={{ minHeight: '100vh', background: '#eef2f7', paddingTop: '88px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '0 24px' }}>

        {/* Header */}
        <div className="anim-fade-up" style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <p style={{ color: '#0d9488', fontWeight: 700, fontSize: '0.7rem', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: '8px' }}>
              Doctor Dashboard
            </p>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.03em', marginBottom: '6px' }}>
              Patient Predictions
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>Review AI diagnoses and add clinical notes.</p>
          </div>
          <Link to="/metrics" style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            padding: '10px 20px', borderRadius: '12px', textDecoration: 'none',
            background: 'linear-gradient(135deg, #0d9488, #0891b2)',
            color: '#fff', fontWeight: 700, fontSize: '0.85rem',
            boxShadow: '0 2px 12px rgba(13,148,136,0.3)',
          }}>
            📊 Model Metrics
          </Link>
        </div>

        {/* Stats */}
        <div className="anim-fade-up" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '28px' }}>
          {[
            { label: 'Total Predictions', value: total,        icon: '📋', color: '#0d9488' },
            { label: 'Unique Patients',   value: new Set(predictions.map(p => p.patient?.id)).size, icon: '👥', color: '#0891b2' },
            { label: 'Most Common',       value: topCondition, icon: '🔍', color: '#6366f1', cap: true },
          ].map((s, i) => (
            <div key={i} style={{
              background: '#fff', border: '1px solid #e2e8f0', borderRadius: '16px',
              padding: '22px 24px', boxShadow: '0 4px 16px rgba(15,23,42,0.05)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <span style={{ fontSize: '1.3rem' }}>{s.icon}</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{s.label}</span>
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 900, color: s.color, letterSpacing: '-0.02em', textTransform: s.cap ? 'capitalize' : 'none' }}>
                {s.value}
              </div>
            </div>
          ))}
        </div>

        {/* Search */}
        <div className="anim-fade-up" style={{ marginBottom: '20px' }}>
          <input
            type="text" placeholder="Search by patient name or condition..."
            value={search} onChange={e => setSearch(e.target.value)}
            style={{
              width: '100%', padding: '13px 16px', borderRadius: '12px',
              border: '1.5px solid #e2e8f0', background: '#fff',
              fontSize: '0.93rem', color: '#0f172a', outline: 'none',
              fontFamily: 'Inter, sans-serif',
              transition: 'border-color 0.2s',
            }}
            onFocus={e => e.target.style.borderColor = '#0d9488'}
            onBlur={e => e.target.style.borderColor = '#e2e8f0'}
          />
        </div>

        {/* List */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', margin: '0 auto 12px', border: '3px solid #e2e8f0', borderTopColor: '#0d9488', animation: 'spin 0.8s linear infinite' }} />
            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Loading predictions...</p>
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '60px 24px', textAlign: 'center' }}>
            <p style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🔍</p>
            <p style={{ fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>No predictions found</p>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
              {predictions.length === 0 ? 'No patients have run diagnoses yet.' : 'Try a different search term.'}
            </p>
          </div>
        )}

        {!loading && filtered.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filtered.map((p, i) => {
              const c = CONDITION_STYLE[p.final_diagnosis] || CONDITION_STYLE.other
              const conf = Math.round(p.confidence * 100)
              return (
                <div key={p.id} className="anim-fade-up" style={{
                  animationDelay: `${i * 0.04}s`,
                  background: '#fff', border: '1px solid #e2e8f0', borderRadius: '16px',
                  padding: '20px 24px', transition: 'box-shadow 0.2s',
                }}
                  onMouseEnter={e => e.currentTarget.style.boxShadow = '0 8px 28px rgba(15,23,42,0.09)'}
                  onMouseLeave={e => e.currentTarget.style.boxShadow = 'none'}
                >
                  <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                    {/* Thumbnail */}
                    <div style={{
                      width: '64px', height: '64px', borderRadius: '12px', flexShrink: 0,
                      background: '#f8fafc', border: '1px solid #e2e8f0',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
                    }}>
                      {p.image_url
                        ? <img src={p.image_url} alt="xray" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        : <span style={{ fontSize: '1.6rem' }}>💬</span>
                      }
                    </div>

                    {/* Info */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '6px' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>
                          {p.patient?.name || 'Unknown'}
                        </span>
                        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>{p.patient?.email}</span>
                        <span style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>·</span>
                        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>{formatDate(p.created_at)}</span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
                        <span style={{
                          display: 'inline-flex', alignItems: 'center', gap: '6px',
                          padding: '4px 12px', borderRadius: '999px', fontSize: '0.78rem', fontWeight: 700,
                          background: c.bg, border: `1px solid ${c.border}`, color: c.color, textTransform: 'capitalize',
                        }}>
                          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: c.dot }} />
                          {p.final_diagnosis}
                        </span>
                        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#64748b' }}>{conf}% confidence</span>
                      </div>

                      {p.symptoms && (
                        <p style={{ fontSize: '0.83rem', color: '#94a3b8', lineHeight: 1.5,
                          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '500px' }}>
                          "{p.symptoms}"
                        </p>
                      )}
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: '8px', flexShrink: 0, alignSelf: 'center' }}>
                      <Link to={`/treatments/${p.final_diagnosis}`} style={{
                        padding: '8px 14px', borderRadius: '10px', fontSize: '0.78rem', fontWeight: 600,
                        border: '1.5px solid #e2e8f0', color: '#64748b', textDecoration: 'none',
                        transition: 'all 0.2s',
                      }}
                        onMouseEnter={e => { e.currentTarget.style.borderColor = '#99f6e4'; e.currentTarget.style.color = '#0d9488' }}
                        onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }}
                      >
                        Treatment
                      </Link>
                      <button onClick={() => { setNoteModal({ predictionId: p.id }); setNoteText('') }}
                        style={{
                          padding: '8px 14px', borderRadius: '10px', fontSize: '0.78rem', fontWeight: 600,
                          border: '1.5px solid #0d9488', color: '#0d9488', background: '#f0fdfa',
                          cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'Inter, sans-serif',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = '#ccfbf1' }}
                        onMouseLeave={e => { e.currentTarget.style.background = '#f0fdfa' }}
                      >
                        + Add Note
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Note Modal */}
      {noteModal && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 1000,
          background: 'rgba(15,23,42,0.5)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px',
        }} onClick={e => { if (e.target === e.currentTarget) setNoteModal(null) }}>
          <div className="anim-fade-up" style={{
            background: '#fff', borderRadius: '20px', padding: '32px',
            width: '100%', maxWidth: '480px',
            boxShadow: '0 24px 64px rgba(15,23,42,0.2)',
          }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginBottom: '6px' }}>Add Clinical Notes</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '20px' }}>
              Prediction #{noteModal.predictionId}
            </p>
            <textarea
              value={noteText}
              onChange={e => setNoteText(e.target.value)}
              rows={5}
              placeholder="Enter your clinical observations, recommendations, or follow-up instructions..."
              style={{
                width: '100%', padding: '14px', borderRadius: '12px',
                border: '1.5px solid #e2e8f0', fontSize: '0.9rem',
                fontFamily: 'Inter, sans-serif', resize: 'vertical', outline: 'none',
                lineHeight: 1.7, color: '#0f172a', background: '#f8fafc',
                transition: 'border-color 0.2s',
              }}
              onFocus={e => e.target.style.borderColor = '#0d9488'}
              onBlur={e => e.target.style.borderColor = '#e2e8f0'}
            />
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px', justifyContent: 'flex-end' }}>
              <button onClick={() => setNoteModal(null)} style={{
                padding: '11px 22px', borderRadius: '10px', border: '1.5px solid #e2e8f0',
                background: 'transparent', color: '#64748b', fontWeight: 600,
                fontSize: '0.875rem', cursor: 'pointer', fontFamily: 'Inter, sans-serif',
              }}>
                Cancel
              </button>
              <button onClick={saveNote} disabled={saving || !noteText.trim()} className="btn-primary" style={{
                padding: '11px 28px', fontSize: '0.875rem',
                opacity: saving || !noteText.trim() ? 0.6 : 1,
                cursor: saving || !noteText.trim() ? 'not-allowed' : 'pointer',
              }}>
                {saving ? 'Saving...' : 'Save Notes'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
