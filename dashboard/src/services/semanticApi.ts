import { apiClient } from './apiClient';
export interface SemanticData {
  kpis: {
    avgSimilarity: number;
    highestSimilarity: number;
    lowestSimilarity: number;
    avgConfidence: number;
    semanticMatches: number;
    semanticDetectionRate: number;
  };
  margin: {
    avgPositiveSimilarity: number;
    avgNegativeSimilarity: number;
    semanticMargin: number;
  };
  similarityDistribution: Array<{
    range: string;
    count: number;
  }>;
  confidenceDistribution: Array<{
    range: string;
    count: number;
  }>;
  scatterPlot: Array<{
    similarity: number;
    confidence: number;
    techniqueId: string;
  }>;
  techniquesTable: Array<{
    techniqueId: string;
    threshold: number;
    avgSimilarity: number;
    highestSimilarity: number;
    lowestSimilarity: number;
    avgConfidence: number;
    positiveMatches: number;
    negativeMatches: number;
    detectionCount: number;
  }>;
  similarityOverTime: Array<{
    timestamp: string;
    similarity: number;
  }>;
}

export const fetchSemanticData = async (filters: Record<string, string>): Promise<SemanticData | null> => {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') params.append(key, value);
    });
    
    const response = await apiClient(`/api/v1/dashboard/semantic?${params.toString()}`);
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching semantic data:', error);
    return null;
  }
};
