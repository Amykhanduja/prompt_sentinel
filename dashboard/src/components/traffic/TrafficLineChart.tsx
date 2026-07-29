import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrafficData } from '../../services/trafficApi';

interface TrafficLineChartProps {
  data: TrafficData['trafficOverTime'] | null;
  loading: boolean;
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
}

export const TrafficLineChart: React.FC<TrafficLineChartProps> = ({ data, loading, timeRange, onTimeRangeChange }) => {
  const hasData = data && data.length > 0;

  return (
    <div className="glass-panel p-5 h-[400px] flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-white">Prompt Traffic Over Time</h3>
        <div className="flex bg-black/40 rounded-lg p-1 border border-white/10">
          {['1h', '24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => onTimeRangeChange(range)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                timeRange === range 
                  ? 'bg-primary text-white shadow-[0_0_10px_rgba(59,130,246,0.3)]' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {range === '1h' ? 'Last Hour' : range === '24h' ? 'Last 24 Hours' : range === '7d' ? 'Last 7 Days' : 'Last 30 Days'}
            </button>
          ))}
        </div>
      </div>
      
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
                <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
              <XAxis 
                dataKey="timestamp" 
                stroke="rgba(255,255,255,0.3)" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} 
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
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
                dataKey="requests" 
                stroke="#3b82f6" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorRequests)" 
                activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
