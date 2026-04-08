import { useState } from 'react'

export default function SymptomInput({ value, onChange }) {
  const [focused, setFocused] = useState(false)

  return (
    <div style={{ width: '100%' }}>
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        rows={5}
        placeholder="e.g. I have sharp pain when eating sweets, sensitivity to cold, and mild swelling near my back molar..."
        style={{
          width: '100%', padding: '14px 16px',
          border: `1.5px solid ${focused ? '#0d9488' : '#e2e8f0'}`,
          borderRadius: '12px', fontSize: '0.93rem',
          color: '#0f172a', background: '#f8fafc',
          outline: 'none', resize: 'vertical',
          fontFamily: 'Inter, sans-serif', lineHeight: 1.7,
          transition: 'border-color 0.2s, box-shadow 0.2s',
          boxShadow: focused ? '0 0 0 3px rgba(13,148,136,0.1)' : 'none',
        }}
      />
      <p style={{ color: '#94a3b8', fontSize: '0.75rem', textAlign: 'right', marginTop: '4px' }}>
        {value.length} / 2000
      </p>
    </div>
  )
}
