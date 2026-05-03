import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, Share2, Coffee, Lightbulb, TrendingUp, ChevronRight, 
  AlertTriangle, CheckCircle2, Calculator,
  Zap, Target
} from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export default function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { result } = location.state || {};
  const [currentTip, setCurrentTip] = useState(0);
  
  if (!result) return <div className="text-center py-20 text-zinc-500 font-black uppercase tracking-[0.5em]">No truth discovered yet.</div>;

  const { 
    seriousness_score, suggestions,
    date_strategy, effort_level, evidence, reasoning,
    should_go_on_date, date_decision_reason,
    boredom_level, psychological_insight, impression_strategy
  } = result;

  const scoreValue = seriousness_score || 0;
  let investmentLabel = "Moderate";
  
  if (scoreValue <= 30) {
    investmentLabel = "Low Investment";
  } else if (scoreValue >= 75) {
    investmentLabel = "High Investment";
  } else {
    investmentLabel = "Moderate Vibe";
  }

  // Personalization: If no tips from AI, use high-quality psychological fallbacks
  const dynamicTips = (impression_strategy && impression_strategy.length >= 3)
    ? impression_strategy.map((text: string, i: number) => ({ title: `Elite Strategy #${i+1}`, text, icon: i === 0 ? "🔥" : i === 1 ? "💎" : "⚡" }))
    : [
        { title: "Psychological Gap", text: "Leave their last non-question message on read for 3+ hours. It shifts the 'pursuer' dynamic instantly.", icon: "💎" },
        { title: "The Mirror Effect", text: "Match their exact reply length and emoji style for 24 hours to create subconscious comfort.", icon: "🌊" },
        { title: "Emotional Anchor", text: "Mention a shared niche memory. It bypasses casual chat and hits the subconscious connection.", icon: "✨" }
      ];

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Velra Truth Discovery',
          text: `My analysis shows a ${scoreValue}% seriousness vibe! Check your own truth on Velra.`,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Share canceled');
      }
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-20 pb-24 pt-10 px-6 relative">
      <div className="vibrant-bg" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div className="flex items-center gap-6">
          <button onClick={() => navigate(-1)} className="p-4 glass-card hover:bg-white transition-all group shadow-lg">
            <ArrowLeft className="w-6 h-6 text-zinc-600 group-hover:text-primary transition-colors" />
          </button>
          <div>
            <h1 className="text-5xl md:text-7xl font-black text-zinc-900 tracking-tighter uppercase leading-none">Intelligence</h1>
            <p className="text-zinc-600 text-lg md:text-xl font-bold uppercase tracking-[0.4em] mt-3">
               THEY’RE SHOWING YOU THE <span className="text-primary">TRUTH</span>. 
               <span className="inline-block transform scale-150 ml-4">🔥</span>
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-4">
          <button 
            onClick={() => navigate('/tips', { state: { chat_history: result?.messages?.join('\n') } })}
            className="glass-card hover:bg-zinc-900 hover:text-white px-8 py-5 flex items-center gap-4 text-sm font-black text-zinc-600 shadow-xl transition-all hover:scale-105 active:scale-95"
          >
             <Lightbulb className="w-5 h-5 text-yellow-500" />
             GET WIN STREAKS
          </button>
          <button 
            onClick={handleShare}
            className="glass-button px-10 py-5 flex items-center gap-4 text-lg font-black shadow-2xl hover:scale-105 active:scale-95 transition-all"
          >
             <Share2 className="w-6 h-6" />
             SHARE
          </button>
        </div>
      </div>

      {/* Verdict & Boredom Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <motion.div 
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className={`glass-card p-10 flex gap-10 border-2 ${should_go_on_date ? 'border-emerald-200 bg-emerald-50/30' : 'border-rose-200 bg-rose-50/30'} shadow-2xl relative overflow-hidden`}
        >
          <div className="flex-1 space-y-4">
            <h2 className={`text-4xl font-black tracking-tighter uppercase ${should_go_on_date ? 'text-emerald-600' : 'text-rose-600'}`}>
              Date Verdict: {should_go_on_date ? 'GO' : 'WAIT'}
            </h2>
            <p className="text-zinc-800 font-bold text-lg leading-relaxed italic">
              “{date_decision_reason}”
            </p>
          </div>
          <div className={`w-24 h-24 rounded-[2.5rem] flex items-center justify-center shrink-0 ${should_go_on_date ? 'bg-emerald-500' : 'bg-rose-500'} text-white shadow-xl`}>
             {should_go_on_date ? <CheckCircle2 className="w-12 h-12" /> : <AlertTriangle className="w-12 h-12" />}
          </div>
        </motion.div>

        <motion.div 
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="glass-card p-10 flex gap-10 border-2 border-indigo-100 bg-indigo-50/30 shadow-2xl relative overflow-hidden"
        >
          <div className="flex-1 space-y-4">
            <h2 className="text-4xl font-black tracking-tighter uppercase text-indigo-600">
               Boredom Level
            </h2>
            <p className="text-zinc-800 font-bold text-lg leading-relaxed italic">
               The conversation energy is currently <span className="text-indigo-600 underline decoration-2">{boredom_level}</span>. 
               {boredom_level.toLowerCase() === 'high' ? " It's time for a drastic vibe change." : " Keep this momentum."}
            </p>
          </div>
          <div className="w-24 h-24 rounded-[2.5rem] bg-indigo-600 flex items-center justify-center shrink-0 text-white shadow-xl">
             <Zap className="w-12 h-12" />
          </div>
        </motion.div>
      </div>

      {/* Psychological Deep-Dive */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="glass-card p-12 bg-zinc-900 text-white space-y-8 shadow-2xl border border-white/10"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div className="space-y-6">
            <h3 className="text-xs font-black text-zinc-500 uppercase tracking-[0.6em]">Psychological Deep-Dive</h3>
            <p className="text-2xl font-bold italic leading-relaxed text-zinc-200">
              “{psychological_insight || "They're strategically mirroring your patterns to gain emotional leverage."}”
            </p>
            <div className="p-8 bg-white/5 rounded-3xl border border-white/10 mt-6">
               <p className="text-zinc-400 font-bold text-sm leading-relaxed">
                 {reasoning || "Based on the linguistic frequency and engagement velocity, this user is exhibiting signs of high intellectual curiosity but guarded emotional availability."}
               </p>
            </div>
          </div>
          
          <div className="space-y-6">
            <h3 className="text-xs font-black text-primary uppercase tracking-[0.6em]">Behavioral Evidence</h3>
            <div className="space-y-4">
               {evidence && evidence.map((e: string, idx: number) => (
                 <motion.div 
                   key={idx}
                   initial={{ opacity: 0, x: 20 }}
                   animate={{ opacity: 1, x: 0 }}
                   transition={{ delay: idx * 0.1 }}
                   className="flex items-center gap-4 p-5 bg-white/5 rounded-2xl border border-white/5 group hover:bg-white/10 transition-all"
                 >
                    <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-black text-xs">
                      {idx + 1}
                    </div>
                    <span className="text-zinc-300 font-bold text-sm tracking-tight">{e}</span>
                 </motion.div>
               ))}
               {!evidence && (
                 <p className="text-zinc-500 italic text-sm">Quantifying signals for behavioral truth...</p>
               )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Swipeable: How to Win Their Heart */}
      <div className="space-y-10">
         <div className="flex items-center justify-between px-4">
            <h2 className="text-3xl font-black text-zinc-900 tracking-tighter uppercase flex items-center gap-6">
              <Target className="w-10 h-10 text-primary" />
              How to Win Their Heart
            </h2>
            <div className="flex gap-3">
               {dynamicTips.map((_: any, i: number) => (
                 <div key={i} className={`w-4 h-4 rounded-full transition-all duration-500 ${i === currentTip ? 'w-12 bg-primary shadow-lg shadow-primary/20' : 'bg-zinc-200'}`} />
               ))}
            </div>
         </div>

         <div className="relative h-96 md:h-72">
           <AnimatePresence mode="wait">
             <motion.div
               key={currentTip}
               initial={{ opacity: 0, scale: 0.95, x: 50 }}
               animate={{ opacity: 1, scale: 1, x: 0 }}
               exit={{ opacity: 0, scale: 0.95, x: -50 }}
               drag="x"
               dragConstraints={{ left: 0, right: 0 }}
               onDragEnd={(_: any, info: any) => {
                 if (info.offset.x < -100) setCurrentTip((prev) => (prev + 1) % dynamicTips.length);
                 if (info.offset.x > 100) setCurrentTip((prev) => (prev - 1 + dynamicTips.length) % dynamicTips.length);
               }}
               className="absolute inset-0 glass-card p-12 bg-white flex flex-col md:flex-row items-center gap-12 cursor-grab active:cursor-grabbing hover:shadow-2xl transition-all duration-500 border-2 border-white"
             >
                <div className="w-24 h-24 rounded-[2rem] bg-rose-50 flex items-center justify-center text-5xl border-2 border-rose-100 shadow-inner shrink-0 scale-125">
                  {dynamicTips[currentTip].icon}
                </div>
                <div className="space-y-4 text-center md:text-left">
                  <h4 className="text-xs font-black text-primary uppercase tracking-[0.8em] italic">Elite Advice</h4>
                  <h5 className="text-2xl md:text-3xl font-black text-zinc-900 uppercase italic tracking-tighter">{dynamicTips[currentTip].title}</h5>
                  <p className="text-zinc-600 font-bold text-xl md:text-2xl leading-relaxed max-w-3xl">
                    {dynamicTips[currentTip].text}
                  </p>
                  <p className="text-[10px] text-zinc-400 font-black uppercase tracking-[0.4em] pt-4">Drag card for your next move ↔</p>
                </div>
             </motion.div>
           </AnimatePresence>
         </div>
      </div>

      {/* Plan & Calculator Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <motion.div className="glass-card p-12 border-primary/20 bg-gradient-to-br from-white/90 to-rose-50/50 flex flex-col gap-10 shadow-xl overflow-hidden">
           <div className="flex items-center justify-between">
              <h3 className="text-xs font-black text-primary uppercase tracking-[0.6em] flex items-center gap-3 italic">
                  <Coffee className="w-5 h-5" /> The Plan
              </h3>
           </div>
           <div className="space-y-6">
              <h4 className="text-5xl font-black text-zinc-900 uppercase italic tracking-wide">{date_strategy?.type || "Coffee"} Date</h4>
              <p className="text-xl font-bold text-zinc-700 italic leading-relaxed bg-white/40 p-6 rounded-3xl border-2 border-white/60 shadow-inner">
                "{date_strategy?.justification}"
              </p>
           </div>
        </motion.div>

        <motion.div className="glass-card p-12 bg-zinc-900 text-white space-y-10 shadow-2xl relative overflow-hidden group">
           <div className="flex items-center justify-between">
              <h3 className="text-xs font-black text-white/40 uppercase tracking-[0.6em] flex items-center gap-3 italic">
                  <Calculator className="w-5 h-5" /> Date Calculator
              </h3>
              <button 
                onClick={() => navigate('/date-calculator')}
                className="p-3 bg-primary/20 rounded-xl hover:bg-primary/40 transition-all group"
                title="Launch Optimizer"
              >
                <TrendingUp className="w-6 h-6 text-primary group-hover:scale-110 transition-transform" />
              </button>
           </div>
           <div className="space-y-8">
              <div className="flex justify-between items-center border-b border-white/5 pb-4">
                 <span className="text-zinc-400 font-bold uppercase tracking-widest text-xs">Estimated Cost</span>
                 <span className="text-4xl font-black text-primary">{date_strategy?.budget || "$$"}</span>
              </div>
              <div className="grid grid-cols-2 gap-6">
                 <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                    <p className="text-[10px] text-zinc-500 font-black uppercase mb-2">Effort Scale</p>
                    <p className="text-lg font-black">{effort_level || "Balanced"}</p>
                 </div>
                 <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                    <p className="text-[10px] text-zinc-500 font-black uppercase mb-2">Psych Check</p>
                    <p className="text-lg font-black">{investmentLabel}</p>
                 </div>
              </div>
           </div>
        </motion.div>
      </div>

       {/* Behavioral Insights */}
       <div className="glass-card p-12 space-y-8 bg-white/80 border-2 border-white shadow-2xl">
          <h3 className="text-xl font-black text-zinc-900 uppercase tracking-widest flex items-center gap-4">
            <Lightbulb className="w-8 h-8 text-yellow-500" />
            Behavioral Insight
          </h3>
          <div className="grid md:grid-cols-2 gap-10">
            {suggestions && suggestions.slice(0, 2).map((s: string, i: number) => (
              <div key={i} className="p-8 rounded-3xl bg-zinc-50 border border-zinc-100 italic font-bold text-xl text-zinc-700 leading-relaxed shadow-inner">
                 “{s}”
              </div>
            ))}
            {(!suggestions || suggestions.length === 0) && (
              <div className="p-8 rounded-3xl bg-zinc-50 border border-zinc-100 italic font-bold text-xl text-zinc-700 leading-relaxed shadow-inner col-span-2">
                 “They’re currently evaluating your social value before deciding their next major emotional move.”
              </div>
            )}
          </div>
       </div>

      {/* Suggestion CTA */}
      <div className="pt-16 flex flex-col items-center gap-12">
        <div className="text-center space-y-4">
           <p className="text-xs font-black text-zinc-500 uppercase tracking-[0.6em]">Endless Clarity Guaranteed</p>
           <h3 className="text-3xl md:text-5xl font-black text-zinc-900 uppercase tracking-tighter leading-none">Your Next Move is Ready</h3>
        </div>
        <Link 
          to="/suggestions" 
          className="glass-button px-24 py-10 text-3xl font-black group shadow-[0_30px_70px_rgba(244,63,94,0.4)] hover:shadow-[0_40px_90px_rgba(244,63,94,0.6)] flex items-center gap-6"
        >
          GENERATE REPLIES
          <ChevronRight className="w-10 h-10 group-hover:translate-x-4 transition-transform duration-500 ease-out" />
        </Link>
      </div>
    </div>
  );
}
