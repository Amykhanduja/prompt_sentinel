import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { SemanticData } from '../../services/semanticApi';

interface DistributionHistogramsProps {
  similarityData: SemanticData['similarityDistribution'] | null;
  confidenceData: SemanticData['confidenceDistribution'] | null;
  loading: boolean;
}

export const DistributionHistograms: React.FC<DistributionHistogramsProps> = ({ similarityData, confidenceData, loading }) => {
  const renderHistogram = (data: Array<{range: string; count: number}> | null, title: string, color: string) => {
    const hasData = data && data.length > 0;

    return (
      <div className="glass-panel p-5 h-[300px] flex flex-col w-full">
        <h3 className="text-sm font-semibold mb-4 text-white uppercase tracking-wider">{title}</h3>
        <div className="flex-1 relative">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 rounded-full border-2 border-white/10 border-t-primary animate-spin"></div>
            </div>
          ) : !hasData ? (
            <div className="absolute inset-0 flex items-center justify-center text-gray-500 text-sm">
              No Data Available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis 
                  dataKey="range" 
                  stroke="rgba(255,255,255,0.3)" 
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} 
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="rgba(255,255,255,0.3)" 
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: 'rgba(18, 18, 26, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="count" radius={[2, 2, 0, 0]}>
                  {data.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-4 h-full">
      {renderHistogram(similarityData, 'Similarity Distribution', '#3b82f6')}
      {renderHistogram(confidenceData, 'Confidence Distribution', '#a855f7')}
    </div>
  );
};
