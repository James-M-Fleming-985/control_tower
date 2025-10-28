/**
 * Professional Design System for Feedback360
 * Updated branding with modern, professional aesthetic
 */

export const designSystem = {
  // Color Palette - Professional & Modern
  colors: {
    // Primary Brand Colors
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',  // Main brand color
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e'
    },
    
    // Secondary Colors - Sophisticated Purple/Violet
    secondary: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',  // Secondary brand
      600: '#9333ea',
      700: '#7c3aed',
      800: '#6b21a8',
      900: '#581c87'
    },
    
    // Neutral Grays
    gray: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a'
    },
    
    // Success/Status Colors
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6'
  },

  // Typography
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      display: ['Cal Sans', 'Inter', 'system-ui', 'sans-serif']
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
      '6xl': '3.75rem'
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800
    }
  },

  // Spacing & Layout
  spacing: {
    xs: '0.5rem',
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
    xl: '3rem',
    '2xl': '4rem',
    '3xl': '6rem'
  },

  // Border Radius
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    full: '9999px'
  },

  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)'
  },

  // Component Styles
  components: {
    button: {
      primary: {
        background: 'linear-gradient(135deg, #0ea5e9 0%, #a855f7 100%)',
        color: 'white',
        fontWeight: 600,
        borderRadius: '0.75rem',
        padding: '0.75rem 1.5rem',
        border: 'none',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
      },
      secondary: {
        background: 'white',
        color: '#334155',
        fontWeight: 600,
        borderRadius: '0.75rem',
        padding: '0.75rem 1.5rem',
        border: '2px solid #e2e8f0',
        cursor: 'pointer',
        transition: 'all 0.2s ease'
      }
    },
    
    card: {
      background: 'white',
      borderRadius: '1rem',
      border: '1px solid #e2e8f0',
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
      padding: '2rem'
    }
  }
};

// Brand Guidelines
export const brandGuidelines = {
  logo: {
    name: "Feedback360",
    tagline: "Professional. Anonymous. Insightful.",
    description: "The modern way to collect honest feedback"
  },
  
  voice: {
    tone: "Professional yet approachable",
    style: "Clear, confident, and trustworthy",
    messaging: [
      "Professional feedback collection",
      "Complete anonymity guaranteed", 
      "Actionable insights for growth",
      "Enterprise-grade security"
    ]
  },
  
  visual: {
    style: "Modern, clean, professional",
    approach: "Minimalist with purposeful color accents",
    imagery: "Abstract, professional, technology-focused"
  }
};