import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, Loader2, Sparkles, 
  Instagram, Linkedin, Twitter, Info, Image as ImageIcon,
  ArrowRight, Search
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';

const CONTEXTS = [
  { label: 'Talking Stage', id: 'talking_stage', icon: '💬' },
  { label: 'Dating', id: 'dating', icon: '🍷' },
  { label: 'Relationship', id: 'relationship', icon: '💍' },
  { label: 'It\'s Complicated', id: 'complicated', icon: '🌀' }
];

const SOCIAL_PLATFORMS = [
  { id: 'instagram', icon: <Instagram className="w-5 h-5 text-rose-400" />, label: 'Instagram', placeholder: 'Paste bio or username...' },
  { id: 'linkedin', icon: <Linkedin className="w-5 h-5 text-indigo-400" />, label: 'LinkedIn', placeholder: 'Paste profile URL...' },
  { id: 'twitter', icon: <Twitter className="w-5 h-5 text-zinc-900" />, label: 'X (Twitter)', placeholder: 'Paste feed or username...' },
];

export default function UnifiedInputPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'profile'>('chat');
  const [context, setContext] = useState(CONTEXTS[0].id);
  const [inputText, setInputText] = useState('');
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result as string;
        setSelectedImages(prev => [...prev, base64].slice(-5)); // Keep last 5
      };
      reader.readAsDataURL(file); // Correct way for images (OCR later)
    });
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() && selectedImages.length === 0) return;
    
    setLoading(true);
    setError(null);

    try {
      if (activeTab === 'chat') {
        const messages = inputText.split('\n').filter(m => m.trim() !== '');
        const response = await apiFetch('/analyze-chat', {
          method: 'POST',
          body: JSON.stringify({
            messages,
            images: selectedImages,
            context,
          }),
        });
        navigate('/result', { state: { result: response } });
      } else {
        const data = await apiFetch('/profile/analyze', {
          method: 'POST',
          body: JSON.stringify({ 
            text: inputText, 
            source: 'manual' // Heuristic handles URL vs text
          }),
        });
        navigate('/profile-result', { state: { profile: data } });
      }
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      className="w-full max-w-4xl mx-auto space-y-12 py-10 px-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="vibrant-bg" />

      {/* Header */}
      <div className="text-center space-y-4">
        <motion.div 
          className="inline-flex items-center gap-2 px-6 py-2 rounded-full bg-white/60 backdrop-blur-xl border border-white/40 shadow-sm text-primary text-[10px] font-black tracking-widest uppercase"
          whileHover={{ scale: 1.05 }}
        >
          <Sparkles className="w-3 h-3" />
          The Intelligence Hub
        </motion.div>
        <h1 className="text-5xl md:text-7xl font-black text-zinc-900 tracking-tighter leading-tight drop-shadow-sm">
          Understand <span className="text-gradient">Their World</span>
        </h1>
        <p className="text-zinc-500 font-bold text-lg md:text-xl italic">
          “Behavioral signals decoded. Stop guessing, start knowing.” 🧠
        </p>
      </div>

      {/* Main Container */}
      <div className="space-y-8">
        {/* Toggle Hub */}
        <div className="flex p-2 bg-zinc-100/50 backdrop-blur-md rounded-[2.5rem] w-full max-w-sm mx-auto border border-white shadow-inner">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-4 px-6 rounded-[2rem] text-xs font-black transition-all duration-500 flex items-center justify-center gap-2 ${
              activeTab === 'chat' ? 'bg-white text-primary shadow-xl scale-105' : 'text-zinc-400 hover:text-zinc-600'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            CHAT DNA
          </button>
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex-1 py-4 px-6 rounded-[2rem] text-xs font-black transition-all duration-500 flex items-center justify-center gap-2 ${
              activeTab === 'profile' ? 'bg-white text-primary shadow-xl scale-105' : 'text-zinc-400 hover:text-zinc-600'
            }`}
          >
            <Search className="w-4 h-4" />
            THE PERSONA
          </button>
        </div>

        {/* Action Area */}
        <div className="glass-card overflow-hidden border-2 border-white/80 shadow-[0_45px_100px_-30px_rgba(0,0,0,0.1)] transition-all duration-700">
          
          {/* Sub Header for Chat */}
          <AnimatePresence mode="wait">
            {activeTab === 'chat' && (
              <motion.div 
                key="chat-header"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-8 pb-0 grid grid-cols-2 md:grid-cols-4 gap-3"
              >
                {CONTEXTS.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setContext(c.id)}
                    className={`p-4 rounded-2xl text-[10px] font-black transition-all duration-300 border ${
                      context === c.id ? 'bg-primary/5 border-primary text-primary shadow-sm' : 'bg-zinc-50/50 border-transparent text-zinc-400 hover:bg-zinc-100'
                    }`}
                  >
                    <span className="text-xl block mb-1">{c.icon}</span>
                    {c.label.toUpperCase()}
                  </button>
                ))}
              </motion.div>
            )}

            {activeTab === 'profile' && (
              <motion.div 
                key="profile-header"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-8 pb-0 flex gap-4 overflow-x-auto scrollbar-hide"
              >
                {SOCIAL_PLATFORMS.map((p) => (
                  <div 
                    key={p.id} 
                    className="flex-shrink-0 group relative cursor-help"
                  >
                    <div className="p-4 rounded-2xl bg-white/40 border border-white hover:border-primary/30 transition-all">
                      {p.icon}
                    </div>
                    {/* Tooltip */}
                    <div className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1 bg-zinc-900 text-white text-[8px] font-black rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none uppercase tracking-tighter">
                      {p.label}
                      <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-zinc-900 rotate-45" />
                    </div>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="p-8 space-y-6 relative">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={activeTab === 'chat' ? "Paste messages here..." : "Paste profile info or URL..."}
              className="w-full h-72 bg-transparent text-zinc-900 placeholder:text-zinc-300 resize-none outline-none font-bold text-xl md:text-2xl leading-relaxed scrollbar-hide"
            />

            {/* Image Preview Bar */}
            <AnimatePresence>
              {selectedImages.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3 pt-4 border-t border-zinc-100"
                >
                  {selectedImages.map((img, idx) => (
                    <div key={idx} className="relative w-16 h-16 rounded-xl overflow-hidden shadow-md group">
                      <img src={img} className="w-full h-full object-cover" />
                      <button 
                        onClick={() => setSelectedImages(prev => prev.filter((_, i) => i !== idx))}
                        className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <span className="text-white text-xs font-black">X</span>
                      </button>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Footer Controls */}
          <div className="p-6 px-8 bg-zinc-50/50 backdrop-blur-xl border-t border-white/50 flex justify-between items-center">
            <div className="flex gap-3">
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="p-4 rounded-[1.2rem] bg-white border border-zinc-100 text-zinc-400 hover:text-primary hover:border-primary/20 transition-all shadow-sm group"
              >
                <ImageIcon className="w-6 h-6 group-hover:scale-110 transition-transform" />
              </button>
              <input type="file" ref={fileInputRef} onChange={handleImageUpload} className="hidden" accept="image/*" multiple />
              
              <div className="p-4 rounded-[1.2rem] bg-white border border-zinc-100 text-zinc-400 transition-all shadow-sm cursor-help group relative">
                <Info className="w-6 h-6" />
                <div className="absolute -top-12 left-0 px-4 py-2 bg-zinc-900 text-white text-[9px] font-bold rounded-xl opacity-0 group-hover:opacity-100 transition-opacity w-48 shadow-2xl pointer-events-none">
                  {activeTab === 'chat' ? "Uploading screenshots automatically extracts text using AI." : "We'll analyze the digital footprint for personality traits."}
                </div>
              </div>
            </div>

            <button
              onClick={handleAnalyze}
              disabled={loading || (!inputText.trim() && selectedImages.length === 0)}
              className="glass-button px-10 py-5 flex items-center gap-3 font-black tracking-widest text-sm shadow-[0_15px_40px_-5px_rgba(244,63,94,0.3)] group"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  {activeTab === 'chat' ? 'ANALYZE VIBE' : 'REVEAL TRUTH'}
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Handling */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="bg-rose-50 border-2 border-rose-100 text-primary p-6 rounded-3xl font-black text-center text-sm shadow-sm"
            >
              ⚠️ {typeof error === 'object' ? JSON.stringify(error) : error}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="text-center opacity-30">
        <p className="text-[10px] font-black uppercase tracking-[0.8em] text-zinc-500">Velra Emotionally Intelligent Core v2.0</p>
      </div>
    </motion.div>
  );
}
