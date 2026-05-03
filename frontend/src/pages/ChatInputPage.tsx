import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud, MessageSquare, Send, Loader2, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';

const CONTEXTS = [
  { label: 'Talking Stage', id: 'talking_stage', icon: '💬' },
  { label: 'Dating', id: 'dating', icon: '🍷' },
  { label: 'Relationship', id: 'relationship', icon: '💍' },
  { label: 'It\'s Complicated', id: 'complicated', icon: '🌀' }
];

export default function ChatInputPage() {
  const [context, setContext] = useState(CONTEXTS[0].id);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setMessage(prev => prev + (prev ? '\n' : '') + text);
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || loading) return;
    
    setLoading(true);
    setError('');

    try {
      const messages = message.split('\n').filter(m => m.trim() !== '');
      const response = await apiFetch('/analyze-chat', {
        method: 'POST',
        body: JSON.stringify({
          messages,
          context,
        }),
      });

      navigate('/result', { state: { result: response } });
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      className="w-full max-w-3xl mx-auto space-y-12 py-10 px-4"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="vibrant-bg" />
      
      <div className="text-center space-y-6">
        <motion.div 
          whileHover={{ scale: 1.05 }}
          className="inline-flex items-center gap-3 px-6 py-2 rounded-full bg-white/60 backdrop-blur-xl text-primary text-xs font-black tracking-[0.3em] uppercase border border-white/40 shadow-sm"
        >
          <Sparkles className="w-4 h-4" />
          The Truth Decoder
        </motion.div>
        <h1 className="text-5xl md:text-7xl font-black text-zinc-900 tracking-tighter leading-none">
          Paste the <span className="text-gradient">Vibe</span>
        </h1>
        <p className="text-zinc-600 font-bold text-lg md:text-xl italic">“You deserve clarity. Stop guessing what they mean.” 💬</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-10">
        <div className="space-y-6">
          <label className="text-xs font-black text-zinc-500 uppercase tracking-[0.2em] ml-2">Current Dynamic</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {CONTEXTS.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setContext(c.id)}
                className={`flex flex-col items-center gap-3 p-6 rounded-3xl text-sm font-black transition-all duration-500 border-2 ${
                  context === c.id 
                    ? 'bg-white border-primary shadow-[0_10px_30px_rgba(244,63,94,0.15)] text-primary scale-105' 
                    : 'glass-card border-transparent text-zinc-500 hover:border-zinc-200'
                }`}
              >
                <span className="text-4xl">{c.icon}</span>
                {c.label}
              </button>
            ))}
          </div>
        </div>

        <div className="relative glass-card group overflow-hidden border-2 border-white/40 focus-within:border-primary/30 transition-all duration-500 shadow-[0_30px_60px_-15px_rgba(0,0,0,0.1)]">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Paste their messages or describe the situation here..."
            disabled={loading}
            className="w-full h-80 bg-white/20 text-zinc-900 placeholder:text-zinc-400 resize-none outline-none p-10 font-inter text-xl leading-relaxed"
          />
          
          <div className="absolute top-10 right-10 text-zinc-200 pointer-events-none group-focus-within:text-primary/10 transition-colors">
            <MessageSquare className="w-20 h-20" />
          </div>

          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            accept=".txt,.json,.csv"
          />

          {loading && (
            <div className="absolute inset-0 bg-white/60 backdrop-blur-xl flex flex-col items-center justify-center space-y-8 z-20">
              <div className="relative">
                <Loader2 className="w-24 h-24 text-primary animate-spin" />
                <div className="absolute inset-0 blur-3xl bg-primary/30 animate-pulse" />
              </div>
              <div className="text-center space-y-3">
                <p className="text-3xl font-black text-zinc-900 tracking-tighter">Decoding Intent...</p>
                <p className="text-zinc-500 font-bold italic text-lg pr-2">“Something deep is being revealed.” ✨</p>
              </div>
            </div>
          )}

          <div className="p-6 bg-white/40 backdrop-blur-xl border-t border-white/40 flex justify-between items-center">
            <button 
              type="button" 
              onClick={() => fileInputRef.current?.click()}
              className="p-4 rounded-2xl bg-zinc-100/50 hover:bg-primary/10 hover:text-primary transition-all duration-300 group shadow-sm text-zinc-500"
              title="Upload Chat File"
            >
              <UploadCloud className="w-8 h-8 group-hover:scale-110 transition-transform" />
            </button>
            
            <button
              type="submit"
              disabled={!message.trim() || loading}
              className="glass-button px-12 py-5 flex items-center gap-4 disabled:opacity-50 font-black tracking-[0.2em] text-lg shadow-[0_15px_35px_rgba(244,63,94,0.2)]"
            >
              {loading ? 'REVEALING...' : 'ANALYZE VIBE'}
              {!loading && <Send className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {error && (
          <motion.p 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-lg text-primary font-black text-center bg-rose-50 p-6 rounded-3xl border-2 border-rose-100 shadow-sm"
          >
            ⚠️ {error}
          </motion.p>
        )}
      </form>

      <div className="text-center pt-8">
        <p className="text-zinc-400 text-xs font-black uppercase tracking-[0.5em]">Emotionally Intelligent Decision Engine</p>
      </div>
    </motion.div>
  );
}
