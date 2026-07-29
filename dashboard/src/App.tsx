// @ts-nocheck
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'sonner';

import { Sidebar } from './components/Sidebar';
import { DashboardOverview } from './pages/DashboardOverview';
import ArtifactScanner from './pages/ArtifactScanner';
import TrafficAnalytics from './pages/TrafficAnalytics';
import DetectionAnalytics from './pages/DetectionAnalytics';
import SemanticAnalytics from './pages/SemanticAnalytics';
import RiskPolicyAnalytics from './pages/RiskPolicyAnalytics';
import SourceAnalytics from './pages/SourceAnalytics';
import KnowledgeAnalytics from './pages/KnowledgeAnalytics';
import InvestigationCenter from './pages/InvestigationCenter';
import SystemHealth from './pages/SystemHealth';

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <Router>
        <div className="flex min-h-screen bg-background relative text-gray-200 font-sans transition-colors duration-300">
          <Toaster theme="system" richColors position="bottom-right" />
        {/* Global Grid Pattern overlay */}
        <div className="fixed inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none z-0"></div>

        <Sidebar />
        
        <div className="flex-1 flex flex-col h-screen overflow-y-auto relative z-10">
          <Routes>
            <Route path="/" element={<DashboardOverview />} />
            <Route path="/artifact-scanner" element={<ArtifactScanner />} />
            <Route path="/traffic" element={<TrafficAnalytics />} />
            <Route path="/detections" element={<DetectionAnalytics />} />
            <Route path="/semantic" element={<SemanticAnalytics />} />
            <Route path="/risk-policy" element={<RiskPolicyAnalytics />} />
            <Route path="/sources" element={<SourceAnalytics />} />
            <Route path="/knowledge" element={<KnowledgeAnalytics />} />
            <Route path="/investigations" element={<InvestigationCenter />} />
            <Route path="/system" element={<SystemHealth />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
