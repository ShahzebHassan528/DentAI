import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { icon: '🦷', title: 'X-Ray Analysis',       desc: 'Advanced image recognition scans your dental X-ray and pinpoints conditions with remarkable accuracy.',            accent: '#0d9488' },
  { icon: '💬', title: 'Symptom Analysis',      desc: 'Describe what you feel in plain language — DentAI understands and maps it to the most likely condition.',         accent: '#0891b2' },
  { icon: '🔀', title: 'Combined Diagnosis',    desc: 'When both image and symptoms are provided, DentAI fuses both signals for a more confident final result.',         accent: '#6366f1' },
  { icon: '📋', title: 'Treatment Suggestions', desc: 'Every diagnosis includes a clear treatment roadmap and home-care tips — no complicated medical jargon.',          accent: '#8b5cf6' },
  { icon: '🔐', title: 'Secure & Private',      desc: 'Your data never leaves our secured infrastructure. Images are encrypted and access-controlled at all times.',     accent: '#059669' },
  { icon: '👨‍⚕️', title: 'Doctor Review',        desc: 'Dentists can review AI findings, add clinical notes, and deliver professional oversight for every case.',        accent: '#0284c7' },
]

const STEPS = [
  { num: '01', title: 'Create Your Account', desc: 'Sign up in seconds — no credit card, no commitment.',           icon: '👤', color: '#0d9488' },
  { num: '02', title: 'Share Your Input',    desc: 'Upload a dental X-ray, describe your pain, or do both.',        icon: '📤', color: '#0891b2' },
  { num: '03', title: 'DentAI Analyses',     desc: 'Our AI engine processes your input and detects the condition.',  icon: '🤖', color: '#6366f1' },
  { num: '04', title: 'Review Your Results', desc: 'Get a clear diagnosis, confidence score, and treatment guide.', icon: '✅', color: '#059669' },
]

const CONDITIONS = [
  { label: 'Dental Cavity',     color: '#92400e', bg: '#fffbeb', border: '#fde68a' },
  { label: 'Healthy Dentition', color: '#065f46', bg: '#ecfdf5', border: '#6ee7b7' },
  { label: 'Impacted Tooth',    color: '#9a3412', bg: '#fff7ed', border: '#fdba74' },
  { label: 'Dental Infection',  color: '#991b1b', bg: '#fef2f2', border: '#fca5a5' },
  { label: 'Other Conditions',  color: '#334155', bg: '#f8fafc', border: '#cbd5e1' },
]

const STATS = [
  { value: '86%',  label: 'Model Accuracy',     color: '#0d9488' },
  { value: '5',    label: 'Conditions Covered', color: '#0891b2' },
  { value: '<3s',  label: 'Response Time',      color: '#6366f1' },
  { value: '2',    label: 'AI Models Fused',    color: '#8b5cf6' },
]

/* ── Reusable section header ── */
function SectionHeader({ tag, title, sub }) {
  return (
    <div className="anim-fade-up" style={{ textAlign: 'center', marginBottom: '56px' }}>
      <p style={{
        color: '#0d9488', fontWeight: 700, fontSize: '0.7rem',
        letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: '14px',
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
      }}>
        <span style={{ flex: 1, maxWidth: '48px', height: '1px', background: '#99f6e4', display: 'inline-block' }} />
        {tag}
        <span style={{ flex: 1, maxWidth: '48px', height: '1px', background: '#99f6e4', display: 'inline-block' }} />
      </p>
      <h2 style={{
        fontSize: 'clamp(1.75rem, 3.5vw, 2.4rem)', fontWeight: 800,
        color: '#0f172a', letterSpacing: '-0.03em', lineHeight: 1.15, marginBottom: '14px',
      }}>
        {title}
      </h2>
      {sub && <p style={{ color: '#94a3b8', fontSize: '1rem', maxWidth: '460px', margin: '0 auto', lineHeight: 1.7 }}>{sub}</p>}
    </div>
  )
}

export default function Landing() {
  const { user } = useAuth()

  return (
    <div style={{ background: '#eef2f7', minHeight: '100vh' }}>

      {/* ════ HERO ════ */}
      <section style={{
        paddingTop: '130px', paddingBottom: '96px',
        background: 'linear-gradient(168deg, #ffffff 0%, #f0fdfa 50%, #eef2f7 100%)',
        borderBottom: '1px solid #dde4ee',
      }}>
        <div style={{ maxWidth: '820px', margin: '0 auto', padding: '0 28px', textAlign: 'center' }}>

          {/* Badge */}
          <div className="anim-fade-up" style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            padding: '7px 18px', borderRadius: '999px', marginBottom: '36px',
            background: '#f0fdfa', border: '1.5px solid #5eead4',
            color: '#0f766e', fontSize: '12.5px', fontWeight: 700, letterSpacing: '0.025em',
          }}>
            <span style={{
              width: '7px', height: '7px', borderRadius: '50%', background: '#0d9488',
              display: 'inline-block', animation: 'pulse-dot 2s ease-in-out infinite',
            }} />
            Smart Dental Diagnosis, Powered by AI
          </div>

          {/* Headline */}
          <h1 className="anim-fade-up d1" style={{
            fontSize: 'clamp(2.8rem, 6vw, 4.8rem)',
            fontWeight: 900, lineHeight: 1.06,
            color: '#0f172a', marginBottom: '4px',
            letterSpacing: '-0.04em',
          }}>
            Your Teeth Deserve
          </h1>
          <h1 className="anim-fade-up d2 shimmer-text" style={{
            fontSize: 'clamp(2.8rem, 6vw, 4.8rem)',
            fontWeight: 900, lineHeight: 1.1,
            marginBottom: '30px', letterSpacing: '-0.04em',
            display: 'block',
          }}>
            Better Answers
          </h1>

          <p className="anim-fade-up d3" style={{
            color: '#64748b', fontSize: '1.15rem', lineHeight: 1.8,
            maxWidth: '520px', margin: '0 auto 44px', fontWeight: 400,
          }}>
            Upload your dental X-ray or describe your symptoms.
            DentAI will take care of the rest — fast, accurate, and free.
          </p>

          <div className="anim-fade-up d4" style={{ display: 'flex', gap: '14px', justifyContent: 'center', flexWrap: 'wrap' }}>
            {user ? (
              <Link to="/predict" className="btn-primary">Start Diagnosis →</Link>
            ) : (
              <>
                <Link to="/register" className="btn-primary">Get Started Free</Link>
                <Link to="/login" className="btn-outline">Sign In</Link>
              </>
            )}
          </div>

          <div className="anim-float anim-fade-up d5" style={{
            fontSize: '5.5rem', marginTop: '64px', lineHeight: 1,
            filter: 'drop-shadow(0 12px 32px rgba(13,148,136,0.2))',
            display: 'block',
          }}>
            🦷
          </div>
        </div>
      </section>

      {/* ════ STATS ════ */}
      <section style={{ background: '#fff', borderBottom: '1px solid #dde4ee' }}>
        <div style={{
          maxWidth: '900px', margin: '0 auto', padding: '0 28px',
          display: 'grid', gridTemplateColumns: 'repeat(4,1fr)',
        }}>
          {STATS.map((s, i) => (
            <div key={i} className="anim-fade-up" style={{
              animationDelay: `${i * 0.08}s`,
              textAlign: 'center', padding: '36px 16px',
              borderRight: i < 3 ? '1px solid #eef2f7' : 'none',
            }}>
              <div style={{ fontSize: '2.4rem', fontWeight: 900, color: s.color, lineHeight: 1, marginBottom: '6px', letterSpacing: '-0.03em' }}>
                {s.value}
              </div>
              <div style={{ color: '#94a3b8', fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ════ HOW IT WORKS ════ */}
      <section style={{ padding: '100px 28px', background: '#eef2f7' }}>
        <div style={{ maxWidth: '1040px', margin: '0 auto' }}>
          <SectionHeader
            tag="How It Works"
            title="Diagnosis in four simple steps"
            sub="No appointments, no waiting rooms. Just clear answers, instantly."
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px,1fr))', gap: '20px' }}>
            {STEPS.map((s, i) => (
              <div key={i} className={`card anim-fade-up d${i+1}`} style={{ padding: '36px 28px', textAlign: 'center' }}>
                <div style={{
                  width: '56px', height: '56px', borderRadius: '16px', fontSize: '1.6rem',
                  background: `${s.color}12`, border: `1.5px solid ${s.color}28`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px',
                }}>
                  {s.icon}
                </div>
                <div style={{ color: s.color, fontSize: '0.65rem', fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', marginBottom: '10px' }}>
                  Step {s.num}
                </div>
                <h3 style={{ color: '#0f172a', fontWeight: 800, fontSize: '1.05rem', marginBottom: '10px', letterSpacing: '-0.01em' }}>
                  {s.title}
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.875rem', lineHeight: 1.7 }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════ FEATURES ════ */}
      <section style={{ padding: '100px 28px', background: '#fff', borderTop: '1px solid #dde4ee' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <SectionHeader
            tag="Features"
            title="Built for patients, trusted by dentists"
            sub="Every feature is designed around one goal — getting you the right answer, fast."
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px,1fr))', gap: '20px' }}>
            {FEATURES.map((f, i) => (
              <div key={i} className={`card anim-fade-up d${(i % 3) + 1}`} style={{ padding: '32px' }}
                onMouseEnter={e => e.currentTarget.style.borderColor = f.accent + '55'}
                onMouseLeave={e => e.currentTarget.style.borderColor = '#e2e8f0'}
              >
                <div style={{
                  width: '50px', height: '50px', borderRadius: '14px', fontSize: '1.5rem',
                  background: `${f.accent}10`, border: `1.5px solid ${f.accent}25`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '18px',
                }}>
                  {f.icon}
                </div>
                <h3 style={{ color: '#0f172a', fontWeight: 700, fontSize: '1.05rem', marginBottom: '10px', letterSpacing: '-0.01em' }}>
                  {f.title}
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: 1.7 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════ CONDITIONS ════ */}
      <section style={{ padding: '100px 28px', background: '#eef2f7', borderTop: '1px solid #dde4ee' }}>
        <div style={{ maxWidth: '700px', margin: '0 auto', textAlign: 'center' }}>
          <SectionHeader
            tag="Conditions We Detect"
            title="What can DentAI diagnose?"
            sub="DentAI currently identifies five dental conditions — with more coming soon."
          />
          <div className="anim-fade-up d2" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
            {CONDITIONS.map((c, i) => (
              <span key={i} style={{
                display: 'inline-flex', alignItems: 'center', gap: '8px',
                padding: '10px 20px', borderRadius: '999px', fontSize: '0.9rem', fontWeight: 600,
                background: c.bg, border: `1.5px solid ${c.border}`, color: c.color,
                transition: 'transform 0.2s, box-shadow 0.2s', cursor: 'default',
              }}
                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.08)' }}
                onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'none' }}
              >
                <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: c.color, flexShrink: 0 }} />
                {c.label}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ════ CTA ════ */}
      {!user && (
        <section style={{ padding: '72px 28px 108px', background: '#fff', borderTop: '1px solid #dde4ee' }}>
          <div className="anim-fade-up" style={{
            maxWidth: '600px', margin: '0 auto', textAlign: 'center',
            background: 'linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%)',
            border: '1.5px solid #99f6e4', borderRadius: '24px', padding: '68px 48px',
            boxShadow: '0 12px 48px rgba(13,148,136,0.1)',
          }}>
            <div className="anim-float" style={{ fontSize: '4rem', marginBottom: '24px', filter: 'drop-shadow(0 8px 20px rgba(13,148,136,0.22))' }}>
              🦷
            </div>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', marginBottom: '14px', letterSpacing: '-0.03em' }}>
              Your next step starts here
            </h2>
            <p style={{ color: '#64748b', marginBottom: '36px', fontSize: '1.05rem', lineHeight: 1.75 }}>
              Join patients getting clearer answers about their dental health — completely free.
            </p>
            <Link to="/register" className="btn-primary" style={{ fontSize: '1rem', padding: '15px 44px' }}>
              Create Free Account
            </Link>
          </div>
        </section>
      )}

      {/* ════ FOOTER ════ */}
      <footer style={{
        borderTop: '1px solid #dde4ee', background: '#fff',
        padding: '24px 40px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <span style={{ fontSize: '1.25rem' }}>🦷</span>
          <span style={{ fontWeight: 800, color: '#0f172a', fontSize: '0.98rem', letterSpacing: '-0.02em' }}>
            Dent<span style={{ color: '#0d9488' }}>AI</span>
          </span>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.82rem' }}>
          © 2025 DentAI. Smart diagnosis for better dental health.
        </p>
        <div style={{ display: 'flex', gap: '24px' }}>
          {['Privacy', 'Terms', 'Contact'].map(l => (
            <a key={l} href="#" style={{ color: '#94a3b8', fontSize: '0.82rem', textDecoration: 'none', fontWeight: 500, transition: 'color 0.2s' }}
              onMouseEnter={e => e.target.style.color = '#0d9488'}
              onMouseLeave={e => e.target.style.color = '#94a3b8'}
            >
              {l}
            </a>
          ))}
        </div>
      </footer>

    </div>
  )
}
