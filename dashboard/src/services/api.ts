export interface DashboardData {
  kpis: {
    totalScanned: number;
    malicious: number;
    benign: number;
    detectionRate: number;
    blocked: number;
    allowed: number;
    reviewQueue: number;
    averageRiskScore: number;
  };
  gauge: {
    overallRiskScore: number;
  };
  detectionsByType: {
    regex: number;
    semantic: number;
    fusion: number;
  };
  decisions: {
    blocked: number;
    allowed: number;
    review: number;
  };
  recentDetections: Array<{
    id: string;
    timestamp: string;
    techniqueId: string;
    techniqueName: string;
    riskScore: number;
    confidence: number;
    detector: string;
    decision: string;
    source: string;
  }>;
}

export const fetchDashboardData = async (): Promise<DashboardData | null> => {
  try {
    const response = await fetch('/api/v1/dashboard/overview');
    if (!response.ok) {
      if (response.status === 404 || response.status === 500) {
        return null;
      }
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return null; // Return null if API fails so UI can show "No Data Available"
  }
};
