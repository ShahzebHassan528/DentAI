import { useState, useCallback } from 'react'

export default function ImageUpload({ onFileSelect }) {
  const [dragging, setDragging] = useState(false)
  const [preview, setPreview] = useState(null)

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return
    setPreview(URL.createObjectURL(file))
    onFileSelect(file)
  }, [onFileSelect])

  function onDrop(e) {
    e.preventDefault(); setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  function clearImage() {
    setPreview(null); onFileSelect(null)
  }

  return (
    <div style={{ width: '100%' }}>
      {preview ? (
        <div style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', border: '1.5px solid #99f6e4' }}>
          <img src={preview} alt="X-ray preview" style={{ width: '100%', maxHeight: '240px', objectFit: 'contain', background: '#f8fafc', display: 'block' }} />
          <button onClick={clearImage} style={{
            position: 'absolute', top: '10px', right: '10px',
            background: '#fff', border: '1.5px solid #e2e8f0',
            color: '#64748b', borderRadius: '8px', padding: '5px 12px',
            fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer',
            transition: 'all 0.2s', fontFamily: 'Inter, sans-serif',
          }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#fca5a5'; e.currentTarget.style.color = '#ef4444' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b' }}
          >
            Remove
          </button>
        </div>
      ) : (
        <label
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            width: '100%', height: '180px', cursor: 'pointer', borderRadius: '12px',
            border: `2px dashed ${dragging ? '#0d9488' : '#cbd5e1'}`,
            background: dragging ? '#f0fdfa' : '#f8fafc',
            transition: 'all 0.2s',
          }}
          onMouseEnter={e => { if (!dragging) { e.currentTarget.style.borderColor = '#0d9488'; e.currentTarget.style.background = '#f0fdfa' } }}
          onMouseLeave={e => { if (!dragging) { e.currentTarget.style.borderColor = '#cbd5e1'; e.currentTarget.style.background = '#f8fafc' } }}
        >
          <input type="file" accept="image/*" style={{ display: 'none' }} onChange={e => handleFile(e.target.files[0])} />
          <span style={{ fontSize: '2.2rem', marginBottom: '10px' }}>🦷</span>
          <p style={{ color: '#334155', fontWeight: 600, fontSize: '0.9rem', marginBottom: '4px' }}>
            Drag & drop your X-ray here
          </p>
          <p style={{ color: '#94a3b8', fontSize: '0.78rem' }}>or click to browse · JPEG, PNG, WebP</p>
        </label>
      )}
    </div>
  )
}
