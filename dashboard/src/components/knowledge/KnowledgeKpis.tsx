import React from 'react';
import { motion } from 'framer-motion';
import { Database, BookOpen, Quote, ShieldMinus, Target, Orbit, SlidersHorizontal, GitMerge } from 'lucide-react';
import { KnowledgeData } from '../../services/knowledgeApi';

interface KnowledgeKpisProps {
  data: KnowledgeData['kpis'] | null;
  loading: boolean;
}

const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);
const formatPercent = (num: number) => `${(num * 100).toFixed(1)}%`;
const formatScore = (num: number) => num.toFixed(2);

export const KnowledgeKpis: React.FC<KnowledgeKpisProps> = ({ data, loading }) => {
  const kpis: any[] = [
    { title: 'Total Techniques', value: data?.totalTechniques, format: formatNumber, icon: Database, color: 'text-primary' },
    { title: 'Canonical Examples', value: data?.totalCanonicalExamples, format: formatNumber, icon: BookOpen, color: 'text-emerald-400' },
    { title: 'Total Paraphrases', value: data?.totalParaphrases, format: formatNumber, icon: Quote, color: 'text-purple-400' },
    { title: 'Negative Examples', value: data?.totalNegativeExamples, format: formatNumber, icon: ShieldMinus, color: 'text-danger' },
    { title: 'Avg Examples/Tech', value: data?.avgExamplesPerTechnique, format: formatScore, icon: Target, color: 'text-warning' },
    { title: 'Avg Coverage', value: data?.avgSemanticCoverage, format: formatPercent, icon: Orbit, color: 'text-cyan-400' },
    { title: 'Avg Threshold', value: data?.avgThreshold, format: formatScore, icon: SlidersHorizontal, color: 'text-pink-400' },
    { title: 'KB Version', value: data?.knowledgeBaseVersion, format: (s: string) => s, icon: GitMerge, color: 'text-gray-300' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
                className={`font-bold tracking-tight truncate ${typeof kpi.value === 'string' ? 'text-xl text-gray-200 font-mono' : 'text-2xl text-white'}`}
                title={String(kpi.value)}
              >
                {typeof kpi.value === 'number' ? kpi.format(kpi.value as number) : kpi.format(kpi.value as string)}
              </motion.span>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
};
