import React, { Suspense, useState, useMemo, useEffect, useCallback } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Header } from './components/Header';
import { QuickStats } from './components/QuickStats';
import { ProviderCard } from './components/ProviderCard';
import { SystemMonitor } from './components/SystemMonitor';
import { NotificationSystem } from './components/NotificationSystem';
import { ConfigurationPanel } from './components/ConfigurationPanel';
import { LoadingSkeleton, ProviderCardSkeleton, SystemMonitorSkeleton } from './components/LoadingSkeleton';
import { ModelInstallationProgress } from './components/ModelInstallationProgress';
import { ModelVersionManager } from './components/ModelVersionManager';
import AdvancedModelSearch from './components/AdvancedModelSearch';
import { ShoppingBag, Settings, BarChart3 } from 'lucide-react';
import { getBackendUrl } from './services/backendConfig';

const PerformanceAnalytics = React.lazy(() => import('./components/PerformanceAnalytics'));
const ModelMarketplace = React.lazy(() => import('./components/ModelMarketplace'));

import { useProviders } from './hooks/useProviders';
import { useSystemInfo } from './hooks/useSystemInfo';
import { useNotifications } from './hooks/useNotifications';
import { useLocalStorage } from './hooks/useLocalStorage';
import { MarketplaceModel, ModelConfiguration, Model, ExtendedModel } from './types';

interface UserSettings {
  autoRefresh: boolean;
  refreshInterval: number;
  notifications: boolean;
  compactView: boolean;
  showSystemMonitor: boolean;
  theme: 'light' | 'dark' | 'auto';
  maxConcurrentRequests: number;
  requestTimeout: number;
}

const defaultSettings: UserSettings = {
  autoRefresh: true,
  refreshInterval: 30,
  notifications: true,
  compactView: false,
  showSystemMonitor: true,
  theme: 'light',
  maxConcurrentRequests: 5,
  requestTimeout: 30
};

function App() {
  // Provider and system state
  const { 
    providers, 
    loading, 
    error, 
    refreshProviders, 
    startModel, 
    stopModel, 
    handleServerAction 
  } = useProviders();
  
  // System information
  const { systemInfo, loading: systemLoading } = useSystemInfo();
  
  // Notifications
  const {
    notifications,
    dismissNotification,
    notifySuccess,
    notifyError,
    notifyWarning
  } = useNotifications();

  // UI State
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showMarketplace, setShowMarketplace] = useState(false);
  const [showConfiguration, setShowConfiguration] = useState(false);
  
  // Model management state
  interface InstallingModel {
    id: string;
    name: string;
    provider: string;
  }
  
  const [installingModel, setInstallingModel] = useState<InstallingModel | null>(null);
  const [versionManagerModel, setVersionManagerModel] = useState<{ 
    id: string; 
    name: string; 
    provider: string 
  } | null>(null);
  
  const [filteredModels, setFilteredModels] = useState<Model[]>([]);
  
  // Provider sorting state
  const [providerSort, setProviderSort] = useState<{
    sortBy: 'name' | 'status' | 'models' | 'none';
    sortOrder: 'asc' | 'desc';
  }>({
    sortBy: 'none',
    sortOrder: 'asc'
  });
  
  // Persistent settings
  const [userSettings, setUserSettings] = useLocalStorage<UserSettings>('model-manager-settings', defaultSettings);

  // Load settings from backend on mount
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const backendUrl = await getBackendUrl();
        const response = await fetch(`${backendUrl}/api/settings`);
        if (response.ok) {
          const backendSettings = await response.json();
          setUserSettings((prev) => ({ ...prev, ...backendSettings }));
        }
      } catch {
        // fallback to localStorage/defaults
      }
    };
    fetchSettings();
  }, [setUserSettings]);

  // Apply dark mode and theme
  useEffect(() => {
    if (userSettings.theme === 'dark' || (userSettings.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [userSettings.theme]);

  // Enhanced server action handler with better error handling and notifications
  const handleServerActionWithNotification = async (
    provider: string, 
    action: 'start' | 'stop' | 'restart', 
    modelName?: string
  ) => {
    try {
      await handleServerAction(provider, action, modelName);
      
      const actionText = action === 'start' ? 'started' : action === 'stop' ? 'stopped' : 'restarted';
      const modelText = modelName ? ` with model ${modelName}` : '';
      
      notifySuccess(
        `${provider.toUpperCase()} ${actionText}`,
        `Server ${actionText} successfully${modelText}`,
        4000
      );
    } catch (error) {
      notifyError(
        `${provider.toUpperCase()} Error`,
        error instanceof Error ? error.message : 'Server action failed',
        6000
      );
    }
  };

  // Enhanced model action handlers with better feedback
  const handleStartModel = async (providerId: string, modelId: string) => {
    const provider = providers.find(p => p.id === providerId);
    const model = provider?.models.find(m => m.id === modelId);
    
    if (!provider || !model) return;

    try {
      await handleServerActionWithNotification(providerId, 'start', modelId);
      notifySuccess(
        'Model Started',
        `${model.name} is now starting on ${provider.displayName}`,
        3000
      );
    } catch (error) {
      notifyError(
        'Start Failed',
        error instanceof Error ? error.message : 'Failed to start model',
        5000
      );
    }
  };

  const handleStopModel = async (providerId: string, modelId: string) => {
    const provider = providers.find(p => p.id === providerId);
    const model = provider?.models.find(m => m.id === modelId);
    
    if (!provider || !model) return;

    try {
      await handleServerActionWithNotification(providerId, 'stop', modelId);
      notifySuccess(
        'Model Stopped',
        `${model.name} has been stopped`,
        3000
      );
    } catch (error) {
      notifyError(
        'Stop Failed',
        error instanceof Error ? error.message : 'Failed to stop model',
        5000
      );
    }
  };

  // Configuration handlers
  const handleSaveConfiguration = (config: ModelConfiguration) => {
    notifySuccess(
      'Configuration Saved',
      `Configuration "${config.name}" has been saved successfully`,
      3000
    );
  };

  const handleDeleteConfiguration = () => {
    notifySuccess(
      'Configuration Deleted',
      'Configuration has been removed',
      3000
    );
  };

  // Enhanced marketplace handlers with installation progress
  const handleInstallModel = async (model: MarketplaceModel) => {
    setInstallingModel({
      id: model.id,
      name: model.name,
      provider: model.provider
    });
  };

  const handleInstallationComplete = (success: boolean = true) => {
    if (success && installingModel) {
      notifySuccess(
        'Model Installed',
        `${installingModel.name} has been installed successfully`,
        4000
      );
      
      // Refresh providers to show new model
      refreshProviders();
    } else if (installingModel) {
      notifyError(
        'Installation Failed',
        `Failed to install ${installingModel.name}`,
        6000
      );
    }
    
    setInstallingModel(null);
  };

  const handleInstallationCancel = () => {
    if (installingModel) {
      notifyWarning(
        'Installation Cancelled',
        `Installation of ${installingModel.name} was cancelled`,
        3000
      );
    }
    setInstallingModel(null);
  };

  // Version management handlers
  const handleOpenVersionManager = (model: Model) => {
    setVersionManagerModel({
      id: model.id,
      name: model.name,
      provider: model.provider
    });
  };

  // Get all models from all providers
  const allModels = useMemo(() => {
    return providers.flatMap(provider => 
      provider.models.map(model => ({
        ...model,
        provider: provider.name
      }))
    );
  }, [providers]);

  // Sorted providers based on sort criteria
  const sortedProviders = useMemo(() => {
    if (providerSort.sortBy === 'none') {
      return providers;
    }

    const sorted = [...providers].sort((a, b) => {
      let comparison = 0;

      switch (providerSort.sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'status': {
          const statusPriority: Record<string, number> = { 
            connected: 3, 
            connecting: 2, 
            starting: 2,
            stopping: 1,
            disconnected: 1, 
            error: 0 
          };
          comparison = (statusPriority[a.status] || 0) - (statusPriority[b.status] || 0);
          break;
        }
        case 'models':
          comparison = a.models.length - b.models.length;
          break;
        default:
          return 0;
      }

      return providerSort.sortOrder === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [providers, providerSort]);

  // Provider sort handlers
  const handleProviderSortChange = useCallback((sortBy: 'name' | 'status' | 'models' | 'none') => {
    setProviderSort(prev => ({
      sortBy,
      sortOrder: prev.sortBy === sortBy && prev.sortOrder === 'asc' ? 'desc' : 'asc'
    }));
  }, []);

  // Handle filtered models from AdvancedModelSearch
  const handleFilteredModels = useCallback((filtered: ExtendedModel[]) => {
    // Convert ExtendedModel to Model with proper type handling
    setFilteredModels(filtered.map(model => ({
      ...model,
      status: model.status && ['loading', 'error', 'available', 'running'].includes(model.status) 
        ? model.status as Model['status'] 
        : 'available',
      lastUsed: model.lastUsed instanceof Date ? model.lastUsed : undefined
    })));
  }, []);
  
  // Auto-refresh providers based on userSettings
  useEffect(() => {
    if (!userSettings.autoRefresh) return;

    const interval = setInterval(() => {
      if (!loading) {
        refreshProviders();
      }
    }, (userSettings.refreshInterval || 30) * 1000);

    return () => clearInterval(interval);
  }, [userSettings.autoRefresh, userSettings.refreshInterval, loading, refreshProviders]);
  
  // Show warning if no providers are connected
  useEffect(() => {
    const connectedProviders = providers.filter(p => p.status === 'connected');
    if (providers.length > 0 && connectedProviders.length === 0) {
      notifyWarning(
        'No Providers Connected',
        'None of your AI providers are currently running. Check the setup instructions.',
        8000
      );
    }
  }, [providers, notifyWarning]);
  
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
        <Header 
          onRefresh={refreshProviders} 
          loading={loading} 
          error={error}
          userSettings={userSettings}
          onSettingsChange={setUserSettings}
        />
        
        <main className="flex-1">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* Quick Stats with loading state */}
            {loading ? (
              <LoadingSkeleton variant="card" className="mb-8" />
            ) : (
              <QuickStats providers={providers} className="mb-8" />
            )}

            {/* Main Layout with Sidebar */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Content - Provider Cards */}
              <div className="lg:col-span-2 space-y-6">
                {/* Provider Sort Controls */}
                {!loading && providers.length > 1 && (
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Providers</h3>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600 dark:text-gray-300">Sort by:</span>
                        <select
                          value={providerSort.sortBy}
                          onChange={(e) => handleProviderSortChange(e.target.value as 'name' | 'status' | 'models' | 'none')}
                          className="text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          aria-label="Sort providers by"
                          title="Sort providers by"
                        >
                          <option value="none">Default</option>
                          <option value="name">Name</option>
                          <option value="status">Status</option>
                          <option value="models">Model Count</option>
                        </select>
                        {providerSort.sortBy !== 'none' && (
                          <button
                            onClick={() => handleProviderSortChange(providerSort.sortBy)}
                            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                            title={`Sort ${providerSort.sortOrder === 'asc' ? 'descending' : 'ascending'}`}
                          >
                            {providerSort.sortOrder === 'asc' ? '↑' : '↓'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {loading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <ProviderCardSkeleton key={i} />
                  ))
                ) : (
                  sortedProviders.map((provider) => (
                    <div key={provider.name} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                      <ProviderCard
                        provider={provider}
                        onStartModel={(modelId) => handleStartModel(provider.id, modelId)}
                        onStopModel={(modelId) => handleStopModel(provider.id, modelId)}
                        onServerAction={handleServerActionWithNotification}
                        onOpenVersionManager={handleOpenVersionManager}
                        compactView={userSettings.compactView}
                        filteredModels={filteredModels.filter(m => m.provider === provider.name)}
                      />
                    </div>
                  ))
                )}
              </div>
              
              {/* Right Sidebar */}
              <div className="lg:col-span-1 space-y-6">
                <div className="sticky top-6 space-y-6">
                  {/* Advanced Model Search - Compact Version */}
                  {allModels.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Model Search</h3>
                      </div>
                      <div className="p-4">
                        <AdvancedModelSearch
                          models={allModels}
                          onFilteredModels={handleFilteredModels}
                          onModelAction={async (action, model) => {
                            try {
                              if (action === 'start') {
                                await startModel(model.provider, model.id);
                                notifySuccess(`Started model: ${model.name}`, 'Success');
                              } else if (action === 'stop') {
                                await stopModel(model.provider, model.id);
                                notifySuccess(`Stopped model: ${model.name}`, 'Success');
                              } else if (action === 'delete') {
                                try {
                                  await stopModel(model.provider, model.id);
                                } catch (stopError) {
                                  console.debug('Model was not running or already stopped:', stopError);
                                }
                                await handleServerAction(
                                  model.provider,
                                  'stop',
                                  model.id
                                );
                                notifySuccess(`Deleted model: ${model.name}`, 'Success');
                              }
                              await refreshProviders();
                            } catch (error) {
                              const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
                              notifyError(`Failed to ${action} model: ${errorMessage}`, 'Error');
                            }
                          }}
                          onRefresh={async () => {
                            try {
                              await refreshProviders();
                              notifySuccess('Models refreshed', 'Success');
                            } catch (error) {
                              const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
                              notifyError(`Failed to refresh models: ${errorMessage}`, 'Error');
                            }
                          }}
                          isLoading={loading}
                          settings={{
                            autoRefresh: userSettings.autoRefresh,
                            refreshInterval: userSettings.refreshInterval
                          }}
                          compactMode={true}
                        />
                      </div>
                    </div>
                  )}

                  {/* System Monitor */}
                  {userSettings.showSystemMonitor && (
                    <div>
                      {systemLoading ? (
                        <SystemMonitorSkeleton />
                      ) : (
                        <SystemMonitor systemInfo={systemInfo} />
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Enhanced Floating Action Buttons */}
        <div className="fixed bottom-6 right-6 flex flex-col space-y-3 z-40">
          <button
            onClick={() => setShowConfiguration(true)}
            className="bg-gray-600 text-white p-3 rounded-full shadow-lg hover:bg-gray-700 transition-colors"
            title="Configuration"
          >
            <Settings className="w-6 h-6" />
          </button>
          
          <button
            onClick={() => setShowMarketplace(true)}
            className="bg-green-600 text-white p-3 rounded-full shadow-lg hover:bg-green-700 transition-colors"
            title="Model Marketplace"
          >
            <ShoppingBag className="w-6 h-6" />
          </button>
          
          <button
            onClick={() => setShowAnalytics(true)}
            className="bg-purple-600 text-white p-3 rounded-full shadow-lg hover:bg-purple-700 transition-colors"
            title="Performance Analytics"
          >
            <BarChart3 className="w-6 h-6" />
          </button>
        </div>

        {/* Modals and Overlays */}
        <div>
          {/* Configuration Panel */}
          {showConfiguration && (
            <ConfigurationPanel
              providers={providers}
              onSaveConfiguration={handleSaveConfiguration}
              onDeleteConfiguration={handleDeleteConfiguration}
              onClose={() => setShowConfiguration(false)}
              userSettings={userSettings}
              onSettingsChange={setUserSettings}
            />
          )}

          {/* Performance Analytics */}
          <Suspense fallback={
            <div className="fixed inset-0 flex items-center justify-center z-50 bg-white/70">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
              <span className="ml-4 text-lg text-gray-700">Loading analytics...</span>
            </div>
          }>
            {showAnalytics && (
              <PerformanceAnalytics
                isOpen={showAnalytics}
                onClose={() => setShowAnalytics(false)}
                providers={providers}
                systemInfo={systemInfo}
              />
            )}
          </Suspense>

          {/* Model Marketplace */}
          <Suspense fallback={
            <div className="fixed inset-0 flex items-center justify-center z-50 bg-white/70">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
              <span className="ml-4 text-lg text-gray-700">Loading marketplace...</span>
            </div>
          }>
            {showMarketplace && (
              <ModelMarketplace
                isOpen={showMarketplace}
                onClose={() => setShowMarketplace(false)}
                onInstallModel={handleInstallModel}
                installedModels={allModels}
              />
            )}
          </Suspense>

          {/* Model Installation Progress */}
          {installingModel && (
            <ModelInstallationProgress
              modelId={installingModel.id}
              modelName={installingModel.name}
              provider={installingModel.provider}
              onComplete={handleInstallationComplete}
              onCancel={handleInstallationCancel}
            />
          )}

          {/* Model Version Manager */}
          {versionManagerModel && (
            <ModelVersionManager
              modelId={versionManagerModel.id}
              modelName={versionManagerModel.name}
              provider={versionManagerModel.provider}
              isOpen={!!versionManagerModel}
              onClose={() => setVersionManagerModel(null)}
            />
          )}

          {/* Notification System */}
          <NotificationSystem 
            notifications={notifications}
            onDismiss={dismissNotification}
          />
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;