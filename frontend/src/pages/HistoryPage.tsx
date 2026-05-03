import { motion } from 'framer-motion';
import { Clock, ArrowRight, Activity, Loader2, Sparkles, MessageCircleHeart, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { apiFetch } from '../api';

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchHistory = async () => {
    try {
      const data = await apiFetch('/history');
      setHistory(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load archives.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this discovery?")) return;
    
    try {
      await apiFetch(`/history/${id}`, { method: 'DELETE' });
      setHistory(prev => prev.filter(item => item.id !== id));
    } catch (err: any) {
      alert("Failed to delete archive: " + err.message);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-16 py-12 px-6 relative">
       <div className="vibrant-bg" />
       
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-10">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-3 px-6 py-2 rounded-full bg-primary/10 text-primary text-xs font-black tracking-[0.3em] uppercase border border-primary/20">
            <Clock className="w-4 h-4" />
            Love Archives
          </div>
          <h1 className="text-5xl md:text-7xl font-black text-zinc-900 tracking-tighter uppercase leading-none">Your Discoveries</h1>
          <p className="text-zinc-500 font-black uppercase tracking-[0.4em] text-sm md:text-base italic">“The truth is recorded here.”</p>
        </div>
        
        {!loading && history.length > 0 && (
          <div className="glass-card px-8 py-4 border-white/50 flex items-center gap-4 shadow-lg backdrop-blur-2xl">
             <Sparkles className="w-5 h-5 text-primary" />
             <span className="text-lg font-black text-zinc-900">{history.length} Analyses</span>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-40 space-y-8 glass-card border-dashed">
            <div className="relative">
              <Loader2 className="w-20 h-20 text-primary animate-spin" />
              <div className="absolute inset-0 blur-3xl bg-primary/30 animate-pulse" />
            </div>
            <p className="text-zinc-500 font-black uppercase tracking-[0.5em] text-sm">Retrieving your archives...</p>
          </div>
        ) : error ? (
          <div className="glass-card p-16 text-center space-y-8 border-red-500/20 bg-rose-50/50">
            <p className="text-red-500 font-black text-xl">{error}</p>
            <button onClick={() => window.location.reload()} className="glass-button px-10 py-4 text-sm">Retry</button>
          </div>
        ) : history.length === 0 ? (
          <div className="glass-card p-24 text-center space-y-10 flex flex-col items-center border-dashed border-white/40">
            <div className="w-32 h-32 bg-zinc-100 rounded-full flex items-center justify-center accent-glow border-2 border-white shadow-inner">
              <MessageCircleHeart className="w-16 h-16 text-zinc-300" />
            </div>
            <div className="space-y-3">
              <h3 className="text-3xl font-black text-zinc-900 tracking-tighter italic">Archive Empty</h3>
              <p className="text-zinc-500 font-bold text-lg">Start your first analysis to reveal the truth.</p>
            </div>
            <Link to="/analyze" className="glass-button px-12 py-5 text-lg flex items-center gap-4">
               Analyze Now
               <ArrowRight className="w-6 h-6" />
            </Link>
          </div>
        ) : (
          <div className="grid gap-6">
            {history.map((item, idx) => (
              <motion.div
                key={item.id || idx}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05, duration: 0.5 }}
                className="glass-card p-10 flex flex-col md:flex-row items-center justify-between gap-8 group hover:border-primary/40 hover:bg-white/90 transition-all cursor-pointer relative overflow-hidden shadow-xl"
              >
                <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-primary via-orange-400 to-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex-1 space-y-4 w-full">
                  <div className="flex justify-between md:justify-start gap-8 items-center">
                    <span className="text-xs font-black text-primary uppercase tracking-[0.2em] bg-primary/10 px-4 py-1 rounded-full border border-primary/20">
                      {item.interest_level} vibe
                    </span>
                    <span className="text-xs font-black text-zinc-400 uppercase tracking-[0.3em] italic">Archive #{history.length - idx}</span>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-zinc-800 font-bold text-xl leading-relaxed max-w-2xl italic">
                      “{item.messages && item.messages.length > 0 ? (item.messages[0].length > 60 ? item.messages[0].substring(0, 60) + '...' : item.messages[0]) : (item.suggested_action || 'No message preview')}”
                    </h3>
                    {item.messages && item.messages.length > 0 && (
                      <div className="space-y-3">
                         <div className="flex flex-wrap gap-2">
                           {item.messages.slice(0, 2).map((msg: string, i: number) => (
                             <span key={i} className="text-[10px] font-black uppercase tracking-widest bg-zinc-50 text-zinc-400 px-3 py-1 rounded-lg border border-zinc-100">
                               {msg.length > 30 ? msg.substring(0, 30) + '...' : msg}
                             </span>
                           ))}
                           {item.messages.length > 2 && (
                             <button 
                               onClick={(e) => {
                                 e.preventDefault();
                                 e.stopPropagation();
                                 const el = document.getElementById(`transcript-${item.id}`);
                                 if (el) el.classList.toggle('hidden');
                               }}
                               className="text-[10px] font-black text-primary px-3 py-1 hover:underline"
                             >
                               +{item.messages.length - 2} more
                             </button>
                           )}
                         </div>
                         <div id={`transcript-${item.id}`} className="hidden space-y-2 pt-2 border-t border-zinc-100">
                            {item.messages.map((msg: string, i: number) => (
                              <p key={i} className="text-xs text-zinc-500 font-medium italic">{msg}</p>
                            ))}
                         </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-12 w-full md:w-auto justify-between md:justify-end">
                  <div className="flex flex-col items-end">
                    <span className="text-4xl font-black text-zinc-900 flex items-center gap-3">
                      <Activity className="w-6 h-6 text-indigo-500" />
                      {item.seriousness_score}%
                    </span>
                    <span className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.4em]">Intensity</span>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <button 
                      onClick={(e) => handleDelete(item.id, e)}
                      className="w-14 h-14 rounded-2xl bg-zinc-50 border border-zinc-100 flex items-center justify-center text-zinc-400 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 transition-all shadow-sm"
                      title="Delete Archive"
                    >
                      <Trash2 className="w-6 h-6" />
                    </button>
                    <Link 
                      to="/result" 
                      state={{ result: item }}
                      className="w-14 h-14 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center text-white group-hover:bg-primary shadow-xl hover:scale-105 transition-all"
                    >
                      <ArrowRight className="w-8 h-8" />
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
