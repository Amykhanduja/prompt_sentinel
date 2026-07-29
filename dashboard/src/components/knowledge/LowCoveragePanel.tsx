import React from 'react';
import { KnowledgeData } from '../../services/knowledgeApi';
import { AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

interface LowCoveragePanelProps {
  data: KnowledgeData['lowCoverageTechniques'] | null;
  loading: boolean;
}

export const LowCoveragePanel: React.FC<LowCoveragePanelProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-[350px] flex flex-col relative overflow-hidden border-danger/20 border">
      <div className="absolute top-0 right-0 w-32 h-32 bg-danger/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="flex items-center gap-2 mb-4 text-white z-10">
        <AlertTriangle className="w-5 h-5 text-danger animate-pulse" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-danger">Low Semantic Coverage</h3>
      </div>
      
      <p className="text-xs text-gray-400 mb-4">
        These techniques lack sufficient semantic examples to reliably detect variations. Adding recommended examples will improve detection rates.
      </p>

      <div className="flex-1 overflow-y-auto relative z-10 pr-2">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex justify-between items-center w-full">
                <div className="w-1/2 h-5 bg-white/10 rounded animate-pulse"></div>
                <div className="w-1/4 h-2 bg-white/10 rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        ) : !hasData ? (
          <div className="absolute inset-0 flex items-center justify-center text-success text-sm">
            All techniques have healthy coverage!
          </div>
        ) : (
          <div className="space-y-4">
            {data.map((tech, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex flex-col gap-1.5"
              >
                <div className="flex justify-between items-end">
                  <div>
                    <span className="text-white font-medium text-sm block">{tech.techniqueId}</span>
                    <span className="text-xs text-gray-500 truncate block max-w-[150px]">{tech.techniqueName}</span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-xs font-bold text-danger">{(tech.coverage * 100).toFixed(1)}% Coverage</span>
                    <span className="text-[10px] text-gray-400">+{tech.recommendedExamples} needed</span>
                  </div>
                </div>
                <div className="w-full bg-black/40 rounded-full h-1.5 overflow-hidden border border-white/5">
                  <div 
                    className="h-full bg-danger transition-all duration-1000 ease-out"
                    style={{ width: `${tech.coverage * 100}%` }}
                  ></div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
