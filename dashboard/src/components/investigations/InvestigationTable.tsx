import React, { useState } from 'react';
import { InvestigationRecord } from '../../services/investigationApi';
import { Search, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

interface InvestigationTableProps {
  data: InvestigationRecord[];
  loading: boolean;
  onRowClick: (record: InvestigationRecord) => void;
}

export const InvestigationTable: React.FC<InvestigationTableProps> = ({ data, loading, onRowClick }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredData = React.useMemo(() => {
    if (!searchTerm) return data;
    const lower = searchTerm.toLowerCase();
    return data.filter(r => 
      (r.prompt || '').toLowerCase().includes(lower) || 
      (r.techniqueId || '').toLowerCase().includes(lower) ||
      (r.id || '').toLowerCase().includes(lower)
    );
  }, [data, searchTerm]);

  const getDecisionColor = (decision: string) => {
    switch (decision?.toLowerCase()) {
      case 'blocked': return 'text-danger bg-danger/10 border-danger/20';
      case 'allowed': return 'text-success bg-success/10 border-success/20';
      case 'review': return 'text-warning bg-warning/10 border-warning/20';
      default: return 'text-gray-400 bg-white/5 border-white/10';
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-danger font-bold';
    if (score >= 50) return 'text-warning font-bold';
    return 'text-success font-bold';
  };

  return (
    <div className="glass-panel p-5 overflow-hidden flex flex-col h-[calc(100vh-250px)]">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Detections</h3>
        <div className="relative w-64">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search prompts or IDs..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-black/40 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-primary/50"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-auto relative">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse w-full"></div>
            ))}
          </div>
        ) : filteredData.length === 0 ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <ShieldAlert className="w-12 h-12 mb-2 opacity-50" />
            <p>No Records Found</p>
          </div>
        ) : (
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-[11px] text-gray-400 uppercase bg-black/20 sticky top-0 backdrop-blur-sm z-10 rounded-t-lg">
              <tr>
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Technique</th>
                <th className="px-4 py-3 font-medium">Prompt Snippet</th>
                <th className="px-4 py-3 font-medium">Risk Score</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Similarity</th>
                <th className="px-4 py-3 font-medium">Detector</th>
                <th className="px-4 py-3 font-medium">Source</th>
                <th className="px-4 py-3 font-medium">Decision</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((item, index) => (
                <motion.tr 
                  key={item.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  onClick={() => onRowClick(item)}
                  className="border-b border-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
                >
                  <td className="px-4 py-3 text-gray-400 font-mono text-xs">{item.timestamp}</td>
                  <td className="px-4 py-3">
                    <span className="text-white block text-xs">{item.techniqueId}</span>
                    <span className="text-gray-500 text-[10px] truncate max-w-[120px] block">{item.techniqueName}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-300 max-w-xs truncate font-mono text-xs opacity-70 group-hover:opacity-100">{item.prompt}</td>
                  <td className={`px-4 py-3 font-mono text-center ${getRiskColor(item.riskScore)}`}>{item.riskScore}</td>
                  <td className="px-4 py-3 text-purple-400 font-mono">{(item.confidence * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3 text-cyan-400 font-mono">{item.similarity.toFixed(3)}</td>
                  <td className="px-4 py-3 text-gray-300 capitalize">{item.detector}</td>
                  <td className="px-4 py-3 text-gray-300 capitalize">{item.source}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-1 rounded text-xs border uppercase tracking-wider font-bold ${getDecisionColor(item.policyDecision)}`}>
                      {item.policyDecision}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
