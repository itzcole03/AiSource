import React, { useState } from 'react';
import { RefreshCw, AlertCircle, Settings } from 'lucide-react';

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

interface HeaderProps {
  onRefresh: () => void;
  loading: boolean;
  error: string | null;
  userSettings: UserSettings;
  onSettingsChange: (settings: UserSettings) => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  onRefresh, 
  loading, 
  error, 
  userSettings, 
  onSettingsChange 
}) => {
  const [showQuickSettings, setShowQuickSettings] = useState(false);

  const toggleSetting = (key: keyof UserSettings) => {
    onSettingsChange({
      ...userSettings,
      [key]: !userSettings[key]
    });
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Unified AI Model Manager
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              Manage Ollama, vLLM, and LM Studio providers
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {error && (
              <div className="flex items-center space-x-2 text-red-600 bg-red-50 px-3 py-2 rounded-lg">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {/* Quick Settings */}
            <div className="relative">
              <button
                onClick={() => setShowQuickSettings(!showQuickSettings)}
                className={`p-2 rounded-lg transition-colors ${
                  showQuickSettings 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                }`}
                title="Quick Settings"
              >
                <Settings className="w-5 h-5" />
              </button>

              {showQuickSettings && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 p-3 z-50">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Quick Settings</h3>
                  
                  <div className="space-y-2">
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Compact View</span>
                      <button
                        onClick={() => toggleSetting('compactView')}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                          userSettings.compactView ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                            userSettings.compactView ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </label>

                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">System Monitor</span>
                      <button
                        onClick={() => toggleSetting('showSystemMonitor')}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                          userSettings.showSystemMonitor ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                            userSettings.showSystemMonitor ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </label>

                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Auto Refresh</span>
                      <button
                        onClick={() => toggleSetting('autoRefresh')}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                          userSettings.autoRefresh ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                            userSettings.autoRefresh ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </label>

                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Notifications</span>
                      <button
                        onClick={() => toggleSetting('notifications')}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                          userSettings.notifications ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                            userSettings.notifications ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </label>
                  </div>
                </div>
              )}
            </div>
            
            <button
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};