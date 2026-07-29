import React from 'react';
import { Search, Terminal, AlertTriangle, Shield, Book, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const SearchCommand: React.FC = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [query, setQuery] = React.useState('');
  const [debouncedQuery, setDebouncedQuery] = React.useState('');
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Debounce logic
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Global shortcut
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Auto-focus input when opened
  React.useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const mockResults = debouncedQuery.length > 1 ? [
    { type: 'technique', title: 'PT-009: Instruction Override', icon: <Terminal className="w-4 h-4 text-primary" /> },
    { type: 'detection', title: 'Critical Event: System Prompt Extraction', icon: <AlertTriangle className="w-4 h-4 text-danger" /> },
    { type: 'kb', title: 'How to block markdown injections', icon: <Book className="w-4 h-4 text-info" /> },
    { type: 'history', title: 'ignore previous instructions...', icon: <Clock className="w-4 h-4 text-gray-400" /> },
  ].filter(r => r.title.toLowerCase().includes(debouncedQuery.toLowerCase())) : [];

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="hidden md:flex items-center gap-2 bg-black/50 border border-white/10 rounded-full pl-3 pr-4 py-1.5 text-sm hover:border-primary/50 hover:ring-1 hover:ring-primary/50 transition-all w-64 text-gray-400 focus:outline-none"
      >
        <Search className="w-4 h-4" />
        <span className="flex-1 text-left">Search everything...</span>
        <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-sans font-medium text-gray-400 bg-white/10 rounded border border-white/5">Ctrl+K</kbd>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-start justify-center pt-32 bg-black/60 backdrop-blur-sm p-4"
          >
            <motion.div
              initial={{ scale: 0.95, y: -20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: -20 }}
              className="w-full max-w-2xl bg-panel border border-white/10 shadow-2xl rounded-xl overflow-hidden flex flex-col"
            >
              <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10 bg-black/20">
                <Search className="w-5 h-5 text-gray-400" />
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Search techniques, detections, history..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500 text-lg"
                />
                <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-xs font-sans font-medium text-gray-400 bg-white/10 rounded border border-white/5">ESC</kbd>
              </div>

              <div className="max-h-96 overflow-y-auto p-2">
                {query.length === 0 ? (
                  <div className="p-8 text-center text-sm text-gray-500 flex flex-col items-center gap-2">
                    <Shield className="w-8 h-8 opacity-20" />
                    <p>Start typing to search your workspace.</p>
                  </div>
                ) : mockResults.length > 0 ? (
                  <div className="space-y-1">
                    {mockResults.map((res, idx) => (
                      <button 
                        key={idx}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/10 text-left transition-colors focus:bg-white/10 focus:outline-none"
                      >
                        {res.icon}
                        <span className="text-sm text-gray-200">{res.title}</span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-sm text-gray-500">
                    No results found for "{query}"
                  </div>
                )}
              </div>
            </motion.div>
            <div className="fixed inset-0 z-[-1]" onClick={() => setIsOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
