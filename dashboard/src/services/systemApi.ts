import { apiClient } from './apiClient';
export interface SystemData {
  kpis: {
    apiStatus: string;
    backendVersion: string;
    uptime: string;
    cpuUsage: number;
    memoryUsage: number;
    currentQueueSize: number;
    avgPipelineLatency: number;
    requestsPerSecond: number;
  };
  metricsOverTime: Array<{
    timestamp: string;
    cpu: number;
    memory: number;
    latency: number;
    rps: number;
  }>;
  engineStatus: {
    regexEngine: string;
    semanticEngine: string;
    fusionEngine: string;
    riskEngine: string;
    policyEngine: string;
    knowledgeBase: string;
  };
  embeddingModelInfo: {
    modelName: string;
    dimensions: number;
    avgEmbeddingTimeMs: number;
    loadingStatus: string;
  };
  recentErrors: Array<{
    timestamp: string;
    component: string;
    message: string;
  }>;
}

export const fetchSystemData = async (): Promise<SystemData | null> => {
  try {
    const response = await apiClient('/api/v1/dashboard/system');
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching system data:', error);
    return null;
  }
};
