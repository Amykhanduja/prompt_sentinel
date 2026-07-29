// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { fetchSourceData, SourceData } from '../services/sourceApi';
import { TopNav } from '../components/TopNav';
import { SourceKpis } from '../components/sources/SourceKpis';
import { SourceFilters } from '../components/sources/SourceFilters';
import { SourceDistributionChart } from '../components/sources/SourceDistributionChart';
import { SourceBenignMaliciousChart } from '../components/sources/SourceBenignMaliciousChart';
import { SourceHeatmap } from '../components/sources/SourceHeatmap';
import { SourceTable } from '../components/sources/SourceTable';

export const SourceAnalytics: React.FC = () => {
  const [data, setData] = useState<SourceData | null>(null);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [filters, setFilters] = useState<Record<string, string>>({
    sourceType: 'all',
    dateRange: '24h',
  });

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const loadData = async () => {
    setLoading(true);
    setStatus('Loading');
    const startTime = performance.now();
    
    try {
      const result = await fetchSourceData(filters);
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
  }, [filters]);

  return (
    <div className="min-h-screen bg-background relative">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[150px] pointer-events-none opacity-40 mix-blend-screen"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-emerald-600/10 rounded-full blur-[120px] pointer-events-none opacity-30 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 pb-8">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Source Analytics</h2>
              <p className="text-gray-400 text-sm">Analyze how different input channels and file types contribute to the threat landscape.</p>
            </div>
          </div>

          <SourceFilters filters={filters} onFilterChange={handleFilterChange} />
          
          <SourceKpis data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-1">
              <SourceDistributionChart data={data?.sourceDistribution || null} loading={loading} />
            </div>
            <div className="lg:col-span-2">
              <SourceBenignMaliciousChart data={data?.benignVsMaliciousBySource || null} loading={loading} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            <div className="lg:col-span-4 h-[400px]">
              <SourceHeatmap data={data?.heatmap || null} loading={loading} />
            </div>
          </div>

          <div className="h-[400px]">
            <SourceTable data={data?.sourcesTable || null} loading={loading} />
          </div>
        </main>
      </div>
    </div>
  );
};

export default SourceAnalytics;
