import React from 'react';
import { User, Settings, Palette, BookOpen, GitBranch, LogOut } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { useAuth } from '../context/AuthContext';

export const UserMenu: React.FC = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      logout();
      window.location.href = '/login';
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <DropdownMenu.Root open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenu.Trigger asChild>
        <button 
          className="flex items-center gap-2 p-1 pl-2 pr-3 rounded-full hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 focus:outline-none focus:ring-2 focus:ring-primary"
          aria-label="User menu"
        >
          <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-primary to-purple-500 flex items-center justify-center shadow-lg">
            <User className="w-3 h-3 text-white" />
          </div>
          <span className="text-sm text-gray-300 font-medium hidden sm:block">{user?.username || 'User'}</span>
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content asChild sideOffset={8} align="end">
          <div className="radix-menu-content w-56 bg-panel border border-white/10 rounded-lg shadow-2xl overflow-hidden z-[100] backdrop-blur-xl">
            <div className="px-4 py-3 border-b border-white/10 bg-black/20">
              <p className="text-sm font-medium text-white">{user?.username || 'User'}</p>
              <p className="text-xs text-gray-400">{user?.email || ''}</p>
            </div>
            <div className="py-1">
              <DropdownMenu.Item asChild>
                <a href="#profile" className="outline-none flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors cursor-pointer">
                  <User className="w-4 h-4" /> Profile
                </a>
              </DropdownMenu.Item>
              <DropdownMenu.Item asChild>
                <a href="#settings" className="outline-none flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors cursor-pointer">
                  <Settings className="w-4 h-4" /> Settings
                </a>
              </DropdownMenu.Item>
              <DropdownMenu.Item asChild>
                <a href="#appearance" className="outline-none flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors cursor-pointer">
                  <Palette className="w-4 h-4" /> Appearance
                </a>
              </DropdownMenu.Item>
            </div>
            <div className="py-1 border-t border-white/10">
              <DropdownMenu.Item asChild>
                <a href="https://github.com" target="_blank" rel="noreferrer" className="outline-none flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors cursor-pointer">
                  <BookOpen className="w-4 h-4" /> Documentation
                </a>
              </DropdownMenu.Item>
              <DropdownMenu.Item asChild>
                <a href="https://github.com" target="_blank" rel="noreferrer" className="outline-none flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors cursor-pointer">
                  <GitBranch className="w-4 h-4" /> GitHub
                </a>
              </DropdownMenu.Item>
            </div>
            <div className="py-1 border-t border-white/10">
              <DropdownMenu.Item asChild>
                <button 
                  onClick={handleLogout} 
                  className="outline-none w-full flex items-center gap-3 px-4 py-2 text-sm text-danger hover:bg-danger/10 transition-colors cursor-pointer"
                >
                  <LogOut className="w-4 h-4" /> Logout
                </button>
              </DropdownMenu.Item>
            </div>
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
};

