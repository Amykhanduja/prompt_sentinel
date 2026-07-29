import React from 'react';
import { Download, FileJson, FileText, Table } from 'lucide-react';
import { NormalizedScanResult } from '../../services/scannerApi';

interface ExportPanelProps {
  data: NormalizedScanResult;
}

export const ExportPanel: React.FC<ExportPanelProps> = ({ data }) => {
  const exportJson = () => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan_${data.metadata.filename}_${new Date().getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportCsv = () => {
    // Basic CSV summarizing detections
    let csv = 'Technique,Detector,Severity,Risk Score\n';
    data.results.forEach(res => {
      res.detections.forEach(det => {
        csv += `"${det.technique || det.name || ''}","${det.detector || ''}","${det.severity || ''}","${res.risk_score || ''}"\n`;
      });
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan_summary_${data.metadata.filename}_${new Date().getTime()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-panel p-5 mt-6">
      <h3 className="text-lg font-bold flex items-center gap-2 text-white mb-4">
        <Download className="w-5 h-5 text-primary" />
        Export Results
      </h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <button 
          onClick={exportJson}
          className="flex flex-col items-center justify-center p-4 rounded-lg border border-white/10 bg-black/20 hover:bg-white/5 hover:border-primary/50 transition-colors group"
        >
          <FileJson className="w-6 h-6 text-gray-400 group-hover:text-primary mb-2" />
          <span className="text-sm font-medium text-gray-300">JSON Report</span>
        </button>
        
        <button 
          onClick={exportCsv}
          className="flex flex-col items-center justify-center p-4 rounded-lg border border-white/10 bg-black/20 hover:bg-white/5 hover:border-primary/50 transition-colors group"
        >
          <Table className="w-6 h-6 text-gray-400 group-hover:text-primary mb-2" />
          <span className="text-sm font-medium text-gray-300">CSV Summary</span>
        </button>
        
        <button 
          disabled
          className="flex flex-col items-center justify-center p-4 rounded-lg border border-white/5 bg-black/10 opacity-50 cursor-not-allowed"
          title="PDF generation coming soon"
        >
          <FileText className="w-6 h-6 text-gray-500 mb-2" />
          <span className="text-sm font-medium text-gray-500">PDF Report</span>
        </button>
      </div>
    </div>
  );
};
