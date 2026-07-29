import React from 'react';
import { TrafficData } from '../../services/trafficApi';
import { motion } from 'framer-motion';

interface LiveActivityFeedProps {
  data: TrafficData['liveActivity'] | null;
  loading: boolean;
}

export const LiveActivityFeed: React.FC<LiveActivityFeedProps> = ({ data, loading }) => {
  const getDecisionBadge = (decision: string) => {
    switch (decision.toLowerCase()) {
      case 'blocked':
        return <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-danger/20 text-danger border border-danger/30">Blocked</span>;
      case 'allowed':
        return <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-success/20 text-success border border-success/30">Allowed</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-warning/20 text-warning border border-warning/30">Review</span>;
    }
  };

  return (
    <div className="glass-panel p-5 h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_#10b981] animate-pulse"></span>
          Live Activity Feed
        </h3>
      </div>
      
      <div className="flex-1 overflow-hidden relative">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-14 bg-white/5 rounded-lg animate-pulse w-full"></div>
            ))}
          </div>
        ) : !data || data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <div className="space-y-2 overflow-y-auto h-full pr-2 pb-2">
            {data.map((item, index) => (
              <motion.div 
                key={item.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-3 bg-black/20 hover:bg-white/5 border border-white/5 rounded-lg transition-colors flex items-center justify-between"
              >
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-white">{item.source}</span>
                    <span className="text-[10px] text-gray-500 font-mono">{item.timestamp}</span>
                  </div>
                  <div className="text-[11px] text-gray-400 font-mono">
                    ID: {item.id}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  {getDecisionBadge(item.decision)}
                  <span className="text-[10px] text-gray-500 font-mono">{item.processingTimeMs.toFixed(1)}ms</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
