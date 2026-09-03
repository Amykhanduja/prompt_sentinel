import React from 'react';
import { motion } from 'framer-motion';
import { Target, CheckCircle2, XCircle, Database } from 'lucide-react';
import { DashboardData } from '../services/api';

interface BenchmarkDetailsProps {
  data: DashboardData['kpis']['benchmarkData'] | null;
  loading: boolean;
}

export const BenchmarkDetails: React.FC<BenchmarkDetailsProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="glass-panel p-6 h-full flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
        <p className="text-gray-400">Loading benchmark telemetry...</p>
      </div>
    );
  }

  if (!data || data.samples === 0) {
    return (
      <div className="glass-panel p-6 h-full flex flex-col items-center justify-center">
        <p className="text-gray-500">No Benchmark Data Available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-panel p-6 h-full flex flex-col"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-purple-500/20 rounded-lg border border-purple-500/30">
          <Target className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white tracking-tight">Benchmark Evaluations</h3>
          <p className="text-xs text-gray-400">Offline dataset evaluation results</p>
        </div>
      </div>

      <div className="space-y-5 flex-grow">
        <div className="flex justify-between items-center border-b border-white/5 pb-3">
          <div className="flex items-center gap-2 text-gray-300">
            <Database className="w-4 h-4 text-gray-500" />
            <span className="text-sm">Dataset Version</span>
          </div>
          <span className="text-sm font-medium text-white px-2 py-1 bg-white/5 rounded">
            {data.dataset_version}
          </span>
        </div>

        <div className="flex justify-between items-center border-b border-white/5 pb-3">
          <div className="flex items-center gap-2 text-gray-300">
            <Target className="w-4 h-4 text-gray-500" />
            <span className="text-sm">Total Samples</span>
          </div>
          <span className="text-sm font-medium text-white">
            {new Intl.NumberFormat('en-US').format(data.samples)}
          </span>
        </div>

        <div className="flex justify-between items-center border-b border-white/5 pb-3">
          <div className="flex items-center gap-2 text-gray-300">
            <CheckCircle2 className="w-4 h-4 text-success" />
            <span className="text-sm">Successful Evals</span>
          </div>
          <span className="text-sm font-medium text-success">
            {new Intl.NumberFormat('en-US').format(data.successful)}
          </span>
        </div>

        <div className="flex justify-between items-center pb-1">
          <div className="flex items-center gap-2 text-gray-300">
            <XCircle className="w-4 h-4 text-danger" />
            <span className="text-sm">Failed Evals</span>
          </div>
          <span className="text-sm font-medium text-danger">
            {new Intl.NumberFormat('en-US').format(data.failed)}
          </span>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-white/10 text-center">
        <p className="text-[10px] text-gray-500 italic">
          Benchmark traffic is isolated and does not affect production statistics or feedback learning.
        </p>
      </div>
    </motion.div>
  );
};
