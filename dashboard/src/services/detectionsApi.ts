import { apiClient } from './apiClient';
export interface DetectionsData {
  kpis: {
    totalDetections: number;
    regexDetections: number;
    semanticDetections: number;
    fusionDetections: number;
    multiTechniquePrompts: number;
    avgTechniquesPerPrompt: number;
    highestRiskTechnique: string;
    mostFrequentTechnique: string;
  };
  techniqueCounts: Array<{
    techniqueId: string;
    count: number;
  }>;
  techniqueEngineBreakdown: Array<{
    techniqueId: string;
    regexOnly: number;
    semanticOnly: number;
    fusion: number;
  }>;
  techniquesTable: Array<{
    techniqueId: string;
    techniqueName: string;
    detectionCount: number;
    avgConfidence: number;
    avgRiskScore: number;
    detectorType: string;
    percentageOfTotal: number;
  }>;
  timeline: Array<{
    timestamp: string;
    [key: string]: any; // Dynamic keys for technique IDs
  }>;
  activeTechniquesInTimeline: string[]; // List of technique keys present in the timeline
}

export const fetchDetectionsData = async (filters: Record<string, string>): Promise<DetectionsData | null> => {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') params.append(key, value);
    });
    
    const response = await apiClient(`/api/v1/dashboard/detections?${params.toString()}`);
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching detections data:', error);
    return null;
  }
};
