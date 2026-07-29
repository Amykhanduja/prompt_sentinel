import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Maximize2, Minimize2, CheckCircle2, Target, Percent } from 'lucide-react';
import { SemanticData } from '../../services/semanticApi';

interface SemanticKpisProps {
  data: SemanticData['kpis'] | null;
  loading: boolean;
}

const formatScore = (num: number) => num.toFixed(3);
const formatPercent = (num: number) => `${(num * 100).toFixed(1)}%`;
const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);

export const SemanticKpis: React.FC<SemanticKpisProps> = ({ data, loading }) => {
  const kpis = [
    { title: 'Avg Similarity', value: data?.avgSimilarity, format: formatScore, icon: BrainCircuit, color: 'text-primary' },
    { title: 'Highest Similarity', value: data?.highestSimilarity, format: formatScore, icon: Maximize2, color: 'text-danger' },
    { title: 'Lowest Similarity', value: data?.lowestSimilarity, format: formatScore, icon: Minimize2, color: 'text-success' },
    { title: 'Avg Confidence', value: data?.avgConfidence, format: formatPercent, icon: Target, color: 'text-purple-400' },
    { title: 'Semantic Matches', value: data?.semanticMatches, format: formatNumber, icon: CheckCircle2, color: 'text-amber-400' },
    { title: 'Detection Rate', value: data?.semanticDetectionRate, format: formatPercent, icon: Percent, color: 'text-emerald-400' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {kpis.map((kpi, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: i * 0.05 }}
          className="glass-panel p-4 flex flex-col justify-between h-28 group"
        >
          <div className="flex justify-between items-start">
            <h3 className="text-xs font-medium text-gray-400 group-hover:text-gray-200 transition-colors uppercase tracking-wider">{kpi.title}</h3>
            <div className={`p-1.5 rounded-md bg-white/5 ${kpi.color}`}>
              <kpi.icon className="w-3.5 h-3.5" />
            </div>
          </div>
          
          <div className="mt-2 truncate">
            {loading ? (
              <div className="h-6 w-16 bg-white/10 rounded animate-pulse"></div>
            ) : data === null || kpi.value === undefined ? (
              <span className="text-sm font-semibold text-gray-500">No Data</span>
            ) : (
              <motion.span 
                key={String(kpi.value)}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-2xl font-bold text-white tracking-tight"
              >
                {kpi.format(kpi.value)}
              </motion.span>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
};
