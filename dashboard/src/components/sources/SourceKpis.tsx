import React from 'react';
import { motion } from 'framer-motion';
import { Layers, FileText, User, Activity, AlertTriangle, ShieldCheck, Target, Crosshair } from 'lucide-react';
import { SourceData } from '../../services/sourceApi';

interface SourceKpisProps {
  data: SourceData['kpis'] | null;
  loading: boolean;
}

const formatScore = (num: number) => num.toFixed(1);
const formatPercent = (num: number) => `${(num * 100).toFixed(1)}%`;
const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);

export const SourceKpis: React.FC<SourceKpisProps> = ({ data, loading }) => {
  const kpis: any[] = [
    { title: 'Total Sources', value: data?.totalSources, format: formatNumber, icon: Layers, color: 'text-primary' },
    { title: 'Most Active', value: data?.mostActiveSource, format: (s: string) => s, icon: Activity, color: 'text-success' },
    { title: 'Highest Risk', value: data?.highestRiskSource, format: (s: string) => s, icon: AlertTriangle, color: 'text-danger' },
    { title: 'Avg Source Risk', value: data?.avgSourceRisk, format: formatScore, icon: Crosshair, color: 'text-warning' },
    { title: 'Files Scanned', value: data?.totalFilesScanned, format: formatNumber, icon: FileText, color: 'text-purple-400' },
    { title: 'User Prompts', value: data?.totalUserPrompts, format: formatNumber, icon: User, color: 'text-pink-400' },
    { title: 'Avg Confidence', value: data?.avgSourceConfidence, format: formatPercent, icon: ShieldCheck, color: 'text-emerald-400' },
    { title: 'Detection Rate', value: data?.sourceDetectionRate, format: formatPercent, icon: Target, color: 'text-cyan-400' },
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
                className={`font-bold tracking-tight truncate ${typeof kpi.value === 'string' ? 'text-lg text-gray-200' : 'text-2xl text-white'}`}
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
