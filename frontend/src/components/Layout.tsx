import { motion, AnimatePresence } from 'framer-motion';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { HeartPulse, History, LogOut, User, Sparkles } from 'lucide-react';
import { useAuth } from '../AuthContext';

const FLOATING_EMOJIS = ['❤️', '💔', '💬', '✨', '🔥', '💖', '🥰', '🌹'];

export default function Layout() {
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Dynamic Vibrant Background */}
      <div className="vibrant-bg" />
      
      {/* Floating Emojis Layer */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        {Array.from({ length: 15 }).map((_, i) => (
          <div
            key={i}
            className="emoji-float"
            style={{
              left: `${(i * 7) % 100}%`,
              animationDelay: `${i * 1.5}s`,
              fontSize: `${(i % 5) * 5 + 20}px`,
            }}
          >
            {FLOATING_EMOJIS[i % FLOATING_EMOJIS.length]}
          </div>
        ))}
      </div>

      <header className="sticky top-0 z-50 py-8 px-6 md:px-12 backdrop-blur-sm pointer-events-none">
        <div className="max-w-7xl mx-auto flex items-center justify-between pointer-events-auto">
          <Link to="/" className="flex items-center gap-2 group">
            <HeartPulse className="w-8 h-8 text-primary group-hover:scale-110 transition-transform" />
            <span className="font-poppins font-bold text-3xl tracking-tight text-gradient">Velra</span>
          </Link>

          <nav className="flex items-center gap-4 sm:gap-6">
            {isAuthenticated ? (
              <>
                <Link to="/analyze" className="text-xs font-black text-zinc-900 hover:text-primary transition-colors flex items-center gap-2 uppercase tracking-widest bg-white/40 px-6 py-3 rounded-2xl backdrop-blur-md border border-white/20 shadow-sm">
                  <Sparkles className="w-5 h-5 text-primary" />
                  <span className="hidden sm:inline">Start Analysis</span>
                </Link>
                <Link to="/history" className="text-xs font-black text-zinc-900 hover:text-primary transition-colors flex items-center gap-2 uppercase tracking-widest bg-white/40 px-4 py-2 rounded-xl backdrop-blur-md border border-white/20">
                  <History className="w-4 h-4" />
                  <span className="hidden sm:inline">Records</span>
                </Link>
                <div className="h-4 w-px bg-zinc-900/10 mx-2 hidden sm:block" />
                <button 
                  onClick={logout}
                  className="text-xs font-black text-primary hover:text-rose-700 transition-colors flex items-center gap-2 px-4 py-2 rounded-xl bg-primary/5 hover:bg-primary/10 border border-primary/10 uppercase tracking-widest"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden md:inline">Exit</span>
                </button>
              </>
            ) : (
              <Link to="/auth" className="glass-button px-8 py-3 text-sm flex items-center gap-2 shadow-xl shadow-primary/20">
                <User className="w-4 h-4" />
                SIGN IN
              </Link>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-grow flex flex-col items-center justify-center p-4 sm:p-8 relative z-10">
        <div className="w-full max-w-5xl">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      <footer className="py-12 text-center text-zinc-900 text-xs font-black tracking-widest uppercase opacity-40 hover:opacity-100 transition-opacity duration-500 relative z-10">
        <p>&copy; {new Date().getFullYear()} Velra. Decoding heartbeats worldwide.</p>
      </footer>
    </div>
  );
}
