import { apiClient } from './apiClient';
export interface SourceData {
  kpis: {
    totalSources: number;
    mostActiveSource: string;
    highestRiskSource: string;
    avgSourceRisk: number;
    totalFilesScanned: number;
    totalUserPrompts: number;
    avgSourceConfidence: number;
    sourceDetectionRate: number;
  };
  sourceDistribution: Array<{
    source: string;
    count: number;
  }>;
  benignVsMaliciousBySource: Array<{
    source: string;
    benign: number;
    malicious: number;
  }>;
  heatmap: Array<{
    source: string;
    techniqueId: string;
    count: number;
  }>;
  sourcesTable: Array<{
    sourceType: string;
    totalInputs: number;
    maliciousInputs: number;
    benignInputs: number;
    avgRisk: number;
    avgConfidence: number;
    detectionRate: number;
  }>;
}

export const fetchSourceData = async (filters: Record<string, string>): Promise<SourceData | null> => {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') params.append(key, value);
    });
    
    const response = await apiClient(`/api/v1/dashboard/sources?${params.toString()}`);
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching source data:', error);
    return null;
  }
};
