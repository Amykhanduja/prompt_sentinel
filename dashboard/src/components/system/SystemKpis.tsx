import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, ShieldAlert, Clock, Cpu, MemoryStick, List, Activity, Zap } from 'lucide-react';
import { SystemData } from '../../services/systemApi';

interface SystemKpisProps {
  data: SystemData['kpis'] | null;
  loading: boolean;
}

const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);
const formatPercent = (num: number) => `${num.toFixed(1)}%`;
const formatMs = (num: number) => `${num.toFixed(1)}ms`;

export const SystemKpis: React.FC<SystemKpisProps> = ({ data, loading }) => {
  const getStatusColor = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'operational' || s === 'online') return 'text-success';
    if (s === 'degraded') return 'text-warning';
    return 'text-danger';
  };

  const kpis = [
    { title: 'API Status', value: data?.apiStatus, format: (s: string) => s, icon: data?.apiStatus?.toLowerCase() === 'operational' ? CheckCircle2 : ShieldAlert, color: getStatusColor(data?.apiStatus || '') },
    { title: 'Backend Version', value: data?.backendVersion, format: (s: string) => s, icon: Zap, color: 'text-primary' },
    { title: 'Uptime', value: data?.uptime, format: (s: string) => s, icon: Clock, color: 'text-emerald-400' },
    { title: 'CPU Usage', value: data?.cpuUsage, format: formatPercent, icon: Cpu, color: 'text-purple-400' },
    { title: 'Memory Usage', value: data?.memoryUsage, format: formatPercent, icon: MemoryStick, color: 'text-pink-400' },
    { title: 'Current Queue', value: data?.currentQueueSize, format: formatNumber, icon: List, color: 'text-warning' },
    { title: 'Avg Pipeline Latency', value: data?.avgPipelineLatency, format: formatMs, icon: Activity, color: 'text-cyan-400' },
    { title: 'Requests / Sec', value: data?.requestsPerSecond, format: formatNumber, icon: Zap, color: 'text-blue-400' },
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
                className={`font-bold tracking-tight truncate ${typeof kpi.value === 'string' ? 'text-xl text-white' : 'text-2xl text-white'}`}
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
