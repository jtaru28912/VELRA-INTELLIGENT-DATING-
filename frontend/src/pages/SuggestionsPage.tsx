import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Copy, Check, Sparkles, X, Heart } from 'lucide-react';

const SUGGESTIONS = [
  {
    id: 1,
    type: 'Flirty & Playful',
    text: "Haha I was wondering when you'd ask! I'm free this weekend, what are you thinking?",
    score: 95
  },
  {
    id: 2,
    type: 'Direct & Chill',
    text: "I'd love to. Friday night works best for me.",
    score: 80
  },
  {
    id: 3,
    type: 'Mysterious',
    text: "Maybe... guess you'll have to convince me 😉",
    score: 70
  }
];

export default function SuggestionsPage() {
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [cards, setCards] = useState(SUGGESTIONS);

  const handleCopy = (id: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const removeCard = (id: number) => {
    setCards((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="w-full max-w-lg mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold font-poppins flex items-center justify-center gap-2">
          <Sparkles className="w-6 h-6 text-pink-400" />
          AI Reply Suggestions
        </h1>
        <p className="text-zinc-400">Swipe or select the perfect reply.</p>
      </div>

      <div className="relative h-[400px] w-full">
        <AnimatePresence>
          {cards.map((card, index) => {
            const isTop = index === cards.length - 1;
            return (
              <motion.div
                key={card.id}
                initial={{ scale: 0.95, opacity: 0, y: 20 }}
                animate={{ 
                  scale: 1 - (cards.length - 1 - index) * 0.05, 
                  opacity: 1 - (cards.length - 1 - index) * 0.2, 
                  y: (cards.length - 1 - index) * 15 
                }}
                exit={{ x: -200, opacity: 0, rotate: -20 }}
                transition={{ duration: 0.3 }}
                className="absolute inset-0 w-full"
                drag={isTop ? "x" : false}
                dragConstraints={{ left: 0, right: 0 }}
                onDragEnd={(_, info) => {
                  if (info.offset.x < -100 || info.offset.x > 100) {
                    removeCard(card.id);
                  }
                }}
              >
                <div className="h-full bg-zinc-900 border border-zinc-800 rounded-3xl p-6 flex flex-col justify-between shadow-2xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-pink-500/10 rounded-bl-full shadow-[0_0_50px_rgba(236,72,153,0.1)] -z-10" />
                  
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold tracking-wider uppercase text-pink-400 bg-pink-500/10 px-3 py-1 rounded-full">
                        {card.type}
                      </span>
                      <span className="flex items-center gap-1 text-sm font-medium text-zinc-400">
                        <Heart className="w-4 h-4 text-pink-500" /> {card.score}% Match
                      </span>
                    </div>
                    <p className="text-xl font-medium text-white leading-relaxed pt-4">
                      "{card.text}"
                    </p>
                  </div>

                  <div className="flex justify-between items-center gap-4 pt-4 border-t border-zinc-800">
                    <button 
                      onClick={() => removeCard(card.id)}
                      className="p-3 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-400 rounded-full transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                    
                    <button 
                      onClick={() => handleCopy(card.id, card.text)}
                      className="flex-1 glass-button py-3 flex justify-center items-center gap-2"
                    >
                      {copiedId === card.id ? (
                        <>
                          <Check className="w-5 h-5" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-5 h-5" />
                          Copy to Clipboard
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
          
          {cards.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500 space-y-4"
            >
              <Sparkles className="w-12 h-12 opacity-20" />
              <p>No more suggestions!</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
