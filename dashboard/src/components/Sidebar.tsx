import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ActivitySquare, ShieldAlert, BrainCircuit, Scale, Target, Library, Search, Server } from 'lucide-react';
import { motion } from 'framer-motion';

export const Sidebar: React.FC = () => {
  const routes = [
    { path: '/', name: 'Overview', icon: LayoutDashboard },
    { path: '/traffic', name: 'Traffic Analytics', icon: ActivitySquare },
    { path: '/detections', name: 'Detections', icon: ShieldAlert },
    { path: '/semantic', name: 'Semantic Analysis', icon: BrainCircuit },
    { path: '/risk-policy', name: 'Risk & Policy', icon: Scale },
    { path: '/sources', name: 'Source Analytics', icon: Target },
    { path: '/knowledge', name: 'Knowledge Base', icon: Library },
    { path: '/investigations', name: 'Investigation Center', icon: Search },
    { path: '/system', name: 'System Health', icon: Server },
  ];

  return (
    <div className="w-64 h-screen bg-black/60 border-r border-white/10 backdrop-blur-xl flex flex-col z-50 sticky top-0 shrink-0">
      <div className="p-6 flex items-center gap-3 border-b border-white/5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.5)]">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <h1 className="text-white font-bold tracking-wider">PROMPT<span className="text-primary font-light">SENTINEL</span></h1>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6 px-3 space-y-2 custom-scrollbar">
        {routes.map((route, i) => (
          <NavLink
            key={route.path}
            to={route.path}
            className={({ isActive }) => 
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative overflow-hidden ${
                isActive 
                  ? 'bg-primary/20 text-white shadow-[0_0_10px_rgba(168,85,247,0.2)] border border-primary/30' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <motion.div 
                    layoutId="active-nav-glow"
                    className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent pointer-events-none"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <route.icon className={`w-5 h-5 transition-colors relative z-10 ${isActive ? 'text-primary' : 'text-gray-500 group-hover:text-gray-300'}`} />
                <span className="font-medium text-sm relative z-10">{route.name}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
      
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-3 bg-black/40 p-3 rounded-xl border border-white/5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold text-xs shadow-inner">
            AK
          </div>
          <div className="flex flex-col">
            <span className="text-white text-xs font-medium">Amy Khanduja</span>
            <span className="text-gray-500 text-[10px] uppercase tracking-wider">SecOps Lead</span>
          </div>
        </div>
      </div>
    </div>
  );
};
