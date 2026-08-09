import { apiClient } from './apiClient';
export interface TrafficData {
  kpis: {
    totalRequests: number;
    requestsToday: number;
    requestsThisHour: number;
    currentRpm: number;
    avgRequestLatencyMs: number;
    avgPreprocessingTimeMs: number;
    avgDetectionTimeMs: number;
    avgPolicyEngineTimeMs: number;
    currentQueueSize: number;
  };
  trafficOverTime: Array<{
    timestamp: string;
    requests: number;
  }>;
  benignVsMalicious: Array<{
    timestamp: string;
    benign: number;
    malicious: number;
  }>;
  sourceDistribution: Array<{
    source: string;
    count: number;
  }>;
  latencyBreakdown: {
    preprocessing: number;
    regex: number;
    semantic: number;
    fusion: number;
    riskEngine: number;
    totalPipeline: number;
  };
  liveActivity: Array<{
    id: string;
    timestamp: string;
    source: string;
    processingTimeMs: number;
    decision: string;
  }>;
}

export const fetchTrafficData = async (timeRange: string, sourceFilter: string): Promise<TrafficData | null> => {
  try {
    const params = new URLSearchParams();
    if (timeRange !== 'all') params.append('range', timeRange);
    if (sourceFilter !== 'all') params.append('source', sourceFilter);
    
    const response = await apiClient(`/api/v1/dashboard/traffic?${params.toString()}`);
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching traffic data:', error);
    return null;
  }
};
