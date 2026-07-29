// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { fetchKnowledgeData, KnowledgeData } from '../services/knowledgeApi';
import { TopNav } from '../components/TopNav';
import { KnowledgeKpis } from '../components/knowledge/KnowledgeKpis';
import { KnowledgeFilters } from '../components/knowledge/KnowledgeFilters';
import { KnowledgeDistributionChart } from '../components/knowledge/KnowledgeDistributionChart';
import { LowCoveragePanel } from '../components/knowledge/LowCoveragePanel';
import { KnowledgeTable } from '../components/knowledge/KnowledgeTable';

export const KnowledgeAnalytics: React.FC = () => {
  const [data, setData] = useState<KnowledgeData | null>(null);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [filters, setFilters] = useState<Record<string, string>>({
    technique: 'all',
  });

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const loadData = async () => {
    setLoading(true);
    setStatus('Loading');
    const startTime = performance.now();
    
    try {
      const result = await fetchKnowledgeData(filters);
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
    const interval = setInterval(loadData, 60000); // Poll every minute for KB changes
    return () => clearInterval(interval);
  }, [filters]);

  return (
    <div className="min-h-screen bg-background relative">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/2 left-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[150px] pointer-events-none opacity-40 mix-blend-screen"></div>
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none opacity-30 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 pb-8">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Knowledge Base Analytics</h2>
              <p className="text-gray-400 text-sm">Monitor semantic knowledge quality, embedding distributions, and model coverage.</p>
            </div>
          </div>

          <KnowledgeFilters filters={filters} onFilterChange={handleFilterChange} />
          
          <KnowledgeKpis data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            <div className="lg:col-span-3">
              <KnowledgeDistributionChart data={data?.knowledgeDistribution || null} loading={loading} />
            </div>
            <div className="lg:col-span-1">
              <LowCoveragePanel data={data?.lowCoverageTechniques || null} loading={loading} />
            </div>
          </div>

          <div className="h-[400px]">
            <KnowledgeTable data={data?.knowledgeTable || null} loading={loading} />
          </div>
        </main>
      </div>
    </div>
  );
};

export default KnowledgeAnalytics;
