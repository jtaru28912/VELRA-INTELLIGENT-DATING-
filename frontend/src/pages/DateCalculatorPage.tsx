import { useState } from 'react';
import { motion } from 'framer-motion';
import { Calculator, Sparkles, ChevronLeft, Loader2, DollarSign, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';

const BUDGETS = [
  { label: 'Low', value: '$', icon: '🥪' },
  { label: 'Mid', value: '$$', icon: '🍝' },
  { label: 'High', value: '$$$', icon: '🍾' }
];

const INTENTS = [
  { label: 'Casual', value: 'casual', icon: '🎮' },
  { label: 'Serious', value: 'serious', icon: '💍' },
  { label: 'First Meet', value: 'first meet', icon: '☕' }
];

export default function DateCalculatorPage() {
  const navigate = useNavigate();
  const [budget, setBudget] = useState(BUDGETS[1].value);
  const [intent, setIntent] = useState(INTENTS[2].value);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<any>(null);

  const calculateDate = async () => {
    setLoading(true);
    try {
      const data = await apiFetch('/calculate/date', {
        method: 'POST',
        body: JSON.stringify({ budget, intent })
      });
      setPlan(data);
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
        <h1 className="text-4xl font-black text-zinc-900 tracking-tighter uppercase">Date Planner</h1>
        <Calculator className="w-8 h-8 text-primary" />
      </div>

      {!plan && !loading && (
         <div className="space-y-12">
            <div className="space-y-6">
              <label className="text-xs font-black text-zinc-400 uppercase tracking-[0.5em] ml-2">Choose Budget</label>
              <div className="grid grid-cols-3 gap-4">
                {BUDGETS.map((b) => (
                  <button
                    key={b.value}
                    onClick={() => setBudget(b.value)}
                    className={`p-6 rounded-3xl flex flex-col items-center gap-2 border-2 transition-all ${
                      budget === b.value ? 'bg-primary/5 border-primary text-primary scale-105 shadow-xl' : 'glass-card border-transparent text-zinc-400'
                    }`}
                  >
                    <span className="text-3xl">{b.icon}</span>
                    <span className="font-black text-xs uppercase">{b.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <label className="text-xs font-black text-zinc-400 uppercase tracking-[0.5em] ml-2">Select intent</label>
              <div className="grid grid-cols-3 gap-4">
                {INTENTS.map((i) => (
                  <button
                    key={i.value}
                    onClick={() => setIntent(i.value)}
                    className={`p-6 rounded-3xl flex flex-col items-center gap-2 border-2 transition-all ${
                      intent === i.value ? 'bg-indigo-50 border-indigo-400 text-indigo-600 scale-105 shadow-xl' : 'glass-card border-transparent text-zinc-400'
                    }`}
                  >
                    <span className="text-3xl">{i.icon}</span>
                    <span className="font-black text-xs uppercase">{i.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <button 
              onClick={calculateDate}
              className="w-full glass-button py-8 text-2xl font-black flex items-center justify-center gap-6 shadow-[0_20px_50px_rgba(244,63,94,0.3)]"
            >
              PLAN THE PERFECT DATE
              <Sparkles className="w-8 h-8" />
            </button>
         </div>
      )}

      {loading && (
        <div className="py-20 flex flex-col items-center gap-8">
          <Loader2 className="w-16 h-16 text-primary animate-spin" />
          <p className="text-xl font-black text-zinc-900 uppercase tracking-widest text-center">Coordinating with Top Venues...</p>
        </div>
      )}

      {plan && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <div className="glass-card p-10 bg-zinc-900 text-white space-y-6 overflow-hidden relative">
            <DollarSign className="absolute -right-10 -top-10 w-40 h-40 text-white/5 rotate-12" />
            <h4 className="text-primary font-black uppercase text-[10px] tracking-[0.5em]">The Master Plan</h4>
            <h5 className="text-4xl font-black tracking-tighter uppercase">{plan.date_type}</h5>
            <p className="text-xl font-bold italic text-zinc-300 leading-relaxed">“{plan.justification}”</p>
            <div className="flex gap-4">
               <div className="px-4 py-2 bg-white/10 rounded-xl text-xs font-black uppercase tracking-widest border border-white/10">
                  EST: {plan.budget_range}
               </div>
            </div>
          </div>

          <div className="grid gap-6">
             <div className="glass-card p-10 space-y-6 bg-white/80 border-2 border-white">
                <h6 className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.8em]">Step-by-Step Experience</h6>
                <div className="space-y-6">
                   {plan.plan.map((step: string, i: number) => (
                      <div key={i} className="flex gap-4 items-start">
                         <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-black text-xs shrink-0">{i+1}</div>
                         <p className="text-zinc-700 font-bold leading-relaxed">{step}</p>
                      </div>
                   ))}
                </div>
             </div>
             
             <div className="glass-card p-10 bg-indigo-50 border-indigo-100 border-2 space-y-4">
                <div className="flex items-center gap-3 text-indigo-600">
                   <Target className="w-6 h-6" />
                   <h6 className="text-xs font-black uppercase tracking-[0.5em]">Senior Strategist Pro Tip</h6>
                </div>
                <p className="text-indigo-900 font-bold italic text-lg leading-relaxed">“{plan.pro_tip}”</p>
             </div>
          </div>

          <button onClick={() => setPlan(null)} className="w-full py-6 text-zinc-400 font-black uppercase text-xs tracking-widest border-2 border-dashed border-zinc-200 rounded-3xl hover:border-primary/20 hover:text-primary transition-all">
             Recalculate another date
          </button>
        </motion.div>
      )}
    </div>
  );
}
