import React, { useState, useEffect } from 'react';
import { TopNav } from '../components/TopNav';
import { FileDropzone } from '../components/artifact/FileDropzone';
import { ScanProgress } from '../components/artifact/ScanProgress';
import { ScanSummary } from '../components/artifact/ScanSummary';
import { DetectionTable } from '../components/artifact/DetectionTable';
import { ExtractionTree } from '../components/artifact/ExtractionTree';
import { FileMetadata } from '../components/artifact/FileMetadata';
import { ExportPanel } from '../components/artifact/ExportPanel';
import { ScanHistory } from '../components/artifact/ScanHistory';
import { scanFile, NormalizedScanResult } from '../services/scannerApi';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

export const ArtifactScanner: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [currentResult, setCurrentResult] = useState<NormalizedScanResult | null>(null);
  const [history, setHistory] = useState<NormalizedScanResult[]>([]);

  // Timer for simulating progress steps smoothly while actual backend is processing
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (scanStatus === 'scanning') {
      const startTime = Date.now();
      interval = setInterval(() => {
        setTimeElapsed(Date.now() - startTime);
        setProgress(p => {
          // Cap simulated progress at 90% until the API returns
          if (p >= 90) return 90;
          return p + (90 - p) * 0.1;
        });
      }, 100);
    }
    return () => clearInterval(interval);
  }, [scanStatus]);

  const handleScan = async (file: File) => {
    if (isScanning) return;
    
    setIsScanning(true);
    setScanStatus('scanning');
    setProgress(0);
    setTimeElapsed(0);
    setCurrentResult(null);

    try {
      const result = await scanFile(file);
      setProgress(100);
      setScanStatus('completed');
      setCurrentResult(result);
      setHistory(prev => [result, ...prev]);
      toast.success('File scanned successfully');
    } catch (err: any) {
      setScanStatus('error');
      toast.error(err.message || 'Failed to scan file');
    } finally {
      setIsScanning(false);
    }
  };

  const handleSelectHistory = (result: NormalizedScanResult) => {
    setCurrentResult(result);
    setScanStatus('completed');
    setProgress(100);
  };

  return (
    <div className="relative w-full">
      {/* Dynamic Background Effects */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none opacity-40 mix-blend-screen z-0"></div>
      
      <div className="relative z-10 w-full px-4 pb-8 max-w-[1600px] mx-auto">
        <TopNav />
        
        <main>
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Artifact Scanner</h2>
              <p className="text-gray-400 text-sm">Deep inspection for documents, HTML, and other file types.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 flex flex-col gap-6">
              <FileDropzone onScan={handleScan} disabled={isScanning} />
              
              <ScanProgress 
                status={scanStatus} 
                progress={progress} 
                timeElapsed={timeElapsed} 
              />
              
              {currentResult && scanStatus === 'completed' && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                  <ScanSummary data={currentResult} />
                  <DetectionTable data={currentResult} />
                </motion.div>
              )}
            </div>
            
            <div className="lg:col-span-1 flex flex-col gap-6">
              {currentResult && scanStatus === 'completed' && (
                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                  <FileMetadata data={currentResult} />
                  <ExtractionTree data={currentResult} />
                  <ExportPanel data={currentResult} />
                </motion.div>
              )}
              <ScanHistory history={history} onSelect={handleSelectHistory} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ArtifactScanner;
