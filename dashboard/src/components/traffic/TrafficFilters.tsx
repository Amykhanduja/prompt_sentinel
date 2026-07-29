import React from 'react';
import { Filter } from 'lucide-react';

interface TrafficFiltersProps {
  sourceFilter: string;
  onSourceFilterChange: (source: string) => void;
}

export const TrafficFilters: React.FC<TrafficFiltersProps> = ({ sourceFilter, onSourceFilterChange }) => {
  const sources = [
    { id: 'all', label: 'All Sources' },
    { id: 'user', label: 'User Input' },
    { id: 'pdf', label: 'PDF' },
    { id: 'docx', label: 'DOCX' },
    { id: 'html', label: 'HTML' },
    { id: 'email', label: 'Email' },
    { id: 'website', label: 'Website' },
    { id: 'api', label: 'API Response' },
    { id: 'zip', label: 'ZIP' },
    { id: 'ocr', label: 'OCR' },
  ];

  return (
    <div className="flex items-center gap-3 mb-6">
      <div className="flex items-center gap-2 text-gray-400">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-medium">Filters:</span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {sources.map((source) => (
          <button
            key={source.id}
            onClick={() => onSourceFilterChange(source.id)}
            className={`px-3 py-1.5 text-xs font-medium rounded-full transition-all border ${
              sourceFilter === source.id
                ? 'bg-primary/20 text-primary border-primary/50 shadow-[0_0_10px_rgba(59,130,246,0.2)]'
                : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-gray-200'
            }`}
          >
            {source.label}
          </button>
        ))}
      </div>
    </div>
  );
};
