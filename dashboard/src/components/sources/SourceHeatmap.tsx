import React, { useMemo } from 'react';
import { SourceData } from '../../services/sourceApi';
import { motion } from 'framer-motion';

interface SourceHeatmapProps {
  data: SourceData['heatmap'] | null;
  loading: boolean;
}

export const SourceHeatmap: React.FC<SourceHeatmapProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  const { sources, techniques, matrix, maxCount } = useMemo(() => {
    if (!hasData) return { sources: [], techniques: [], matrix: {}, maxCount: 0 };
    
    const srcSet = new Set<string>();
    const techSet = new Set<string>();
    let max = 0;
    
    data!.forEach(d => {
      srcSet.add(d.source);
      techSet.add(d.techniqueId);
      if (d.count > max) max = d.count;
    });
    
    const srcList = Array.from(srcSet).sort();
    const techList = Array.from(techSet).sort();
    
    const mat: Record<string, Record<string, number>> = {};
    srcList.forEach(s => {
      mat[s] = {};
      techList.forEach(t => {
        mat[s][t] = 0;
      });
    });
    
    data!.forEach(d => {
      mat[d.source][d.techniqueId] = d.count;
    });
    
    return { sources: srcList, techniques: techList, matrix: mat, maxCount: max };
  }, [data, hasData]);

  const getOpacity = (count: number) => {
    if (count === 0) return 0.05;
    return Math.max(0.2, count / maxCount);
  };

  return (
    <div className="glass-panel p-5 overflow-hidden flex flex-col h-full min-h-[350px]">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Detections by Source and Technique</h3>
      </div>
      
      <div className="flex-1 overflow-auto relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border-4 border-white/10 border-t-primary animate-spin"></div>
          </div>
        ) : !hasData ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <div className="inline-block min-w-full">
            <div className="flex">
              {/* Top-left empty cell */}
              <div className="w-24 shrink-0 h-10"></div>
              {/* Column Headers (Techniques) */}
              {techniques.map(tech => (
                <div key={tech} className="w-16 shrink-0 h-10 flex items-center justify-center -rotate-45 origin-bottom-left whitespace-nowrap text-[10px] text-gray-400 font-mono">
                  {tech}
                </div>
              ))}
            </div>
            
            {/* Rows (Sources) */}
            {sources.map((source, rIdx) => (
              <div key={source} className="flex mb-1 items-center group">
                <div className="w-24 shrink-0 text-right pr-4 text-xs font-medium text-gray-300 truncate">
                  {source}
                </div>
                {techniques.map((tech, cIdx) => {
                  const count = matrix[source][tech];
                  return (
                    <motion.div 
                      key={`${source}-${tech}`}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: (rIdx * 0.05) + (cIdx * 0.02) }}
                      className="w-12 h-8 mx-0.5 rounded-md relative flex items-center justify-center group/cell cursor-pointer"
                      style={{ 
                        backgroundColor: `rgba(239, 68, 68, ${getOpacity(count)})`,
                        border: count > 0 ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(255, 255, 255, 0.05)'
                      }}
                    >
                      {count > 0 && <span className="text-[10px] font-mono text-white opacity-0 group-hover/cell:opacity-100 transition-opacity">{count}</span>}
                      
                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-2 hidden group-hover/cell:block z-50 bg-black/90 border border-white/10 px-2 py-1 rounded text-xs whitespace-nowrap shadow-xl">
                        <span className="text-gray-400">{source} &rarr; {tech}:</span> <span className="text-white font-bold">{count}</span>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
