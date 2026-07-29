import React from 'react';
import { Server, Activity, Clock, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';

interface BackendStatusProps {
  status: 'Connected' | 'Disconnected' | 'Loading';
  latency: number | null;
  lastUpdated: Date | null;
}

export const BackendStatus: React.FC<BackendStatusProps> = ({ status, latency, lastUpdated }) => {
  return (
    <div className="glass-panel p-5">
      <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
        <Server className="w-5 h-5 text-primary" />
        Backend Node Status
      </h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-black/30 p-3 rounded-lg border border-white/5 flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${status === 'Connected' ? 'bg-success/20 text-success shadow-[0_0_10px_rgba(16,185,129,0.3)]' : status === 'Disconnected' ? 'bg-danger/20 text-danger shadow-[0_0_10px_rgba(239,68,68,0.3)]' : 'bg-warning/20 text-warning animate-pulse'}`}>
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-gray-400">Connection</p>
            <p className="font-semibold text-white">{status}</p>
          </div>
        </div>

        <div className="bg-black/30 p-3 rounded-lg border border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/20 text-primary flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.3)]">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-gray-400">API Latency</p>
            <p className="font-semibold text-white">
              {status === 'Loading' ? '...' : latency !== null ? `${latency}ms` : 'N/A'}
            </p>
          </div>
        </div>

        <div className="bg-black/30 p-3 rounded-lg border border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-gray-400">Last Update</p>
            <p className="font-semibold text-white text-sm">
              {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
            </p>
          </div>
        </div>

        <div className="bg-black/30 p-3 rounded-lg border border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-pink-500/20 text-pink-400 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-gray-400">Version</p>
            <p className="font-semibold text-white font-mono text-sm">v1.0.0-rc2</p>
          </div>
        </div>
      </div>
    </div>
  );
};
