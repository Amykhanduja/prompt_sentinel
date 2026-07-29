import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { SemanticData } from '../../services/semanticApi';

interface SemanticTrendChartProps {
  data: SemanticData['similarityOverTime'] | null;
  loading: boolean;
}

export const SemanticTrendChart: React.FC<SemanticTrendChartProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-[300px] flex flex-col">
      <h3 className="text-lg font-semibold mb-6 text-white">Semantic Similarity Trend</h3>
      
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
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis 
                dataKey="timestamp" 
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} 
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                domain={[0, 1]}
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(18, 18, 26, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Area 
                type="monotone" 
                dataKey="similarity" 
                stroke="#10b981" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorTrend)" 
                activeDot={{ r: 6, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
