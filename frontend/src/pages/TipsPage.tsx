import { useState } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, Sparkles, ChevronLeft, Loader2, Target, Gift, Brain } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { apiFetch } from '../api';

export default function TipsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { chat_history, profile_text } = location.state || {};
  const [loading, setLoading] = useState(false);
  const [tips, setTips] = useState<any>(null);

  const fetchTips = async (mode: 'general' | 'personalized') => {
    setLoading(true);
    try {
      const data = await apiFetch('/tips/generate', {
        method: 'POST',
        body: JSON.stringify({
          chat_history: chat_history || "",
          profile_text: profile_text || "",
          mode
        })
      });
      setTips(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-12 py-10 px-6">
      <div className="vibrant-bg" />
      
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="p-4 glass-card hover:bg-white transition-all shadow-lg group">
          <ChevronLeft className="w-6 h-6 text-zinc-600 group-hover:text-primary" />
        </button>
        <h1 className="text-4xl font-black text-zinc-900 tracking-tighter uppercase">Dating Strategy</h1>
        <Sparkles className="w-8 h-8 text-primary" />
      </div>

      {!tips && !loading && (
         <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <button 
              onClick={() => fetchTips('general')}
              className="glass-card p-10 flex flex-col items-center gap-6 group hover:border-primary/40 transition-all hover:scale-105"
            >
               <div className="w-20 h-20 rounded-full bg-rose-50 flex items-center justify-center text-rose-500 shadow-inner">
                  <Lightbulb className="w-10 h-10" />
               </div>
               <div className="text-center">
                  <h3 className="text-xl font-black text-zinc-900 uppercase">General Chat Tips</h3>
                  <p className="text-zinc-500 text-sm font-medium mt-2">Based on current conversation energy.</p>
               </div>
            </button>

            <button 
              onClick={() => fetchTips('personalized')}
              className="glass-card p-10 flex flex-col items-center gap-6 group hover:border-primary/40 transition-all hover:scale-105"
            >
               <div className="w-20 h-20 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-500 shadow-inner">
                  <Brain className="w-10 h-10" />
               </div>
               <div className="text-center">
                  <h3 className="text-xl font-black text-zinc-900 uppercase">Profile-Based Tips</h3>
                  <p className="text-zinc-500 text-sm font-medium mt-2">Personalized strategies for their personality.</p>
               </div>
            </button>
         </div>
      )}

      {loading && (
        <div className="py-20 flex flex-col items-center gap-8">
          <Loader2 className="w-16 h-16 text-primary animate-spin" />
          <p className="text-xl font-black text-zinc-900 uppercase tracking-widest">Generating Strategy...</p>
        </div>
      )}

      {tips && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-10"
        >
          <div className="glass-card p-10 bg-zinc-900 text-white space-y-4">
             <h4 className="text-primary font-black uppercase text-[10px] tracking-[0.5em]">Strategist Summary</h4>
             <p className="text-2xl font-bold italic text-zinc-200">“{tips.summary}”</p>
             <div className="pt-4 flex items-center gap-3">
                <span className="text-xs font-black text-zinc-500 uppercase tracking-widest">Vibe Check:</span>
                <span className="px-4 py-1 bg-white/10 rounded-full text-xs font-black text-primary">{tips.vibe_check}</span>
             </div>
          </div>

          <div className="grid gap-6">
             {tips.tips.map((tip: any, i: number) => (
                <div key={i} className="glass-card p-8 flex gap-8 items-center border border-white">
                   <div className="w-16 h-16 rounded-2xl bg-zinc-50 flex items-center justify-center shrink-0 shadow-inner text-2xl">
                      {tip.category === 'topic' ? <Target className="text-emerald-500" /> : tip.category === 'gift' ? <Gift className="text-rose-500" /> : <Brain className="text-indigo-500" />}
                   </div>
                   <div className="space-y-2">
                      <h5 className="text-xs font-black text-zinc-400 uppercase tracking-widest">{tip.title}</h5>
                      <p className="text-xl font-bold text-zinc-900 leading-relaxed">{tip.content}</p>
                   </div>
                </div>
             ))}
          </div>

          <button onClick={() => setTips(null)} className="w-full py-6 text-zinc-400 font-black uppercase text-xs tracking-widest border-2 border-dashed border-zinc-200 rounded-3xl hover:border-primary/20 hover:text-primary transition-all">
             Try Another mode
          </button>
        </motion.div>
      )}
    </div>
  );
}
