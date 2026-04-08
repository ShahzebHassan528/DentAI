import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'

const CLASSES = ['cavity', 'healthy', 'impacted', 'infection', 'other']

const CLASS_COLORS = {
  cavity:    '#f59e0b',
  healthy:   '#10b981',
  impacted:  '#f97316',
  infection: '#ef4444',
  other:     '#64748b',
}

const CONDITION_BG = {
  cavity:    '#fffbeb',
  healthy:   '#ecfdf5',
  impacted:  '#fff7ed',
  infection: '#fef2f2',
  other:     '#f8fafc',
}

function MetricCard({ label, value, sub, color = '#0d9488' }) {
  return (
    <div style={{
      background: '#fff', borderRadius: '14px', border: '1.5px solid #e2e8f0',
      padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '4px',
    }}>
      <p style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8',
        textTransform: 'uppercase', letterSpacing: '0.1em', margin: 0 }}>{label}</p>
      <p style={{ fontSize: '2rem', fontWeight: 800, color, margin: '4px 0 0' }}>{value}</p>
      {sub && <p style={{ fontSize: '0.78rem', color: '#64748b', margin: 0 }}>{sub}</p>}
    </div>
  )
}

function ConfusionMatrix({ matrix, classes }) {
  if (!matrix || !classes) return null
  const maxVal = Math.max(...matrix.flat())

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ borderCollapse: 'collapse', fontSize: '0.8rem', width: '100%' }}>
        <thead>
          <tr>
            <th style={{ padding: '8px 10px', color: '#94a3b8', fontWeight: 600,
              textAlign: 'right', fontSize: '0.72rem' }}>Actual ↓ / Pred →</th>
            {classes.map(c => (
              <th key={c} style={{ padding: '8px 10px', color: CLASS_COLORS[c] || '#0d9488',
                fontWeight: 700, textAlign: 'center', fontSize: '0.72rem',
                textTransform: 'capitalize' }}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, ri) => (
            <tr key={ri}>
              <td style={{ padding: '6px 10px', fontWeight: 700,
                color: CLASS_COLORS[classes[ri]] || '#0d9488',
                textTransform: 'capitalize', fontSize: '0.78rem', textAlign: 'right' }}>
                {classes[ri]}
              </td>
              {row.map((val, ci) => {
                const isDiag = ri === ci
                const alpha  = maxVal > 0 ? val / maxVal : 0
                const bg     = isDiag
                  ? `rgba(13,148,136,${0.15 + alpha * 0.55})`
                  : val > 0 ? `rgba(239,68,68,${alpha * 0.45})` : '#f8fafc'
                return (
                  <td key={ci} style={{
                    padding: '8px 10px', textAlign: 'center', fontWeight: isDiag ? 800 : 500,
                    background: bg,
                    color: isDiag ? '#0f766e' : val > 0 ? '#991b1b' : '#cbd5e1',
                    borderRadius: '6px', fontSize: '0.85rem',
                  }}>
                    {val}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function PerClassTable({ perClass, classes }) {
  if (!perClass) return null
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
            {['Condition', 'Precision', 'Recall', 'F1 Score', 'Support'].map(h => (
              <th key={h} style={{ padding: '10px 14px', textAlign: h === 'Condition' ? 'left' : 'center',
                fontWeight: 700, color: '#475569', fontSize: '0.75rem',
                textTransform: 'uppercase', letterSpacing: '0.06em' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {classes.map(cls => {
            const row = perClass[cls] || {}
            const color = CLASS_COLORS[cls] || '#64748b'
            const bg = CONDITION_BG[cls] || '#f8fafc'
            return (
              <tr key={cls} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '12px 14px' }}>
                  <span style={{
                    display: 'inline-block', padding: '4px 12px', borderRadius: '20px',
                    background: bg, color, fontWeight: 700, fontSize: '0.8rem',
                    textTransform: 'capitalize', border: `1px solid ${color}40`
                  }}>{cls}</span>
                </td>
                {['precision', 'recall', 'f1'].map(k => (
                  <td key={k} style={{ padding: '12px 14px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexDirection: 'column', gap: '4px' }}>
                      <span style={{ fontWeight: 700, color: '#0f172a' }}>
                        {((row[k] || 0) * 100).toFixed(1)}%
                      </span>
                      <div style={{ width: '60px', height: '4px', background: '#e2e8f0',
                        borderRadius: '999px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${(row[k] || 0) * 100}%`,
                          background: color, borderRadius: '999px' }} />
                      </div>
                    </div>
                  </td>
                ))}
                <td style={{ padding: '12px 14px', textAlign: 'center',
                  color: '#64748b', fontWeight: 600 }}>{row.support ?? '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function ThresholdChart({ rows, recommended }) {
  if (!rows || rows.length === 0) return null
  return (
    <div>
      <p style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '12px', margin: '0 0 12px' }}>
        Recommended threshold: <strong style={{ color: '#0d9488' }}>{recommended}</strong>
        &nbsp;— highest threshold where accuracy ≥ 85% with ≥ 50% coverage.
      </p>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end',
        overflowX: 'auto', paddingBottom: '4px' }}>
        {rows.map(r => {
          const isRec = r.threshold === recommended
          const barH  = Math.round(r.accuracy_when_confident * 120)
          return (
            <div key={r.threshold} style={{ display: 'flex', flexDirection: 'column',
              alignItems: 'center', gap: '4px', minWidth: '52px' }}>
              <span style={{ fontSize: '0.68rem', fontWeight: 700,
                color: isRec ? '#0d9488' : '#0f172a' }}>
                {(r.accuracy_when_confident * 100).toFixed(0)}%
              </span>
              <div style={{
                width: '36px', height: `${barH}px`,
                background: isRec ? '#0d9488' : '#99f6e4',
                border: isRec ? '2px solid #0d9488' : '1px solid #99f6e4',
                borderRadius: '6px 6px 2px 2px',
                position: 'relative', cursor: 'default',
              }} title={`Coverage: ${(r.coverage*100).toFixed(0)}%`} />
              <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>{r.threshold}</span>
              <span style={{ fontSize: '0.62rem', color: '#cbd5e1' }}>
                {(r.coverage * 100).toFixed(0)}%
              </span>
            </div>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
        <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>▲ Accuracy &nbsp;|&nbsp; bottom label = threshold &nbsp;|&nbsp; % below = coverage</span>
      </div>
    </div>
  )
}

export default function Metrics() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('efficientnet')

  useEffect(() => {
    client.get('/predict/metrics')
      .then(r => setMetrics(r.data))
      .catch(e => setError(e?.response?.data?.detail || 'Failed to load metrics'))
      .finally(() => setLoading(false))
  }, [])

  const en = metrics?.efficientnet || {}
  const bt = metrics?.bert || {}
  const fu = metrics?.fusion || {}

  return (
    <div style={{ minHeight: '100vh', background: '#eef2f7', fontFamily: 'Inter, sans-serif' }}>
      {/* Header */}
      <div style={{ background: '#fff', borderBottom: '1.5px solid #e2e8f0',
        padding: '20px 32px', display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <Link to="/doctor" style={{ textDecoration: 'none', color: '#64748b',
            fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            ← Dashboard
          </Link>
          <span style={{ color: '#cbd5e1' }}>|</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: 36, height: 36, borderRadius: '10px',
              background: 'linear-gradient(135deg, #0d9488, #0891b2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#fff', fontSize: '1.1rem' }}>📊</div>
            <div>
              <p style={{ margin: 0, fontWeight: 800, fontSize: '1rem', color: '#0f172a' }}>
                Model Performance Metrics
              </p>
              <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
                EfficientNetV2 · BERT · Late Fusion
              </p>
            </div>
          </div>
        </div>
        {metrics?.generated_at && (
          <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
            Last evaluated: {new Date(metrics.generated_at).toLocaleString()}
          </p>
        )}
      </div>

      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>

        {loading && (
          <div style={{ textAlign: 'center', padding: '80px' }}>
            <div style={{ width: 40, height: 40, border: '4px solid #e2e8f0',
              borderTopColor: '#0d9488', borderRadius: '50%', margin: '0 auto 16px',
              animation: 'spin 0.9s linear infinite' }} />
            <p style={{ color: '#64748b' }}>Loading metrics…</p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}

        {error && (
          <div style={{ background: '#fef2f2', border: '1.5px solid #fca5a5',
            borderRadius: '14px', padding: '32px', textAlign: 'center' }}>
            <p style={{ fontSize: '2rem', marginBottom: '8px' }}>⚠️</p>
            <p style={{ fontWeight: 700, color: '#991b1b', marginBottom: '8px' }}>{error}</p>
            <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
              Run&nbsp;
              <code style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '6px',
                fontFamily: 'monospace', fontSize: '0.8rem' }}>
                python -m app.ml.evaluate
              </code>
              &nbsp;in the backend to generate metrics.
            </p>
          </div>
        )}

        {metrics && !loading && (
          <>
            {/* Top summary cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '16px', marginBottom: '28px' }}>
              <MetricCard
                label="EfficientNet Accuracy"
                value={en.test_accuracy ? `${(en.test_accuracy * 100).toFixed(1)}%` : '—'}
                sub={`${en.num_test_samples ?? 0} test images`}
                color="#0d9488"
              />
              <MetricCard
                label="EfficientNet F1"
                value={en.test_f1_macro ? `${(en.test_f1_macro * 100).toFixed(1)}%` : '—'}
                sub="Macro F1 score"
                color="#0891b2"
              />
              <MetricCard
                label="BERT Accuracy"
                value={bt.val_accuracy ? `${(bt.val_accuracy * 100).toFixed(1)}%` : '—'}
                sub={`${bt.num_val_samples ?? 0} val samples`}
                color="#7c3aed"
              />
              <MetricCard
                label="BERT F1"
                value={bt.val_f1_macro ? `${(bt.val_f1_macro * 100).toFixed(1)}%` : '—'}
                sub="Macro F1 score"
                color="#ec4899"
              />
            </div>

            {/* Fusion info banner */}
            <div style={{ background: 'linear-gradient(135deg, #f0fdfa, #eff6ff)',
              border: '1.5px solid #99f6e4', borderRadius: '14px',
              padding: '18px 24px', marginBottom: '28px',
              display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.4rem' }}>🔀</span>
              <div style={{ flex: 1 }}>
                <p style={{ margin: '0 0 4px', fontWeight: 700, color: '#0f172a', fontSize: '0.9rem' }}>
                  Late Fusion Strategy
                </p>
                <p style={{ margin: 0, color: '#475569', fontSize: '0.82rem', fontFamily: 'monospace' }}>
                  final_prob = <strong style={{ color: '#0d9488' }}>0.6</strong> × EfficientNet_prob +&nbsp;
                  <strong style={{ color: '#7c3aed' }}>0.4</strong> × BERT_prob
                </p>
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                {[
                  { label: 'EfficientNet', w: '0.6', color: '#0d9488' },
                  { label: 'BERT', w: '0.4', color: '#7c3aed' },
                ].map(({ label, w, color }) => (
                  <div key={label} style={{ textAlign: 'center', padding: '8px 16px',
                    background: '#fff', borderRadius: '10px', border: `1.5px solid ${color}40` }}>
                    <p style={{ margin: 0, fontSize: '1.3rem', fontWeight: 800, color }}>{w}</p>
                    <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8' }}>{label}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tab switcher */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
              {[
                { key: 'efficientnet', label: '🦷 EfficientNetV2' },
                { key: 'bert', label: '🧠 BERT' },
              ].map(({ key, label }) => (
                <button key={key} onClick={() => setActiveTab(key)} style={{
                  padding: '8px 20px', borderRadius: '10px', fontSize: '0.85rem',
                  fontWeight: 600, cursor: 'pointer', border: 'none', transition: 'all 0.2s',
                  background: activeTab === key ? '#0d9488' : '#fff',
                  color: activeTab === key ? '#fff' : '#64748b',
                  boxShadow: activeTab === key ? '0 2px 10px rgba(13,148,136,0.25)' : 'none',
                  outline: activeTab !== key ? '1.5px solid #e2e8f0' : 'none',
                }}>{label}</button>
              ))}
            </div>

            {/* EfficientNet tab */}
            {activeTab === 'efficientnet' && (
              <div style={{ display: 'grid', gap: '20px' }}>
                {/* Per-class table */}
                <div style={{ background: '#fff', borderRadius: '16px',
                  border: '1.5px solid #e2e8f0', padding: '24px' }}>
                  <h3 style={{ margin: '0 0 16px', fontSize: '1rem', fontWeight: 700,
                    color: '#0f172a' }}>Per-Class Performance — Test Set</h3>
                  <PerClassTable perClass={en.per_class} classes={en.classes || CLASSES} />
                </div>

                {/* Confusion matrix */}
                <div style={{ background: '#fff', borderRadius: '16px',
                  border: '1.5px solid #e2e8f0', padding: '24px' }}>
                  <h3 style={{ margin: '0 0 4px', fontSize: '1rem', fontWeight: 700,
                    color: '#0f172a' }}>Confusion Matrix</h3>
                  <p style={{ margin: '0 0 16px', fontSize: '0.78rem', color: '#94a3b8' }}>
                    Green diagonal = correct predictions · Red = misclassifications
                  </p>
                  <ConfusionMatrix matrix={en.confusion_matrix} classes={en.classes || CLASSES} />
                </div>

                {/* Threshold analysis */}
                <div style={{ background: '#fff', borderRadius: '16px',
                  border: '1.5px solid #e2e8f0', padding: '24px' }}>
                  <h3 style={{ margin: '0 0 16px', fontSize: '1rem', fontWeight: 700,
                    color: '#0f172a' }}>Confidence Threshold Analysis</h3>
                  <ThresholdChart
                    rows={en.threshold_analysis}
                    recommended={en.recommended_threshold}
                  />
                </div>
              </div>
            )}

            {/* BERT tab */}
            {activeTab === 'bert' && (
              <div style={{ display: 'grid', gap: '20px' }}>
                <div style={{ background: '#fff', borderRadius: '16px',
                  border: '1.5px solid #e2e8f0', padding: '24px' }}>
                  <h3 style={{ margin: '0 0 16px', fontSize: '1rem', fontWeight: 700,
                    color: '#0f172a' }}>Per-Class Performance — Validation Set</h3>
                  <PerClassTable perClass={bt.per_class} classes={bt.classes || CLASSES} />
                </div>

                <div style={{ background: '#fff', borderRadius: '16px',
                  border: '1.5px solid #e2e8f0', padding: '24px' }}>
                  <h3 style={{ margin: '0 0 4px', fontSize: '1rem', fontWeight: 700,
                    color: '#0f172a' }}>Confusion Matrix</h3>
                  <p style={{ margin: '0 0 16px', fontSize: '0.78rem', color: '#94a3b8' }}>
                    Green diagonal = correct predictions · Red = misclassifications
                  </p>
                  <ConfusionMatrix matrix={bt.confusion_matrix} classes={bt.classes || CLASSES} />
                </div>

                <div style={{ background: '#fff', borderRadius: '16px',
                  border: '1.5px solid #e2e8f0', padding: '24px' }}>
                  <h3 style={{ margin: '0 0 16px', fontSize: '1rem', fontWeight: 700,
                    color: '#0f172a' }}>Confidence Threshold Analysis</h3>
                  <ThresholdChart
                    rows={bt.threshold_analysis}
                    recommended={bt.recommended_threshold}
                  />
                </div>
              </div>
            )}

            {/* How to re-run */}
            <div style={{ marginTop: '24px', background: '#f8fafc',
              border: '1.5px solid #e2e8f0', borderRadius: '14px', padding: '20px 24px' }}>
              <p style={{ margin: '0 0 8px', fontWeight: 700, color: '#0f172a', fontSize: '0.875rem' }}>
                🔄 Re-generate metrics after retraining
              </p>
              <code style={{ fontSize: '0.82rem', color: '#0d9488',
                background: '#f0fdfa', padding: '8px 14px', borderRadius: '8px',
                display: 'inline-block', fontFamily: 'monospace' }}>
                cd DentAI_Dev/backend &amp;&amp; python -m app.ml.evaluate
              </code>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
