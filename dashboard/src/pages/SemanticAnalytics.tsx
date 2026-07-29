import React, { useEffect, useState } from 'react';
import { fetchSemanticData, SemanticData } from '../services/semanticApi';
import { TopNav } from '../components/TopNav';
import { SemanticKpis } from '../components/semantic/SemanticKpis';
import { SemanticFilters } from '../components/semantic/SemanticFilters';
import { SemanticMargin } from '../components/semantic/SemanticMargin';
import { DistributionHistograms } from '../components/semantic/DistributionHistograms';
import { SimilarityScatterPlot } from '../components/semantic/SimilarityScatterPlot';
import { SemanticTechniquesTable } from '../components/semantic/SemanticTechniquesTable';
import { SemanticTrendChart } from '../components/semantic/SemanticTrendChart';

export const SemanticAnalytics: React.FC = () => {
  const [data, setData] = useState<SemanticData | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  
  const [filters, setFilters] = useState<Record<string, string>>({
    technique: 'all',
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
      const result = await fetchSemanticData(filters);
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
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/2 left-0 w-[500px] h-[500px] bg-green-600/10 rounded-full blur-[150px] pointer-events-none opacity-40 mix-blend-screen"></div>
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none opacity-30 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 pb-8">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Semantic Analytics</h2>
              <p className="text-gray-400 text-sm">Analyze embedding similarity distributions, threshold margins, and confidence scaling.</p>
            </div>
          </div>

          <SemanticFilters filters={filters} onFilterChange={handleFilterChange} />
          
          <SemanticKpis data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            <div className="lg:col-span-1">
              <SemanticMargin data={data?.margin || null} loading={loading} />
            </div>
            <div className="lg:col-span-1">
              <DistributionHistograms 
                similarityData={data?.similarityDistribution || null} 
                confidenceData={data?.confidenceDistribution || null} 
                loading={loading} 
              />
            </div>
            <div className="lg:col-span-2">
              <SimilarityScatterPlot 
                data={data?.scatterPlot || null} 
                loading={loading} 
              />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-3">
              <SemanticTrendChart 
                data={data?.similarityOverTime || null} 
                loading={loading} 
              />
            </div>
          </div>

          <div className="h-[400px]">
            <SemanticTechniquesTable 
              data={data?.techniquesTable || null} 
              loading={loading} 
            />
          </div>
        </main>
      </div>
    </div>
  );
};

export default SemanticAnalytics;
