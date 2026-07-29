// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { fetchDetectionsData, DetectionsData } from '../services/detectionsApi';
import { TopNav } from '../components/TopNav';
import { DetectionKpis } from '../components/detections/DetectionKpis';
import { DetectionFilters } from '../components/detections/DetectionFilters';
import { TechniqueBarChart } from '../components/detections/TechniqueBarChart';
import { TechniqueStackedChart } from '../components/detections/TechniqueStackedChart';
import { TechniquesTable } from '../components/detections/TechniquesTable';
import { DetectionTimeline } from '../components/detections/DetectionTimeline';

export const DetectionAnalytics: React.FC = () => {
  const [data, setData] = useState<DetectionsData | null>(null);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [filters, setFilters] = useState<Record<string, string>>({
    technique: 'all',
    detector: 'all',
    severity: 'all',
    source: 'all',
    dateRange: '24h',
  });

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleRowClick = (techniqueId: string) => {
    console.log(`Preparing to navigate to investigation view for technique: ${techniqueId}`);
    // Future investigation page routing goes here
  };

  const loadData = async () => {
    setLoading(true);
    setStatus('Loading');
    const startTime = performance.now();
    
    try {
      const result = await fetchDetectionsData(filters);
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
      <div className="absolute top-1/3 left-1/3 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none opacity-40 mix-blend-screen"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-pink-600/10 rounded-full blur-[150px] pointer-events-none opacity-30 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 pb-8">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Detection Analytics</h2>
              <p className="text-gray-400 text-sm">Deep dive into technique frequency, engine performance, and threat severity.</p>
            </div>
          </div>

          <DetectionFilters filters={filters} onFilterChange={handleFilterChange} />
          
          <DetectionKpis data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <TechniqueBarChart 
              data={data?.techniqueCounts || null} 
              loading={loading} 
            />
            <TechniqueStackedChart 
              data={data?.techniqueEngineBreakdown || null} 
              loading={loading} 
            />
          </div>

          <div className="mb-6">
            <DetectionTimeline 
              data={data?.timeline || null} 
              activeKeys={data?.activeTechniquesInTimeline || []}
              loading={loading} 
            />
          </div>

          <div className="h-[400px]">
            <TechniquesTable 
              data={data?.techniquesTable || null} 
              loading={loading} 
              onRowClick={handleRowClick}
            />
          </div>
        </main>
      </div>
    </div>
  );
};

export default DetectionAnalytics;
