/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'agri-green': {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        'earth': {
          100: '#f5f0ed',
          200: '#e2d8ce',
          300: '#c8b9a6',
          400: '#a8a29e',
          500: '#82776b',
          600: '#6b5b47',
          700: '#554938',
          800: '#44403c',
          900: '#38322c',
        },
        'risk-low': '#22c55e',
        'risk-moderate': '#eab308',
        'risk-high': '#f97316',
        'risk-critical': '#ef4444',
      },
    },
  },
  plugins: [],
};
