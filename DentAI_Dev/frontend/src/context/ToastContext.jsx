import { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500)
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div style={{
        position: 'fixed', bottom: '28px', right: '28px',
        zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '10px',
      }}>
        {toasts.map(t => (
          <div key={t.id} style={{
            display: 'flex', alignItems: 'center', gap: '12px',
            padding: '14px 18px', borderRadius: '14px', minWidth: '280px', maxWidth: '380px',
            background: '#fff', boxShadow: '0 8px 32px rgba(15,23,42,0.14)',
            border: `1.5px solid ${t.type === 'error' ? '#fca5a5' : t.type === 'warning' ? '#fde68a' : '#6ee7b7'}`,
            animation: 'slideInToast 0.3s ease',
          }}>
            <span style={{ fontSize: '1.2rem', flexShrink: 0 }}>
              {t.type === 'error' ? '❌' : t.type === 'warning' ? '⚠️' : '✅'}
            </span>
            <p style={{ flex: 1, fontSize: '0.875rem', fontWeight: 600, color: '#0f172a', lineHeight: 1.5 }}>
              {t.message}
            </p>
            <button onClick={() => removeToast(t.id)} style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: '#94a3b8', fontSize: '1rem', padding: '0 2px', lineHeight: 1,
            }}>×</button>
          </div>
        ))}
      </div>
      <style>{`
        @keyframes slideInToast {
          from { opacity: 0; transform: translateX(20px); }
          to   { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </ToastContext.Provider>
  )
}

export function useToast() {
  return useContext(ToastContext)
}
