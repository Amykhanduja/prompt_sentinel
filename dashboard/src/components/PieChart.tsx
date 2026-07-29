import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { DashboardData } from '../services/api';

interface DecisionsPieChartProps {
  data: DashboardData['decisions'] | null;
  loading: boolean;
}

const COLORS = ['#ef4444', '#10b981', '#f59e0b']; // Danger (Blocked), Success (Allowed), Warning (Review)

export const DecisionsPieChart: React.FC<DecisionsPieChartProps> = ({ data, loading }) => {
  const chartData = data ? [
    { name: 'Blocked', value: data.blocked },
    { name: 'Allowed', value: data.allowed },
    { name: 'Review', value: data.review },
  ] : [];

  const hasData = chartData.some(item => item.value > 0);

  return (
    <div className="glass-panel p-5 h-[350px] flex flex-col">
      <h3 className="text-lg font-semibold mb-4 text-white">Action Decisions</h3>
      
      <div className="flex-1 relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full border-4 border-white/10 border-t-primary animate-spin"></div>
          </div>
        ) : !data || !hasData ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                stroke="rgba(0,0,0,0)"
                labelLine={false}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(18, 18, 26, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
