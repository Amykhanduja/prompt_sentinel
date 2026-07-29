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

export const TopNav: React.FC = () => {
  const [testPrompt, setTestPrompt] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);

  const handleScanPrompt = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && testPrompt.trim()) {
      setIsScanning(true);
      try {
        const res = await fetch('/api/v1/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: testPrompt })
        });
        const data = await res.json();
        setScanResult(data);
      } catch (err) {
        console.error("Failed to reach scanner endpoint.");
      }
      setIsScanning(false);
    }
  };

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
                <div className="bg-black/30 p-4 rounded-lg border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Prompt</p>
                  <p className="text-white font-mono text-sm">{scanResult.prompt}</p>
                </div>
                
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

                {scanResult.detections && scanResult.detections.length > 0 ? (
                  <div className="bg-danger/10 border border-danger/30 p-4 rounded-lg">
                    <p className="text-sm text-danger font-medium mb-2">Detections</p>
                    <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                      {scanResult.detections.map((det: any, idx: number) => (
                        <li key={idx}>
                          {typeof det === 'string' ? det : `${det.technique} (${det.detector})`}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="bg-success/10 border border-success/30 p-4 rounded-lg">
                    <p className="text-sm text-success font-medium flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      No threats detected. Safe to process.
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
