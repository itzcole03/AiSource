import React from 'react';
import { SystemInfo } from '../types';
import { Cpu, HardDrive, Zap, Monitor } from 'lucide-react';

interface SystemMonitorProps {
  systemInfo: SystemInfo | null;
}

export const SystemMonitor: React.FC<SystemMonitorProps> = ({ systemInfo }) => {
  if (!systemInfo) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Monitor</h3>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  const getUsageColor = (usage: number) => {
    if (usage >= 80) return 'bg-red-500';
    if (usage >= 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getUsageTextColor = (usage: number) => {
    if (usage >= 80) return 'text-red-600 dark:text-red-400';
    if (usage >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-green-600 dark:text-green-400';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 flex items-center space-x-2">
        <Monitor className="w-5 h-5" />
        <span>System Monitor</span>
      </h3>
      
      <div className="space-y-6">
        {/* CPU Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">CPU</span>
            </div>
            <span className={`text-sm font-medium ${getUsageTextColor(systemInfo.cpu.usage)}`}>
              {systemInfo.cpu.usage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(systemInfo.cpu.usage)}`}
              style={{ width: `${systemInfo.cpu.usage}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{systemInfo.cpu.cores} cores</p>
        </div>

        {/* RAM Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <HardDrive className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">RAM</span>
            </div>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
              {systemInfo.ram.used} / {systemInfo.ram.total}
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-purple-500 transition-all duration-300"
              style={{ 
                width: `${(parseFloat(systemInfo.ram.used) / parseFloat(systemInfo.ram.total)) * 100}%` 
              }}
            />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{systemInfo.ram.available} available</p>
        </div>

        {/* GPU Usage */}
        {systemInfo.gpus.map((gpu, index) => (
          <div key={index}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">GPU {index + 1}</span>
              </div>
              <span className={`text-sm font-medium ${getUsageTextColor(gpu.utilization)}`}>
                {gpu.utilization}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(gpu.utilization)}`}
                style={{ width: `${gpu.utilization}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate" title={gpu.name}>
              {gpu.name}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500">{gpu.memory}</p>
          </div>
        ))}

        {/* Provider Status Summary */}
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Provider Status</h4>
          <div className="space-y-2">
            {systemInfo.providers && Object.entries(systemInfo.providers).map(([name, status]) => (
              <div key={name} className="flex items-center justify-between">
                <span className="text-xs text-gray-600 dark:text-gray-300 capitalize">{name}</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    status.running ? 'bg-green-500' : status.installed ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {status.running ? 'Running' : status.installed ? 'Stopped' : 'Not Installed'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};