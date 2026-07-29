import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { SourceData } from '../../services/sourceApi';

interface SourceBenignMaliciousChartProps {
  data: SourceData['benignVsMaliciousBySource'] | null;
  loading: boolean;
}

export const SourceBenignMaliciousChart: React.FC<SourceBenignMaliciousChartProps> = ({ data, loading }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-[350px] flex flex-col">
      <h3 className="text-lg font-semibold mb-6 text-white">Benign vs Malicious by Source</h3>
      
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
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={true} vertical={false} />
              <XAxis 
                type="number" 
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                dataKey="source" 
                type="category" 
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <Tooltip 
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                contentStyle={{ backgroundColor: 'rgba(18, 18, 26, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Bar dataKey="malicious" name="Malicious" stackId="a" fill="#ef4444" />
              <Bar dataKey="benign" name="Benign" stackId="a" fill="#10b981" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
