import React from 'react';

interface LoadingStateProps {
  message?: string;
}

export default function LoadingState({ message = 'Analyzing your crop...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-agri-green-600 mb-4"></div>
      <p className="text-lg text-earth-700">{message}</p>
      <p className="text-sm text-earth-400 mt-2">
        Running disease prediction, fetching weather, and calculating risk...
      </p>
    </div>
  );
}
