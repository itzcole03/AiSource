export interface Model {
  id: string;
  name: string;
  provider: 'ollama' | 'vllm' | 'lmstudio';
  size: string;
  format?: string;
  status: 'available' | 'running' | 'loading' | 'error';
  processor?: string;
  memoryUsage?: number;
  uptime?: number;
  port?: number;
  lastUsed?: Date;
  parameters?: {
    temperature?: number;
    maxTokens?: number;
    topP?: number;
  };
}

export interface Provider {
  id: string;
  name: 'ollama' | 'vllm' | 'lmstudio';
  displayName: string;
  status: 'connected' | 'disconnected' | 'error' | 'starting' | 'stopping';
  version?: string;
  apiUrl: string;
  models: Model[];
  capabilities: string[];
  serverStatus?: 'running' | 'stopped' | 'starting' | 'stopping' | 'error';
}

export interface SystemInfo {
  gpus: Array<{
    name: string;
    memory: string;
    utilization: number;
  }>;
  ram: {
    total: string;
    used: string;
    available: string;
  };
  cpu: {
    cores: number;
    usage: number;
  };
  providers?: {
    lmstudio: ProviderStatus;
    ollama: ProviderStatus;
    vllm: ProviderStatus;
  };
}

export interface ProviderStatus {
  installed: boolean;
  running: boolean;
  path: string;
}

export interface ModelMetrics {
  requestsPerMinute: number;
  averageResponseTime: number;
  errorRate: number;
  tokensGenerated: number;
}

export interface ServerCommand {
  provider: 'ollama' | 'vllm' | 'lmstudio';
  action: 'start' | 'stop' | 'restart';
  modelName?: string;
}

export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  duration?: number;
}

// New types for advanced features

export interface ModelConfiguration {
  id: string;
  name: string;
  provider: 'ollama' | 'vllm' | 'lmstudio';
  modelName: string;
  parameters: {
    temperature: number;
    maxTokens: number;
    topP: number;
    topK?: number;
    repeatPenalty?: number;
    contextLength?: number;
    batchSize?: number;
    numGpus?: number;
    customArgs?: string;
  };
  createdAt: Date;
  isDefault: boolean;
}

export interface PerformanceMetrics {
  timestamp: Date;
  requestsPerMinute: number;
  averageResponseTime: number;
  errorRate: number;
  tokensGenerated: number;
  cpuUsage: number;
  memoryUsage: number;
  gpuUsage: number;
}

export interface ModelUsageStats {
  modelName: string;
  provider: string;
  totalRequests: number;
  totalTokens: number;
  avgResponseTime: number;
  uptime: number;
}

export type ModelCategory = 'chat' | 'code' | 'text' | 'embedding' | 'multimodal';

export interface MarketplaceModel {
  id: string;
  name: string;
  description: string;
  provider: string;
  category: string;
  size: string;
  downloads: number;
  rating: number;
  tags: string[];
  modelUrl: string;
  homepage: string;
  license: string;
  lastUpdated: Date;
  bestUse?: string;
  requirements?: {
    minRam?: string;
    recommendedRam?: string;
    gpuSupport?: boolean;
  };
  isInstalled: boolean;
  isOfficial: boolean;
}

export interface GlobalSettings {
  autoRefresh: boolean;
  refreshInterval: number;
  notifications: boolean;
  darkMode: boolean;
  autoStart: boolean;
  logLevel: 'debug' | 'info' | 'warning' | 'error';
}

export interface ExtendedModel extends Omit<Model, 'lastUsed'|'status'> {
  lastUsed?: Date | string | null;
  status?: Model['status'] | string;
}