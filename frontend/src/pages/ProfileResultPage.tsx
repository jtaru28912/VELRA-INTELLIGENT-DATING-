import { useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Brain, Target, MessageSquareCode, Heart, AlertCircle, TrendingUp, ChevronLeft, Sparkles } from 'lucide-react';

export default function ProfileResultPage() {
  const location = useLocation();
  const { profile } = location.state || {};

  if (!profile) return <div className="text-center py-20">No personality data found.</div>;

  const { summary, personality_type, interests, lifestyle, communication_style, values } = profile.extracted_traits;

  const sections = [
    { title: 'Personality Type', icon: <Brain className="w-5 h-5 text-purple-600" />, content: personality_type, color: 'border-purple-500/30' },
    { title: 'Communication style', icon: <MessageSquareCode className="w-5 h-5 text-blue-600" />, content: communication_style, color: 'border-blue-500/30' },
    { title: 'Lifestyle', icon: <Target className="w-5 h-5 text-rose-600" />, content: lifestyle, color: 'border-rose-500/30' },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto space-y-12 py-10 px-6 relative">
      <div className="vibrant-bg" />
      
      <div className="flex items-center justify-between">
        <Link to="/analyze" className="p-4 glass-card hover:bg-white transition-all group shadow-lg">
          <ChevronLeft className="w-6 h-6 text-zinc-600 group-hover:text-primary" />
        </Link>
        <div className="text-center">
          <h1 className="text-5xl font-black text-zinc-900 tracking-tighter uppercase leading-none">Personality Profile</h1>
          <p className="text-zinc-500 text-xs font-black uppercase tracking-[0.5em] mt-2">Target Intelligence Report</p>
        </div>
        <div className="w-12 h-12 bg-white/60 backdrop-blur-xl rounded-2xl flex items-center justify-center border border-white/40 shadow-sm">
          <Sparkles className="w-6 h-6 text-primary" />
        </div>
      </div>

      {/* Narrative Summary */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-10 bg-white/60 backdrop-blur-3xl border-2 border-white shadow-2xl"
      >
        <h2 className="text-xs font-black text-primary uppercase tracking-[0.6em] mb-6 italic">Evaluation Summary</h2>
        <p className="text-2xl md:text-3xl font-black text-zinc-800 italic leading-relaxed tracking-tight">
          “{summary || `I have successfully evaluated this profile. They appear to be a ${personality_type} individual with a ${lifestyle} lifestyle.`}”
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {sections.map((s, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`glass-card p-6 border-b-2 ${s.color} space-y-3`}
          >
            <div className="flex items-center gap-2 text-zinc-500">
              {s.icon}
              <span className="text-xs font-bold uppercase tracking-widest">{s.title}</span>
            </div>
            <p className="text-xl font-bold text-white">{s.content}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <motion.div 
          initial={{ opacity: 0, x: -20 }} 
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-8 space-y-6"
        >
          <div className="space-y-6">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-zinc-400">
                <Heart className="w-5 h-5 text-pink-500" />
                <h2 className="text-lg font-bold text-white uppercase tracking-tight">Core Values</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {values.map((v: string) => (
                  <span key={v} className="px-3 py-1 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-sm">
                    {v}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-zinc-400">
                <Target className="w-5 h-5 text-indigo-500" />
                <h2 className="text-lg font-bold text-white uppercase tracking-tight">Interests</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {interests.map((i: string) => (
                  <span key={i} className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm">
                    {i}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }} 
          animate={{ opacity: 1, x: 0 }}
          className="glass-card p-8 bg-gradient-to-br from-zinc-900 to-zinc-950 border-primary/20 space-y-6"
        >
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-primary" />
            <h2 className="text-xl font-bold text-gradient">Win Strategy</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-5 rounded-2xl bg-white/5 border border-white/5 space-y-2">
              <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Ideal Approach</span>
              <p className="text-zinc-200">
                Since they value <span className="text-pink-300 font-medium">social engagement</span>, avoid being too passive. Lead with open-ended questions about their travel experiences.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-primary/5 border border-primary/10 space-y-2">
              <div className="flex items-center gap-2 text-primary">
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-widest">Keep in Mind</span>
              </div>
              <p className="text-zinc-300">
                They likely prefer directness. Don't hide behind too many emojis or vague plans. Be clear about why you find their profile interesting.
              </p>
            </div>
          </div>

          <Link to="/analyze" state={{ profile_id: profile.id }} className="w-full glass-button py-3 text-center block mt-4">
            Analyze Chat with this Profile
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
