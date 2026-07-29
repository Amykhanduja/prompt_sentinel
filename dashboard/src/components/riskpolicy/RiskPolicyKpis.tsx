import React from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldAlert, Maximize2, Minimize2, Ban, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';
import { RiskPolicyData } from '../../services/riskPolicyApi';

interface RiskPolicyKpisProps {
  data: RiskPolicyData['kpis'] | null;
  loading: boolean;
}

const formatScore = (num: number) => num.toFixed(1);
const formatPercent = (num: number) => `${(num * 100).toFixed(1)}%`;
const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);
const formatTime = (num: number) => `${num.toFixed(1)}ms`;

export const RiskPolicyKpis: React.FC<RiskPolicyKpisProps> = ({ data, loading }) => {
  const kpis: any[] = [
    { title: 'Avg Risk Score', value: data?.avgRiskScore, format: formatScore, icon: Activity, color: 'text-primary' },
    { title: 'Highest Risk Score', value: data?.highestRiskScore, format: formatScore, icon: Maximize2, color: 'text-danger' },
    { title: 'Lowest Risk Score', value: data?.lowestRiskScore, format: formatScore, icon: Minimize2, color: 'text-success' },
    { title: 'Avg Confidence', value: data?.avgConfidence, format: formatPercent, icon: ShieldAlert, color: 'text-purple-400' },
    { title: 'Blocked Decisions', value: data?.blockedDecisions, format: formatNumber, icon: Ban, color: 'text-danger' },
    { title: 'Allowed Decisions', value: data?.allowedDecisions, format: formatNumber, icon: CheckCircle2, color: 'text-success' },
    { title: 'Review Decisions', value: data?.reviewDecisions, format: formatNumber, icon: AlertTriangle, color: 'text-warning' },
    { title: 'Avg Policy Time', value: data?.avgPolicyDecisionTimeMs, format: formatTime, icon: Clock, color: 'text-cyan-400' },
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
