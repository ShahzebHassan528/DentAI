import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function NotFound() {
  const { user } = useAuth()

  return (
    <div style={{
      minHeight: '100vh', background: '#eef2f7',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Inter, sans-serif', padding: '48px 24px',
    }}>
      <div style={{ textAlign: 'center', maxWidth: '440px' }} className="anim-fade-up">

        <div style={{
          width: '80px', height: '80px', borderRadius: '24px', fontSize: '2.4rem',
          background: 'linear-gradient(135deg, #f0fdfa, #eff6ff)',
          border: '1.5px solid #99f6e4',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 28px',
          boxShadow: '0 8px 24px rgba(13,148,136,0.1)',
        }}>
          🦷
        </div>

        <h1 style={{
          fontSize: '5rem', fontWeight: 900, color: '#0d9488',
          letterSpacing: '-0.04em', lineHeight: 1, marginBottom: '12px',
        }}>
          404
        </h1>

        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f172a', marginBottom: '10px' }}>
          Page not found
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.65, marginBottom: '32px' }}>
          The page you're looking for doesn't exist or may have been moved.
          Let's get you back on track.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/" style={{
            padding: '12px 24px', borderRadius: '12px', textDecoration: 'none',
            background: 'linear-gradient(135deg, #0d9488, #0891b2)',
            color: '#fff', fontWeight: 700, fontSize: '0.9rem',
            boxShadow: '0 4px 14px rgba(13,148,136,0.25)',
          }}>
            ← Home
          </Link>
          {user && (
            <Link to="/predict" style={{
              padding: '12px 24px', borderRadius: '12px', textDecoration: 'none',
              background: '#fff', color: '#0d9488', fontWeight: 700, fontSize: '0.9rem',
              border: '1.5px solid #99f6e4',
            }}>
              Run a Diagnosis
            </Link>
          )}
        </div>

      </div>
    </div>
  )
}
