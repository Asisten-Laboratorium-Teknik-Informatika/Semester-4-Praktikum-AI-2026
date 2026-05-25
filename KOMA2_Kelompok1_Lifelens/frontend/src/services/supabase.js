import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

// Hanya inisialisasi jika credentials tersedia
export const supabase = (supabaseUrl && supabaseAnonKey)
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null

export const isAuthEnabled = () => supabase !== null

export async function signInWithGoogle() {
  if (!supabase) return { error: 'Supabase not configured' }
  return supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: `${window.location.origin}/auth/callback` },
  })
}

export async function signInWithEmail(email, password) {
  if (!supabase) return { error: 'Supabase not configured' }
  return supabase.auth.signInWithPassword({ email, password })
}

export async function signUp(email, password) {
  if (!supabase) return { error: 'Supabase not configured' }
  return supabase.auth.signUp({ email, password })
}

export async function signOut() {
  if (!supabase) return
  return supabase.auth.signOut()
}

export async function getUser() {
  if (!supabase) return null
  const { data } = await supabase.auth.getUser()
  return data?.user || null
}
