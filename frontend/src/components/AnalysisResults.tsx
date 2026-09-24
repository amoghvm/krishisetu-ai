import React from 'react';
import type { CombinedAnalysisResponse } from '../api/types';
import DiseaseResult from './DiseaseResult';
import WeatherResult from './WeatherResult';
import RiskResult from './RiskResult';

interface AnalysisResultsProps {
  data: CombinedAnalysisResponse;
}

export default function AnalysisResults({ data }: AnalysisResultsProps) {
  return (
    <div className="space-y-6">
      <DiseaseResult
        prediction={data.prediction}
        low_confidence={data.low_confidence}
        confidence_threshold={data.confidence_threshold}
        message={data.message}
        model_info={data.model_info}
      />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <WeatherResult weather={data.weather} />
        <RiskResult risk={data.risk} />
      </div>
    </div>
  );
}
