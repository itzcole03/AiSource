import React, { useState, useEffect } from 'react';
import { Save, RotateCcw, Plus, Trash2, Edit3, X, CheckCircle } from 'lucide-react';
import { Provider, ModelConfiguration } from '../types';
import { getBackendUrl } from '../services/backendConfig';

interface ConfigurationPanelProps {
  providers: Provider[];
  onSaveConfiguration: (config: ModelConfiguration) => void;
  onDeleteConfiguration: (configId: string) => void;
  onClose: () => void;
  userSettings: any;
  onSettingsChange: (settings: any) => void;
}

export const ConfigurationPanel: React.FC<ConfigurationPanelProps> = ({
  providers,
  onSaveConfiguration,
  onDeleteConfiguration,
  onClose,
  userSettings,
  onSettingsChange
}) => {
  const [activeTab, setActiveTab] = useState<'global' | 'models' | 'providers'>('global');
  const [configurations, setConfigurations] = useState<ModelConfiguration[]>([]);
  const [editingConfig, setEditingConfig] = useState<ModelConfiguration | null>(null);
  const [showSaveConfirmation, setShowSaveConfirmation] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Load configurations from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('model-configurations');
    if (saved) {
      setConfigurations(JSON.parse(saved));
    }
  }, []);

  // Save configurations to localStorage
  const saveConfigurations = (configs: ModelConfiguration[]) => {
    setConfigurations(configs);
    localStorage.setItem('model-configurations', JSON.stringify(configs));
  };

  const createNewConfiguration = () => {
    const newConfig: ModelConfiguration = {
      id: Date.now().toString(),
      name: 'New Configuration',
      provider: 'ollama',
      modelName: '',
      parameters: {
        temperature: 0.7,
        maxTokens: 2048,
        topP: 0.9,
        topK: 40,
        repeatPenalty: 1.1,
        contextLength: 4096,
        batchSize: 1,
        numGpus: 1,
        customArgs: ''
      },
      createdAt: new Date(),
      isDefault: false
    };
    setEditingConfig(newConfig);
  };

  const saveConfiguration = () => {
    if (!editingConfig) return;

    const updatedConfigs = configurations.some(c => c.id === editingConfig.id)
      ? configurations.map(c => c.id === editingConfig.id ? editingConfig : c)
      : [...configurations, editingConfig];

    saveConfigurations(updatedConfigs);
    onSaveConfiguration(editingConfig);
    setEditingConfig(null);
  };

  const deleteConfiguration = (configId: string) => {
    const updatedConfigs = configurations.filter(c => c.id !== configId);
    saveConfigurations(updatedConfigs);
    onDeleteConfiguration(configId);
  };

  const resetToDefaults = () => {
    if (!editingConfig) return;
    
    setEditingConfig({
      ...editingConfig,
      parameters: {
        temperature: 0.7,
        maxTokens: 2048,
        topP: 0.9,
        topK: 40,
        repeatPenalty: 1.1,
        contextLength: 4096,
        batchSize: 1,
        numGpus: 1,
        customArgs: ''
      }
    });
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    try {
      // Save to backend
      const backendUrl = await getBackendUrl();
      const response = await fetch(`${backendUrl}/api/settings`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(userSettings)
      });
      
      if (response.ok) {
        // Also save to localStorage as backup
        localStorage.setItem('model-manager-settings', JSON.stringify(userSettings));
        setShowSaveConfirmation(true);
        setTimeout(() => setShowSaveConfirmation(false), 3000);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Configuration Manager</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 dark:bg-gray-700 border-r border-gray-200 dark:border-gray-600">
            <div className="p-4">
              <div className="space-y-2">
                {['global', 'models', 'providers'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab as any)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === tab
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)} Settings
                  </button>
                ))}
              </div>
            </div>

            {activeTab === 'models' && (
              <div className="p-4 border-t border-gray-200 dark:border-gray-600">
                <button
                  onClick={createNewConfiguration}
                  className="w-full flex items-center space-x-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Config</span>
                </button>

                <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                  {configurations.map((config) => (
                    <div
                      key={config.id}
                      className="flex items-center justify-between p-2 bg-white dark:bg-gray-600 rounded border border-gray-200 dark:border-gray-500"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {config.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-300">
                          {config.provider} • {config.modelName || 'No model'}
                        </p>
                      </div>
                      <div className="flex space-x-1">
                        <button
                          onClick={() => setEditingConfig(config)}
                          className="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900 rounded"
                        >
                          <Edit3 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => deleteConfiguration(config.id)}
                          className="p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto max-h-[calc(90vh-80px)] bg-white dark:bg-gray-800">
            {activeTab === 'global' && (
              <GlobalSettings 
                settings={userSettings}
                onSettingsChange={onSettingsChange}
              />
            )}

            {activeTab === 'models' && editingConfig && (
              <ModelConfigurationForm
                config={editingConfig}
                providers={providers}
                onChange={setEditingConfig}
                onSave={saveConfiguration}
                onReset={resetToDefaults}
              />
            )}

            {activeTab === 'providers' && (
              <ProviderSettings providers={providers} />
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-4 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
          <button
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors"
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
          
          {showSaveConfirmation && (
            <div className="flex items-center text-green-600 dark:text-green-400">
              <CheckCircle className="w-5 h-5 mr-1" />
              Settings saved!
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface GlobalSettingsProps {
  settings: any;
  onSettingsChange: (settings: any) => void;
}

const GlobalSettings: React.FC<GlobalSettingsProps> = ({ settings, onSettingsChange }) => {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white">Global Settings</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Auto Refresh
            </label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.autoRefresh}
                onChange={(e) => onSettingsChange({...settings, autoRefresh: e.target.checked})}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 dark:after:border-gray-600 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {settings.autoRefresh && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Refresh Interval (seconds)
              </label>
              <input
                type="number"
                value={settings.refreshInterval || 30}
                onChange={(e) => onSettingsChange({...settings, refreshInterval: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="5"
                max="300"
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Enable Notifications</label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.notifications}
                onChange={(e) => onSettingsChange({...settings, notifications: e.target.checked})}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Compact View</label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.compactView}
                onChange={(e) => onSettingsChange({...settings, compactView: e.target.checked})}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Show System Monitor</label>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.showSystemMonitor}
                onChange={(e) => onSettingsChange({...settings, showSystemMonitor: e.target.checked})}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Theme</label>
            <select
              value={settings.theme || 'light'}
              onChange={(e) => onSettingsChange({...settings, theme: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">Performance</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Max Concurrent Requests
            </label>
            <input
              type="number"
              value={settings.maxConcurrentRequests || 5}
              onChange={(e) => onSettingsChange({...settings, maxConcurrentRequests: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="1"
              max="20"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Request Timeout (seconds)
            </label>
            <input
              type="number"
              value={settings.requestTimeout || 30}
              onChange={(e) => onSettingsChange({...settings, requestTimeout: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="5"
              max="120"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

interface ModelConfigurationFormProps {
  config: ModelConfiguration;
  providers: Provider[];
  onChange: (config: ModelConfiguration) => void;
  onSave: () => void;
  onReset: () => void;
}

const ModelConfigurationForm: React.FC<ModelConfigurationFormProps> = ({
  config,
  providers,
  onChange,
  onSave,
  onReset
}) => {
  const availableModels = providers
    .find(p => p.name === config.provider)?.models || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Model Configuration</h3>
        <div className="flex space-x-2">
          <button
            onClick={onReset}
            className="flex items-center space-x-1 px-3 py-1.5 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset</span>
          </button>
          <button
            onClick={onSave}
            className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Configuration Name
            </label>
            <input
              type="text"
              value={config.name}
              onChange={(e) => onChange({...config, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Provider</label>
            <select
              value={config.provider}
              onChange={(e) => onChange({...config, provider: e.target.value as any})}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="ollama">Ollama</option>
              <option value="vllm">vLLM</option>
              <option value="lmstudio">LM Studio</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Model</label>
            <select
              value={config.modelName}
              onChange={(e) => onChange({...config, modelName: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a model...</option>
              {availableModels.map((model) => (
                <option key={model.id} value={model.name}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Temperature ({config.parameters.temperature})
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.parameters.temperature}
              onChange={(e) => onChange({
                ...config,
                parameters: {...config.parameters, temperature: parseFloat(e.target.value)}
              })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Max Tokens</label>
            <input
              type="number"
              value={config.parameters.maxTokens}
              onChange={(e) => onChange({
                ...config,
                parameters: {...config.parameters, maxTokens: parseInt(e.target.value)}
              })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="1"
              max="8192"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Top P ({config.parameters.topP})
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={config.parameters.topP}
              onChange={(e) => onChange({
                ...config,
                parameters: {...config.parameters, topP: parseFloat(e.target.value)}
              })}
              className="w-full accent-blue-600"
            />
          </div>
        </div>
      </div>

      {config.provider === 'vllm' && (
        <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">vLLM Specific Settings</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Number of GPUs</label>
              <input
                type="number"
                value={config.parameters.numGpus}
                onChange={(e) => onChange({
                  ...config,
                  parameters: {...config.parameters, numGpus: parseInt(e.target.value)}
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="1"
                max="8"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Batch Size</label>
              <input
                type="number"
                value={config.parameters.batchSize}
                onChange={(e) => onChange({
                  ...config,
                  parameters: {...config.parameters, batchSize: parseInt(e.target.value)}
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="1"
                max="256"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ProviderSettings: React.FC<{providers: Provider[]}> = ({ providers }) => {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white">Provider Settings</h3>
      
      {providers.map((provider) => (
        <div key={provider.name} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">{provider.displayName}</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">API URL</label>
              <input
                type="text"
                value={provider.apiUrl}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
              <div className={`px-3 py-2 rounded-lg text-sm font-medium ${
                provider.status === 'connected' ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300' :
                provider.status === 'disconnected' ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300' :
                'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300'
              }`}>
                {provider.status.charAt(0).toUpperCase() + provider.status.slice(1)}
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Capabilities</label>
            <div className="flex flex-wrap gap-2">
              {provider.capabilities.map((capability) => (
                <span
                  key={capability}
                  className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300 text-xs font-medium rounded-full"
                >
                  {capability}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};