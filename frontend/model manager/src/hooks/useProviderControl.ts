import { useState } from 'react';
import { useNotifications } from './useNotifications';
import { getBackendUrl } from '../services/backendConfig';

type ProviderAction = 'start' | 'stop' | 'restart' | 'status';

interface ProviderControlResult {
  status: 'success' | 'error';
  message?: string;
  logs?: string[];
  port?: number;
  pid?: number;
}

export function useProviderControl() {
  const [isLoading, setIsLoading] = useState(false);
  const { addNotification } = useNotifications();

  const controlProvider = async (
    action: ProviderAction,
    provider: string,
    modelPath?: string
  ): Promise<ProviderControlResult> => {
    setIsLoading(true);
    
    try {
      const backendUrl = await getBackendUrl();
      const response = await fetch(`${backendUrl}/api/providers/${provider}/${action}`, {
        method: action === 'status' ? 'GET' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: action === 'start' ? JSON.stringify({ modelPath }) : undefined
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ProviderControlResult = await response.json();

      addNotification(
        result.status === 'success' ? 'success' : 'error',
        `${provider} ${action} ${result.status === 'success' ? 'successful' : 'failed'}`,
        result.message || (action === 'start' ? 'Server started in background' : ''),
        5000
      );

      return result;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      
      addNotification(
        'error',
        `${provider} ${action} failed`,
        message,
        8000
      );

      return { 
        status: 'error', 
        message,
        ...(error instanceof Error && { logs: [error.stack || ''] })
      };
    } finally {
      setIsLoading(false);
    }
  };

  return { controlProvider, isLoading };
}
