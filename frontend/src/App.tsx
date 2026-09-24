import React from 'react';
import AnalyzePage from './pages/AnalyzePage';

function App() {
  return (
    <div className="min-h-screen bg-agri-green-50 text-earth-800">
      <header className="bg-white shadow-sm border-b border-agri-green-200">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-agri-green-700">KrishiSetu AI</h1>
          <p className="text-sm text-earth-500">Crop Disease Identification & Risk Advisory</p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-6">
        <AnalyzePage />
      </main>
      <footer className="bg-white border-t border-agri-green-200 mt-auto">
        <div className="container mx-auto px-4 py-3 text-center text-xs text-earth-400">
          Prototype rule-based risk assessment. Not scientifically validated.
        </div>
      </footer>
    </div>
  );
}

export default App;
