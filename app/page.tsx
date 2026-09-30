import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import Dashboard from '@/components/dashboard'

export default async function Home() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')
  const { data: items } = await supabase.from('dashboard_items').select('id,title,description,status,created_at').order('created_at', { ascending: false })
  return <Dashboard email={user.email ?? ''} initialItems={items ?? []} />
}
