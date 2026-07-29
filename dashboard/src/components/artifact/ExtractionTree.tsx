import React from 'react';
import { NormalizedScanResult } from '../../services/scannerApi';
import { Layers, FileText } from 'lucide-react';

interface ExtractionTreeProps {
  data: NormalizedScanResult;
}

export const ExtractionTree: React.FC<ExtractionTreeProps> = ({ data }) => {
  // If the backend returned a flat list of objects instead of a tree, 
  // we can display them as a list for now, or group them if there's hierarchy info.
  // We'll just display a simple list of parsed objects since we just have an array of results.
  
  if (data.results.length <= 1) return null;

  return (
    <div className="glass-panel p-5 mt-6">
      <h3 className="text-lg font-bold flex items-center gap-2 text-white mb-4">
        <Layers className="w-5 h-5 text-primary" />
        Recursive Extraction Tree
      </h3>
      
      <div className="space-y-3">
        {data.results.map((res, idx) => (
          <div key={idx} className="flex flex-col gap-2 p-3 bg-black/20 rounded-lg border border-white/5 ml-4 relative">
            {/* Tree connecting line visual */}
            <div className="absolute -left-4 top-4 w-4 h-px bg-white/20"></div>
            <div className="absolute -left-4 top-0 bottom-4 w-px bg-white/20"></div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-200">Extracted Object {idx + 1}</span>
              </div>
              <span className="text-xs bg-black/40 px-2 py-1 rounded text-gray-400">
                {res.prompt.length} chars
              </span>
            </div>
            
            <div className="text-xs text-gray-500 truncate max-w-full">
              {res.prompt.substring(0, 100)}...
            </div>
            
            {res.detections.length > 0 && (
              <div className="mt-1">
                <span className="text-xs font-bold text-danger bg-danger/10 px-2 py-0.5 rounded-full border border-danger/20">
                  {res.detections.length} Threat{res.detections.length !== 1 ? 's' : ''} Found
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
