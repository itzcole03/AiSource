import React from 'react';
import { Model } from '../types';
import { Play, Square, Clock, HardDrive, Cpu, Zap, AlertCircle, Package, ExternalLink } from 'lucide-react';

interface ModelCardProps {
  model: Model;
  onStart?: () => void;
  onStop?: () => void;
  onOpenVersionManager?: () => void;
  compactView?: boolean;
}

export const ModelCard: React.FC<ModelCardProps> = ({ 
  model, 
  onStart, 
  onStop, 
  onOpenVersionManager,
  compactView = false 
}) => {
  const getStatusColor = () => {
    switch (model.status) {
      case 'running':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 border-green-200 dark:border-green-700';
      case 'loading':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-700';
      case 'error':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300 border-red-200 dark:border-red-700';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  const getStatusIcon = () => {
    switch (model.status) {
      case 'running':
        return <Zap className="w-3 h-3" />;
      case 'loading':
        return <div className="w-3 h-3 border border-blue-600 border-t-transparent rounded-full animate-spin" />;
      case 'error':
        return <AlertCircle className="w-3 h-3" />;
      default:
        return <Square className="w-3 h-3" />;
    }
  };

  const formatUptime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const canStart = model.status === 'available' || model.status === 'error';
  const canStop = model.status === 'running';
  const isLoading = model.status === 'loading';

  if (compactView) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-colors">
        <div className="flex items-center justify-between mb-2">
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {model.name}
            </h4>
            <div className="text-xs text-gray-500 dark:text-gray-400">{model.size}</div>
          </div>
          
          <div className={`px-2 py-1 rounded-full text-xs font-medium border flex items-center space-x-1 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="capitalize">{model.status}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex space-x-1">
            {canStart && (
              <button
                onClick={onStart}
                disabled={isLoading}
                className="flex items-center space-x-1 px-2 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="w-3 h-3" />
                <span>Start</span>
              </button>
            )}
            
            {canStop && (
              <button
                onClick={onStop}
                className="flex items-center space-x-1 px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 transition-colors"
              >
                <Square className="w-3 h-3" />
                <span>Stop</span>
              </button>
            )}
          </div>

          {onOpenVersionManager && (
            <button
              onClick={onOpenVersionManager}
              className="p-1 text-gray-400 dark:text-gray-300 hover:text-gray-600 dark:hover:text-gray-100 rounded transition-colors"
              title="Manage Versions"
            >
              <Package className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-colors model-card ${compactView ? 'compact' : 'p-4'}`}>
      <div className={`flex items-center justify-between ${compactView ? 'mb-2' : 'mb-3'}`}>
        <div className="flex-1 min-w-0">
          <h4 className={`font-medium text-gray-900 dark:text-white truncate ${compactView ? 'text-xs' : 'text-sm'}`}>
            {model.name}
          </h4>
          <div className={`flex items-center space-x-2 mt-1 text-gray-500 dark:text-gray-400 model-info ${compactView ? 'text-xs' : 'text-xs'}`}>
            <div className="flex items-center space-x-1">
              <HardDrive className={compactView ? 'w-2.5 h-2.5' : 'w-3 h-3'} />
              <span>{model.size}</span>
            </div>
            {!compactView && model.format && (
              <div className="flex items-center space-x-1">
                <span className="w-1 h-1 bg-gray-400 dark:bg-gray-500 rounded-full" />
                <span>{model.format}</span>
              </div>
            )}
            {!compactView && model.processor && (
              <div className="flex items-center space-x-1">
                <Cpu className="w-3 h-3" />
                <span>{model.processor}</span>
              </div>
            )}
          </div>
        </div>
        
        <div className={`rounded-full font-medium border flex items-center space-x-1 ${getStatusColor()} ${
          compactView ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-xs'
        }`}>
          {getStatusIcon()}
          {!compactView && <span className="capitalize">{model.status}</span>}
        </div>
      </div>

      {/* Running Model Details - Hidden in compact mode */}
      {!compactView && model.status === 'running' && (
        <div className="mb-3 p-2 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
          <div className="grid grid-cols-2 gap-2 text-xs">
            {model.uptime !== undefined && (
              <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-300">
                <Clock className="w-3 h-3" />
                <span>Uptime: {formatUptime(model.uptime)}</span>
              </div>
            )}
            {model.port && (
              <div className="text-gray-600 dark:text-gray-300">
                Port: {model.port}
              </div>
            )}
            {model.memoryUsage && (
              <div className="text-gray-600 dark:text-gray-300">
                Memory: {model.memoryUsage}MB
              </div>
            )}
            {model.lastUsed && (
              <div className="text-gray-600 dark:text-gray-300">
                Last used: {model.lastUsed.toLocaleDateString()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className={`flex items-center justify-between model-actions ${compactView ? 'gap-1' : 'gap-2'}`}>
        <div className={`flex items-center ${compactView ? 'space-x-1' : 'space-x-2'}`}>
          {canStart && (
            <button
              onClick={onStart}
              disabled={isLoading}
              className={`flex items-center space-x-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
                compactView ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-xs'
              }`}
            >
              <Play className={compactView ? 'w-2.5 h-2.5' : 'w-3 h-3'} />
              {!compactView && <span>Start</span>}
            </button>
          )}
          
          {canStop && (
            <button
              onClick={onStop}
              className={`flex items-center space-x-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors ${
                compactView ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-xs'
              }`}
            >
              <Square className={compactView ? 'w-2.5 h-2.5' : 'w-3 h-3'} />
              {!compactView && <span>Stop</span>}
            </button>
          )}

          {!compactView && model.status === 'running' && model.provider === 'ollama' && (
            <button
              onClick={() => window.open(`http://localhost:11434/api/generate`, '_blank')}
              className="px-2 py-1.5 text-xs text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 border border-gray-300 dark:border-gray-600 rounded hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
            >
              Test API
            </button>
          )}
        </div>

        <div className="flex items-center space-x-1">
          {onOpenVersionManager && !compactView && (
            <button
              onClick={onOpenVersionManager}
              className="p-1.5 text-gray-400 dark:text-gray-300 hover:text-gray-600 dark:hover:text-gray-100 rounded transition-colors"
              title="Manage Versions"
            >
              <Package className="w-4 h-4" />
            </button>
          )}
          
          {!compactView && model.provider === 'lmstudio' && model.status === 'running' && (
            <button
              onClick={() => window.open(`http://localhost:1234`, '_blank')}
              className="p-1.5 text-gray-400 dark:text-gray-300 hover:text-gray-600 dark:hover:text-gray-100 rounded transition-colors"
              title="Open LM Studio"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};