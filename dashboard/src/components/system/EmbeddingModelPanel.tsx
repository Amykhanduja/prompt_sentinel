import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Loader2, CheckCircle2, ShieldAlert } from 'lucide-react';
import { SystemData } from '../../services/systemApi';

interface EmbeddingModelPanelProps {
  data: SystemData['embeddingModelInfo'] | null;
  loading: boolean;
}

export const EmbeddingModelPanel: React.FC<EmbeddingModelPanelProps> = ({ data, loading }) => {
  const getStatusIcon = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'loaded') return <CheckCircle2 className="w-5 h-5 text-success" />;
    if (s === 'loading') return <Loader2 className="w-5 h-5 text-warning animate-spin" />;
    return <ShieldAlert className="w-5 h-5 text-danger" />;
  };

  return (
    <div className="glass-panel p-5 h-full flex flex-col relative overflow-hidden border-t-2 border-purple-500/50">
      <div className="absolute bottom-0 right-0 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="flex justify-between items-start mb-6 z-10">
        <div className="flex items-center gap-2 text-white">
          <Brain className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-semibold uppercase tracking-wider">Embedding Model</h3>
        </div>
        {!loading && data && (
          <div className="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/10 shadow-inner">
            {getStatusIcon(data.loadingStatus)}
            <span className="text-xs font-bold uppercase tracking-wider text-gray-300">
              {data.loadingStatus}
            </span>
          </div>
        )}
      </div>
      
      <div className="flex-1 flex flex-col justify-center relative z-10">
        {loading ? (
          <div className="space-y-4">
            <div className="w-3/4 h-8 bg-white/10 rounded animate-pulse"></div>
            <div className="w-1/2 h-6 bg-white/10 rounded animate-pulse"></div>
            <div className="w-2/3 h-6 bg-white/10 rounded animate-pulse"></div>
          </div>
        ) : !data ? (
          <div className="flex items-center justify-center text-gray-500 h-full">
            No Data Available
          </div>
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div>
              <span className="text-[10px] text-gray-500 uppercase block mb-1">Active Model</span>
              <span className="text-2xl font-bold text-white tracking-tight">{data.modelName}</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                <span className="text-[10px] text-gray-500 uppercase block mb-1">Vector Dimensions</span>
                <span className="text-xl font-mono text-cyan-400">{data.dimensions}</span>
              </div>
              <div className="bg-black/40 p-4 rounded-lg border border-white/5">
                <span className="text-[10px] text-gray-500 uppercase block mb-1">Avg Embed Time</span>
                <span className="text-xl font-mono text-purple-400">{data.avgEmbeddingTimeMs.toFixed(1)}ms</span>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};
