import React, { useEffect, useState } from 'react';
import { fetchRiskPolicyData, RiskPolicyData } from '../services/riskPolicyApi';
import { TopNav } from '../components/TopNav';
import { RiskPolicyKpis } from '../components/riskpolicy/RiskPolicyKpis';
import { RiskPolicyFilters } from '../components/riskpolicy/RiskPolicyFilters';
import { RiskScoreHistogram } from '../components/riskpolicy/RiskScoreHistogram';
import { RiskTrendChart } from '../components/riskpolicy/RiskTrendChart';
import { DecisionsByTechniqueChart } from '../components/riskpolicy/DecisionsByTechniqueChart';
import { RiskPolicyTechniquesTable } from '../components/riskpolicy/RiskPolicyTechniquesTable';
import { CompoundRulesPanel } from '../components/riskpolicy/CompoundRulesPanel';
import { DuplicatePenaltiesChart } from '../components/riskpolicy/DuplicatePenaltiesChart';

export const RiskPolicyAnalytics: React.FC = () => {
  const [data, setData] = useState<RiskPolicyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  
  const [filters, setFilters] = useState<Record<string, string>>({
    technique: 'all',
    decision: 'all',
    severity: 'all',
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
      const result = await fetchRiskPolicyData(filters);
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
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [filters]);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/4 right-0 w-[500px] h-[500px] bg-red-600/10 rounded-full blur-[150px] pointer-events-none opacity-40 mix-blend-screen"></div>
      <div className="absolute bottom-1/4 left-0 w-[600px] h-[600px] bg-orange-600/10 rounded-full blur-[120px] pointer-events-none opacity-30 mix-blend-screen"></div>
      
      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 pb-8">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Risk & Policy Analytics</h2>
              <p className="text-gray-400 text-sm">Monitor decision outcomes, compound rules, and risk score thresholds.</p>
            </div>
          </div>

          <RiskPolicyFilters filters={filters} onFilterChange={handleFilterChange} />
          
          <RiskPolicyKpis data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-1">
              <RiskScoreHistogram data={data?.riskScoreHistogram || null} loading={loading} />
            </div>
            <div className="lg:col-span-2">
              <RiskTrendChart data={data?.riskTrend || null} loading={loading} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            <div className="lg:col-span-1 h-[350px]">
              <CompoundRulesPanel data={data?.compoundRuleActivations || null} loading={loading} />
            </div>
            <div className="lg:col-span-3">
              <DecisionsByTechniqueChart data={data?.decisionsByTechnique || null} loading={loading} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            <div className="lg:col-span-3 h-[400px]">
              <RiskPolicyTechniquesTable data={data?.techniquesTable || null} loading={loading} />
            </div>
            <div className="lg:col-span-1">
              <DuplicatePenaltiesChart data={data?.duplicatePenaltiesOverTime || null} loading={loading} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default RiskPolicyAnalytics;
