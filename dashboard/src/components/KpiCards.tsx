import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, Target, Ban, CheckCircle2, AlertTriangle, Activity } from 'lucide-react';
import { DashboardData } from '../services/api';

interface KpiCardsProps {
  data: DashboardData['kpis'] | null;
  loading: boolean;
}

const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);

export const KpiCards: React.FC<KpiCardsProps> = ({ data, loading }) => {
  const kpis = [
    { title: 'Total Prompts Scanned', value: data?.totalScanned, icon: Activity, color: 'text-primary' },
    { title: 'Malicious Prompts', value: data?.malicious, icon: ShieldAlert, color: 'text-danger' },
    { title: 'Benign Prompts', value: data?.benign, icon: ShieldCheck, color: 'text-success' },
    { title: 'Detection Rate', value: data?.detectionRate !== undefined ? `${data.detectionRate}%` : undefined, icon: Target, color: 'text-warning' },
    { title: 'Blocked', value: data?.blocked, icon: Ban, color: 'text-danger' },
    { title: 'Allowed', value: data?.allowed, icon: CheckCircle2, color: 'text-success' },
    { title: 'Review Queue', value: data?.reviewQueue, icon: AlertTriangle, color: 'text-warning' },
    { title: 'Average Risk Score', value: data?.averageRiskScore !== undefined ? data.averageRiskScore.toFixed(1) : undefined, icon: Activity, color: 'text-primary' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {kpis.map((kpi, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: i * 0.1 }}
          className="glass-panel p-5 flex flex-col justify-between h-32 group"
        >
          <div className="flex justify-between items-start">
            <h3 className="text-sm font-medium text-gray-400 group-hover:text-gray-200 transition-colors">{kpi.title}</h3>
            <div className={`p-2 rounded-lg bg-white/5 ${kpi.color}`}>
              <kpi.icon className="w-4 h-4" />
            </div>
          </div>
          
          <div className="mt-4">
            {loading ? (
              <div className="h-8 w-24 bg-white/10 rounded animate-pulse"></div>
            ) : data === null || kpi.value === undefined ? (
              <span className="text-lg font-semibold text-gray-500">No Data Available</span>
            ) : (
              <motion.span 
                key={String(kpi.value)} // Animate on value change
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-3xl font-bold text-white tracking-tight"
              >
                {typeof kpi.value === 'number' ? formatNumber(kpi.value) : kpi.value}
              </motion.span>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
};
