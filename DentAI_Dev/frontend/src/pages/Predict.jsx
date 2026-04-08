import { useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'
import ImageUpload from '../components/ImageUpload'
import SymptomInput from '../components/SymptomInput'
import PredictionResult from '../components/PredictionResult'
import { useAuth } from '../context/AuthContext'

const TABS = [
  { key: 'combined', icon: '🔀', label: 'Combined',  desc: 'Image + Symptoms' },
  { key: 'image',    icon: '🦷', label: 'X-Ray',     desc: 'Image only' },
  { key: 'text',     icon: '💬', label: 'Symptoms',  desc: 'Text only' },
]

export default function Predict() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('combined')
  const [imageFile, setImageFile] = useState(null)
  const [symptoms, setSymptoms] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)

    if (activeTab === 'image' && !imageFile) return setError('Please select an X-ray image.')
    if (activeTab === 'text' && symptoms.trim().length < 3) return setError('Please describe your symptoms.')
    if (activeTab === 'combined' && !imageFile && symptoms.trim().length < 3) return setError('Please provide an image or symptom description.')

    setLoading(true)
    try {
      let res
      if (activeTab === 'image') {
        const fd = new FormData(); fd.append('file', imageFile)
        res = await client.post('/predict/image', fd)
      } else if (activeTab === 'text') {
        res = await client.post('/predict/text', { symptoms })
      } else {
        const fd = new FormData()
        if (imageFile) fd.append('file', imageFile)
        if (symptoms.trim()) fd.append('symptoms', symptoms)
        res = await client.post('/predict/combined', fd)
      }
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#eef2f7', paddingTop: '88px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '680px', margin: '0 auto', padding: '0 24px' }}>

        {/* ── Page Header ── */}
        <div className="anim-fade-up" style={{ marginBottom: '32px' }}>
          <p style={{ color: '#0d9488', fontWeight: 700, fontSize: '0.7rem', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: '8px' }}>
            AI Diagnosis
          </p>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.03em', marginBottom: '6px' }}>
            Start Your Diagnosis
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            Welcome back, <span style={{ color: '#0d9488', fontWeight: 600 }}>{user?.name}</span>. Choose an input method below.
          </p>
        </div>

        {/* ── Tabs ── */}
        <div className="anim-fade-up" style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '24px',
        }}>
          {TABS.map(tab => (
            <button key={tab.key} onClick={() => { setActiveTab(tab.key); setResult(null); setError('') }}
              style={{
                padding: '14px 12px', borderRadius: '14px', border: '1.5px solid',
                borderColor: activeTab === tab.key ? '#0d9488' : '#e2e8f0',
                background: activeTab === tab.key ? '#f0fdfa' : '#fff',
                cursor: 'pointer', textAlign: 'center',
                transition: 'all 0.2s',
                boxShadow: activeTab === tab.key ? '0 4px 16px rgba(13,148,136,0.12)' : 'none',
              }}>
              <div style={{ fontSize: '1.4rem', marginBottom: '4px' }}>{tab.icon}</div>
              <div style={{ fontWeight: 700, fontSize: '0.88rem', color: activeTab === tab.key ? '#0f766e' : '#334155' }}>
                {tab.label}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '2px' }}>{tab.desc}</div>
            </button>
          ))}
        </div>

        {/* ── Form Card ── */}
        <div className="anim-fade-up" style={{
          background: '#fff', border: '1px solid #e2e8f0',
          borderRadius: '20px', padding: '32px',
          boxShadow: '0 8px 32px rgba(15,23,42,0.07)',
          marginBottom: '20px',
        }}>
          <form onSubmit={handleSubmit}>
            {(activeTab === 'image' || activeTab === 'combined') && (
              <div style={{ marginBottom: activeTab === 'combined' ? '20px' : '24px' }}>
                <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '10px', letterSpacing: '0.02em' }}>
                  DENTAL X-RAY IMAGE {activeTab === 'combined' && <span style={{ color: '#94a3b8', fontWeight: 500 }}>(optional)</span>}
                </label>
                <ImageUpload onFileSelect={setImageFile} />
              </div>
            )}

            {(activeTab === 'text' || activeTab === 'combined') && (
              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '10px', letterSpacing: '0.02em' }}>
                  DESCRIBE YOUR SYMPTOMS {activeTab === 'combined' && <span style={{ color: '#94a3b8', fontWeight: 500 }}>(optional)</span>}
                </label>
                <SymptomInput value={symptoms} onChange={setSymptoms} />
              </div>
            )}

            {error && (
              <div style={{
                background: '#fef2f2', border: '1.5px solid #fca5a5',
                color: '#b91c1c', borderRadius: '10px', padding: '12px 16px',
                fontSize: '0.875rem', marginBottom: '20px', fontWeight: 500,
              }}>
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary" style={{
              width: '100%', padding: '15px', fontSize: '1rem',
              opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer',
              textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
            }}>
              {loading ? (
                <>
                  <span style={{
                    width: '16px', height: '16px', borderRadius: '50%',
                    border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff',
                    display: 'inline-block', animation: 'spin 0.7s linear infinite',
                  }} />
                  Analysing...
                </>
              ) : 'Run Diagnosis →'}
            </button>
          </form>
        </div>

        {/* ── Result ── */}
        {result && (
          <div className="anim-fade-up">
            <PredictionResult result={result} mode={result.mode} />
            <Link
              to={`/treatments/${result.final_diagnosis || result.diagnosis}`}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                marginTop: '12px', padding: '14px', width: '100%',
                border: '1.5px solid #99f6e4', color: '#0d9488',
                borderRadius: '14px', textDecoration: 'none',
                fontWeight: 700, fontSize: '0.9rem',
                background: '#f0fdfa',
                transition: 'background 0.2s, border-color 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = '#ccfbf1'; e.currentTarget.style.borderColor = '#0d9488' }}
              onMouseLeave={e => { e.currentTarget.style.background = '#f0fdfa'; e.currentTarget.style.borderColor = '#99f6e4' }}
            >
              📋 View Treatment Suggestions
            </Link>
          </div>
        )}

      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
