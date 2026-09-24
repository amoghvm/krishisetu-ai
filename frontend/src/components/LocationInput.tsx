import React, { useState, useEffect } from 'react';

interface LocationInputProps {
  latitude: string;
  longitude: string;
  onLatitudeChange: (value: string) => void;
  onLongitudeChange: (value: string) => void;
  latError?: string | null;
  lonError?: string | null;
}

export default function LocationInput({
  latitude,
  longitude,
  onLatitudeChange,
  onLongitudeChange,
  latError,
  lonError,
}: LocationInputProps) {
  const [touched, setTouched] = useState<{ lat: boolean; lon: boolean }>({ lat: false, lon: false });

  const validateLat = (value: string): string | null => {
    if (value === '' || value === undefined) return null;
    const num = parseFloat(value);
    if (isNaN(num)) return null;
    if (num < -90 || num > 90) return 'Latitude must be between -90 and 90.';
    return null;
  };

  const validateLon = (value: string): string | null => {
    if (value === '' || value === undefined) return null;
    const num = parseFloat(value);
    if (isNaN(num)) return null;
    if (num < -180 || num > 180) return 'Longitude must be between -180 and 180.';
    return null;
  };

  const effectiveLatError = latError || (touched.lat ? validateLat(latitude) : null);
  const effectiveLonError = lonError || (touched.lon ? validateLon(longitude) : null);

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-earth-700">Farm Location</h3>
      <p className="text-xs text-earth-500">
        Enter the coordinates of the field where the leaf was collected.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="latitude" className="block text-sm font-medium text-earth-800 mb-1">
            Latitude
          </label>
          <input
            type="number"
            id="latitude"
            name="latitude"
            value={latitude}
            onChange={(e) => onLatitudeChange(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, lat: true }))}
            placeholder="e.g. 12.9716"
            step="0.0001"
            min="-90"
            max="90"
            className={`w-full px-3 py-2 border rounded focus:outline-none focus:ring-1 focus:ring-agri-green-500 ${
              effectiveLatError ? 'border-red-400' : 'border-earth-300'
            }`}
          />
          {effectiveLatError && <p className="mt-1 text-xs text-red-600">{effectiveLatError}</p>}
          {!effectiveLatError && (
            <p className="mt-1 text-xs text-earth-400">Valid range: -90 to 90</p>
          )}
        </div>

        <div>
          <label htmlFor="longitude" className="block text-sm font-medium text-earth-800 mb-1">
            Longitude
          </label>
          <input
            type="number"
            id="longitude"
            name="longitude"
            value={longitude}
            onChange={(e) => onLongitudeChange(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, lon: true }))}
            placeholder="e.g. 77.5946"
            step="0.0001"
            min="-180"
            max="180"
            className={`w-full px-3 py-2 border rounded focus:outline-none focus:ring-1 focus:ring-agri-green-500 ${
              effectiveLonError ? 'border-red-400' : 'border-earth-300'
            }`}
          />
          {effectiveLonError && <p className="mt-1 text-xs text-red-600">{effectiveLonError}</p>}
          {!effectiveLonError && (
            <p className="mt-1 text-xs text-earth-400">Valid range: -180 to 180</p>
          )}
        </div>
      </div>
    </div>
  );
}
