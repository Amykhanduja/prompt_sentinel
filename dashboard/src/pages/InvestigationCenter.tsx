// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { fetchInvestigations, InvestigationRecord } from '../services/investigationApi';
import { TopNav } from '../components/TopNav';
import { InvestigationFilters } from '../components/investigations/InvestigationFilters';
import { InvestigationTable } from '../components/investigations/InvestigationTable';
import { InvestigationDrawer } from '../components/investigations/InvestigationDrawer';

export const InvestigationCenter: React.FC = () => {
  const [data, setData] = useState<InvestigationRecord[]>([]);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [filters, setFilters] = useState<Record<string, string>>({
    technique: 'all',
    detector: 'all',
    severity: 'all',
    source: 'all',
    decision: 'all',
    dateRange: '24h',
  });

  const [selectedRecord, setSelectedRecord] = useState<InvestigationRecord | null>(null);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const loadData = async () => {
    setLoading(true);
    setStatus('Loading');
    const startTime = performance.now();
    
    try {
      const result = await fetchInvestigations(filters);
      const endTime = performance.now();
      
      if (result) {
        setData(result);
        setStatus('Connected');
        setLatency(Math.round(endTime - startTime));
      } else {
        setData([]);
        setStatus('Disconnected');
        setLatency(null);
      }
    } catch (error) {
      setData([]);
      setStatus('Disconnected');
      setLatency(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Poll more frequently for investigations (10s)
    return () => clearInterval(interval);
  }, [filters]);

  return (
    <div className="min-h-screen bg-background relative flex flex-col">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none opacity-40 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 w-full px-4 pb-8 flex-1 flex flex-col max-w-[1800px] mx-auto">
        <TopNav />
        
        <main className="flex-1 flex flex-col">
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Investigation Center</h2>
              <p className="text-gray-400 text-sm">Deep inspection of individual events, semantic matches, and policy execution.</p>
            </div>
          </div>

          <InvestigationFilters filters={filters} onFilterChange={handleFilterChange} />
          
          <div className="flex-1">
            <InvestigationTable 
              data={data} 
              loading={loading} 
              onRowClick={setSelectedRecord}
            />
          </div>
        </main>
      </div>

      {selectedRecord && (
        <InvestigationDrawer 
          record={selectedRecord} 
          onClose={() => setSelectedRecord(null)} 
        />
      )}
    </div>
  );
};

export default InvestigationCenter;
