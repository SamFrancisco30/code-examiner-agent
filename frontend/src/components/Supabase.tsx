
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://cnfwgtjvshyicamfhgwq.supabase.co'
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
if (!supabaseKey) {
  throw new Error('SUPABASE_KEY is not defined in the environment variables');
}
export const supabase = createClient(supabaseUrl, supabaseKey);