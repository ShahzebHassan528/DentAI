import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const inputStyle = {
  width: '100%', padding: '13px 16px',
  border: '1.5px solid #e2e8f0', borderRadius: '12px',
  fontSize: '0.95rem', color: '#0f172a', background: '#f8fafc',
  outline: 'none', fontFamily: 'Inter, sans-serif',
  transition: 'border-color 0.2s, box-shadow 0.2s',
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [focused, setFocused] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.email, form.password)
      navigate('/predict')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', background: '#eef2f7',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '100px 24px 48px',
    }}>
      <div style={{ width: '100%', maxWidth: '440px' }} className="anim-fade-up">

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '60px', height: '60px', borderRadius: '18px', fontSize: '1.8rem',
            background: 'linear-gradient(135deg, #ccfbf1, #cffafe)',
            border: '1.5px solid #5eead4',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px',
            boxShadow: '0 8px 24px rgba(13,148,136,0.15)',
          }}>
            🦷
          </div>
          <h1 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.03em', marginBottom: '8px' }}>
            Welcome back
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            Sign in to your DentAI account
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: '#fff', border: '1px solid #e2e8f0',
          borderRadius: '20px', padding: '36px',
          boxShadow: '0 8px 32px rgba(15,23,42,0.07)',
        }}>

          {error && (
            <div style={{
              background: '#fef2f2', border: '1.5px solid #fca5a5',
              color: '#b91c1c', borderRadius: '10px', padding: '12px 16px',
              fontSize: '0.875rem', marginBottom: '20px', fontWeight: 500,
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Email */}
            <div style={{ marginBottom: '18px' }}>
              <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '8px', letterSpacing: '0.02em' }}>
                EMAIL ADDRESS
              </label>
              <input
                type="email" required
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                onFocus={() => setFocused('email')}
                onBlur={() => setFocused('')}
                placeholder="you@example.com"
                style={{
                  ...inputStyle,
                  borderColor: focused === 'email' ? '#0d9488' : '#e2e8f0',
                  boxShadow: focused === 'email' ? '0 0 0 3px rgba(13,148,136,0.1)' : 'none',
                }}
              />
            </div>

            {/* Password */}
            <div style={{ marginBottom: '26px' }}>
              <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '8px', letterSpacing: '0.02em' }}>
                PASSWORD
              </label>
              <input
                type="password" required
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                onFocus={() => setFocused('password')}
                onBlur={() => setFocused('')}
                placeholder="••••••••"
                style={{
                  ...inputStyle,
                  borderColor: focused === 'password' ? '#0d9488' : '#e2e8f0',
                  boxShadow: focused === 'password' ? '0 0 0 3px rgba(13,148,136,0.1)' : 'none',
                }}
              />
            </div>

            {/* Submit */}
            <button type="submit" disabled={loading} className="btn-primary" style={{
              width: '100%', padding: '14px', fontSize: '0.98rem',
              opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer',
              textAlign: 'center',
            }}>
              {loading ? 'Signing in...' : 'Sign In →'}
            </button>
          </form>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '22px 0' }}>
            <div style={{ flex: 1, height: '1px', background: '#f1f5f9' }} />
            <span style={{ color: '#cbd5e1', fontSize: '0.78rem', fontWeight: 600 }}>OR</span>
            <div style={{ flex: 1, height: '1px', background: '#f1f5f9' }} />
          </div>

          <p style={{ textAlign: 'center', color: '#64748b', fontSize: '0.9rem' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: '#0d9488', fontWeight: 700, textDecoration: 'none' }}
              onMouseEnter={e => e.target.style.color = '#0f766e'}
              onMouseLeave={e => e.target.style.color = '#0d9488'}
            >
              Create one free
            </Link>
          </p>
        </div>

        {/* Back */}
        <p style={{ textAlign: 'center', marginTop: '20px' }}>
          <Link to="/" style={{ color: '#94a3b8', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 500,
            transition: 'color 0.2s' }}
            onMouseEnter={e => e.target.style.color = '#0d9488'}
            onMouseLeave={e => e.target.style.color = '#94a3b8'}
          >
            ← Back to home
          </Link>
        </p>
      </div>
    </div>
  )
}
