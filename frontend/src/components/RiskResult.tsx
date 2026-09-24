import React from 'react';
import type { RiskAnalysisResponse } from '../api/types';

interface RiskResultProps {
  risk: RiskAnalysisResponse;
}

const RISK_COLORS: Record<string, string> = {
  low: 'bg-risk-low text-white',
  moderate: 'bg-risk-moderate text-white',
  high: 'bg-risk-high text-white',
  critical: 'bg-risk-critical text-white',
};

const RISK_DESCRIPTIONS: Record<string, string> = {
  low: 'Routine monitoring recommended. Conditions appear favorable.',
  moderate: 'Increased vigilance advised. Monitor crops for changes.',
  high: 'Active risk. Inspect crops frequently for disease or pest symptoms.',
  critical: 'Urgent attention needed. Seek expert guidance immediately.',
};

export default function RiskResult({ risk }: RiskResultProps) {
  const colorClass = RISK_COLORS[risk.risk_level] || 'bg-earth-500 text-white';
  const description = RISK_DESCRIPTIONS[risk.risk_level] || 'Review the risk factors and recommendations.';

  const scorePercent = Math.min((risk.risk_score / 100) * 100, 100);

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold text-earth-800 mb-4 flex items-center">
        <span className="mr-3 text-2xl">⚠️</span>
        Outbreak Risk Assessment
      </h2>

      <div className="mb-4 flex items-center justify-between">
        <span className={`px-4 py-2 rounded-full font-bold text-lg ${colorClass}`}>
          {risk.risk_level.toUpperCase()}
        </span>
        <span className="text-3xl font-bold text-earth-800">
          {risk.risk_score.toFixed(0)}/100
        </span>
      </div>

      <div className="mb-4">
        <div className="w-full bg-earth-200 rounded-full h-4 overflow-hidden">
          <div
            className={`h-full transition-all ${
              risk.risk_level === 'critical'
                ? 'bg-risk-critical'
                : risk.risk_level === 'high'
                ? 'bg-risk-high'
                : risk.risk_level === 'moderate'
                ? 'bg-risk-moderate'
                : 'bg-risk-low'
            }`}
            style={{ width: `${scorePercent}%` }}
          />
        </div>
        <p className="text-xs text-earth-400 mt-1">{description}</p>
      </div>

      {risk.contributing_factors.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-earth-700 mb-2">Contributing Factors</h3>
          <ul className="space-y-1">
            {risk.contributing_factors.map((factor, idx) => (
              <li key={idx} className="text-sm">
                <span className="font-medium text-earth-700">{factor.factor}</span>
                <span className={`ml-2 px-2 py-0.5 rounded text-xs font-bold ${
                  factor.points > 0 ? 'bg-agri-green-100 text-agri-green-800' : 'bg-earth-100 text-earth-600'
                }`}>
                  +{factor.points.toFixed(0)}
                </span>
                <p className="text-xs text-earth-500 mt-0.5">{factor.description}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-3 p-3 bg-agri-green-50 border border-agri-green-200 rounded-lg">
        <p className="text-sm text-agri-green-800">{risk.recommendation}</p>
      </div>

      <p className="text-xs text-earth-400 italic">{risk.disclaimer}</p>
    </div>
  );
}
