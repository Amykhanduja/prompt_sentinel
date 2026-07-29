import React, { useState } from 'react';
import { InvestigationRecord } from '../../services/investigationApi';
import { X, Download, ShieldAlert, AlignLeft, CheckCircle2, AlertTriangle, Ban, FileJson } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface InvestigationDrawerProps {
  record: InvestigationRecord | null;
  onClose: () => void;
}

export const InvestigationDrawer: React.FC<InvestigationDrawerProps> = ({ record, onClose }) => {
  const [activeTab, setActiveTab] = useState<'details' | 'json' | 'raw'>('details');

  if (!record) return null;

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(record, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", `investigation_${record.id}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision?.toLowerCase()) {
      case 'blocked': return <Ban className="w-5 h-5 text-danger" />;
      case 'allowed': return <CheckCircle2 className="w-5 h-5 text-success" />;
      case 'review': return <AlertTriangle className="w-5 h-5 text-warning" />;
      default: return <ShieldAlert className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="fixed inset-y-0 right-0 w-[800px] bg-black/95 border-l border-white/10 shadow-2xl z-50 flex flex-col backdrop-blur-xl"
      >
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-white/10 bg-white/5">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-white/5 rounded-lg border border-white/10">
              {getDecisionIcon(record.policyDecision)}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Investigation: {record.id}</h2>
              <p className="text-sm text-gray-400">{record.timestamp} &bull; {record.source.toUpperCase()}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={handleExport}
              className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
              title="Export to JSON"
            >
              <Download className="w-5 h-5" />
            </button>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/10 bg-black/50 px-6">
          {[
            { id: 'details', label: 'Detection Details', icon: AlignLeft },
            { id: 'json', label: 'Structured Data', icon: FileJson },
            { id: 'raw', label: 'Raw Backend Response', icon: FileJson }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id 
                  ? 'border-primary text-primary' 
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Top Metrics Grid */}
              <div className="grid grid-cols-4 gap-4">
                <div className="glass-panel p-3">
                  <span className="text-[10px] uppercase tracking-wider text-gray-500 block mb-1">Technique</span>
                  <span className="text-sm font-bold text-white block truncate" title={record.techniqueName}>{record.techniqueId}</span>
                </div>
                <div className="glass-panel p-3">
                  <span className="text-[10px] uppercase tracking-wider text-gray-500 block mb-1">Risk Score</span>
                  <span className={`text-lg font-bold ${record.riskScore >= 80 ? 'text-danger' : record.riskScore >= 50 ? 'text-warning' : 'text-success'}`}>{record.riskScore}</span>
                </div>
                <div className="glass-panel p-3">
                  <span className="text-[10px] uppercase tracking-wider text-gray-500 block mb-1">Confidence</span>
                  <span className="text-lg font-bold text-purple-400">{(record.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="glass-panel p-3">
                  <span className="text-[10px] uppercase tracking-wider text-gray-500 block mb-1">Detector</span>
                  <span className="text-sm font-bold text-cyan-400 uppercase">{record.detector}</span>
                </div>
              </div>

              {/* Prompts */}
              <div className="space-y-4">
                <div className="glass-panel p-4">
                  <h4 className="text-xs font-semibold uppercase text-gray-400 mb-2">Original Prompt</h4>
                  <div className="bg-black/50 p-3 rounded border border-white/5 font-mono text-sm text-gray-300 max-h-40 overflow-y-auto whitespace-pre-wrap">
                    {record.originalPrompt || record.prompt}
                  </div>
                </div>
                {record.preprocessedPrompt && record.preprocessedPrompt !== (record.originalPrompt || record.prompt) && (
                  <div className="glass-panel p-4">
                    <h4 className="text-xs font-semibold uppercase text-gray-400 mb-2">Preprocessed Prompt</h4>
                    <div className="bg-black/50 p-3 rounded border border-white/5 font-mono text-sm text-gray-300 max-h-40 overflow-y-auto whitespace-pre-wrap">
                      {record.preprocessedPrompt}
                    </div>
                  </div>
                )}
              </div>

              {/* Semantic Info (if applicable) */}
              {record.detector !== 'regex' && (
                <div className="glass-panel p-4">
                  <h4 className="text-xs font-semibold uppercase text-gray-400 mb-3">Semantic Analysis</h4>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-black/40 p-3 rounded border border-white/5">
                      <span className="text-[10px] text-gray-500 uppercase block">Similarity Score</span>
                      <span className="text-xl font-mono text-cyan-400">{record.similarity.toFixed(4)}</span>
                    </div>
                    {record.semanticMatchInfo?.highestMatchScore && (
                      <div className="bg-black/40 p-3 rounded border border-white/5">
                        <span className="text-[10px] text-gray-500 uppercase block">Highest Match Score</span>
                        <span className="text-xl font-mono text-primary">{record.semanticMatchInfo.highestMatchScore.toFixed(4)}</span>
                      </div>
                    )}
                  </div>
                  
                  {record.semanticMatchInfo && (
                    <div className="flex gap-2 text-xs font-mono">
                      {record.semanticMatchInfo.canonicalMatched && <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">Canonical Match</span>}
                      {record.semanticMatchInfo.paraphraseMatched && <span className="px-2 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded">Paraphrase Match</span>}
                      {record.semanticMatchInfo.negativeMatched && <span className="px-2 py-1 bg-danger/10 text-danger border border-danger/20 rounded">Negative Match</span>}
                    </div>
                  )}

                  {record.matchedExamples && record.matchedExamples.length > 0 && (
                    <div className="mt-4">
                      <span className="text-xs text-gray-500 uppercase mb-2 block">Matched KB Examples</span>
                      <ul className="space-y-2">
                        {record.matchedExamples.map((ex, i) => (
                          <li key={i} className="bg-white/5 p-2 rounded border border-white/5 text-xs text-gray-300 font-mono">
                            {ex}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Regex Info */}
              {record.detector !== 'semantic' && record.regexPattern && (
                <div className="glass-panel p-4 border-l-2 border-l-primary">
                  <h4 className="text-xs font-semibold uppercase text-gray-400 mb-2">Regex Trigger</h4>
                  <div className="bg-black/50 p-2 rounded border border-white/5 font-mono text-sm text-primary break-all">
                    {record.regexPattern}
                  </div>
                </div>
              )}

              {/* Risk Breakdown */}
              {record.riskBreakdown && Object.keys(record.riskBreakdown).length > 0 && (
                <div className="glass-panel p-4">
                  <h4 className="text-xs font-semibold uppercase text-gray-400 mb-3">Risk Calculation Breakdown</h4>
                  <div className="space-y-2">
                    {Object.entries(record.riskBreakdown).map(([key, val]) => (
                      <div key={key} className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">{key}</span>
                        <span className="font-mono text-white">+{val}</span>
                      </div>
                    ))}
                    <div className="pt-2 mt-2 border-t border-white/10 flex justify-between items-center text-sm font-bold">
                      <span className="text-white">Total Risk Score</span>
                      <span className="text-danger font-mono">{record.riskScore}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'json' && (
            <div className="bg-[#1e1e1e] p-4 rounded-lg overflow-auto border border-white/10 h-full">
              <pre className="text-xs text-[#d4d4d4] font-mono leading-relaxed">
                {JSON.stringify(record, null, 2)}
              </pre>
            </div>
          )}

          {activeTab === 'raw' && (
            <div className="bg-[#1e1e1e] p-4 rounded-lg overflow-auto border border-white/10 h-full">
              <pre className="text-xs text-[#d4d4d4] font-mono leading-relaxed">
                {JSON.stringify(record.rawBackendResponse || { error: 'No raw backend response attached' }, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
