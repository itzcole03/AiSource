import React from 'react';
import { Provider } from '../types';
import { Server, Zap, AlertTriangle, CheckCircle } from 'lucide-react';

interface QuickStatsProps {
  providers: Provider[];
  className?: string;
}

export const QuickStats: React.FC<QuickStatsProps> = ({ providers, className = '' }) => {
  const totalProviders = providers.length;
  const connectedProviders = providers.filter(p => p.status === 'connected').length;
  const totalModels = providers.reduce((sum, p) => sum + p.models.length, 0);
  const runningModels = providers.reduce((sum, p) => sum + p.models.filter(m => m.status === 'running').length, 0);

  const stats = [
    {
      label: 'Providers',
      value: `${connectedProviders}/${totalProviders}`,
      subtext: 'Connected',
      icon: Server,
      color: connectedProviders === totalProviders ? 'text-green-600 dark:text-green-400' : connectedProviders > 0 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400',
      bgColor: connectedProviders === totalProviders ? 'bg-green-50 dark:bg-green-900/20' : connectedProviders > 0 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-red-50 dark:bg-red-900/20',
    },
    {
      label: 'Models',
      value: totalModels.toString(),
      subtext: 'Available',
      icon: CheckCircle,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      label: 'Running',
      value: runningModels.toString(),
      subtext: 'Active Models',
      icon: Zap,
      color: runningModels > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400',
      bgColor: runningModels > 0 ? 'bg-green-50 dark:bg-green-900/20' : 'bg-gray-50 dark:bg-gray-800',
    },
    {
      label: 'Issues',
      value: providers.filter(p => p.status === 'error').length.toString(),
      subtext: 'Errors',
      icon: AlertTriangle,
      color: providers.some(p => p.status === 'error') ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400',
      bgColor: providers.some(p => p.status === 'error') ? 'bg-red-50 dark:bg-red-900/20' : 'bg-gray-50 dark:bg-gray-800',
    },
  ];

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className={`${stat.bgColor} rounded-xl p-6 border border-gray-200 dark:border-gray-700`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-300">{stat.label}</p>
                  <p className={`text-2xl font-bold ${stat.color} mt-1`}>
                    {stat.value}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{stat.subtext}</p>
                </div>
                <div className={`p-3 rounded-lg ${stat.color.replace('text-', 'bg-').replace('-600', '-100').replace('dark:text-', 'dark:bg-').replace('dark:bg-', 'dark:bg-').replace('-400', '-900/30')}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};