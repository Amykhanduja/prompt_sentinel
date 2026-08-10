import { useEffect, useRef, useCallback } from 'react';

type WebSocketEvent = {
  event: string;
  data: any;
};

export const useDashboardWebSocket = (
  onScanCompleted: (data: any) => void,
  onReconnect?: () => void
) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use the current host to derive the WS URL, as REST APIs use relative paths
    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
    
    console.log('[WebSocket] Connecting to', wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('[WebSocket] Connected');
      const wasReconnecting = reconnectTimeout.current !== null;
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
      if (wasReconnecting && onReconnect) {
        onReconnect();
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const message: WebSocketEvent = JSON.parse(event.data);
        if (message.event === 'scan_completed') {
          console.log('[WebSocket] scan_completed received');
          onScanCompleted(message.data);
        }
      } catch (err) {
        // safely ignore malformed JSON
        console.error('[WebSocket] Failed to parse message', err);
      }
    };

    ws.current.onclose = () => {
      console.log('[WebSocket] Disconnected');
      ws.current = null;
      // Reconnect with delay
      reconnectTimeout.current = setTimeout(() => {
        console.log('[WebSocket] Reconnecting...');
        connect();
      }, 5000);
    };

    ws.current.onerror = () => {
      // Browser handles emitting close event after error, so cleanup is done in onclose
    };
  }, [onScanCompleted]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        // Prevent onclose from attempting reconnection during unmount
        ws.current.onclose = null;
        ws.current.close();
        ws.current = null;
      }
    };
  }, [connect]);
};
