import React from 'react';

interface ErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export default function ErrorState({ error, onRetry }: ErrorStateProps) {
  let title = 'Something went wrong';
  let suggestion = 'Please check your inputs and try again.';

  if (error.toLowerCase().includes('not loaded') || error.toLowerCase().includes('model')) {
    title = 'Disease model unavailable';
    suggestion = 'The backend model is still loading or could not be initialized. Please try again shortly.';
  } else if (error.toLowerCase().includes('latitude') || error.toLowerCase().includes('longitude')) {
    title = 'Invalid location';
    suggestion = 'Please check your latitude and longitude values.';
  } else if (error.toLowerCase().includes('image') || error.toLowerCase().includes('format') || error.toLowerCase().includes('file')) {
    title = 'Invalid image';
    suggestion = 'Please upload a clear leaf photo in JPEG, PNG, or WEBP format.';
  } else if (error.toLowerCase().includes('weather') || error.toLowerCase().includes('timeout') || error.toLowerCase().includes('reach')) {
    title = 'Weather data unavailable';
    suggestion = 'Could not retrieve weather data for the selected location. Please verify the coordinates or try again later.';
  } else if (error.toLowerCase().includes('network') || error.toLowerCase().includes('fetch')) {
    title = 'Connection failed';
    suggestion = 'Cannot reach the KrishiSetu AI backend. Please ensure the server is running.';
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div className="flex justify-center mb-3">
        <svg
          className="h-10 w-10 text-red-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-red-800 mb-2">{title}</h3>
      <p className="text-sm text-red-700 mb-4 break-words">{error}</p>
      <p className="text-xs text-red-600">{suggestion}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-2 bg-agri-green-600 text-white rounded hover:bg-agri-green-700 transition-colors text-sm"
        >
          Try again
        </button>
      )}
    </div>
  );
}
