import React from 'react';
import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from 'next-themes';
import { motion, AnimatePresence } from 'framer-motion';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [isOpen, setIsOpen] = React.useState(false);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => setMounted(true), []);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key.toLowerCase() === 't' && !e.ctrlKey && !e.metaKey) {
        setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [resolvedTheme, setTheme]);

  if (!mounted) return null;

  return (
    <DropdownMenu.Root open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenu.Trigger asChild>
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          aria-label="Toggle theme"
        >
          <AnimatePresence mode="wait" initial={false}>
            {resolvedTheme === 'dark' ? (
              <motion.div key="dark" initial={{ opacity: 0, rotate: -90 }} animate={{ opacity: 1, rotate: 0 }} exit={{ opacity: 0, rotate: 90 }} transition={{ duration: 0.2 }}>
                <Moon className="w-4 h-4" />
              </motion.div>
            ) : (
              <motion.div key="light" initial={{ opacity: 0, rotate: -90 }} animate={{ opacity: 1, rotate: 0 }} exit={{ opacity: 0, rotate: 90 }} transition={{ duration: 0.2 }}>
                <Sun className="w-4 h-4" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>
      </DropdownMenu.Trigger>
      
      <DropdownMenu.Portal>
        <DropdownMenu.Content asChild sideOffset={8} align="end">
          <div className="radix-menu-content w-36 bg-panel border border-white/10 rounded-lg shadow-2xl overflow-hidden z-[100] backdrop-blur-xl">
            <DropdownMenu.Item asChild>
              <button onClick={() => setTheme('light')} className={`w-full outline-none text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-white/10 cursor-pointer ${theme === 'light' ? 'text-primary' : 'text-gray-300'}`}>
                <Sun className="w-4 h-4" /> Light
              </button>
            </DropdownMenu.Item>
            <DropdownMenu.Item asChild>
              <button onClick={() => setTheme('dark')} className={`w-full outline-none text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-white/10 cursor-pointer ${theme === 'dark' ? 'text-primary' : 'text-gray-300'}`}>
                <Moon className="w-4 h-4" /> Dark
              </button>
            </DropdownMenu.Item>
            <DropdownMenu.Item asChild>
              <button onClick={() => setTheme('system')} className={`w-full outline-none text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-white/10 cursor-pointer ${theme === 'system' ? 'text-primary' : 'text-gray-300'}`}>
                <Monitor className="w-4 h-4" /> System
              </button>
            </DropdownMenu.Item>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
};
