/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary:   '#1A7A3E',
          accent:    '#639922',
          tint:      '#E8F5EE',
          border:    '#C6E6D2',
        },
        surface: {
          white:     '#FFFFFF',
          offwhite:  '#F9FAFB',
          dark:      '#111111',
        },
        text: {
          primary:   '#111111',
          body:      '#374151',
          muted:     '#6B7280',
        },
        ui: {
          border:    '#D1D5DB',
          error:     '#DC2626',
          warning:   '#92400E',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
      },
      animation: {
        'slide-in-top': 'slideInTop 0.25s ease-out',
        'fade-in':      'fadeIn 0.2s ease-out',
      },
      keyframes: {
        slideInTop: {
          '0%':   { opacity: '0', transform: 'translateY(-12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}