import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { HeartPulse, Loader2, AlertCircle, CheckCircle2, KeyRound, Mail } from 'lucide-react';
import { useAuth } from '../AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { supabase } from '../supabaseClient';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [isForgot, setIsForgot] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const { login, signup, acceptTc } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const errorCode = params.get('error_code');
    if (errorCode === 'bad_oauth_state') {
      setError("OAuth State Mismatch: Ensure 'http://localhost:5173/auth/callback' is in your Supabase 'Redirect URLs' list.");
    } else if (params.get('error')) {
      setError(params.get('error_description') || "Authentication failed.");
    }
  }, [location]);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');

    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        // Explicitly use localhost:5173 to ensure consistency with Supabase allow-list
        redirectTo: 'http://localhost:5173/auth/callback'
      }
    });

    if (error) {
      console.error("Supabase OAuth Error:", error.message);
      setError("Google login failed. Please try again.");
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    // Mocking the backend reset call
    setTimeout(() => {
      setSuccess('If this email exists, a reset link was sent.');
      setLoading(false);
    }, 1200);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLogin && !agreed) {
      setError('You must agree to the Terms & Conditions');
      return;
    }
    if (!isLogin && password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(email, password);
        await acceptTc();
      }
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  if (isForgot) {
    return (
      <div className="w-full max-w-xl mx-auto py-16 px-6">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card p-12 space-y-8">
          <button onClick={() => setIsForgot(false)} className="text-primary font-black text-xs uppercase tracking-widest hover:underline">← Back to Login</button>
          <div className="text-center space-y-2">
            <h2 className="text-4xl font-black text-zinc-900 tracking-tighter uppercase">Reset Password</h2>
            <p className="text-zinc-500 font-bold text-sm">WE’LL SEND A SECURE LINK TO YOUR EMAIL.</p>
          </div>
          {success ? (
            <div className="p-6 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center gap-3 font-bold">
              <CheckCircle2 className="w-6 h-6" /> {success}
            </div>
          ) : (
            <form onSubmit={handleForgotPassword} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-black text-zinc-900 uppercase tracking-widest ml-1">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full bg-white/50 border border-zinc-200 rounded-2xl p-6 pl-16 outline-none focus:border-primary/50 text-zinc-900 font-bold text-lg" placeholder="your@email.com" />
                </div>
              </div>
              <button disabled={loading} type="submit" className="w-full glass-button py-6 text-xl">{loading ? <Loader2 className="animate-spin" /> : 'SEND RESET LINK'}</button>
            </form>
          )}
        </motion.div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl mx-auto py-16 px-6">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-10 space-y-10 relative overflow-hidden text-zinc-900 border-2 border-white/50"
      >
        <div className="text-center space-y-6">
          <motion.div 
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="w-20 h-20 bg-primary/10 rounded-3xl flex items-center justify-center mx-auto border border-primary/20 accent-glow"
          >
            <HeartPulse className="w-10 h-10 text-primary" />
          </motion.div>
          <div className="space-y-1">
            <h1 className="text-5xl font-black text-zinc-900 tracking-tighter uppercase leading-tight">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h1>
          </div>
        </div>

        <div className="space-y-6">
          <button 
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full bg-white border border-zinc-200 py-5 flex items-center justify-center gap-4 hover:bg-zinc-50 transition-all rounded-2xl shadow-sm group"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (
              <>
                <svg className="w-6 h-6 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 12-4.53z" fill="#EA4335"/>
                </svg>
                <span className="font-bold uppercase tracking-widest text-sm">Continue with Google</span>
              </>
            )}
          </button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-zinc-100"></div></div>
            <div className="relative flex justify-center">
              <span className="bg-white px-4 text-zinc-400 font-black text-[10px] uppercase tracking-[0.3em]">Or use Email</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-[11px] font-black text-zinc-900 uppercase tracking-widest ml-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full bg-white/50 border border-zinc-200 rounded-2xl p-6 pl-16 outline-none focus:border-primary/50 text-zinc-900 font-bold text-lg"
                  placeholder="name@email.com"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center ml-1">
                <label className="text-[11px] font-black text-zinc-900 uppercase tracking-widest">Password</label>
                {isLogin && (
                  <button type="button" onClick={() => setIsForgot(true)} className="text-[10px] font-bold text-primary hover:underline uppercase tracking-widest">Forgot Password?</button>
                )}
              </div>
              <div className="relative">
                <KeyRound className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-white/50 border border-zinc-200 rounded-2xl p-6 pl-16 outline-none focus:border-primary/50 text-zinc-900 font-bold text-lg"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {!isLogin && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="space-y-2">
                <label className="text-[11px] font-black text-zinc-900 uppercase tracking-widest ml-1">Confirm Password</label>
                <div className="relative">
                   <KeyRound className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                   <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full bg-white/50 border border-zinc-200 rounded-2xl p-6 pl-16 outline-none focus:border-primary/50 text-zinc-900 font-bold text-lg"
                    placeholder="••••••••"
                  />
                </div>
              </motion.div>
            )}
          </div>

          {!isLogin && (
            <div className="flex items-center gap-4 p-5 bg-zinc-50 border border-zinc-100 rounded-2xl">
              <button 
                type="button"
                onClick={() => setAgreed(!agreed)}
                className={`w-8 h-8 rounded-lg border transition-all flex items-center justify-center shrink-0 ${agreed ? 'bg-primary border-primary shadow-lg' : 'border-zinc-300 bg-white'}`}
              >
                {agreed && <CheckCircle2 className="w-5 h-5 text-white" />}
              </button>
              <p className="text-[11px] font-black text-zinc-700 uppercase tracking-widest">
                I agree to the <a href="https://jtaru28912.github.io/verla-legal/terms.html" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Terms of Service</a> & <a href="https://jtaru28912.github.io/verla-legal/privacy.html" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Privacy Policy</a>
              </p>
            </div>
          )}

          {error && (
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex items-center gap-3 p-5 bg-rose-50 border border-rose-100 rounded-2xl text-rose-500 text-xs font-black uppercase tracking-widest">
              <AlertCircle className="w-5 h-5" /> {error}
            </motion.div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full glass-button py-6 text-xl font-black shadow-xl"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (isLogin ? 'LOG IN' : 'SIGN UP')}
          </button>
        </form>

        <div className="text-center">
           <p className="text-xs font-black text-zinc-400 uppercase tracking-widest">
            {isLogin ? "New to Velra?" : "Already joined?"}
            <button onClick={() => setIsLogin(!isLogin)} className="text-primary font-black ml-3 hover:underline">
              {isLogin ? 'SIGN UP' : 'SIGN IN'}
            </button>
           </p>
        </div>
      </motion.div>
    </div>
  );
}
