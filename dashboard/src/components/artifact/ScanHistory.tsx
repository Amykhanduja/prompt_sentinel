import React from 'react';
import { History, File } from 'lucide-react';
import { NormalizedScanResult } from '../../services/scannerApi';

interface ScanHistoryProps {
  history: NormalizedScanResult[];
  onSelect: (result: NormalizedScanResult) => void;
}

export const ScanHistory: React.FC<ScanHistoryProps> = ({ history, onSelect }) => {
  if (history.length === 0) return null;

  return (
    <div className="glass-panel p-5 mt-6">
      <h3 className="text-lg font-bold flex items-center gap-2 text-white mb-4">
        <History className="w-5 h-5 text-primary" />
        Recent Scans
      </h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-xs text-gray-400 bg-black/40">
              <th className="p-3 font-medium">Timestamp</th>
              <th className="p-3 font-medium">Filename</th>
              <th className="p-3 font-medium">Risk Score</th>
              <th className="p-3 font-medium">Decision</th>
              <th className="p-3 font-medium">Techniques</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {history.map((scan, idx) => {
              const totalDetections = scan.results.reduce((acc, r) => acc + r.detections.length, 0);
              const maxRisk = Math.max(...scan.results.map(r => r.risk_score || 0), 0);
              const highestRiskResult = scan.results.reduce((prev, curr) => (curr.risk_score > (prev.risk_score || 0)) ? curr : prev, scan.results[0]);
              
              return (
                <tr 
                  key={idx}
                  onClick={() => onSelect(scan)}
                  className="border-b border-white/5 hover:bg-white/10 cursor-pointer transition-colors"
                >
                  <td className="p-3 text-gray-400 text-xs">
                    {new Date(scan.metadata.uploadTime).toLocaleTimeString()}
                  </td>
                  <td className="p-3 font-medium text-gray-200 max-w-[150px] truncate">
                    <div className="flex items-center gap-2">
                      <File className="w-3 h-3 text-gray-500 shrink-0" />
                      <span className="truncate">{scan.metadata.filename}</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <span className={`font-bold ${maxRisk >= 40 ? 'text-warning' : maxRisk >= 100 ? 'text-danger' : 'text-success'}`}>
                      {maxRisk}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      highestRiskResult?.action === 'BLOCK' ? 'text-danger bg-danger/10 border border-danger/30' :
                      highestRiskResult?.action === 'MONITOR' ? 'text-warning bg-warning/10 border border-warning/30' :
                      'text-success bg-success/10 border border-success/30'
                    }`}>
                      {highestRiskResult?.action || 'ALLOW'}
                    </span>
                  </td>
                  <td className="p-3 text-gray-300">
                    {totalDetections}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
