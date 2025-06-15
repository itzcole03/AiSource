import React, { useState, useEffect } from 'react';
import { Download, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface ModelInstallationProgressProps {
  modelId: string;
  modelName: string;
  provider: string;
  onComplete: (success: boolean) => void;
  onCancel: () => void;
}

export const ModelInstallationProgress: React.FC<ModelInstallationProgressProps> = ({
  modelId,
  modelName,
  provider,
  onComplete,
  onCancel
}) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'downloading' | 'installing' | 'complete' | 'error'>('downloading');
  const [error, setError] = useState<string | null>(null);
  const [downloadSpeed, setDownloadSpeed] = useState<string>('');
  const [eta, setEta] = useState<string>('');

  useEffect(() => {
    simulateInstallation();
  }, []);

  const simulateInstallation = async () => {
    try {
      // Simulate download progress
      for (let i = 0; i <= 80; i += Math.random() * 5) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setProgress(Math.min(i, 80));
        
        // Simulate download metrics
        const speed = (Math.random() * 50 + 10).toFixed(1);
        const remaining = ((80 - i) / 10).toFixed(0);
        setDownloadSpeed(`${speed} MB/s`);
        setEta(`${remaining}s remaining`);
      }

      setStatus('installing');
      setDownloadSpeed('');
      setEta('Installing...');

      // Simulate installation
      for (let i = 80; i <= 100; i += Math.random() * 3) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setProgress(Math.min(i, 100));
      }

      setStatus('complete');
      setProgress(100);
      setTimeout(() => onComplete(true), 1000);

    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Installation failed');
      setTimeout(() => onComplete(false), 2000);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'downloading':
      case 'installing':
        return <Download className="w-6 h-6 text-blue-500 animate-bounce" />;
      case 'complete':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'downloading':
        return 'Downloading model...';
      case 'installing':
        return 'Installing model...';
      case 'complete':
        return 'Installation complete!';
      case 'error':
        return 'Installation failed';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'downloading':
      case 'installing':
        return 'bg-blue-500';
      case 'complete':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            {getStatusIcon()}
          </div>
          
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Installing {modelName}
          </h3>
          
          <p className="text-sm text-gray-600 mb-4">
            Provider: {provider.charAt(0).toUpperCase() + provider.slice(1)}
          </p>

          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>{getStatusText()}</span>
              <span>{progress.toFixed(0)}%</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${getStatusColor()}`}
                style={{ width: `${progress}%` }}
              />
            </div>
            
            {(downloadSpeed || eta) && (
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>{downloadSpeed}</span>
                <span>{eta}</span>
              </div>
            )}
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            </div>
          )}

          {status !== 'complete' && status !== 'error' && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
};