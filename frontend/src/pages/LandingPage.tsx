import { motion } from 'framer-motion';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center space-y-16 relative">
      <div className="vibrant-bg" />

      {/* Hero Section */}
      <div className="space-y-8 max-w-4xl px-4 relative z-10">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-8 py-3 rounded-full glass-card border-white/10 text-rose-400 font-black text-xs tracking-[0.4em] mb-4 accent-glow uppercase"
        >
          <Sparkles className="w-5 h-5 text-rose-500" />
          Velra
        </motion.div>

        <motion.h1
          className="text-7xl md:text-9xl font-black tracking-tighter leading-[0.85] text-zinc-900"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.8 }}
        >
          See what they <br />
          <span className="text-gradient drop-shadow-[0_0_50px_rgba(244,63,94,0.4)]">really mean.</span>
        </motion.h1>

        <motion.div
          className="space-y-6 max-w-2xl mx-auto"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8 }}
        >
          <p className="text-3xl md:text-4xl text-zinc-800 font-black leading-tight uppercase tracking-tighter">
            Stop guessing. Start knowing. ❤️
          </p>
        </motion.div>
      </div>

      {/* CTA Section */}
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.8 }}
        className="pt-10 relative z-10"
      >
        <Link
          to="/analyze"
          className="glass-button inline-flex items-center gap-6 px-12 py-8 text-3xl font-black group shadow-[0_20px_60px_-15px_rgba(244,63,94,0.4)]"
        >
          ANALYZE NOW
          <ArrowRight className="w-8 h-8 group-hover:translate-x-3 transition-transform" />
        </Link>
      </motion.div>

      {/* Social Proof Hook */}
      <div className="pt-24 grid grid-cols-1 md:grid-cols-3 gap-10 w-full max-w-6xl px-4 relative z-10">
        {[
          { text: "YOU DESERVE CLARITY", icon: "✨" },
          { text: "STOP GUESSING. START KNOWING.", icon: "🧠" },
          { text: "UNDERSTAND THEM BEFORE YOU INVEST", icon: "🔥" }
        ].map((hook, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 + (i * 0.2) }}
            className="glass-card p-10 border-white/20 flex flex-col items-center gap-6 group hover:border-primary/40 transition-all duration-500 hover:scale-105"
          >
            <span className="text-5xl group-hover:scale-125 transition-transform duration-500 shadow-sm">{hook.icon}</span>
            <p className="text-zinc-900 font-black uppercase tracking-[0.2em] text-xs text-center">{hook.text}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
