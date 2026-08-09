import { apiClient } from './apiClient';
export interface RiskPolicyData {
  kpis: {
    avgRiskScore: number;
    highestRiskScore: number;
    lowestRiskScore: number;
    avgConfidence: number;
    blockedDecisions: number;
    allowedDecisions: number;
    reviewDecisions: number;
    avgPolicyDecisionTimeMs: number;
  };
  riskScoreHistogram: Array<{
    range: string;
    count: number;
  }>;
  riskTrend: Array<{
    timestamp: string;
    avgRisk: number;
  }>;
  decisionsByTechnique: Array<{
    techniqueId: string;
    blocked: number;
    allowed: number;
    review: number;
  }>;
  compoundRuleActivations: Array<{
    ruleName: string;
    activations: number;
  }>;
  duplicatePenaltiesOverTime: Array<{
    timestamp: string;
    penalties: number;
  }>;
  techniquesTable: Array<{
    techniqueId: string;
    avgRisk: number;
    highestRisk: number;
    lowestRisk: number;
    decisionCount: number;
    avgConfidence: number;
    avgPolicyScore: number;
  }>;
}

export const fetchRiskPolicyData = async (filters: Record<string, string>): Promise<RiskPolicyData | null> => {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') params.append(key, value);
    });

    const queryString = params.toString();
    
    // Fetch both endpoints concurrently
    const [riskRes, policyRes] = await Promise.all([
      apiClient(`/api/v1/dashboard/risk?${queryString}`),
      apiClient(`/api/v1/dashboard/policy?${queryString}`)
    ]);

    if (!riskRes.ok || !policyRes.ok) {
      if ((riskRes.status === 404 || riskRes.status === 500) || (policyRes.status === 404 || policyRes.status === 500)) {
        return null;
      }
      throw new Error('Network response was not ok');
    }

    const riskData = await riskRes.json();
    const policyData = await policyRes.json();

    // Merge backend responses into the unified interface
    return {
      kpis: {
        avgRiskScore: riskData.kpis?.avgRiskScore,
        highestRiskScore: riskData.kpis?.highestRiskScore,
        lowestRiskScore: riskData.kpis?.lowestRiskScore,
        avgConfidence: riskData.kpis?.avgConfidence,
        blockedDecisions: policyData.kpis?.blockedDecisions,
        allowedDecisions: policyData.kpis?.allowedDecisions,
        reviewDecisions: policyData.kpis?.reviewDecisions,
        avgPolicyDecisionTimeMs: policyData.kpis?.avgPolicyDecisionTimeMs,
      },
      riskScoreHistogram: riskData.riskScoreHistogram || [],
      riskTrend: riskData.riskTrend || [],
      decisionsByTechnique: policyData.decisionsByTechnique || [],
      compoundRuleActivations: policyData.compoundRuleActivations || [],
      duplicatePenaltiesOverTime: riskData.duplicatePenaltiesOverTime || [],
      // The table relies on combining risk technique data and policy decision counts.
      // We assume the backend provides the table rows in either riskData or policyData, or we map it if they come separated.
      // For simplicity, we assume the backend handles returning the combined tabular data under riskData.techniquesTable
      techniquesTable: riskData.techniquesTable || [],
    };
  } catch (error) {
    console.error('Error fetching risk and policy data:', error);
    return null;
  }
};
