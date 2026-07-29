import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Search, BrainCircuit, Network, Layers, Target, AlertTriangle, Crosshair } from 'lucide-react';
import { DetectionsData } from '../../services/detectionsApi';

interface DetectionKpisProps {
  data: DetectionsData['kpis'] | null;
  loading: boolean;
}

const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);

export const DetectionKpis: React.FC<DetectionKpisProps> = ({ data, loading }) => {
  const kpis: any[] = [
    { title: 'Total Detections', value: data?.totalDetections, format: formatNumber, icon: ShieldAlert, color: 'text-danger' },
    { title: 'Regex Detections', value: data?.regexDetections, format: formatNumber, icon: Search, color: 'text-blue-400' },
    { title: 'Semantic Detections', value: data?.semanticDetections, format: formatNumber, icon: BrainCircuit, color: 'text-purple-400' },
    { title: 'Fusion Detections', value: data?.fusionDetections, format: formatNumber, icon: Network, color: 'text-amber-400' },
    { title: 'Multi-Technique', value: data?.multiTechniquePrompts, format: formatNumber, icon: Layers, color: 'text-pink-400' },
    { title: 'Avg Techniques/Prompt', value: data?.avgTechniquesPerPrompt, format: (n: number) => n.toFixed(1), icon: Target, color: 'text-emerald-400' },
    { title: 'Highest Risk', value: data?.highestRiskTechnique, format: (s: string) => s, icon: AlertTriangle, color: 'text-danger' },
    { title: 'Most Frequent', value: data?.mostFrequentTechnique, format: (s: string) => s, icon: Crosshair, color: 'text-primary' },
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
              <div className="h-6 w-20 bg-white/10 rounded animate-pulse"></div>
            ) : data === null || kpi.value === undefined ? (
              <span className="text-sm font-semibold text-gray-500">No Data</span>
            ) : (
              <motion.span 
                key={String(kpi.value)}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`text-2xl font-bold tracking-tight truncate ${typeof kpi.value === 'string' ? 'text-lg text-gray-200' : 'text-white'}`}
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
