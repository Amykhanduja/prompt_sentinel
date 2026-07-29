import React from 'react';
import { Filter } from 'lucide-react';

interface KnowledgeFiltersProps {
  filters: Record<string, string>;
  onFilterChange: (key: string, value: string) => void;
}

export const KnowledgeFilters: React.FC<KnowledgeFiltersProps> = ({ filters, onFilterChange }) => {
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
    </div>
  );
};
