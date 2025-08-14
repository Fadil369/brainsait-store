/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Custom color palette from the HTML prototype
      colors: {
        primary: '#00d4aa',
        secondary: '#00a886',
        accent: '#ff6b35',
        'vision-green': '#00d4aa',
        'vision-purple': '#7c3aed',
        dark: '#000000',
        'dark-secondary': '#0a0a0a',
        light: '#ffffff',
        gray: '#94a3b8',
        'gray-light': '#e2e8f0',
        'glass-bg': 'rgba(255, 255, 255, 0.05)',
        'glass-border': 'rgba(255, 255, 255, 0.1)',
        'text-primary': '#ffffff',
        'text-secondary': '#94a3b8',
        success: '#10b981',
        warning: '#f59e0b',
      },
      // Custom spacing system
      spacing: {
        'xs': '0.25rem',
        'sm': '0.5rem',
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '3rem',
        '3xl': '4rem',
      },
      // Typography
      fontFamily: {
        sans: [
          '-apple-system', 
          'BlinkMacSystemFont', 
          'Segoe UI', 
          'SF Pro Display', 
          'Noto Sans Arabic', 
          'Roboto', 
          'Oxygen', 
          'Ubuntu', 
          'sans-serif'
        ],
        arabic: [
          'Noto Sans Arabic',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'sans-serif'
        ],
      },
      fontSize: {
        'clamp-xs': 'clamp(0.75rem, 2vw, 0.875rem)',
        'clamp-sm': 'clamp(0.875rem, 2vw, 1rem)',
        'clamp-base': 'clamp(1rem, 2.5vw, 1.125rem)',
        'clamp-lg': 'clamp(1.125rem, 3vw, 1.25rem)',
        'clamp-xl': 'clamp(1.25rem, 3.5vw, 1.5rem)',
        'clamp-2xl': 'clamp(1.5rem, 4vw, 1.875rem)',
        'clamp-3xl': 'clamp(1.875rem, 5vw, 2.25rem)',
        'clamp-4xl': 'clamp(2.25rem, 6vw, 3rem)',
        'clamp-hero': 'clamp(2rem, 6vw, 4.5rem)',
      },
      // Animations and transitions
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'fade-in-up': 'fadeInUp 1s ease',
        'slide-down': 'slideDown 0.5s ease-out',
        'slide-in': 'slideIn 0.3s ease',
        'float': 'float 15s infinite ease-in-out',
        'mesh-float': 'meshFloat 20s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '25%': { transform: 'translate(30px, -50px) rotate(90deg)' },
          '50%': { transform: 'translate(-30px, 30px) rotate(180deg)' },
          '75%': { transform: 'translate(50px, 20px) rotate(270deg)' },
        },
        meshFloat: {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '33%': { transform: 'translate(-20px, -20px) rotate(1deg)' },
          '66%': { transform: 'translate(20px, -10px) rotate(-1deg)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 212, 170, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 212, 170, 0.6)' },
        },
      },
      // Backdrop blur and filters
      backdropBlur: {
        '4xl': '72px',
      },
      // Grid and layout
      gridTemplateColumns: {
        'auto-fit': 'repeat(auto-fit, minmax(300px, 1fr))',
        'auto-fill': 'repeat(auto-fill, minmax(250px, 1fr))',
      },
      // Box shadows
      boxShadow: {
        'glow': '0 0 20px rgba(0, 212, 170, 0.3)',
        'glow-lg': '0 10px 30px rgba(0, 212, 170, 0.4)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1)',
        'glass-lg': '0 20px 40px rgba(0, 212, 170, 0.15)',
      },
      // Border radius
      borderRadius: {
        'xl': '1.25rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      // Background gradients
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, var(--primary), var(--vision-purple))',
        'gradient-accent': 'linear-gradient(135deg, var(--accent), var(--warning))',
        'gradient-glass': 'linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(124, 58, 237, 0.1))',
        'gradient-mesh': `
          radial-gradient(circle at 20% 50%, rgba(0, 212, 170, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(124, 58, 237, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 50% 20%, rgba(255, 107, 53, 0.08) 0%, transparent 50%)
        `,
      },
      // Clip paths for geometric shapes
      clipPath: {
        'triangle': 'polygon(50% 0%, 0% 100%, 100% 100%)',
        'diamond': 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)',
      },
      // Screen sizes for responsive design
      screens: {
        'xs': '475px',
        '3xl': '1600px',
      },
      // Z-index layers
      zIndex: {
        'background': '-1',
        'navigation': '1000',
        'modal': '2000',
        'cart': '2000',
        'demo': '3000',
        'notification': '4000',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    // Custom plugin for RTL support
    function({ addUtilities, theme }) {
      const newUtilities = {
        '.rtl': {
          direction: 'rtl',
        },
        '.ltr': {
          direction: 'ltr',
        },
        // Glassmorphism utilities
        '.glass': {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px) saturate(180%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.glass-hover': {
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
          borderColor: theme('colors.vision-green'),
        },
        // Gradient text utilities
        '.gradient-text': {
          background: 'linear-gradient(135deg, #ffffff 30%, #00d4aa 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
        '.gradient-text-primary': {
          background: 'linear-gradient(135deg, #00d4aa, #7c3aed)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
      };
      addUtilities(newUtilities);
    },
  ],
};