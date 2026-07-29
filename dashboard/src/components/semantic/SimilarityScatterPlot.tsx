import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';
import { SemanticData } from '../../services/semanticApi';

interface SimilarityScatterPlotProps {
  data: SemanticData['scatterPlot'] | null;
  loading: boolean;
}

export const SimilarityScatterPlot: React.FC<SimilarityScatterPlotProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-6 text-white">Similarity vs Confidence</h3>
      
      <div className="flex-1 relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border-4 border-white/10 border-t-primary animate-spin"></div>
          </div>
        ) : !hasData ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                type="number" 
                dataKey="similarity" 
                name="Similarity" 
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                domain={[0, 1]}
                label={{ value: 'Similarity Score', position: 'bottom', fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
              />
              <YAxis 
                type="number" 
                dataKey="confidence" 
                name="Confidence" 
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                domain={[0, 1]}
                label={{ value: 'Confidence', angle: -90, position: 'left', fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
              />
              <ZAxis type="category" dataKey="techniqueId" name="Technique" />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3', stroke: 'rgba(255,255,255,0.1)' }}
                contentStyle={{ backgroundColor: 'rgba(18, 18, 26, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Scatter name="Prompts" data={data} fill="#ec4899" fillOpacity={0.6} />
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
