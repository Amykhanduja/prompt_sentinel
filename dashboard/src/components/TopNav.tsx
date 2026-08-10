
// @ts-nocheck
import React, { useState } from 'react';
import { Shield, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { ConnectionStatus } from './ConnectionStatus';
import { SearchCommand } from './SearchCommand';
import { RefreshButton } from './RefreshButton';
import { NotificationCenter } from './NotificationCenter';
import { ThemeToggle } from './ThemeToggle';
import { UserMenu } from './UserMenu';

import { useDashboardWebSocket } from '../hooks/useDashboardWebSocket';

export const TopNav: React.FC = () => {
  const [scanResult, setScanResult] = useState<any>(null);

  useDashboardWebSocket((data) => {
    // Only show if it's a new scan
    setScanResult(data);
  });

  return (
    <>
      <nav className="glass-panel sticky top-0 z-50 flex items-center justify-between px-6 py-4 mb-8 rounded-none border-t-0 border-x-0 border-b-white/10 bg-panel">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/20 rounded-lg neon-accent">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent hidden sm:block">
            PromptSentinel
          </h1>
          
          <ConnectionStatus />
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <SearchCommand />
          <RefreshButton />
          <NotificationCenter />
          <ThemeToggle />
          <div className="w-px h-6 bg-white/10 mx-1 sm:mx-2"></div>
          <UserMenu />
        </div>
      </nav>

      {/* Real-time Scan Result Modal */}
      <AnimatePresence>
        {scanResult && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="glass-panel w-full max-w-2xl bg-panel p-6 border border-white/20 shadow-2xl relative"
            >
              <button 
                onClick={() => setScanResult(null)}
                className="absolute top-4 right-4 p-1 rounded-md hover:bg-white/10 text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
              
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Shield className="w-6 h-6 text-primary" />
                Live Scan Result
              </h2>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-black/30 p-4 rounded-lg border border-white/10">
                    <p className="text-sm text-gray-400 mb-1">Action Taken</p>
                    <p className={`text-xl font-bold ${scanResult.action === 'BLOCK' ? 'text-danger' : scanResult.action === 'MONITOR' ? 'text-warning' : 'text-success'}`}>
                      {scanResult.action}
                    </p>
                  </div>
                  <div className="bg-black/30 p-4 rounded-lg border border-white/10">
                    <p className="text-sm text-gray-400 mb-1">Risk Score</p>
                    <p className="text-xl font-bold text-white">{scanResult.risk_score} <span className="text-sm font-normal text-gray-400">({scanResult.severity})</span></p>
                  </div>
                </div>

                <div className="bg-black/30 p-4 rounded-lg border border-white/10">
                  <p className="text-sm text-gray-400 font-bold mb-2">Detection</p>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Total Detections</p>
                      <p className="text-white font-medium">{scanResult.detections_count || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Source</p>
                      <p className="text-white font-medium">{scanResult.source || 'UNKNOWN'}</p>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-400 font-bold mb-2 mt-4">Obfuscation</p>
                  {scanResult.obfuscation_detected ? (
                    <div className="space-y-2 border-l-2 border-warning pl-3">
                      <div className="flex items-center gap-2 text-warning font-bold">
                        <span>Obfuscation detected</span>
                      </div>
                      
                      {scanResult.obfuscation_adjustment > 0 && (
                        <div className="text-sm text-gray-300">
                          Obfuscation risk adjustment: <span className="text-danger font-bold">+{scanResult.obfuscation_adjustment}</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-400 italic">
                      No obfuscation detected
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
