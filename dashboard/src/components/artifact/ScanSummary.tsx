import React from 'react';
import { NormalizedScanResult } from '../../services/scannerApi';
import { AlertTriangle, Search, Layers, ShieldAlert } from 'lucide-react';

interface ScanSummaryProps {
  data: NormalizedScanResult;
}

export const ScanSummary: React.FC<ScanSummaryProps> = ({ data }) => {
  // Aggregate stats across all results
  const totalDetections = data.results.reduce((acc, r) => acc + r.detections.length, 0);
  const maxRiskScore = Math.max(...data.results.map(r => r.risk_score || 0), 0);
  
  const getActionColor = (action: string) => {
    switch (action?.toUpperCase()) {
      case 'BLOCK': return 'text-danger bg-danger/10 border-danger/30';
      case 'MONITOR': return 'text-warning bg-warning/10 border-warning/30';
      default: return 'text-success bg-success/10 border-success/30';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high': return 'text-danger';
      case 'medium': return 'text-warning';
      default: return 'text-success';
    }
  };

  // Assume the highest risk dictates the overall action
  const highestRiskResult = data.results.reduce((prev, curr) => (curr.risk_score > (prev.risk_score || 0)) ? curr : prev, data.results[0]);
  const action = highestRiskResult?.action || 'ALLOW';
  const severity = highestRiskResult?.severity || 'low';

  const allDetections = data.results.flatMap(r => r.detections);
  const detectorCounts = allDetections.reduce((acc: any, d: any) => {
    const type = (d.detector || 'unknown').toLowerCase();
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const confidenceGroups = allDetections.reduce((acc: any, d: any) => {
    const c = d.confidence || 0;
    if (c > 0.9) acc.high++;
    else if (c >= 0.5) acc.medium++;
    else acc.low++;
    return acc;
  }, { high: 0, medium: 0, low: 0 });
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div className="glass-panel p-5 flex flex-col justify-between">
        <div className="flex items-center gap-2 mb-2">
          <ShieldAlert className="w-5 h-5 text-gray-400" />
          <h4 className="text-sm text-gray-400 font-medium">Policy Decision</h4>
        </div>
        <div className={`mt-2 inline-flex items-center justify-center px-4 py-2 rounded-lg border font-bold text-lg ${getActionColor(action)}`}>
          {action}
        </div>
      </div>

      <div className="glass-panel p-5 flex flex-col justify-between">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-5 h-5 text-gray-400" />
          <h4 className="text-sm text-gray-400 font-medium">Max Risk Score</h4>
        </div>
        <div className="flex items-end gap-3">
          <span className={`text-4xl font-bold ${getSeverityColor(severity)}`}>{maxRiskScore}</span>
          <span className={`text-sm font-medium mb-1 uppercase ${getSeverityColor(severity)}`}>{severity}</span>
        </div>
      </div>

      <div className="glass-panel p-5 flex flex-col justify-between">
        <div className="flex items-center gap-2 mb-2">
          <Search className="w-5 h-5 text-gray-400" />
          <h4 className="text-sm text-gray-400 font-medium">Total Detections</h4>
        </div>
        <div className="text-3xl font-bold text-white">
          {totalDetections}
        </div>
      </div>

      <div className="glass-panel p-5 flex flex-col justify-between">
        <div className="flex items-center gap-2 mb-2">
          <Layers className="w-5 h-5 text-gray-400" />
          <h4 className="text-sm text-gray-400 font-medium">Extracted Objects</h4>
        </div>
        <div className="text-3xl font-bold text-white">
          {data.results.length}
        </div>
      </div>
      
      {/* Detector Distribution */}
      <div className="glass-panel p-5 md:col-span-2 lg:col-span-4 mt-2">
        <h4 className="text-sm text-gray-400 font-medium mb-4">Detector & Risk Breakdown</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-xs text-gray-500 uppercase mb-2">Detectors</div>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Regex</span>
                <span className="font-medium text-white">{detectorCounts.regex || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Semantic</span>
                <span className="font-medium text-white">{detectorCounts.semantic || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Fusion</span>
                <span className="font-medium text-white">{detectorCounts.fusion || 0}</span>
              </div>
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase mb-2">Confidence</div>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">High (&gt;90%)</span>
                <span className="font-medium text-white">{confidenceGroups.high}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Medium (50-90%)</span>
                <span className="font-medium text-white">{confidenceGroups.medium}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Low (&lt;50%)</span>
                <span className="font-medium text-white">{confidenceGroups.low}</span>
              </div>
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase mb-2">Risk Breakdown</div>
            <div className="space-y-2 max-h-24 overflow-y-auto custom-scrollbar">
              {highestRiskResult?.risk_breakdown && highestRiskResult.risk_breakdown.length > 0 ? (
                highestRiskResult.risk_breakdown.map((rb: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center text-sm border-b border-white/5 pb-1">
                    <span className="text-gray-300 truncate max-w-[150px]" title={rb.factor}>{rb.factor}</span>
                    <span className="font-medium text-danger">+{rb.score}</span>
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500 italic">No risk modifiers applied.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
