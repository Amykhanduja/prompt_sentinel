import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle, Loader2 } from 'lucide-react';

interface ScanProgressProps {
  status: 'idle' | 'scanning' | 'completed' | 'error';
  progress: number; // 0 to 100
  timeElapsed: number; // in ms
}

const stages = [
  { id: 'upload', label: 'Uploading File', threshold: 10 },
  { id: 'parse', label: 'Parsing Document', threshold: 30 },
  { id: 'extract', label: 'Recursive Extraction', threshold: 45 },
  { id: 'preprocess', label: 'Preprocessing', threshold: 60 },
  { id: 'regex', label: 'Regex Detection', threshold: 75 },
  { id: 'semantic', label: 'Semantic Detection', threshold: 85 },
  { id: 'fusion', label: 'Fusion & Risk Scoring', threshold: 95 },
  { id: 'policy', label: 'Policy Evaluation', threshold: 100 },
];

export const ScanProgress: React.FC<ScanProgressProps> = ({ status, progress, timeElapsed }) => {
  if (status === 'idle') return null;

  return (
    <div className="glass-panel p-6 mb-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold flex items-center gap-2">
          {status === 'scanning' ? (
            <Loader2 className="text-primary w-6 h-6 animate-spin" />
          ) : status === 'completed' ? (
            <CheckCircle className="text-success w-6 h-6" />
          ) : (
            <Circle className="text-danger w-6 h-6" />
          )}
          Scan Progress
        </h3>
        <div className="text-sm text-gray-400 font-mono">
          {(timeElapsed / 1000).toFixed(1)}s elapsed
        </div>
      </div>

      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-primary bg-primary/20">
              {status === 'scanning' ? 'In Progress' : status === 'completed' ? 'Complete' : 'Failed'}
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-primary">
              {progress}%
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-white/10">
          <motion.div 
            initial={{ width: 0 }} 
            animate={{ width: `${progress}%` }} 
            className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${status === 'error' ? 'bg-danger' : 'bg-primary'}`}
          ></motion.div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        {stages.map((stage, idx) => {
          const isCompleted = progress >= stage.threshold || status === 'completed';
          const isCurrent = progress < stage.threshold && progress >= (idx > 0 ? stages[idx-1].threshold : 0) && status === 'scanning';
          
          return (
            <div key={stage.id} className={`flex items-center gap-3 p-3 rounded-lg border ${isCurrent ? 'bg-primary/10 border-primary/30' : isCompleted ? 'bg-success/10 border-success/20' : 'bg-black/20 border-white/5 opacity-50'}`}>
              {isCompleted ? (
                <CheckCircle className="w-5 h-5 text-success" />
              ) : isCurrent ? (
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              ) : (
                <Circle className="w-5 h-5 text-gray-500" />
              )}
              <span className={`text-sm font-medium ${isCurrent ? 'text-primary' : isCompleted ? 'text-success' : 'text-gray-400'}`}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
