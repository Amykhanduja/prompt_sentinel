// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { TopNav } from '../components/TopNav';
import { KpiCards } from '../components/KpiCards';
import { RiskGauge } from '../components/RiskGauge';
import { DetectionsDonutChart } from '../components/DonutChart';
import { DecisionsPieChart } from '../components/PieChart';
import { RecentDetections } from '../components/RecentDetections';
import { BackendStatus } from '../components/BackendStatus';
import { fetchDashboardData, DashboardData } from '../services/api';

export const DashboardOverview: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [status, setStatus] = useState<'Connected' | 'Disconnected' | 'Loading'>('Loading');
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadData = async () => {
    setLoading(true);
    setStatus('Loading');
    const startTime = performance.now();
    
    try {
      const result = await fetchDashboardData();
      const endTime = performance.now();
      
      if (result) {
        setData(result);
        setStatus('Connected');
        setLatency(Math.round(endTime - startTime));
        setLastUpdated(new Date());
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
  }, []);

  return (
    <div className="relative w-full">
      {/* Dynamic Background Effects */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none opacity-50 mix-blend-screen"></div>
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[150px] pointer-events-none opacity-40 mix-blend-screen"></div>
      
      <div className="relative z-10 w-full px-4 pb-8 max-w-[1600px] mx-auto">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Platform Overview</h2>
              <p className="text-gray-400 text-sm">High-level telemetry on active detections and incoming prompt traffic.</p>
            </div>
          </div>

          <KpiCards data={data?.kpis || null} loading={loading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-1 h-[350px]">
              <RiskGauge data={data?.gauge || null} loading={loading} />
            </div>
            <div className="lg:col-span-1 h-[350px]">
              <DetectionsDonutChart data={data?.detectionsByType || null} loading={loading} />
            </div>
            <div className="lg:col-span-1 h-[350px]">
              <DecisionsPieChart data={data?.decisions || null} loading={loading} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-[400px]">
              <RecentDetections data={data?.recentDetections || null} loading={loading} />
            </div>
            <div className="lg:col-span-1 h-[400px]">
              <BackendStatus status={status} latency={latency} lastUpdated={lastUpdated} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
