import { apiCall, APIError, healthCheck } from './api';
import { Model } from '../types';

const OLLAMA_BASE_URL = 'http://localhost:11434';

export class OllamaService {
  private baseUrl: string;

  constructor(baseUrl: string = OLLAMA_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async checkHealth(): Promise<boolean> {
    return await healthCheck(`${this.baseUrl}/api/tags`);
  }

  async getVersion(): Promise<string | undefined> {
    try {
      const response = await apiCall(`${this.baseUrl}/api/version`);
      return response.version;
    } catch {
      return undefined;
    }
  }

  async getServerInfo(): Promise<any> {
    try {
      return await apiCall(`${this.baseUrl}/api/version`);
    } catch {
      return null;
    }
  }

  async listModels(): Promise<Model[]> {
    try {
      const response = await apiCall(`${this.baseUrl}/api/tags`);
      return response.models?.map((model: any) => ({
        id: model.name,
        name: model.name,
        provider: 'ollama' as const,
        size: this.formatSize(model.size),
        format: model.details?.format || 'GGUF',
        status: 'available' as const,
        lastUsed: model.modified_at ? new Date(model.modified_at) : undefined,
        parameters: {
          temperature: 0.7,
          maxTokens: 2048,
          topP: 0.9
        }
      })) || [];
    } catch (error) {
      console.error('Failed to fetch Ollama models:', error);
      return [];
    }
  }

  async getRunningModels(): Promise<Model[]> {
    try {
      const response = await apiCall(`${this.baseUrl}/api/ps`);
      const currentTime = Date.now();
      
      return response.models?.map((model: any) => {
        // Calculate actual uptime from expires_at
        let uptime = 0;
        if (model.expires_at) {
          const expiresAt = new Date(model.expires_at).getTime();
          const loadTime = expiresAt - (5 * 60 * 1000); // Assuming 5min default keep-alive
          uptime = Math.max(0, Math.floor((currentTime - loadTime) / 1000));
        }

        return {
          id: model.name,
          name: model.name,
          provider: 'ollama' as const,
          size: this.formatSize(model.size),
          format: model.details?.format || 'GGUF',
          status: 'running' as const,
          processor: this.getProcessorType(model),
          uptime,
          port: 11434,
          memoryUsage: this.estimateMemoryUsage(model.size),
          parameters: {
            temperature: 0.7,
            maxTokens: 2048,
            topP: 0.9
          }
        };
      }) || [];
    } catch (error) {
      console.error('Failed to fetch running Ollama models:', error);
      return [];
    }
  }

  async startModel(modelName: string): Promise<void> {
    try {
      // Use a minimal prompt to load the model
      await apiCall(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        body: JSON.stringify({
          model: modelName,
          prompt: 'Hello',
          stream: false,
          options: {
            num_predict: 1,
          }
        }),
      });
    } catch (error) {
      if (error instanceof APIError && error.message.includes('model not found')) {
        throw new APIError(`Model "${modelName}" not found. Please pull it first with: ollama pull ${modelName}`);
      }
      throw new APIError(`Failed to start model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async stopModel(modelName: string): Promise<void> {
    try {
      await apiCall(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        body: JSON.stringify({
          model: modelName,
          keep_alive: 0,
        }),
      });
    } catch (error) {
      throw new APIError(`Failed to stop model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async pullModel(modelName: string, onProgress?: (progress: number) => void): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/pull`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: modelName,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new APIError(`Failed to pull model: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new APIError('Failed to read response stream');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line);
              if (data.completed && data.total && onProgress) {
                const progress = (data.completed / data.total) * 100;
                onProgress(progress);
              }
            } catch (e) {
              // Ignore JSON parse errors
            }
          }
        }
      }
    } catch (error) {
      throw new APIError(`Failed to pull model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async deleteModel(modelName: string): Promise<void> {
    try {
      await apiCall(`${this.baseUrl}/api/delete`, {
        method: 'DELETE',
        body: JSON.stringify({
          name: modelName,
        }),
      });
    } catch (error) {
      throw new APIError(`Failed to delete model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async generateCompletion(modelName: string, prompt: string, options?: any): Promise<any> {
    try {
      return await apiCall(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        body: JSON.stringify({
          model: modelName,
          prompt,
          stream: false,
          ...options,
        }),
      });
    } catch (error) {
      throw new APIError(`Failed to generate completion: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async chatCompletion(modelName: string, messages: any[], options?: any): Promise<any> {
    try {
      return await apiCall(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        body: JSON.stringify({
          model: modelName,
          messages,
          stream: false,
          ...options,
        }),
      });
    } catch (error) {
      throw new APIError(`Failed to generate chat completion: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private formatSize(bytes: number): string {
    if (!bytes) return 'Unknown';
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  private getProcessorType(model: any): string {
    // Determine processor type based on model details
    if (model.details?.families?.includes('gpu')) {
      return 'GPU';
    }
    if (model.details?.quantization_level) {
      return 'CPU (Quantized)';
    }
    return 'CPU';
  }

  private estimateMemoryUsage(sizeBytes: number): number {
    if (!sizeBytes) return 0;
    // Estimate memory usage in MB (models typically use slightly more than their file size)
    return Math.round((sizeBytes / (1024 * 1024)) * 1.2);
  }
}