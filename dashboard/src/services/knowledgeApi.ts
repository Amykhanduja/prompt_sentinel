import { apiClient } from './apiClient';
export interface KnowledgeData {
  kpis: {
    totalTechniques: number;
    totalCanonicalExamples: number;
    totalParaphrases: number;
    totalNegativeExamples: number;
    avgExamplesPerTechnique: number;
    avgSemanticCoverage: number;
    avgThreshold: number;
    knowledgeBaseVersion: string;
  };
  knowledgeDistribution: Array<{
    techniqueId: string;
    canonicalCount: number;
    paraphraseCount: number;
    negativeCount: number;
  }>;
  lowCoverageTechniques: Array<{
    techniqueId: string;
    techniqueName: string;
    coverage: number;
    recommendedExamples: number;
  }>;
  knowledgeTable: Array<{
    techniqueId: string;
    canonicalExampleCount: number;
    paraphraseCount: number;
    negativeExampleCount: number;
    threshold: number;
    avgSimilarity: number;
    detectionCount: number;
  }>;
}

export const fetchKnowledgeData = async (filters: Record<string, string>): Promise<KnowledgeData | null> => {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') params.append(key, value);
    });
    
    const response = await apiClient(`/api/v1/dashboard/knowledge?${params.toString()}`);
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching knowledge data:', error);
    return null;
  }
};
