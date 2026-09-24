import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary orange palette
        primary: {
          DEFAULT: '#F59E0B',
          50:  '#FFFBEB',
          100: '#FFF3C4',
          200: '#FFE782',
          300: '#FFD43B',
          400: '#FFC107',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
          light: '#FFF7ED',
          hover: '#D97706',
        },
        // Surfaces
        surface: {
          DEFAULT: '#F9FAFB',
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          card: '#FFFFFF',
        },
        // Text
        content: {
          primary:   '#111827',
          secondary: '#6B7280',
          tertiary:  '#9CA3AF',
          inverse:   '#FFFFFF',
        },
        // Semantic
        success: { DEFAULT: '#16A34A', light: '#DCFCE7', dark: '#166534' },
        warning: { DEFAULT: '#F59E0B', light: '#FEF3C7', dark: '#B45309' },
        danger:  { DEFAULT: '#DC2626', light: '#FEE2E2', dark: '#991B1B' },
        info:    { DEFAULT: '#2563EB', light: '#DBEAFE', dark: '#1E40AF' },
        // Risk specific
        risk: {
          low:    '#16A34A',
          medium: '#F59E0B',
          high:   '#DC2626',
          'low-bg':    '#DCFCE7',
          'medium-bg': '#FEF3C7',
          'high-bg':   '#FEE2E2',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '1rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '68': '17rem',
        '72': '18rem',
        '84': '21rem',
        '88': '22rem',
        '96': '24rem',
      },
      borderRadius: {
        'sm': '6px',
        DEFAULT: '10px',
        'md': '10px',
        'lg': '12px',
        'xl': '14px',
        '2xl': '16px',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px 0 rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04)',
        'dropdown': '0 8px 24px -4px rgba(0,0,0,0.12), 0 4px 8px -4px rgba(0,0,0,0.08)',
        'modal': '0 20px 60px -10px rgba(0,0,0,0.20)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(8px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        slideInRight: { '0%': { opacity: '0', transform: 'translateX(-8px)' }, '100%': { opacity: '1', transform: 'translateX(0)' } },
      },
      gridTemplateColumns: {
        'sidebar': '260px 1fr',
        'sidebar-collapsed': '64px 1fr',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
};

export default config;
