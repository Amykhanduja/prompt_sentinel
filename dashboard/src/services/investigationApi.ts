import { apiClient } from './apiClient';
export interface InvestigationRecord {
  id: string;
  timestamp: string;
  prompt: string;
  techniqueId: string;
  techniqueName: string;
  confidence: number;
  similarity: number;
  detector: string;
  riskScore: number;
  policyDecision: string;
  source: string;
  
  // Detailed fields for drawer
  originalPrompt?: string;
  preprocessedPrompt?: string;
  riskBreakdown?: Record<string, number>;
  semanticMatchInfo?: {
    canonicalMatched?: boolean;
    paraphraseMatched?: boolean;
    negativeMatched?: boolean;
    highestMatchScore?: number;
  };
  regexPattern?: string;
  matchedExamples?: string[];
  rawBackendResponse?: Record<string, any>;
}

export const fetchInvestigations = async (filters: Record<string, string>): Promise<InvestigationRecord[]> => {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') params.append(key, value);
    });
    
    const response = await apiClient(`/api/v1/dashboard/recent?${params.toString()}`);
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return [];
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    // Assuming backend returns { records: [...] } or just an array [...]
    return Array.isArray(data) ? data : data.records || [];
  } catch (error) {
    console.error('Error fetching investigations:', error);
    return [];
  }
};
