import React, { useState } from 'react';
import { Provider } from '../types';
import { Play, Square, RotateCcw, Terminal, Loader2, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface ServerControlsProps {
  provider: Provider;
  onServerAction: (provider: string, action: 'start' | 'stop' | 'restart', modelName?: string) => Promise<void>;
}

export const ServerControls: React.FC<ServerControlsProps> = ({ provider, onServerAction }) => {
  const [isLoading, setIsLoading] = useState(false);

  const [showCommands, setShowCommands] = useState(false);

  const handleServerAction = async (action: 'start' | 'stop' | 'restart') => {
    setIsLoading(true);
    try {
      // For vLLM, ignore model selection, just start/stop/restart silently
      await onServerAction(provider.name, action);
    } finally {
      setIsLoading(false);
    }
  };

  const getServerStatusIcon = () => {
    if (isLoading) {
      return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
    }
    
    switch (provider.status) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'disconnected':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'starting':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'stopping':
        return <Loader2 className="w-4 h-4 animate-spin text-orange-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusText = () => {
    if (isLoading) return 'Processing...';
    
    switch (provider.status) {
      case 'connected': return 'Running';
      case 'disconnected': return 'Stopped';
      case 'starting': return 'Starting...';
      case 'stopping': return 'Stopping...';
      default: return 'Unknown';
    }
  };

  const canStart = provider.status === 'disconnected' && !isLoading;
  const canStop = provider.status === 'connected' && !isLoading;
  const canRestart = (provider.status === 'connected' || provider.status === 'disconnected') && !isLoading;

  const getCommands = () => {
    const commands = {
      ollama: [
        'ollama serve',
        'ollama pull <model-name>',
        'ollama list',
        'ollama ps'
      ],
      vllm: [
        'python -m vllm.entrypoints.openai.api_server'
      ],
      lmstudio: [
        'Open LM Studio application',
        'Go to Local Server tab',
        'Click "Start Server"'
      ]
    };
    return commands[provider.name] || [];
  };  return (
    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mt-4 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {getServerStatusIcon()}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Server Status: {getStatusText()}
          </span>
        </div>
        
        <button
          onClick={() => setShowCommands(!showCommands)}
          className="flex items-center space-x-1 px-2 py-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded transition-colors"
        >
          <Terminal className="w-3 h-3" />
          <span>Commands</span>
        </button>
      </div>

      {/* Server Control Buttons */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handleServerAction('start')}
          disabled={!canStart}
          className="flex items-center space-x-1 px-3 py-1.5 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Play className="w-3 h-3" />
          <span>Start</span>
        </button>

        <button
          onClick={() => handleServerAction('stop')}
          disabled={!canStop}
          className="flex items-center space-x-1 px-3 py-1.5 bg-red-500 text-white text-sm rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Square className="w-3 h-3" />
          <span>Stop</span>
        </button>

        <button
          onClick={() => handleServerAction('restart')}
          disabled={!canRestart}
          className="flex items-center space-x-1 px-3 py-1.5 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Restart</span>
        </button>
      </div>

      {/* Command Reference */}
      {showCommands && (
        <div className="mt-4 p-3 bg-gray-900 dark:bg-gray-950 rounded text-xs border border-gray-700 dark:border-gray-600">
          <div className="text-gray-300 dark:text-gray-400 mb-2 font-medium">Manual Commands:</div>
          {getCommands().map((command, index) => (
            <div key={index} className="text-green-400 dark:text-green-300 font-mono mb-1">
              {command}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};