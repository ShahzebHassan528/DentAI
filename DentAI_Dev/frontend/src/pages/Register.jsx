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

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'patient' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [focused, setFocused] = useState('')

  function validate() {
    if (!form.name.trim() || form.name.trim().length < 2) return 'Full name must be at least 2 characters.'
    if (!form.email.trim()) return 'Email address is required.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'Please enter a valid email address.'
    if (!form.password) return 'Password is required.'
    if (form.password.length < 8) return 'Password must be at least 8 characters.'
    if (!/[A-Z]/.test(form.password)) return 'Password must contain at least one uppercase letter.'
    if (!/[0-9]/.test(form.password)) return 'Password must contain at least one number.'
    return null
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const validationError = validate()
    if (validationError) return setError(validationError)
    setError('')
    setLoading(true)
    try {
      await register(form.name, form.email, form.password, form.role)
      navigate('/predict')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
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
            Create your account
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            Start diagnosing with AI — it's free
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

            {/* Full Name */}
            <div style={{ marginBottom: '18px' }}>
              <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '8px', letterSpacing: '0.02em' }}>
                FULL NAME
              </label>
              <input
                type="text" required
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                onFocus={() => setFocused('name')}
                onBlur={() => setFocused('')}
                placeholder="John Doe"
                style={{
                  ...inputStyle,
                  borderColor: focused === 'name' ? '#0d9488' : '#e2e8f0',
                  boxShadow: focused === 'name' ? '0 0 0 3px rgba(13,148,136,0.1)' : 'none',
                }}
              />
            </div>

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
            <div style={{ marginBottom: '18px' }}>
              <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '8px', letterSpacing: '0.02em' }}>
                PASSWORD
              </label>
              <input
                type="password" required minLength={8}
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                onFocus={() => setFocused('password')}
                onBlur={() => setFocused('')}
                placeholder="Min. 8 characters"
                style={{
                  ...inputStyle,
                  borderColor: focused === 'password' ? '#0d9488' : '#e2e8f0',
                  boxShadow: focused === 'password' ? '0 0 0 3px rgba(13,148,136,0.1)' : 'none',
                }}
              />
              {/* Password strength bar */}
              {form.password.length > 0 && (() => {
                const checks = [
                  form.password.length >= 8,
                  /[A-Z]/.test(form.password),
                  /[0-9]/.test(form.password),
                  /[^A-Za-z0-9]/.test(form.password),
                ]
                const score = checks.filter(Boolean).length
                const labels = ['', 'Weak', 'Fair', 'Good', 'Strong']
                const colors = ['', '#ef4444', '#f59e0b', '#3b82f6', '#10b981']
                return (
                  <div style={{ marginTop: '8px' }}>
                    <div style={{ display: 'flex', gap: '4px', marginBottom: '4px' }}>
                      {[1,2,3,4].map(i => (
                        <div key={i} style={{
                          flex: 1, height: '3px', borderRadius: '999px',
                          background: i <= score ? colors[score] : '#e2e8f0',
                          transition: 'background 0.3s',
                        }} />
                      ))}
                    </div>
                    <p style={{ fontSize: '0.72rem', color: colors[score], fontWeight: 600, margin: 0 }}>
                      {labels[score]}
                      {score < 4 && <span style={{ color: '#94a3b8', fontWeight: 400 }}> — add uppercase, number, or symbol</span>}
                    </p>
                  </div>
                )
              })()}
            </div>

            {/* Role */}
            <div style={{ marginBottom: '26px' }}>
              <label style={{ display: 'block', fontSize: '0.83rem', fontWeight: 700, color: '#334155', marginBottom: '10px', letterSpacing: '0.02em' }}>
                I AM A
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                {[
                  { key: 'patient', label: 'Patient', icon: '🧑', desc: 'I need a diagnosis' },
                  { key: 'doctor',  label: 'Doctor',  icon: '👨‍⚕️', desc: 'I review cases' },
                ].map(r => (
                  <button key={r.key} type="button" onClick={() => setForm({ ...form, role: r.key })}
                    style={{
                      padding: '14px 12px', borderRadius: '12px', border: '1.5px solid',
                      borderColor: form.role === r.key ? '#0d9488' : '#e2e8f0',
                      background: form.role === r.key ? '#f0fdfa' : '#f8fafc',
                      cursor: 'pointer', textAlign: 'center',
                      transition: 'all 0.2s',
                    }}>
                    <div style={{ fontSize: '1.4rem', marginBottom: '4px' }}>{r.icon}</div>
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: form.role === r.key ? '#0f766e' : '#334155' }}>
                      {r.label}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>{r.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Submit */}
            <button type="submit" disabled={loading} className="btn-primary" style={{
              width: '100%', padding: '14px', fontSize: '0.98rem',
              opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer',
              textAlign: 'center',
            }}>
              {loading ? 'Creating account...' : 'Create Account →'}
            </button>
          </form>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '22px 0' }}>
            <div style={{ flex: 1, height: '1px', background: '#f1f5f9' }} />
            <span style={{ color: '#cbd5e1', fontSize: '0.78rem', fontWeight: 600 }}>OR</span>
            <div style={{ flex: 1, height: '1px', background: '#f1f5f9' }} />
          </div>

          <p style={{ textAlign: 'center', color: '#64748b', fontSize: '0.9rem' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: '#0d9488', fontWeight: 700, textDecoration: 'none' }}
              onMouseEnter={e => e.target.style.color = '#0f766e'}
              onMouseLeave={e => e.target.style.color = '#0d9488'}
            >
              Sign in
            </Link>
          </p>
        </div>

        {/* Back */}
        <p style={{ textAlign: 'center', marginTop: '20px' }}>
          <Link to="/" style={{ color: '#94a3b8', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 500 }}
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
