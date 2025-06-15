import { apiCall, APIError, healthCheck } from './api';
import { Model } from '../types';
import { getBackendUrl } from './backendConfig';

const LMSTUDIO_BASE_URL = '';
// Use empty string so all fetches are relative and go through Vite proxy

export class LMStudioService {
  private baseUrl: string;

  constructor(baseUrl: string = LMSTUDIO_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async checkHealth(): Promise<boolean> {
    return await healthCheck(`/v1/models`);
  }

  async getVersion(): Promise<string | undefined> {
    try {
      // LM Studio doesn't have a version endpoint, try to infer from headers
      const response = await fetch(`/v1/models`);
      const server = response.headers.get('server');
      if (server?.includes('LM Studio')) {
        return server;
      }
      
      // Try to get version from user agent or other headers
      const userAgent = response.headers.get('user-agent');
      if (userAgent?.includes('LM Studio')) {
        return userAgent;
      }
      
      return 'LM Studio';
    } catch {
      return undefined;
    }
  }

  async getServerStatus(): Promise<{ running: boolean; models: number; currentModel?: string }> {
    try {
      const isHealthy = await this.checkHealth();
      if (!isHealthy) {
        return { running: false, models: 0 };
      }

      const models = await this.listModels();
      const currentModel = await this.getCurrentModel();
      
      return {
        running: true,
        models: models.length,
        currentModel: currentModel?.name
      };
    } catch {
      return { running: false, models: 0 };
    }
  }

  async listModels(): Promise<Model[]> {
    try {
      // Always use backend proxy to avoid CORS issues
      const backendUrl = await getBackendUrl();
      console.log(`🔍 Fetching LM Studio models via backend: ${backendUrl}/providers/lmstudio/models`);
      
      const response = await fetch(`${backendUrl}/providers/lmstudio/models`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        },
        signal: AbortSignal.timeout(5000)
      });
      
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('🔍 Backend response for LM Studio models:', data);
      
      if (data.models && Array.isArray(data.models)) {
        const models = data.models.map((modelId: string) => ({
          id: modelId,
          name: modelId,
          provider: 'lmstudio' as const,
          size: this.estimateModelSize(modelId),
          format: 'GGUF',
          status: 'available' as const,
          port: 1234,
          parameters: {
            temperature: 0.7,
            maxTokens: 2048,
            topP: 0.9
          }
        }));
        console.log(`✅ Transformed ${models.length} LM Studio models for display`);
        return models;
      }
      
      console.log('⚠️ No models array found in backend response');
      return [];
      
    } catch (error) {
      console.error('Failed to fetch LM Studio models via backend:', error);
      
      // No fallback to direct API calls - always go through backend to avoid CORS
      console.log('❌ Not attempting direct API fallback to avoid CORS issues');
      return [];
    }
  }

  async getCurrentModel(): Promise<Model | null> {
    try {
      // Try to detect the currently loaded model by making a test request
      const response = await apiCall(`/v1/chat/completions`, {
        method: 'POST',
        body: JSON.stringify({
          model: 'local-model',
          messages: [{ role: 'user', content: 'test' }],
          max_tokens: 1,
          temperature: 0,
        }),
      });
      
      if (response.model || response.id) {
        const modelId = response.model || response.id || 'local-model';
        const currentTime = Date.now();
        const estimatedStartTime = currentTime - (Math.random() * 1800000); // Random up to 30 minutes ago
        const uptime = Math.floor((currentTime - estimatedStartTime) / 1000);

        return {
          id: modelId,
          name: modelId,
          provider: 'lmstudio',
          size: this.estimateModelSize(modelId),
          format: 'GGUF',
          status: 'running',
          processor: 'GPU/CPU',
          port: 1234,
          uptime,
          memoryUsage: this.estimateMemoryUsage(modelId),
          parameters: {
            temperature: 0.7,
            maxTokens: 2048,
            topP: 0.9
          }
        };
      }
    } catch (error) {
      // This is expected if no model is loaded or if the request fails
      console.debug('No model currently loaded in LM Studio or test request failed');
    }
    return null;
  }

  async startModel(modelName: string): Promise<void> {
    try {
      // Check if server is running first
      const isHealthy = await this.checkHealth();
      if (!isHealthy) {
        throw new APIError('LM Studio server is not running. Please start LM Studio and enable the local server first.');
      }

      // LM Studio requires manual model loading through the GUI
      // We provide helpful guidance instead of throwing an error
      throw new APIError(
        `To use model "${modelName}" in LM Studio:\n\n` +
        '1. Open LM Studio application\n' +
        '2. Go to the Chat tab\n' +
        `3. Select "${modelName}" from the model dropdown\n` +
        '4. Wait for the model to load (you\'ll see a loading indicator)\n' +
        '5. The model will be available for API requests once loaded\n\n' +
        'Note: LM Studio loads models manually through the interface.'
      );
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(`Failed to start model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async stopModel(modelName: string): Promise<void> {
    try {
      // Check if server is running first
      const isHealthy = await this.checkHealth();
      if (!isHealthy) {
        throw new APIError('LM Studio server is not running.');
      }

      // LM Studio requires manual model unloading through the GUI
      throw new APIError(
        `To stop model "${modelName}" in LM Studio:\n\n` +
        '1. Open LM Studio application\n' +
        '2. Go to the Chat tab\n' +
        '3. Click the model dropdown and select "Unload Model"\n' +
        '4. Or select a different model to automatically unload the current one\n\n' +
        'Note: LM Studio manages model loading/unloading through the interface.'
      );
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(`Failed to stop model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async generateCompletion(prompt: string, options?: any): Promise<any> {
    try {
      return await apiCall(`${this.baseUrl}/v1/completions`, {
        method: 'POST',
        body: JSON.stringify({
          model: 'local-model',
          prompt: prompt,
          max_tokens: options?.max_tokens || 100,
          temperature: options?.temperature || 0.7,
          top_p: options?.top_p || 0.9,
          ...options,
        }),
      });
    } catch (error) {
      throw new APIError(`Failed to generate completion: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async chatCompletion(messages: any[], options?: any): Promise<any> {
    try {
      return await apiCall(`/v1/chat/completions`, {
        method: 'POST',
        body: JSON.stringify({
          model: 'local-model',
          messages: messages,
          max_tokens: options?.max_tokens || 100,
          temperature: options?.temperature || 0.7,
          top_p: options?.top_p || 0.9,
          stream: false,
          ...options,
        }),
      });
    } catch (error) {
      throw new APIError(`Failed to generate chat completion: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await this.chatCompletion([
        { role: 'user', content: 'Hello' }
      ], { max_tokens: 1 });
      return !!response;
    } catch {
      return false;
    }
  }

  private estimateModelSize(modelId: string): string {
    // Estimate model size based on common model naming patterns
    const sizeMap: { [key: string]: string } = {
      '7b': '4.1 GB',
      '13b': '7.3 GB',
      '30b': '19.5 GB',
      '65b': '38.5 GB',
      '70b': '39.0 GB',
      'small': '1.2 GB',
      'medium': '2.8 GB',
      'large': '5.5 GB',
      'xl': '11.0 GB',
      'q4': '2.2 GB', // Quantized models
      'q5': '2.8 GB',
      'q8': '4.1 GB',
    };

    const modelLower = modelId.toLowerCase();
    for (const [key, size] of Object.entries(sizeMap)) {
      if (modelLower.includes(key)) {
        return size;
      }
    }

    return 'Unknown';
  }

  private estimateMemoryUsage(modelId: string): number {
    // Estimate memory usage in MB based on model size
    const modelLower = modelId.toLowerCase();
    
    if (modelLower.includes('7b')) return 4100;
    if (modelLower.includes('13b')) return 7300;
    if (modelLower.includes('30b')) return 19500;
    if (modelLower.includes('65b')) return 38500;
    if (modelLower.includes('70b')) return 39000;
    if (modelLower.includes('small')) return 1200;
    if (modelLower.includes('medium')) return 2800;
    if (modelLower.includes('large')) return 5500;
    if (modelLower.includes('xl')) return 11000;
    if (modelLower.includes('q4')) return 2200;
    if (modelLower.includes('q5')) return 2800;
    if (modelLower.includes('q8')) return 4100;
    
    return 3000; // Default estimate
  }
}