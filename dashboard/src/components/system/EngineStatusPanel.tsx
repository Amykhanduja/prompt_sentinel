import React from 'react';
import { motion } from 'framer-motion';
import { Server, CheckCircle2, ShieldAlert } from 'lucide-react';
import { SystemData } from '../../services/systemApi';

interface EngineStatusPanelProps {
  data: SystemData['engineStatus'] | null;
  loading: boolean;
}

export const EngineStatusPanel: React.FC<EngineStatusPanelProps> = ({ data, loading }) => {
  const getStatusColor = (status: string) => {
    if (status?.toLowerCase() === 'online') return 'text-success';
    if (status?.toLowerCase() === 'offline') return 'text-danger';
    return 'text-warning';
  };

  const getStatusIcon = (status: string) => {
    if (status?.toLowerCase() === 'online') return <CheckCircle2 className="w-4 h-4 text-success" />;
    return <ShieldAlert className="w-4 h-4 text-danger animate-pulse" />;
  };

  const engines = [
    { label: 'Regex Engine', key: 'regexEngine' as keyof typeof data },
    { label: 'Semantic Engine', key: 'semanticEngine' as keyof typeof data },
    { label: 'Fusion Engine', key: 'fusionEngine' as keyof typeof data },
    { label: 'Risk Engine', key: 'riskEngine' as keyof typeof data },
    { label: 'Policy Engine', key: 'policyEngine' as keyof typeof data },
    { label: 'Knowledge Base', key: 'knowledgeBase' as keyof typeof data },
  ];

  return (
    <div className="glass-panel p-5 h-full flex flex-col relative overflow-hidden border-t-2 border-primary/50">
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="flex items-center gap-2 mb-6 text-white z-10">
        <Server className="w-5 h-5 text-primary" />
        <h3 className="text-sm font-semibold uppercase tracking-wider">Engine Status</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto relative z-10 pr-2">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex justify-between items-center w-full bg-black/40 p-3 rounded-lg border border-white/5">
                <div className="w-1/2 h-4 bg-white/10 rounded animate-pulse"></div>
                <div className="w-1/4 h-4 bg-white/10 rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        ) : !data ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <div className="space-y-3">
            {engines.map((engine, index) => {
              const status = data[engine.key] as string;
              return (
                <motion.div 
                  key={engine.key}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex justify-between items-center bg-black/40 p-3 rounded-lg border border-white/5 hover:bg-white/5 transition-colors group"
                >
                  <span className="text-xs font-mono text-gray-300 group-hover:text-white transition-colors">
                    {engine.label}
                  </span>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(status)}
                    <span className={`text-xs font-bold uppercase tracking-widest ${getStatusColor(status)}`}>
                      {status || 'UNKNOWN'}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
