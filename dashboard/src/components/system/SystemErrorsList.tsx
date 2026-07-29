import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Terminal } from 'lucide-react';
import { SystemData } from '../../services/systemApi';

interface SystemErrorsListProps {
  data: SystemData['recentErrors'] | null;
  loading: boolean;
}

export const SystemErrorsList: React.FC<SystemErrorsListProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-full flex flex-col relative overflow-hidden border-t-2 border-danger/50">
      <div className="absolute top-0 left-0 w-32 h-32 bg-danger/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="flex items-center gap-2 mb-4 text-white z-10">
        <AlertTriangle className="w-5 h-5 text-danger" />
        <h3 className="text-sm font-semibold uppercase tracking-wider">Recent Backend Errors</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto relative z-10 pr-2">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="w-full h-16 bg-white/5 rounded-lg animate-pulse border border-white/5"></div>
            ))}
          </div>
        ) : !hasData ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-success">
            <CheckCircleIcon className="w-8 h-8 mb-2 opacity-50" />
            <span className="text-sm">Zero exceptions logged</span>
          </div>
        ) : (
          <div className="space-y-3">
            {data.map((err, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-black/60 p-3 rounded-lg border border-danger/20 hover:border-danger/50 transition-colors group"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-mono text-danger bg-danger/10 px-2 py-0.5 rounded border border-danger/20 uppercase tracking-widest">
                    {err.component}
                  </span>
                  <span className="text-[10px] text-gray-500 font-mono">{err.timestamp}</span>
                </div>
                <div className="flex gap-2 items-start text-xs text-gray-300 font-mono bg-black/40 p-2 rounded border border-white/5 overflow-x-auto">
                  <Terminal className="w-3 h-3 text-gray-500 shrink-0 mt-0.5" />
                  <span className="whitespace-pre-wrap">{err.message}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const CheckCircleIcon = (props: any) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);
