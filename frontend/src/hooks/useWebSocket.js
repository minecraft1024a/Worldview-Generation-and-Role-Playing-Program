import { useState, useEffect, useCallback } from 'react';
import webSocketService from '../services/websocket';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);

  const connect = useCallback(async () => {
    try {
      await webSocketService.connect();
      setIsConnected(true);
      setError(null);
    } catch (err) {
      setError(err.message);
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    webSocketService.disconnect();
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((type, data) => {
    try {
      webSocketService.send(type, data);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  const addMessageListener = useCallback((type, callback) => {
    webSocketService.on(type, callback);
    return () => webSocketService.off(type, callback);
  }, []);

  useEffect(() => {
    // 监听连接状态变化
    const handleConnectionChange = () => {
      setIsConnected(webSocketService.isConnected);
    };

    const handleError = (data) => {
      setError(data.message || 'WebSocket error');
    };

    const handleMaxReconnect = () => {
      setError('连接失败，请刷新页面重试');
    };

    webSocketService.on('error', handleError);
    webSocketService.on('max_reconnect_reached', handleMaxReconnect);

    return () => {
      webSocketService.off('error', handleError);
      webSocketService.off('max_reconnect_reached', handleMaxReconnect);
    };
  }, []);

  return {
    isConnected,
    error,
    messages,
    connect,
    disconnect,
    sendMessage,
    addMessageListener
  };
};
