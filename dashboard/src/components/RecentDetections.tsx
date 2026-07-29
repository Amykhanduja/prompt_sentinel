// @ts-nocheck
import React from 'react';
import { DashboardData } from '../services/api';
import { ShieldAlert, AlertCircle, Info } from 'lucide-react';
import { motion } from 'framer-motion';

interface RecentDetectionsProps {
  data: DashboardData['recentDetections'] | null;
  loading: boolean;
}

export const RecentDetections: React.FC<RecentDetectionsProps> = ({ data, loading }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-danger bg-danger/10 border-danger/20';
    if (score >= 50) return 'text-warning bg-warning/10 border-warning/20';
    return 'text-success bg-success/10 border-success/20';
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision.toLowerCase()) {
      case 'blocked':
        return <span className="px-2 py-1 rounded-md text-xs font-medium bg-danger/20 text-danger border border-danger/30">Blocked</span>;
      case 'allowed':
        return <span className="px-2 py-1 rounded-md text-xs font-medium bg-success/20 text-success border border-success/30">Allowed</span>;
      default:
        return <span className="px-2 py-1 rounded-md text-xs font-medium bg-warning/20 text-warning border border-warning/30">Review</span>;
    }
  };

  return (
    <div className="glass-panel p-5 overflow-hidden flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Detections</h3>
        <button className="text-sm text-primary hover:text-primary/80 transition-colors">View All</button>
      </div>
      
      <div className="flex-1 overflow-x-auto relative">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse w-full"></div>
            ))}
          </div>
        ) : !data || data.length === 0 ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <ShieldAlert className="w-12 h-12 mb-2 opacity-50" />
            <p>No Data Available</p>
          </div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-400 uppercase bg-black/20 sticky top-0 backdrop-blur-sm z-10 rounded-t-lg">
              <tr>
                <th className="px-4 py-3 font-medium rounded-tl-lg">Timestamp</th>
                <th className="px-4 py-3 font-medium">Technique</th>
                <th className="px-4 py-3 font-medium text-center">Score</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Detector</th>
                <th className="px-4 py-3 font-medium">Decision</th>
                <th className="px-4 py-3 font-medium rounded-tr-lg">Source</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <motion.tr 
                  key={item.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                >
                  <td className="px-4 py-3 whitespace-nowrap text-gray-300 font-mono text-xs">{item.timestamp}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col">
                      <span className="text-white font-medium group-hover:text-primary transition-colors">{item.techniqueName}</span>
                      <span className="text-xs text-gray-500 font-mono">{item.techniqueId}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className={`inline-flex items-center justify-center w-8 h-8 rounded-full border font-bold text-xs ${getScoreColor(item.riskScore)}`}>
                      {item.riskScore}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="w-full bg-white/10 rounded-full h-1.5 mb-1 mt-1.5">
                      <div className="bg-primary h-1.5 rounded-full" style={{ width: `${item.confidence * 100}%` }}></div>
                    </div>
                    <span className="text-xs text-gray-400">{(item.confidence * 100).toFixed(0)}%</span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">
                    <span className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_5px_#a855f7]"></div>
                      {item.detector}
                    </span>
                  </td>
                  <td className="px-4 py-3">{getDecisionBadge(item.decision)}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{item.source}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
