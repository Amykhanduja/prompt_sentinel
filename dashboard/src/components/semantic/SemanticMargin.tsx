import React from 'react';
import { SemanticData } from '../../services/semanticApi';
import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';

interface SemanticMarginProps {
  data: SemanticData['margin'] | null;
  loading: boolean;
}

export const SemanticMargin: React.FC<SemanticMarginProps> = ({ data, loading }) => {
  return (
    <div className="glass-panel p-5 h-full flex flex-col justify-center relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <h3 className="text-sm font-semibold mb-6 text-gray-300 uppercase tracking-widest text-center">Semantic Margin Analysis</h3>
      
      {loading ? (
        <div className="space-y-6 flex flex-col items-center">
          <div className="w-24 h-8 bg-white/10 rounded animate-pulse"></div>
          <div className="w-32 h-10 bg-white/10 rounded animate-pulse"></div>
          <div className="w-24 h-8 bg-white/10 rounded animate-pulse"></div>
        </div>
      ) : !data ? (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          No Data Available
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center space-y-6 z-10">
          <div className="flex flex-col items-center">
            <span className="text-xs text-danger flex items-center gap-1 mb-1 bg-danger/10 px-2 py-0.5 rounded-full border border-danger/20">
              <Check className="w-3 h-3" /> Positive Matches
            </span>
            <span className="text-2xl font-mono font-bold text-white shadow-danger/20">{data.avgPositiveSimilarity.toFixed(3)}</span>
          </div>

          <div className="relative w-full flex justify-center items-center py-2">
            <div className="absolute left-1/2 -translate-x-1/2 w-px h-full bg-white/10"></div>
            <motion.div 
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="bg-black/60 border border-purple-500/30 px-4 py-2 rounded-xl flex flex-col items-center shadow-[0_0_15px_rgba(168,85,247,0.2)] z-10 backdrop-blur-md"
            >
              <span className="text-[10px] text-purple-300 uppercase tracking-widest mb-1">Margin</span>
              <span className="text-xl font-bold text-purple-400">Δ {data.semanticMargin.toFixed(3)}</span>
            </motion.div>
          </div>

          <div className="flex flex-col items-center">
            <span className="text-xl font-mono font-bold text-white">{data.avgNegativeSimilarity.toFixed(3)}</span>
            <span className="text-xs text-success flex items-center gap-1 mt-1 bg-success/10 px-2 py-0.5 rounded-full border border-success/20">
              <X className="w-3 h-3" /> Negative Matches
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
