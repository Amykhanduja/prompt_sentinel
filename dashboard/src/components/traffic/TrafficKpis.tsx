import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Clock, Server, Zap, Database, Cpu, Layers, List } from 'lucide-react';
import { TrafficData } from '../../services/trafficApi';

interface TrafficKpisProps {
  data: TrafficData['kpis'] | null;
  loading: boolean;
}

const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num);
const formatMs = (num: number) => `${num.toFixed(1)}ms`;

export const TrafficKpis: React.FC<TrafficKpisProps> = ({ data, loading }) => {
  const kpis: any[] = [
    { title: 'Total Requests', value: data?.totalRequests, format: formatNumber, icon: Database, color: 'text-primary' },
    { title: 'Requests Today', value: data?.requestsToday, format: formatNumber, icon: Activity, color: 'text-success' },
    { title: 'Requests This Hour', value: data?.requestsThisHour, format: formatNumber, icon: Clock, color: 'text-warning' },
    { title: 'Current RPM', value: data?.currentRpm, format: formatNumber, icon: Zap, color: 'text-danger' },
    { title: 'Avg Request Latency', value: data?.avgRequestLatencyMs, format: formatMs, icon: Server, color: 'text-primary' },
    { title: 'Avg Preprocessing', value: data?.avgPreprocessingTimeMs, format: formatMs, icon: Layers, color: 'text-success' },
    { title: 'Avg Detection Time', value: data?.avgDetectionTimeMs, format: formatMs, icon: Zap, color: 'text-warning' },
    { title: 'Avg Policy Engine', value: data?.avgPolicyEngineTimeMs, format: formatMs, icon: Cpu, color: 'text-purple-400' },
    { title: 'Current Queue Size', value: data?.currentQueueSize, format: formatNumber, icon: List, color: 'text-pink-400' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
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
          
          <div className="mt-2">
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
