'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'

export default function LoginPage() {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setMessage('')
    const supabase = createClient()
    const result = mode === 'login'
      ? await supabase.auth.signInWithPassword({ email, password })
      : await supabase.auth.signUp({ email, password, options: { emailRedirectTo: process.env.NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL ?? `${window.location.origin}/auth/callback` } })
    setBusy(false)
    if (result.error) { setMessage(mode === 'login' ? 'Invalid email or password.' : result.error.message); return }
    if (mode === 'signup') { setMessage('Check your email to confirm your account.'); return }
    window.location.href = '/'
  }

  return <main className="auth-shell"><div className="auth-card"><div className="eyebrow">SIGNAL / WORKSPACE</div><h1>{mode === 'login' ? 'Welcome back.' : 'Start your workspace.'}</h1><p className="muted">Turn scattered thoughts into a clear operating rhythm.</p><form onSubmit={submit}><label>Email<input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@company.com" /></label><label>Password<input type="password" required minLength={6} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 6 characters" /></label>{message && <p className="form-message">{message}</p>}<button className="primary-button" disabled={busy}>{busy ? 'Working…' : mode === 'login' ? 'Enter workspace' : 'Create account'}</button></form><button className="text-button" onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setMessage('') }}>{mode === 'login' ? 'Need an account? Sign up' : 'Already have an account? Log in'}</button></div></main>
}
