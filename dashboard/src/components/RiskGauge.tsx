import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';
import { DashboardData } from '../services/api';
import { motion } from 'framer-motion';

interface RiskGaugeProps {
  data: DashboardData['gauge'] | null;
  loading: boolean;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ data, loading }) => {
  const score = data?.overallRiskScore ?? 0;
  
  let color = '#10b981'; // Green (0-30)
  if (score > 30 && score <= 60) color = '#f59e0b'; // Yellow (31-60)
  else if (score > 60 && score <= 85) color = '#f97316'; // Orange (61-85)
  else if (score > 85) color = '#ef4444'; // Red (86-100)

  const chartData = [{ name: 'Risk', value: score, fill: color }];

  return (
    <div className="glass-panel p-5 h-[350px] flex flex-col relative overflow-hidden">
      {/* 3D background accent */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <h3 className="text-lg font-semibold mb-4 text-white z-10">Overall Risk Score</h3>
      
      <div className="flex-1 relative z-10">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full border-4 border-white/10 border-t-primary animate-spin"></div>
          </div>
        ) : !data ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Data Available
          </div>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <div className="w-full h-full relative" style={{ perspective: '1000px' }}>
              <motion.div 
                initial={{ rotateX: 20 }}
                animate={{ rotateX: 0 }}
                transition={{ duration: 1, type: 'spring' }}
                className="w-full h-full"
                style={{ transformStyle: 'preserve-3d' }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart 
                    cx="50%" 
                    cy="50%" 
                    innerRadius="70%" 
                    outerRadius="90%" 
                    barSize={20} 
                    data={chartData} 
                    startAngle={180} 
                    endAngle={0}
                  >
                    <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                    <RadialBar
                      background={{ fill: 'rgba(255,255,255,0.05)' }}
                      dataKey="value"
                      cornerRadius={10}
                      label={false}
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
              </motion.div>
            </div>
            <div className="absolute inset-0 flex flex-col items-center justify-center mt-12 pointer-events-none">
              <motion.span 
                key={score}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-5xl font-bold font-mono tracking-tighter"
                style={{ color, textShadow: `0 0 20px ${color}80` }}
              >
                {score.toFixed(1)}
              </motion.span>
              <span className="text-sm text-gray-400 mt-1 uppercase tracking-widest">Risk Level</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
