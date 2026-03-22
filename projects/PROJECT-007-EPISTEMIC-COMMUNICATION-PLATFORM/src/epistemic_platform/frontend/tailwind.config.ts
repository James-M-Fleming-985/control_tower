import type { Config } from 'tailwindcss';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#1b1b1b',
        foreground: '#ffffff',
        card: {
          DEFAULT: '#2d2d2d',
          foreground: '#d1d1d1',
          border: '#3b3b3b',
        },
        primary: {
          DEFAULT: '#6264A7',
          foreground: '#ffffff',
          hover: '#7B83EB',
        },
        accent: {
          DEFAULT: '#7B83EB',
          foreground: '#ffffff',
        },
        muted: {
          DEFAULT: '#2d2d2d',
          foreground: '#a0a0a0',
        },
        destructive: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff',
        },
        success: {
          DEFAULT: '#66bb6a',
          light: 'rgba(76, 175, 80, 0.15)',
        },
        border: '#3b3b3b',
        input: '#3b3b3b',
        ring: '#6264A7',
        sidebar: {
          DEFAULT: '#252525',
          foreground: '#d1d1d1',
          border: '#3b3b3b',
          active: 'rgba(98, 100, 167, 0.2)',
        },
      },
      fontFamily: {
        sans: ["'Segoe UI'", '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      borderRadius: {
        lg: '14px',
        md: '10px',
        sm: '8px',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'pulse-dot': {
          '0%, 80%, 100%': { transform: 'scale(0)' },
          '40%': { transform: 'scale(1)' },
        },
        'xp-fill': {
          '0%': { width: '0%' },
          '100%': { width: 'var(--xp-width)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        'pulse-dot': 'pulse-dot 1.4s infinite ease-in-out both',
        'xp-fill': 'xp-fill 1s ease-out forwards',
      },
    },
  },
  plugins: [],
} satisfies Config;
