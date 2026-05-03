import { useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, Briefcase, Loader2, Sparkles, ArrowRight, Globe, Globe2, Share2, Search, Link as LinkIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';

const SOCIAL_ICONS = [
  { icon: <Camera className="w-5 h-5 text-rose-400" />, label: 'Instagram DNA' },
  { icon: <Briefcase className="w-5 h-5 text-indigo-400" />, label: 'LinkedIn Professional' },
  { icon: <Share2 className="w-5 h-5 text-sky-400" />, label: 'X (Twitter) Feed' },
  { icon: <Globe className="w-5 h-5 text-emerald-400" />, label: 'Public Web Bio' }
];

export default function ProfileInputPage() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (text.length < 10) {
      setError('Please provide at least a few lines or a link to analyze.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await apiFetch('/profile/analyze', {
        method: 'POST',
        body: JSON.stringify({ text, source: 'manual' }),
      });
      navigate('/profile-result', { state: { profile: data } });
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Make sure you are logged in.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 py-8 px-6 relative">
      <div className="vibrant-bg" />

      <div className="text-center space-y-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="inline-flex items-center gap-3 px-8 py-3 rounded-full bg-white/60 backdrop-blur-xl border border-white/50 text-primary text-sm font-black tracking-[0.3em] mb-4 shadow-lg uppercase"
        >
          <Sparkles className="w-5 h-5" />
          Velra DNA Decoder
        </motion.div>

        <div className="relative inline-block">
          <h1 className="text-6xl md:text-8xl font-black text-zinc-900 tracking-tighter leading-none">
            Understand Their <span className="text-gradient">World</span>
          </h1>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
            className="absolute -right-16 -top-8 w-16 h-16 bg-white/40 rounded-full flex items-center justify-center border-4 border-white shadow-xl backdrop-blur-md"
          >
            <Globe2 className="w-8 h-8 text-primary/60" />
          </motion.div>
        </div>

        <p className="text-zinc-500 font-black text-xl md:text-2xl italic max-w-2xl mx-auto leading-relaxed">
          “They’re showing you their brand. Let’s see who they really are.”
        </p>
      </div>

      <div className="space-y-6">
        <div className="relative glass-card border-white shadow-[0_30px_60px_-20px_rgba(244,63,94,0.1)] focus-within:ring-4 focus-within:ring-primary/10 transition-all duration-500 bg-white/50 overflow-hidden group">
          <div className="flex items-center justify-between p-7 px-10 border-b border-white/80 bg-white/40">
            <div className="flex items-center gap-3">
              <Search className="w-4 h-4 text-zinc-400" />
              <span className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.5em]">Digital Fingerprint Identification</span>
            </div>
            <div className="flex gap-6">
              {SOCIAL_ICONS.map((s, i) => (
                <div key={i} className="group/icon relative">
                  <div className="text-zinc-300 group-focus-within:text-zinc-600 group-hover/icon:text-primary transition-all duration-300 scale-110">
                    {s.icon}
                  </div>
                  {/* Pop Tooltip */}
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.5 }}
                    whileHover={{ opacity: 1, y: 0, scale: 1 }}
                    className="absolute -top-12 left-1/2 -translate-x-1/2 px-4 py-2 bg-zinc-900 text-white text-[9px] font-black rounded-xl opacity-0 transition-opacity pointer-events-none whitespace-nowrap uppercase tracking-[0.2em] z-50 border-2 border-white/20 shadow-2xl"
                  >
                    {s.label}
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-zinc-900 rotate-45" />
                  </motion.div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
              placeholder="Paste Instagram Bio, LinkedIn URL, or their favorite poem..."
              className="w-full h-64 bg-transparent text-zinc-900 placeholder:text-zinc-300 resize-none outline-none p-10 font-mono text-xl font-bold leading-relaxed scrollbar-hide"
            />
            <div className="absolute top-12 left-10 pointer-events-none opacity-[0.03] group-focus-within:opacity-[0.08] transition-opacity">
              <LinkIcon className="w-40 h-40 text-black rotate-12" />
            </div>
          </div>

          <div className="absolute right-12 bottom-12 opacity-5 group-focus-within:opacity-10 transition-opacity pointer-events-none">
            <Globe className="w-32 h-32 text-zinc-900" />
          </div>

          {loading && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-2xl flex flex-col items-center justify-center space-y-10 z-30">
              <div className="relative">
                <Loader2 className="w-24 h-24 text-primary animate-spin" />
                <div className="absolute inset-0 blur-3xl bg-primary/30" />
              </div>
              <div className="text-center space-y-4">
                <p className="text-4xl font-black text-zinc-900 tracking-tighter">MAPING IDENTITY CODES...</p>
                <p className="text-zinc-500 italic font-bold text-lg">“Wait until you see what’s behind the mask.” ✨</p>
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-6 items-center">
          {error && (
            <motion.p
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-primary font-black text-lg bg-rose-50 px-12 py-5 rounded-3xl border-2 border-rose-100 shadow-md"
            >
              ⚠️ {error}
            </motion.p>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || text.length < 10}
            className="w-full md:w-auto min-w-[320px] glass-button py-8 text-2xl font-black flex items-center justify-center gap-6 group relative shadow-[0_20px_50px_rgba(244,63,94,0.3)]"
          >
            ANALYZE DNA
            <ArrowRight className="w-8 h-8 group-hover:translate-x-3 transition-transform duration-700 ease-out" />
          </button>

          <p className="text-zinc-600 font-bold uppercase tracking-[0.8em] text-xs opacity-60">One Link. Infinite Insights.</p>
        </div>
      </div>
    </div>
  );
}
