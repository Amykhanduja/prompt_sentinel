import React, { useEffect, useState } from 'react';
import { fetchSystemData, SystemData } from '../services/systemApi';
import { TopNav } from '../components/TopNav';
import { SystemKpis } from '../components/system/SystemKpis';
import { SystemMetricsCharts } from '../components/system/SystemMetricsCharts';
import { EngineStatusPanel } from '../components/system/EngineStatusPanel';
import { EmbeddingModelPanel } from '../components/system/EmbeddingModelPanel';
import { SystemErrorsList } from '../components/system/SystemErrorsList';

export const SystemHealth: React.FC = () => {
  const [data, setData] = useState<SystemData | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);

  const loadData = async () => {
    // Only set loading true on initial load
    if (!data) setLoading(true);
    const startTime = performance.now();
    
    try {
      const result = await fetchSystemData();
      const endTime = performance.now();
      
      if (result) {
        setData(result);
        setStatus('Connected');
        setLatency(Math.round(endTime - startTime));
      } else {
        setData(null);
        setStatus('Disconnected');
        setLatency(null);
      }
    } catch (error) {
      setData(null);
      setStatus('Disconnected');
      setLatency(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Fast polling for system health (5s)
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      {/* Dynamic Background Effects */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none opacity-30 mix-blend-screen"></div>
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none opacity-20 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 w-full px-4 pb-8 flex-1 flex flex-col max-w-[1600px] mx-auto">
        <TopNav />
        
        <main className="flex-1 flex flex-col">
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">System Health</h2>
              <p className="text-gray-400 text-sm">Real-time telemetry, engine status, and embedding performance.</p>
            </div>
          </div>
          
          <SystemKpis data={data?.kpis || null} loading={loading} />
          
          <div className="mb-6">
            <SystemMetricsCharts data={data?.metricsOverTime || null} loading={loading} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[300px]">
            <div className="lg:col-span-1 h-full">
              <EngineStatusPanel data={data?.engineStatus || null} loading={loading} />
            </div>
            <div className="lg:col-span-1 h-full">
              <EmbeddingModelPanel data={data?.embeddingModelInfo || null} loading={loading} />
            </div>
            <div className="lg:col-span-1 h-full">
              <SystemErrorsList data={data?.recentErrors || null} loading={loading} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SystemHealth;
