import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { KnowledgeData } from '../../services/knowledgeApi';

interface KnowledgeDistributionChartProps {
  data: KnowledgeData['knowledgeDistribution'] | null;
  loading: boolean;
}

export const KnowledgeDistributionChart: React.FC<KnowledgeDistributionChartProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-[350px] flex flex-col">
      <h3 className="text-lg font-semibold mb-6 text-white">Knowledge Distribution by Technique</h3>
      
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
            <BarChart data={data} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
              <XAxis 
                dataKey="techniqueId" 
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
                contentStyle={{ backgroundColor: 'rgba(18, 18, 26, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Bar dataKey="canonicalCount" name="Canonical" stackId="a" fill="#10b981" />
              <Bar dataKey="paraphraseCount" name="Paraphrases" stackId="a" fill="#3b82f6" />
              <Bar dataKey="negativeCount" name="Negative" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
