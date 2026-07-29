import React from 'react';
import { Filter } from 'lucide-react';

interface InvestigationFiltersProps {
  filters: Record<string, string>;
  onFilterChange: (key: string, value: string) => void;
}

export const InvestigationFilters: React.FC<InvestigationFiltersProps> = ({ filters, onFilterChange }) => {
  return (
    <div className="flex flex-wrap items-center gap-4 mb-6 p-4 glass-panel">
      <div className="flex items-center gap-2 text-gray-400">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-medium">Filters:</span>
      </div>
      
      <select 
        value={filters.technique || 'all'}
        onChange={(e) => onFilterChange('technique', e.target.value)}
        className="bg-black/40 border border-white/10 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
      >
        <option value="all">All Techniques</option>
        <option value="T1566">T1566 - Phishing</option>
        <option value="T1190">T1190 - Exploit Public-Facing App</option>
        <option value="T1059">T1059 - Command and Scripting</option>
      </select>

      <select 
        value={filters.detector || 'all'}
        onChange={(e) => onFilterChange('detector', e.target.value)}
        className="bg-black/40 border border-white/10 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
      >
        <option value="all">All Detectors</option>
        <option value="regex">Regex</option>
        <option value="semantic">Semantic</option>
        <option value="fusion">Fusion</option>
      </select>

      <select 
        value={filters.severity || 'all'}
        onChange={(e) => onFilterChange('severity', e.target.value)}
        className="bg-black/40 border border-white/10 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
      >
        <option value="all">All Severities</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>

      <select 
        value={filters.source || 'all'}
        onChange={(e) => onFilterChange('source', e.target.value)}
        className="bg-black/40 border border-white/10 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
      >
        <option value="all">All Sources</option>
        <option value="user">User</option>
        <option value="pdf">PDF</option>
        <option value="api">API</option>
      </select>

      <select 
        value={filters.decision || 'all'}
        onChange={(e) => onFilterChange('decision', e.target.value)}
        className="bg-black/40 border border-white/10 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50"
      >
        <option value="all">All Decisions</option>
        <option value="blocked">Blocked</option>
        <option value="allowed">Allowed</option>
        <option value="review">Review</option>
      </select>

      <select 
        value={filters.dateRange || '24h'}
        onChange={(e) => onFilterChange('dateRange', e.target.value)}
        className="bg-black/40 border border-white/10 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary/50 ml-auto"
      >
        <option value="1h">Last Hour</option>
        <option value="24h">Last 24 Hours</option>
        <option value="7d">Last 7 Days</option>
        <option value="30d">Last 30 Days</option>
      </select>
    </div>
  );
};
