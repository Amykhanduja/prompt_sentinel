import React from 'react';
import { Bell, Trash2, CheckCircle2, AlertTriangle, Info, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';
import * as Popover from '@radix-ui/react-popover';

interface Notification {
  id: string;
  timestamp: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  message: string;
  read: boolean;
  category: string;
}

export const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  
  const { data, isLoading, isError } = useQuery<Notification[]>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await fetch('/api/v1/dashboard/notifications');
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    },
    refetchInterval: 15000,
  });

  const [localNotifs, setLocalNotifs] = React.useState<Notification[]>([]);
  
  React.useEffect(() => {
    if (data) {
      setLocalNotifs(data);
    }
  }, [data]);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key.toLowerCase() === 'n' && !e.ctrlKey && !e.metaKey) {
        setIsOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  const unreadCount = localNotifs.filter(n => !n.read).length;

  const markAllAsRead = () => {
    setLocalNotifs(prev => prev.map(n => ({ ...n, read: true })));
    toast.success('All notifications marked as read');
  };

  const clearAll = () => {
    setLocalNotifs([]);
    toast.success('All notifications cleared');
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'low': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };
  
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'high': return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'low': return <Info className="w-4 h-4 text-blue-500" />;
      default: return <Info className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <Popover.Root open={isOpen} onOpenChange={setIsOpen}>
      <Popover.Trigger asChild>
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors relative focus:outline-none focus:ring-2 focus:ring-primary"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 flex items-center justify-center w-4 h-4 text-[10px] font-bold text-white bg-danger rounded-full shadow-[0_0_8px_#ef4444]">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </motion.button>
      </Popover.Trigger>
      
      <Popover.Portal>
        <Popover.Content asChild sideOffset={8} align="end">
          <div
            className="radix-menu-content w-80 sm:w-96 bg-panel border border-white/10 rounded-xl shadow-2xl overflow-hidden z-[100] backdrop-blur-xl flex flex-col"
            style={{ maxHeight: 'calc(100vh - 100px)' }}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/20">
              <h3 className="font-semibold text-gray-200">Notifications</h3>
              <div className="flex items-center gap-2">
                <button 
                  onClick={markAllAsRead} 
                  title="Mark all as read"
                  className="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                >
                  <CheckCircle2 className="w-4 h-4" />
                </button>
                <button 
                  onClick={clearAll}
                  title="Clear all"
                  className="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="overflow-y-auto flex-1 p-2 space-y-2 min-h-[300px]">
              {isLoading && <div className="p-4 text-center text-sm text-gray-400">Loading notifications...</div>}
              {isError && <div className="p-4 text-center text-sm text-gray-400">No notifications available.</div>}
              {!isLoading && !isError && localNotifs.length === 0 && (
                <div className="p-8 text-center text-sm text-gray-400 flex flex-col items-center gap-2">
                  <Bell className="w-8 h-8 opacity-20" />
                  <p>You're all caught up!</p>
                </div>
              )}
              
              {!isLoading && !isError && localNotifs.map(n => (
                <div 
                  key={n.id} 
                  className={`p-3 rounded-lg border flex gap-3 transition-colors cursor-pointer ${getSeverityColor(n.severity)} ${!n.read ? 'opacity-100' : 'opacity-60 bg-transparent'}`}
                  onClick={() => setLocalNotifs(prev => prev.map(x => x.id === n.id ? { ...x, read: true } : x))}
                >
                  <div className="mt-0.5">{getSeverityIcon(n.severity)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start mb-1">
                      <h4 className="text-sm font-medium truncate pr-2 text-gray-100">{n.title}</h4>
                      <span className="text-[10px] whitespace-nowrap text-gray-400">
                        {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 line-clamp-2">{n.message}</p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="p-2 border-t border-white/10 bg-black/20 text-center">
              <button className="text-xs text-primary hover:text-primary/80 font-medium">
                View all activity
              </button>
            </div>
          </div>
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
};

