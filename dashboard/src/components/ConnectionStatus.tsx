import { apiClient } from '../services/apiClient';
import React from 'react';
import { Activity } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

export const ConnectionStatus: React.FC = () => {
  const { data, isError, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await apiClient('/api/v1/dashboard/system');
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    },
    refetchInterval: 10000, // Poll every 10 seconds
  });

  const status = isError ? 'Disconnected' : isLoading ? 'Reconnecting' : 'Connected';
  const latency = data?.kpis?.avgPipelineLatency ?? null;
  const version = data?.kpis?.backendVersion ?? '1.0.0';

  return (
    <div className="flex items-center gap-2 text-xs md:text-sm px-3 py-1.5 rounded-full bg-white/5 border border-white/10" title={`Backend Version: ${version}`}>
      <div 
        className={`w-2 h-2 rounded-full ${
          status === 'Connected' ? 'bg-success shadow-[0_0_8px_#10b981]' 
          : status === 'Disconnected' ? 'bg-danger shadow-[0_0_8px_#ef4444]' 
          : 'bg-warning animate-pulse'
        }`} 
      />
      <span className="text-gray-300 font-medium hidden sm:inline">{status}</span>
      {latency !== null && status === 'Connected' && (
        <>
          <span className="text-gray-500 mx-1 hidden sm:inline">|</span>
          <Activity className="w-3 h-3 text-primary hidden sm:inline" />
          <span className="text-gray-300 hidden sm:inline">{latency}ms</span>
        </>
      )}
    </div>
  );
};
