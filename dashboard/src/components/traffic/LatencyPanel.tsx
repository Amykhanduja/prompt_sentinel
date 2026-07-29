import React from 'react';
import { TrafficData } from '../../services/trafficApi';
import { Layers, Search, BrainCircuit, Network, ShieldCheck, Activity } from 'lucide-react';

interface LatencyPanelProps {
  data: TrafficData['latencyBreakdown'] | null;
  loading: boolean;
}

export const LatencyPanel: React.FC<LatencyPanelProps> = ({ data, loading }) => {
  const steps = [
    { name: 'Preprocessing', key: 'preprocessing', icon: Layers, color: 'text-blue-400', bg: 'bg-blue-400/20' },
    { name: 'Regex Engine', key: 'regex', icon: Search, color: 'text-purple-400', bg: 'bg-purple-400/20' },
    { name: 'Semantic Analysis', key: 'semantic', icon: BrainCircuit, color: 'text-pink-400', bg: 'bg-pink-400/20' },
    { name: 'Fusion Engine', key: 'fusion', icon: Network, color: 'text-amber-400', bg: 'bg-amber-400/20' },
    { name: 'Risk Scoring', key: 'riskEngine', icon: ShieldCheck, color: 'text-emerald-400', bg: 'bg-emerald-400/20' },
  ];

  return (
    <div className="glass-panel p-5 h-[350px] flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-white">Pipeline Latency Breakdown</h3>
        <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-primary" />
          <span className="text-xs font-medium text-gray-300">
            Total: {loading ? '...' : data ? `${data.totalPipeline.toFixed(1)}ms` : 'N/A'}
          </span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto relative pr-2">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center gap-3 w-full">
                <div className="w-8 h-8 rounded-full bg-white/10 animate-pulse"></div>
                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-white/10 animate-pulse" style={{ width: `${Math.random() * 60 + 20}%` }}></div>
                </div>
                <div className="w-12 h-4 bg-white/10 rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        ) : !data ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <div className="space-y-5">
            {steps.map((step, index) => {
              const val = data[step.key as keyof typeof data] as number;
              const percentage = Math.min(100, (val / data.totalPipeline) * 100);
              
              return (
                <div key={index} className="flex flex-col gap-1.5 group">
                  <div className="flex justify-between items-center text-sm">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded-md ${step.bg} ${step.color}`}>
                        <step.icon className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-gray-300 group-hover:text-white transition-colors">{step.name}</span>
                    </div>
                    <span className="font-mono text-xs text-gray-400">{val.toFixed(2)}ms</span>
                  </div>
                  <div className="w-full bg-black/40 rounded-full h-1.5 overflow-hidden">
                    <div 
                      className={`h-full ${step.bg.replace('/20', '')} transition-all duration-1000 ease-out`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
