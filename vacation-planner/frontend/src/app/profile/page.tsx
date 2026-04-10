import { redirect } from 'next/navigation';

// /profile is deprecated — /dashboard is the canonical My Trips page.
export default function ProfileRedirect() {
  redirect('/dashboard');
}
