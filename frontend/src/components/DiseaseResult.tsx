import React from 'react';
import type { DiseasePrediction } from '../api/types';

interface DiseaseResultProps {
  prediction: DiseasePrediction;
  low_confidence: boolean;
  confidence_threshold: number;
  message: string;
  model_info: Record<string, unknown>;
}

export default function DiseaseResult({
  prediction,
  low_confidence,
  confidence_threshold,
  message,
  model_info,
}: DiseaseResultProps) {
  const confidencePercent = (prediction.confidence * 100).toFixed(1);
  const confidenceColor = prediction.confidence >= confidence_threshold
    ? 'bg-agri-green-500'
    : 'bg-amber-500';

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold text-earth-800 mb-4 flex items-center">
        <span className="mr-3 text-2xl">🔬</span>
        Disease Detection
      </h2>

      <div className="mb-4">
        <span className="text-sm font-medium text-earth-500">Detected</span>
        <p className="text-2xl font-bold text-earth-900 mt-1">
          {prediction.crop} — {prediction.disease}
        </p>
        <p className="text-sm text-earth-400 mt-1 font-mono">{prediction.class_name}</p>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="font-medium text-earth-700">Confidence</span>
          <span className="font-bold">{confidencePercent}%</span>
        </div>
        <div className="w-full bg-earth-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all ${confidenceColor}`}
            style={{ width: `${Math.min(prediction.confidence * 100, 100)}%` }}
          />
        </div>
        <p className="text-xs text-earth-400 mt-1">
          Threshold: {(confidence_threshold * 100).toFixed(0)}%
        </p>
      </div>

      {low_confidence && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-sm text-amber-800">
            ⚠️ Low confidence prediction. The image may be blurry, poorly lit, or the condition
            may be at an early stage. Consider re-taking the photo for a more accurate result.
          </p>
        </div>
      )}

      <div className="mb-3">
        <p className="text-sm text-earth-700">{message}</p>
      </div>

      {model_info && (
        <div className="text-xs text-earth-400 border-t pt-2">
          Model: {String(model_info.architecture || 'ResNet18')} · v{String(model_info.version || '1.0.0')}
          {' · '}
          {String(model_info.num_classes || '38')} classes
        </div>
      )}
    </div>
  );
}
