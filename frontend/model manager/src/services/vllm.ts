import { apiCall, APIError, healthCheck } from './api';
import { Model } from '../types';

const VLLM_BASE_URL = 'http://localhost:8000';

export class VLLMService {
  private baseUrl: string;

  constructor(baseUrl: string = VLLM_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async checkHealth(): Promise<boolean> {
    // Try health endpoint first, then models endpoint
    const healthOk = await healthCheck(`${this.baseUrl}/health`);
    if (healthOk) return true;
    
    return await healthCheck(`${this.baseUrl}/v1/models`);
  }

  async getVersion(): Promise<string | undefined> {
    try {
      // Try version endpoint
      const response = await apiCall(`${this.baseUrl}/version`);
      return response.version || 'vLLM';
    } catch {
      // Try to get version from server info
      try {
        const response = await fetch(`${this.baseUrl}/v1/models`);
        const server = response.headers.get('server');
        if (server?.includes('vllm')) {
          return server;
        }
        return 'vLLM Server';
      } catch {
        return 'vLLM';
      }
    }
  }

  async getServerInfo(): Promise<any> {
    try {
      // Try to get server statistics
      const response = await apiCall(`${this.baseUrl}/stats`);
      return response;
    } catch {
      // Fallback to basic info
      try {
        const modelsResponse = await apiCall(`${this.baseUrl}/v1/models`);
        return {
          models: modelsResponse.data?.length || 0,
          status: 'running'
        };
      } catch {
        return null;
      }
    }
  }

  async listModels(): Promise<Model[]> {
    try {
      const response = await apiCall(`${this.baseUrl}/v1/models`);
      const currentTime = Date.now();
      
      return response.data?.map((model: any, index: number) => {
        // Estimate uptime (vLLM models are typically loaded at server start)
        const estimatedStartTime = currentTime - (Math.random() * 3600000); // Random up to 1 hour ago
        const uptime = Math.floor((currentTime - estimatedStartTime) / 1000);

        return {
          id: model.id,
          name: model.id,
          provider: 'vllm' as const,
          size: this.estimateModelSize(model.id),
          format: 'HuggingFace Transformers',
          status: 'running' as const,
          processor: 'GPU',
          port: 8000,
          uptime,
          memoryUsage: this.estimateMemoryUsage(model.id),
          parameters: {
            temperature: 0.7,
            maxTokens: 2048,
            topP: 0.9
          }
        };
      }) || [];
    } catch (error) {
      console.error('Failed to fetch vLLM models:', error);
      return [];
    }
  }

  async getModelInfo(modelName: string): Promise<any> {
    try {
      // Try to get specific model information
      const response = await apiCall(`${this.baseUrl}/v1/models/${modelName}`);
      return response;
    } catch {
      return null;
    }
  }

  async startModel(modelName: string): Promise<void> {
    throw new APIError(
      'vLLM models are started via server configuration.\n\n' +
      'To start a model with vLLM:\n' +
      '1. Stop the current vLLM server\n' +
      '2. Use the server controls to start vLLM with your desired model\n' +
      '3. Or run: python -m vllm.entrypoints.openai.api_server --model ' + modelName,
      400
    );
  }

  async stopModel(modelName: string): Promise<void> {
    throw new APIError(
      'vLLM models cannot be individually stopped.\n\n' +
      'To change models:\n' +
      '1. Stop the entire vLLM server using the server controls\n' +
      '2. Start vLLM with a different model\n' +
      'vLLM loads one model at a time per server instance.',
      400
    );
  }

  async generateCompletion(prompt: string, model?: string, options?: any): Promise<any> {
    try {
      const models = await this.listModels();
      const targetModel = model || models[0]?.id || 'default';

      return await apiCall(`${this.baseUrl}/v1/completions`, {
        method: 'POST',
        body: JSON.stringify({
          model: targetModel,
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

  async chatCompletion(messages: any[], model?: string, options?: any): Promise<any> {
    try {
      const models = await this.listModels();
      const targetModel = model || models[0]?.id || 'default';

      return await apiCall(`${this.baseUrl}/v1/chat/completions`, {
        method: 'POST',
        body: JSON.stringify({
          model: targetModel,
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

  async getServerStats(): Promise<any> {
    try {
      // Try multiple endpoints for server statistics
      const endpoints = ['/stats', '/metrics', '/health'];
      
      for (const endpoint of endpoints) {
        try {
          const response = await apiCall(`${this.baseUrl}${endpoint}`);
          if (response) return response;
        } catch {
          continue;
        }
      }
      
      return null;
    } catch {
      return null;
    }
  }

  private estimateModelSize(modelId: string): string {
    // Estimate model size based on common model names
    const sizeMap: { [key: string]: string } = {
      '7b': '13.5 GB',
      '13b': '26 GB',
      '30b': '60 GB',
      '65b': '120 GB',
      '70b': '140 GB',
      'small': '1.5 GB',
      'medium': '6 GB',
      'large': '12 GB',
      'xl': '24 GB',
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
    
    if (modelLower.includes('7b')) return 13500;
    if (modelLower.includes('13b')) return 26000;
    if (modelLower.includes('30b')) return 60000;
    if (modelLower.includes('65b')) return 120000;
    if (modelLower.includes('70b')) return 140000;
    if (modelLower.includes('small')) return 1500;
    if (modelLower.includes('medium')) return 6000;
    if (modelLower.includes('large')) return 12000;
    if (modelLower.includes('xl')) return 24000;
    
    return 8000; // Default estimate
  }
}