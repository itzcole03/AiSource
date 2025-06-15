import React, { useState } from 'react';
import { Provider, Model } from '../types';
import { ModelCard } from './ModelCard';
import { ServerControls } from './ServerControls';
import { CheckCircle, XCircle, AlertCircle, Server, ExternalLink, Package, Grid, List } from 'lucide-react';
import { useProviderControl } from '../hooks/useProviderControl';
import { NotificationSystem } from './NotificationSystem';

interface ProviderCardProps {
  provider: Provider;
  onStartModel: (modelId: string) => void;
  onStopModel: (modelId: string) => void;
  onServerAction: (provider: string, action: 'start' | 'stop' | 'restart', modelName?: string) => Promise<void>;
  onOpenVersionManager?: (model: Model) => void;
  compactView?: boolean;
  filteredModels?: Model[];
}

export const ProviderCard: React.FC<ProviderCardProps> = ({ 
  provider, 
  onStartModel, 
  onStopModel,
  onOpenVersionManager,
  compactView = false,
  filteredModels
}) => {
  // Unified provider control hook
  const { controlProvider } = useProviderControl();

  const [notifications, setNotifications] = useState<Array<{
    id: string;
    type: 'success' | 'error' | 'warning';
    title: string;
    message: string;
    duration: number;
    timestamp: Date;
  }>>([]);
  const [showLog, setShowLog] = useState(false);
  
  // Load viewMode from localStorage with 'grid' as default
  const getStoredViewMode = (): 'grid' | 'list' => {
    try {
      const stored = localStorage.getItem(`viewMode-${provider.id}`);
      return stored === 'list' ? 'list' : 'grid'; // Always default to 'grid' for best UX
    } catch {
      return 'grid';
    }
  };
  
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(getStoredViewMode());
  
  // Save viewMode to localStorage when it changes
  const handleViewModeChange = (newViewMode: 'grid' | 'list') => {
    setViewMode(newViewMode);
    try {
      localStorage.setItem(`viewMode-${provider.id}`, newViewMode);
    } catch (error) {
      console.warn('Failed to save view mode preference:', error);
    }
  };

  const handleStart = async () => {
    const result = await controlProvider('start', provider.id);
    if (result.status === 'success') {
      setNotifications(n => [...n, { 
        id: Date.now().toString(), 
        type: 'success', 
        title: 'Started', 
        message: `${provider.displayName} started successfully`, 
        duration: 3500,
        timestamp: new Date(Date.now())
      }]);
    } else {
      setNotifications(n => [...n, { 
        id: Date.now().toString(), 
        type: 'error', 
        title: 'Start Failed', 
        message: 'Failed to start provider', 
        duration: 0,
        timestamp: new Date(Date.now())
      }]);
      setShowLog(true);
    }
  };

  const handleStop = async () => {
    const result = await controlProvider('stop', provider.id);
    if (result.status === 'success') {
      setNotifications(n => [...n, { 
        id: Date.now().toString(), 
        type: 'success', 
        title: 'Stopped', 
        message: `${provider.displayName} stopped successfully`, 
        duration: 3500,
        timestamp: new Date(Date.now())
      }]);
    } else {
      setNotifications(n => [...n, { 
        id: Date.now().toString(), 
        type: 'error', 
        title: 'Stop Failed', 
        message: 'Failed to stop provider', 
        duration: 0,
        timestamp: new Date(Date.now())
      }]);
      setShowLog(true);
    }
  };

  const handleDismissNotification = (id: string) => {
    setNotifications(n => n.filter(notif => notif.id !== id));
  };

  const handleCloseLog = () => setShowLog(false);

  const getStatusIcon = () => {
    switch (provider.status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'starting':
        return <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'stopping':
        return <div className="w-5 h-5 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (provider.status) {
      case 'connected':
        return 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20';
      case 'disconnected':
        return 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20';
      case 'starting':
        return 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20';
      case 'stopping':
        return 'border-orange-200 dark:border-orange-800 bg-orange-50 dark:bg-orange-900/20';
      case 'error':
        return 'border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20';
    }
  };

  const getStatusText = () => {
    switch (provider.status) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'starting':
        return 'Starting...';
      case 'stopping':
        return 'Stopping...';
      case 'error':
        return 'Error';
    }
  };

  const getServiceInstructions = () => {
    switch (provider.name) {
      case 'ollama':
        return {
          install: 'Download from https://ollama.ai',
          start: 'Run "ollama serve" in terminal',
          check: 'Verify with "ollama list"'
        };
      case 'vllm':
        return {
          install: 'pip install vllm',
          start: 'python -m vllm.entrypoints.openai.api_server --model <model_name>',
          check: 'Check http://localhost:8000/health'
        };
      case 'lmstudio':
        return {
          install: 'Download from https://lmstudio.ai',
          start: 'Open LM Studio and start local server',
          check: 'Enable "Start Server" in LM Studio'
        };
    }
  };

  const runningModels = provider.models.filter(m => m.status === 'running').length;
  const totalModels = provider.models.length;
  const instructions = getServiceInstructions();
  
  // Use filtered models if provided, otherwise use all models
  const modelsToShow = filteredModels || provider.models;

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className={`p-6 border-b ${getStatusColor()}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white dark:bg-gray-700 rounded-lg shadow-sm">
                <Server className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{provider.displayName}</h3>
                  <button
                    onClick={() => window.open(provider.apiUrl, '_blank')}
                    className="p-1 text-gray-400 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 rounded transition-colors"
                    title={`Open ${provider.apiUrl}`}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center space-x-2 mt-1">
                  {getStatusIcon()}
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    {getStatusText()}
                  </span>
                  {provider.version && (
                    <span className="text-sm text-gray-400 dark:text-gray-500">• v{provider.version}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Model Stats and View Toggle */}
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {runningModels}/{totalModels}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Models Running</div>
              </div>

              {modelsToShow.length > 0 && (
                <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                  <button
                    onClick={() => handleViewModeChange('grid')}
                    className={`p-2 rounded transition-all ${
                      viewMode === 'grid' 
                        ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm ring-2 ring-blue-200 dark:ring-blue-400' 
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                    title="Card View (Recommended)"
                  >
                    <Grid className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleViewModeChange('list')}
                    className={`p-2 rounded transition-all ${
                      viewMode === 'list' 
                        ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm ring-2 ring-blue-200 dark:ring-blue-400' 
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                    title="Compact List View"
                  >
                    <List className="w-4 h-4" />
                  </button>
                  {viewMode === 'list' && (
                    <div className="ml-2 text-xs text-blue-600 dark:text-blue-400 font-medium">
                      Try Card View →
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="p-6">
          {provider.status === 'disconnected' ? (
            <div className="space-y-3 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">Setup Instructions</h4>
              <div className="space-y-2">
                <div className="flex items-start space-x-2">
                  <span className="font-medium text-blue-600 dark:text-blue-400">1.</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{instructions.install}</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="font-medium text-blue-600 dark:text-blue-400">2.</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{instructions.start}</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="font-medium text-blue-600 dark:text-blue-400">3.</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{instructions.check}</span>
                </div>
              </div>
            </div>
          ) : modelsToShow.length > 0 ? (
            <div>
              {viewMode === 'grid' ? (
                <div className={`grid gap-4 ${
                  compactView 
                    ? 'grid-cols-1 md:grid-cols-3 lg:grid-cols-4' 
                    : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                }`}>
                  {modelsToShow.map(model => (
                    <ModelCard
                      key={model.id}
                      model={model}
                      onStart={() => onStartModel(model.id)}
                      onStop={() => onStopModel(model.id)}
                      onOpenVersionManager={onOpenVersionManager ? () => onOpenVersionManager(model) : undefined}
                      compactView={compactView}
                    />
                  ))}
                </div>
              ) : (
                <div>
                  {/* Helpful banner for list view users */}
                  <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Grid className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        <span className="text-sm text-blue-800 dark:text-blue-300 font-medium">
                          Try Card View for a better experience!
                        </span>
                      </div>
                      <button
                        onClick={() => handleViewModeChange('grid')}
                        className="px-3 py-1 bg-blue-600 dark:bg-blue-700 text-white text-xs rounded hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
                      >
                        Switch to Cards
                      </button>
                    </div>
                  </div>
                  
                  {/* List view content */}
                  <div className="space-y-2">
                    {modelsToShow.map(model => (
                      <div key={model.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            model.status === 'running' ? 'bg-green-500' :
                            model.status === 'loading' ? 'bg-blue-500 animate-pulse' :
                            model.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                          }`} />
                          <div>
                            <div className="font-medium text-gray-900 dark:text-white">{model.name}</div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">{model.size} • {model.format}</div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {onOpenVersionManager && (
                            <button
                              onClick={() => onOpenVersionManager(model)}
                              className="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
                              title="Manage Versions"
                            >
                              <Package className="w-4 h-4" />
                            </button>
                          )}
                          {model.status === 'available' && (
                            <button
                              onClick={() => onStartModel(model.id)}
                              className="px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 transition-colors"
                            >
                              Start
                            </button>
                          )}
                          {model.status === 'running' && (
                            <button
                              onClick={() => onStopModel(model.id)}
                              className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 transition-colors"
                            >
                              Stop
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Server className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
              <p>No models available</p>
              <p className="text-sm">Models will appear here when the provider is connected</p>
            </div>
          )}
        </div>

        {/* Capabilities */}
        <div className="px-6 pb-6">
          <div className="flex flex-wrap gap-2">
            {provider.capabilities.map((capability) => (
              <span
                key={capability}
                className="px-2 py-1 bg-white dark:bg-gray-600 text-xs font-medium text-gray-600 dark:text-gray-300 rounded-full border border-gray-200 dark:border-gray-500"
              >
                {capability}
              </span>
            ))}
          </div>
        </div>

        {/* Server Controls */}
        <ServerControls 
          provider={provider} 
          onServerAction={async (_providerName, action) => {
            if (action === 'start') await handleStart();
            else if (action === 'stop') await handleStop();
          }}
        />
      </div>

      <NotificationSystem notifications={notifications} onDismiss={handleDismissNotification} />
      
      {showLog && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-lg w-full p-6 relative border border-gray-200 dark:border-gray-700">
            <button onClick={handleCloseLog} className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300">✕</button>
            <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Provider Log</h3>
            <pre className="bg-gray-100 dark:bg-gray-700 rounded p-3 text-xs max-h-80 overflow-y-auto whitespace-pre-wrap text-gray-900 dark:text-gray-100">{/* providerLog || */ 'No log available.'}</pre>
          </div>
        </div>
      )}
    </>
  );
}