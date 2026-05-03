import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { Loader2 } from 'lucide-react';

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleAuth = async () => {
      console.log("AuthCallback: Starting session retrieval...");
      const { data, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error("Auth Callback: Supabase session error:", error.message);
        navigate('/auth?error=' + encodeURIComponent(error.message));
        return;
      }

      if (!data.session) {
        console.warn("Auth Callback: No session found. This may be due to a state mismatch or expired code.");
        navigate('/auth?error=No+session+found');
        return;
      }

      const { user, access_token } = data.session;
      
      // Sync with our backend
      try {
        const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:10000';
        const response = await fetch(`${BASE_URL}/auth/google/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            email: user.email, 
            provider_id: user.id,
            access_token: access_token
          }),
        });

        if (!response.ok) throw new Error("Backend sync failed");

        const syncData = await response.json();
        
        // Store our backend token
        localStorage.setItem('velra_token', syncData.access_token);
        localStorage.setItem('velra_tc_accepted', String(syncData.accepted_tc));
        
        // Redirect to the main analysis page
        window.location.href = '/analyze';
      } catch (err) {
        console.error("Sync Error:", err);
        navigate('/auth');
      }
    };

    handleAuth();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950">
      <div className="text-center space-y-4">
        <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
        <p className="text-zinc-500 font-bold uppercase tracking-widest text-sm italic animate-pulse">
            Authenticating with the truth...
        </p>
      </div>
    </div>
  );
}
