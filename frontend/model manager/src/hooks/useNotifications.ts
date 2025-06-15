import { useState, useCallback } from 'react';
import { NotificationState } from '../types';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<NotificationState[]>([]);

  const addNotification = useCallback((
    type: NotificationState['type'],
    title: string,
    message: string,
    duration: number = 5000
  ) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const notification: NotificationState = {
      id,
      type,
      title,
      message,
      timestamp: new Date(),
      duration
    };

    setNotifications(prev => [...prev, notification]);
    return id;
  }, []);

  const dismissNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const notifySuccess = useCallback((title: string, message: string, duration?: number) => {
    return addNotification('success', title, message, duration);
  }, [addNotification]);

  const notifyError = useCallback((title: string, message: string, duration?: number) => {
    return addNotification('error', title, message, duration);
  }, [addNotification]);

  const notifyWarning = useCallback((title: string, message: string, duration?: number) => {
    return addNotification('warning', title, message, duration);
  }, [addNotification]);

  const notifyInfo = useCallback((title: string, message: string, duration?: number) => {
    return addNotification('info', title, message, duration);
  }, [addNotification]);

  return {
    notifications,
    addNotification,
    dismissNotification,
    clearAllNotifications,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo
  };
};