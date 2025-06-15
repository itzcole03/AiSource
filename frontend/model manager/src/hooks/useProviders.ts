import { useState, useEffect, useCallback } from 'react';
import { Provider, Model } from '../types';
import { OllamaService } from '../services/ollama';
import { VLLMService } from '../services/vllm';
import { LMStudioService } from '../services/lmstudio';
import { ServerManagerService } from '../services/serverManager';
import { getCachedBackendUrl, resetBackendUrlCache } from '../services/backendConfig';

const ollamaService = new OllamaService();
const vllmService = new VLLMService();
const lmstudioService = new LMStudioService();
const serverManager = new ServerManagerService();

export const useProviders = () => {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProviderData = useCallback(async () => {
    // Get backend status with enhanced error handling
    let backendStatus: any = { providers: {} };
    try {
      const backendUrl = await getCachedBackendUrl();
      const response = await fetch(`${backendUrl}/providers/status`, {
        signal: AbortSignal.timeout(8000)
      });
      if (response.ok) {
        const statusData = await response.json();
        backendStatus = statusData; // This should have a .providers property
        console.log('✅ Backend status retrieved:', backendStatus);
      } else {
        console.warn(`Backend status request failed: ${response.status}`);
        resetBackendUrlCache(); // Reset cache on error
      }
    } catch (error) {
      console.warn('Could not fetch backend status:', error);
      resetBackendUrlCache(); // Reset cache on error
    }

    const providerPromises = [
      // Ollama
      (async () => {
        try {
          // Check backend status first, fallback to direct health check
          const backendRunning = backendStatus.providers?.ollama?.status === 'running';
          const isHealthy = backendRunning || await ollamaService.checkHealth();
          
          if (!isHealthy) {
            return {
              id: 'ollama',
              name: 'ollama' as const,
              displayName: 'Ollama',
              status: 'disconnected' as const,
              apiUrl: 'http://localhost:11434',
              capabilities: ['Chat', 'Embeddings', 'Code Generation', 'Local Models'],
              models: [],
              serverStatus: 'stopped' as const,
            };
          }

          const [version, availableModels, runningModels] = await Promise.allSettled([
            ollamaService.getVersion(),
            ollamaService.listModels(),
            ollamaService.getRunningModels(),
          ]);

          // Merge available and running models with error handling
          const allModels: Model[] = [];
          
          if (availableModels.status === 'fulfilled') {
            allModels.push(...availableModels.value);
          }
          
          if (runningModels.status === 'fulfilled') {
            runningModels.value.forEach((runningModel: Model) => {
              const existingIndex = allModels.findIndex(m => m.id === runningModel.id);
              if (existingIndex >= 0) {
                allModels[existingIndex] = runningModel;
              } else {
                allModels.push(runningModel);
              }
            });
          }

          return {
            id: 'ollama',
            name: 'ollama' as const,
            displayName: 'Ollama',
            status: 'connected' as const,
            version: version.status === 'fulfilled' ? version.value : undefined,
            apiUrl: 'http://localhost:11434',
            capabilities: ['Chat', 'Embeddings', 'Code Generation', 'Local Models'],
            models: allModels,
            serverStatus: 'running' as const,
          };
        } catch (error) {
          console.error('Ollama error:', error);
          return {
            id: 'ollama',
            name: 'ollama' as const,
            displayName: 'Ollama',
            status: 'error' as const,
            apiUrl: 'http://localhost:11434',
            capabilities: ['Chat', 'Embeddings', 'Code Generation', 'Local Models'],
            models: [],
            serverStatus: 'error' as const,
          };
        }
      })(),

      // vLLM
      (async () => {
        try {
          // Check backend status first, fallback to direct health check
          const backendRunning = backendStatus.providers?.vllm?.status === 'running';
          const isHealthy = backendRunning || await vllmService.checkHealth();
          
          if (!isHealthy) {
            return {
              id: 'vllm',
              name: 'vllm' as const,
              displayName: 'vLLM',
              status: 'disconnected' as const,
              apiUrl: 'http://localhost:8000',
              capabilities: ['High-throughput Inference', 'Batching', 'Streaming', 'OpenAI Compatible'],
              models: [],
              serverStatus: 'stopped' as const,
            };
          }

          const [version, models] = await Promise.allSettled([
            vllmService.getVersion(),
            vllmService.listModels(),
          ]);

          return {
            id: 'vllm',
            name: 'vllm' as const,
            displayName: 'vLLM',
            status: 'connected' as const,
            version: version.status === 'fulfilled' ? version.value : undefined,
            apiUrl: 'http://localhost:8000',
            capabilities: ['High-throughput Inference', 'Batching', 'Streaming', 'OpenAI Compatible'],
            models: models.status === 'fulfilled' ? models.value : [],
            serverStatus: 'running' as const,
          };
        } catch (error) {
          console.error('vLLM error:', error);
          return {
            id: 'vllm',
            name: 'vllm' as const,
            displayName: 'vLLM',
            status: 'error' as const,
            apiUrl: 'http://localhost:8000',
            capabilities: ['High-throughput Inference', 'Batching', 'Streaming', 'OpenAI Compatible'],
            models: [],
            serverStatus: 'error' as const,
          };
        }
      })(),

      // LM Studio
      (async () => {
        try {
          // Check backend status first - trust backend completely for LM Studio
          const backendRunning = backendStatus.providers?.lmstudio?.status === 'running';
          
          if (!backendRunning) {
            console.log('⚠️ LM Studio not detected by backend, marking as disconnected');
            return {
              id: 'lmstudio',
              name: 'lmstudio' as const,
              displayName: 'LM Studio',
              status: 'disconnected' as const,
              apiUrl: 'http://localhost:1234',
              capabilities: ['Local Models', 'Chat Interface', 'Model Quantization', 'OpenAI Compatible'],
              models: [],
              serverStatus: 'stopped' as const,
            };
          }

          // If backend detects LM Studio, fetch models via backend proxy
          console.log('✅ LM Studio detected by backend, fetching models via proxy...');
          const modelCount = backendStatus.providers?.lmstudio?.models || 0;
          
          const [models] = await Promise.allSettled([
            lmstudioService.listModels(),
          ]);

          let allModels: Model[] = [];
          if (models.status === 'fulfilled') {
            allModels = models.value;
            console.log(`✅ Retrieved ${allModels.length} LM Studio models via backend proxy`);
          } else {
            console.warn('❌ Failed to fetch LM Studio models:', models.reason);
            // Create placeholder models based on backend count
            for (let i = 0; i < modelCount; i++) {
              allModels.push({
                id: `model-${i + 1}`,
                name: `LM Studio Model ${i + 1}`,
                provider: 'lmstudio' as const,
                size: 'Unknown',
                status: 'available' as const,
              });
            }
          }

          return {
            id: 'lmstudio',
            name: 'lmstudio' as const,
            displayName: 'LM Studio',
            status: 'connected' as const,
            version: 'Backend Detected',
            apiUrl: 'http://localhost:1234',
            capabilities: ['Local Models', 'Chat Interface', 'Model Quantization', 'OpenAI Compatible'],
            models: allModels,
            serverStatus: 'running' as const,
          };
        } catch (error) {
          console.error('LM Studio error:', error);
          return {
            id: 'lmstudio',
            name: 'lmstudio' as const,
            displayName: 'LM Studio',
            status: 'error' as const,
            apiUrl: 'http://localhost:1234',
            capabilities: ['Local Models', 'Chat Interface', 'Model Quantization', 'OpenAI Compatible'],
            models: [],
            serverStatus: 'error' as const,
          };
        }
      })(),
    ];

    return Promise.all(providerPromises);
  }, []);

  const refreshProviders = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const providerData = await loadProviderData();
      setProviders(providerData);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load providers';
      setError(errorMessage);
      console.error('Failed to refresh providers:', error);
    } finally {
      setLoading(false);
    }
  }, [loadProviderData]);

  const handleServerAction = useCallback(async (providerId: string, action: 'start' | 'stop' | 'restart', modelName?: string) => {
    // Update provider status to show loading state
    setProviders(prev => prev.map(p => 
      p.id === providerId 
        ? { ...p, status: action === 'start' ? 'starting' : action === 'stop' ? 'stopping' : 'starting' }
        : p
    ));

    try {
      const provider = providers.find(p => p.id === providerId);
      if (!provider) {
        throw new Error(`Provider with ID ${providerId} not found`);
      }

      const result = await serverManager.executeServerCommand({
        provider: provider.name as 'ollama' | 'vllm' | 'lmstudio',
        action,
        modelName
      });

      if (result.success) {
        console.log('✅ Server action successful:', result.message);
        
        // Refresh providers after a delay to allow server to start/stop
        setTimeout(() => {
          refreshProviders();
        }, action === 'start' ? 4000 : 1500);
      } else {
        setError(result.message);
        // Revert status on error
        setProviders(prev => prev.map(p => 
          p.id === providerId 
            ? { ...p, status: 'error' }
            : p
        ));
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Server action failed';
      setError(errorMessage);
      
      // Revert status on error
      setProviders(prev => prev.map(p => 
        p.id === providerId 
          ? { ...p, status: 'error' }
          : p
      ));
    }
  }, [refreshProviders]);

  const startModel = useCallback(async (providerId: string, modelId: string) => {
    const provider = providers.find(p => p.id === providerId);
    if (!provider) {
      throw new Error(`Provider with ID ${providerId} not found`);
    }

    // Update model status to loading
    setProviders(prev => prev.map(p => ({
      ...p,
      models: p.models.map(m => 
        m.id === modelId ? { ...m, status: 'loading' as const } : m
      )
    })));

    try {
      switch (provider.name) {
        case 'ollama':
          await ollamaService.startModel(modelId);
          break;
        case 'vllm':
          await vllmService.startModel(modelId);
          break;
        case 'lmstudio':
          await lmstudioService.startModel(modelId);
          break;
      }

      // Refresh to get updated status
      setTimeout(() => refreshProviders(), 3000);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to start model');
      
      // Revert status on error
      setProviders(prev => prev.map(p => ({
        ...p,
        models: p.models.map(m => 
          m.id === modelId ? { ...m, status: 'error' as const } : m
        )
      })));
    }
  }, [providers, refreshProviders]);

  const stopModel = useCallback(async (providerId: string, modelId: string) => {
    const provider = providers.find(p => p.id === providerId);
    if (!provider) {
      throw new Error(`Provider with ID ${providerId} not found`);
    }

    try {
      switch (provider.name) {
        case 'ollama':
          await ollamaService.stopModel(modelId);
          break;
        case 'vllm':
          await vllmService.stopModel(modelId);
          break;
        case 'lmstudio':
          await lmstudioService.stopModel(modelId);
          break;
      }

      // Update model status immediately
      setProviders(prev => prev.map(p => ({
        ...p,
        models: p.models.map(m => 
          m.id === modelId 
            ? { ...m, status: 'available' as const, uptime: undefined, memoryUsage: undefined }
            : m
        )
      })));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to stop model');
    }
  }, [providers]);

  // Initial load with delay to avoid simultaneous requests
  useEffect(() => {
    const timeout = setTimeout(() => {
      refreshProviders();
    }, 1000);
    return () => clearTimeout(timeout);
  }, [refreshProviders]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(refreshProviders, 30000);
    return () => clearInterval(interval);
  }, [refreshProviders]);

  // Update uptime for running models
  useEffect(() => {
    const interval = setInterval(() => {
      setProviders(prev => prev.map(provider => ({
        ...provider,
        models: provider.models.map(model => 
          model.status === 'running' && model.uptime !== undefined
            ? { ...model, uptime: model.uptime + 1 }
            : model
        )
      })));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    providers,
    loading,
    error,
    refreshProviders,
    startModel,
    stopModel,
    handleServerAction,
  };
};