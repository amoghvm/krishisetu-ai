import React, { useState } from 'react';
import ImageUpload from '../components/ImageUpload';
import LocationInput from '../components/LocationInput';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import AnalysisResults from '../components/AnalysisResults';
import { analyzeCrop, ApiClientError } from '../api/client';
import type { CombinedAnalysisResponse } from '../api/types';

export default function AnalyzePage() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [latError, setLatError] = useState<string | null>(null);
  const [lonError, setLonError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<CombinedAnalysisResponse | null>(null);

  const validateInputs = (): boolean => {
    let valid = true;

    const lat = parseFloat(latitude);
    if (isNaN(lat) || lat < -90 || lat > 90) {
      setLatError('Enter a valid latitude (-90 to 90).');
      valid = false;
    } else {
      setLatError(null);
    }

    const lon = parseFloat(longitude);
    if (isNaN(lon) || lon < -180 || lon > 180) {
      setLonError('Enter a valid longitude (-180 to 180).');
      valid = false;
    } else {
      setLonError(null);
    }

    if (!selectedImage) {
      setError('Please select a leaf image to upload.');
      valid = false;
    }

    return valid;
  };

  const handleAnalyze = async () => {
    setError(null);
    setResults(null);

    if (!validateInputs() || !selectedImage) return;

    setIsLoading(true);

    try {
      const lat = parseFloat(latitude);
      const lon = parseFloat(longitude);
      const response = await analyzeCrop(selectedImage, lat, lon);
      setResults(response);
    } catch (e) {
      if (e instanceof ApiClientError) {
        setError(e.message);
      } else if (e instanceof Error) {
        setError(e.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setResults(null);
  };

  const canAnalyze = !!selectedImage && !!latitude && !!longitude;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Input Section */}
      {!results && !isLoading && (
        <div className="space-y-6">
          {/* Image Upload */}
          <div>
            <h2 className="text-lg font-medium text-earth-800 mb-2">Leaf Image</h2>
            <ImageUpload
              selectedImage={selectedImage}
              onImageSelect={setSelectedImage}
            />
          </div>

          {/* Location Inputs */}
          <LocationInput
            latitude={latitude}
            longitude={longitude}
            onLatitudeChange={setLatitude}
            onLongitudeChange={setLongitude}
            latError={latError}
            lonError={lonError}
          />

          {/* Analyze Button */}
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!canAnalyze}
            className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center ${
              canAnalyze
                ? 'bg-agri-green-600 hover:bg-agri-green-700 text-white'
                : 'bg-earth-200 text-earth-400 cursor-not-allowed'
            }`}
          >
            <span className="mr-2">🔍</span>
            Analyze Crop
          </button>

          {/* Hint */}
          <p className="text-xs text-earth-400 text-center">
            Bengaluru demo: latitude 12.9716, longitude 77.5946
          </p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <ErrorState error={error} onRetry={handleRetry} />
      )}

      {/* Loading State */}
      {isLoading && <LoadingState />}

      {/* Results */}
      {results && !isLoading && (
        <div className="space-y-6">
          <AnalysisResults data={results} />
          <button
            type="button"
            onClick={() => {
              setResults(null);
              setSelectedImage(null);
              setLatitude('');
              setLongitude('');
            }}
            className="w-full py-2 px-4 border border-earth-300 rounded-lg text-earth-700 hover:bg-earth-50 transition-colors text-sm"
          >
            New Analysis
          </button>
        </div>
      )}
    </div>
  );
}
