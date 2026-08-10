import React, { useState } from 'react';
import { NormalizedScanResult } from '../../services/scannerApi';
import { Shield, Target, ChevronDown, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface DetectionTableProps {
  data: NormalizedScanResult;
}

export const DetectionTable: React.FC<DetectionTableProps> = ({ data }) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (id: string) => {
    const newSet = new Set(expandedRows);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedRows(newSet);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high': return 'text-danger bg-danger/10 border-danger/30';
      case 'medium': return 'text-warning bg-warning/10 border-warning/30';
      default: return 'text-success bg-success/10 border-success/30';
    }
  };

  const allDetections = data.results.flatMap((res, i) => 
    res.detections.map((det, j) => ({
      ...det,
      id: `${i}-${j}`,
      sourceText: res.prompt
    }))
  );

  if (allDetections.length === 0) {
    return (
      <div className="glass-panel p-10 flex flex-col items-center justify-center text-center">
        <div className="w-16 h-16 bg-success/20 rounded-full flex items-center justify-center mb-4">
          <Shield className="w-8 h-8 text-success" />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">No Threats Detected</h3>
        <p className="text-gray-400">The scanned artifact is clean. No malicious techniques or policy violations were found.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel overflow-hidden">
      <div className="p-5 border-b border-white/10 flex justify-between items-center bg-black/20">
        <h3 className="text-lg font-bold flex items-center gap-2 text-white">
          <Target className="w-5 h-5 text-primary" />
          Detected Techniques
        </h3>
        <span className="bg-primary/20 text-primary text-xs font-bold px-2 py-1 rounded-full">
          {allDetections.length} Detections
        </span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-sm text-gray-400 bg-black/40">
              <th className="p-4 font-medium w-10"></th>
              <th className="p-4 font-medium">Technique</th>
              <th className="p-4 font-medium">Detector</th>
              <th className="p-4 font-medium">Severity</th>
              <th className="p-4 font-medium">Confidence</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {allDetections.map((det) => (
              <React.Fragment key={det.id}>
                <tr 
                  className={`border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors ${expandedRows.has(det.id) ? 'bg-white/5' : ''}`}
                  onClick={() => toggleRow(det.id)}
                >
                  <td className="p-4">
                    {expandedRows.has(det.id) ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                  </td>
                  <td className="p-4 font-medium text-gray-200">
                    {det.technique || det.name || 'Unknown Technique'}
                  </td>
                  <td className="p-4 text-gray-400">
                    <span className="px-2 py-1 bg-black/40 rounded border border-white/10 text-xs">
                      {det.detector || 'Unknown'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold border ${getSeverityColor(det.severity)}`}>
                      {(det.severity || 'low').toUpperCase()}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300">
                    {det.confidence ? `${(det.confidence * 100).toFixed(0)}%` : 'N/A'}
                  </td>
                </tr>
                <AnimatePresence>
                  {expandedRows.has(det.id) && (
                    <motion.tr
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="bg-black/30 border-b border-white/5"
                    >
                      <td colSpan={5} className="p-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Detection Details</h4>
                            <div className="space-y-2 text-sm text-gray-300">
                              {det.description && <p>{det.description}</p>}
                              {det.pattern && (
                                <div className="mt-2">
                                  <span className="text-xs text-gray-500">Pattern Matched:</span>
                                  <code className="block bg-black/50 p-2 rounded mt-1 text-primary border border-primary/20 font-mono text-xs">
                                    {det.pattern}
                                  </code>
                                </div>
                              )}
                            </div>
                          </div>

                          {det.detection_context?.obfuscation_detected && (
                            <div className="mt-4 lg:mt-0">
                              <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Obfuscation</h4>
                              <div className="space-y-2 text-sm text-gray-300">
                                <div className="flex items-center gap-2 text-warning font-bold">
                                  <span>Obfuscation detected</span>
                                </div>
                                {det.detection_context.transformations && det.detection_context.transformations.length > 0 && (
                                  <div className="mt-2">
                                    <span className="text-xs text-gray-500">Transformations:</span>
                                    <ul className="list-disc list-inside mt-1">
                                      {det.detection_context.transformations.map((t: string, idx: number) => {
                                        const names: Record<string, string> = {
                                          'LEETSPEAK_NORMALIZED': 'Leetspeak',
                                          'CONFUSABLE_NORMALIZED': 'Unicode Confusable',
                                          'HOMOGLYPH_NORMALIZED': 'Homoglyph',
                                          'OCR_NORMALIZED': 'OCR Artifact',
                                          'WHITESPACE_NORMALIZED': 'Whitespace',
                                          'REPETITION_NORMALIZED': 'Character Repetition',
                                          'MARKDOWN_CLEANED': 'Markdown Obfuscation',
                                          'MIXED_LANGUAGE_NORMALIZED': 'Mixed Script'
                                        };
                                        return <li key={idx} className="text-gray-300">{names[t] || t}</li>;
                                      })}
                                    </ul>
                                  </div>
                                )}
                                {det.detection_context.obfuscation_adjustment && det.detection_context.obfuscation_adjustment > 0 && (
                                  <div className="mt-2">
                                    <span className="text-xs text-gray-500">Risk Adjustment: </span>
                                    <span className="text-danger font-bold">+{det.detection_context.obfuscation_adjustment}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          <div className={det.detection_context?.obfuscation_detected ? "lg:col-span-2 mt-4" : "mt-4 lg:mt-0"}>
                            <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Extracted Context</h4>
                            <div className="bg-black/50 p-3 rounded border border-white/10 text-xs font-mono text-gray-400 max-h-32 overflow-y-auto custom-scrollbar">
                              {det.match_text || det.sourceText.substring(0, 300) + (det.sourceText.length > 300 ? '...' : '')}
                            </div>
                          </div>
                        </div>
                      </td>
                    </motion.tr>
                  )}
                </AnimatePresence>
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
