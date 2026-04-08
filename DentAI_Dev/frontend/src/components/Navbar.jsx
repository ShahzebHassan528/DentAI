import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid #e2e8f0',
      height: '64px', display: 'flex', alignItems: 'center',
    }}>
      <div style={{
        maxWidth: '1100px', margin: '0 auto', padding: '0 28px',
        width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        {/* Logo */}
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '34px', height: '34px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #0d9488, #0891b2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '18px', boxShadow: '0 4px 12px rgba(13,148,136,0.3)',
          }}>🦷</div>
          <span style={{ fontWeight: 800, fontSize: '1.15rem', color: '#0f172a', letterSpacing: '-0.02em' }}>
            Dent<span style={{ color: '#0d9488' }}>AI</span>
          </span>
        </Link>

        {/* Right */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {user ? (
            <>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '6px 14px', borderRadius: '10px',
                background: '#f1faf9', border: '1px solid #ccfbf1',
              }}>
                <div style={{
                  width: '28px', height: '28px', borderRadius: '50%',
                  background: 'linear-gradient(135deg, #0d9488, #0891b2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#fff', fontSize: '12px', fontWeight: 700,
                }}>
                  {user.name?.charAt(0).toUpperCase()}
                </div>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0f172a' }}>{user.name}</span>
                <span style={{
                  fontSize: '0.7rem', fontWeight: 600, textTransform: 'capitalize',
                  background: '#ccfbf1', color: '#0f766e', padding: '2px 8px', borderRadius: '999px',
                }}>{user.role}</span>
              </div>
              <Link to={user?.role === 'doctor' ? '/doctor' : '/dashboard'} style={{
                padding: '8px 16px', fontSize: '0.875rem', fontWeight: 600,
                border: '1.5px solid #e2e8f0', borderRadius: '10px', color: '#64748b',
                textDecoration: 'none', transition: 'all 0.2s',
              }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#0d9488'; e.currentTarget.style.color = '#0d9488' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }}
              >
                Dashboard
              </Link>
              <Link to="/predict" className="btn-primary" style={{ padding: '8px 20px', fontSize: '0.875rem' }}>
                Diagnose
              </Link>
              <button onClick={() => { logout(); navigate('/') }} style={{
                padding: '8px 16px', fontSize: '0.875rem', fontWeight: 500,
                border: '1px solid #e2e8f0', borderRadius: '10px', background: 'transparent',
                color: '#64748b', cursor: 'pointer', transition: 'all 0.2s',
              }}
                onMouseEnter={e => { e.target.style.borderColor = '#fca5a5'; e.target.style.color = '#ef4444' }}
                onMouseLeave={e => { e.target.style.borderColor = '#e2e8f0'; e.target.style.color = '#64748b' }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" style={{
                padding: '8px 18px', fontSize: '0.875rem', fontWeight: 600,
                color: '#475569', textDecoration: 'none', borderRadius: '10px',
                transition: 'color 0.2s',
              }}
                onMouseEnter={e => e.target.style.color = '#0d9488'}
                onMouseLeave={e => e.target.style.color = '#475569'}
              >
                Login
              </Link>
              <Link to="/register" className="btn-primary" style={{ padding: '9px 22px', fontSize: '0.875rem' }}>
                Get Started Free
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
