import React, { useState } from 'react';
import { KnowledgeData } from '../../services/knowledgeApi';
import { motion } from 'framer-motion';
import { ArrowUpDown, ShieldAlert } from 'lucide-react';

interface KnowledgeTableProps {
  data: KnowledgeData['knowledgeTable'] | null;
  loading: boolean;
}

type SortKey = keyof KnowledgeData['knowledgeTable'][0];

export const KnowledgeTable: React.FC<KnowledgeTableProps> = ({ data, loading }) => {
  const [sortKey, setSortKey] = useState<SortKey>('canonicalExampleCount');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('desc');
    }
  };

  const sortedData = React.useMemo(() => {
    if (!data) return [];
    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortKey, sortOrder]);

  return (
    <div className="glass-panel p-5 overflow-hidden flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Knowledge Base Registry</h3>
      </div>
      
      <div className="flex-1 overflow-x-auto relative">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse w-full"></div>
            ))}
          </div>
        ) : !data || data.length === 0 ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <ShieldAlert className="w-12 h-12 mb-2 opacity-50" />
            <p>No Data Available</p>
          </div>
        ) : (
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-[11px] text-gray-400 uppercase bg-black/20 sticky top-0 backdrop-blur-sm z-10 rounded-t-lg">
              <tr>
                {[
                  { key: 'techniqueId', label: 'Technique' },
                  { key: 'canonicalExampleCount', label: 'Canonical' },
                  { key: 'paraphraseCount', label: 'Paraphrases' },
                  { key: 'negativeExampleCount', label: 'Negatives' },
                  { key: 'threshold', label: 'Threshold' },
                  { key: 'avgSimilarity', label: 'Avg Similarity' },
                  { key: 'detectionCount', label: 'Detections' },
                ].map((col) => (
                  <th 
                    key={col.key} 
                    className="px-4 py-3 font-medium cursor-pointer hover:text-white transition-colors group select-none"
                    onClick={() => handleSort(col.key as SortKey)}
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      <ArrowUpDown className={`w-3 h-3 ${sortKey === col.key ? 'text-primary' : 'opacity-0 group-hover:opacity-50'}`} />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedData.map((item, index) => (
                <motion.tr 
                  key={item.techniqueId}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors group"
                >
                  <td className="px-4 py-3 text-white font-mono text-xs">{item.techniqueId}</td>
                  <td className="px-4 py-3 text-emerald-400 font-mono">{item.canonicalExampleCount}</td>
                  <td className="px-4 py-3 text-purple-400 font-mono">{item.paraphraseCount}</td>
                  <td className="px-4 py-3 text-danger font-mono">{item.negativeExampleCount}</td>
                  <td className="px-4 py-3 text-gray-300 font-mono">{item.threshold.toFixed(2)}</td>
                  <td className="px-4 py-3 text-cyan-400 font-mono">{item.avgSimilarity.toFixed(3)}</td>
                  <td className="px-4 py-3 text-white font-mono font-bold">{item.detectionCount.toLocaleString()}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
