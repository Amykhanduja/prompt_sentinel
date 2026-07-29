import React, { useEffect, useState } from 'react';
import { fetchTrafficData, TrafficData } from '../services/trafficApi';
import { TopNav } from '../components/TopNav';
import { TrafficKpis } from '../components/traffic/TrafficKpis';
import { TrafficLineChart } from '../components/traffic/TrafficLineChart';
import { TrafficAreaChart } from '../components/traffic/TrafficAreaChart';
import { SourceDistributionChart } from '../components/traffic/SourceDistributionChart';
import { LatencyPanel } from '../components/traffic/LatencyPanel';
import { LiveActivityFeed } from '../components/traffic/LiveActivityFeed';
import { TrafficFilters } from '../components/traffic/TrafficFilters';

export const TrafficAnalytics: React.FC = () => {
  const [data, setData] = useState<TrafficData | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  
  // Filters state
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [sourceFilter, setSourceFilter] = useState<string>('all');

  const loadData = async () => {
    setLoading(true);
    setStatus('Loading');
    const startTime = performance.now();
    
    try {
      const result = await fetchTrafficData(timeRange, sourceFilter);
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
    const interval = setInterval(loadData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, [timeRange, sourceFilter]);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none opacity-40 mix-blend-screen"></div>
      <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[150px] pointer-events-none opacity-30 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 pb-8">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Traffic Analytics</h2>
              <p className="text-gray-400 text-sm">Monitor prompt volume, latencies, and real-time processing.</p>
            </div>
          </div>

          <TrafficFilters sourceFilter={sourceFilter} onSourceFilterChange={setSourceFilter} />
          
          <TrafficKpis data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <TrafficLineChart 
              data={data?.trafficOverTime || null} 
              loading={loading} 
              timeRange={timeRange}
              onTimeRangeChange={setTimeRange}
            />
            <TrafficAreaChart 
              data={data?.benignVsMalicious || null} 
              loading={loading} 
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <SourceDistributionChart data={data?.sourceDistribution || null} loading={loading} />
            </div>
            <div className="lg:col-span-1">
              <LatencyPanel data={data?.latencyBreakdown || null} loading={loading} />
            </div>
            <div className="lg:col-span-1 h-[350px]">
              <LiveActivityFeed data={data?.liveActivity || null} loading={loading} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default TrafficAnalytics;
