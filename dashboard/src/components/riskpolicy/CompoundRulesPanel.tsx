import React from 'react';
import { RiskPolicyData } from '../../services/riskPolicyApi';
import { GitMerge } from 'lucide-react';
import { motion } from 'framer-motion';

interface CompoundRulesPanelProps {
  data: RiskPolicyData['compoundRuleActivations'] | null;
  loading: boolean;
}

export const CompoundRulesPanel: React.FC<CompoundRulesPanelProps> = ({ data, loading }) => {
  return (
    <div className="glass-panel p-5 h-full flex flex-col relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="flex items-center gap-2 mb-6 text-white z-10">
        <GitMerge className="w-5 h-5 text-primary" />
        <h3 className="text-sm font-semibold uppercase tracking-wider">Compound Rules</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto relative z-10 pr-2">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex justify-between items-center w-full">
                <div className="w-3/4 h-5 bg-white/10 rounded animate-pulse"></div>
                <div className="w-8 h-5 bg-white/10 rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        ) : !data || data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <div className="space-y-3">
            {data.map((rule, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex justify-between items-center bg-black/40 p-3 rounded-lg border border-white/5 hover:bg-white/5 transition-colors group"
              >
                <span className="text-xs font-mono text-gray-300 group-hover:text-primary transition-colors truncate pr-4">
                  {rule.ruleName}
                </span>
                <span className="px-2 py-1 bg-white/10 rounded text-xs font-bold text-white shadow-inner">
                  {rule.activations}
                </span>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
