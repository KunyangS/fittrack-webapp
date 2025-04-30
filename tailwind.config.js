/**
 * tailwind.config.js
 * Config for Sports Data Analytics Web App
 *
 * Design System:
 * - Style: Modern, vibrant, user-friendly
 * - Shapes: Softly rounded overall. Large rounds for cards/containers,
 *           circular for small icon buttons, pill-shaped for larger action buttons.
 * - Elevation: Use of shadows for a layered, floating feel.
 * - Color: Energetic primary, complementary secondary, distinct accent,
 *          full range of neutrals, and clear semantic colors. Avoids monochrome.
 * - Typography: Clean sans-serif for body (Inter), distinct sans-serif for headings (Montserrat).
 */

// Import default theme and colors for extension
const defaultTheme = require('tailwindcss/defaultTheme');
const colors = require('tailwindcss/colors');

module.exports = {
  // Purge unused styles in production for performance.
  content: [
    './src/**/*.{js,jsx,ts,tsx,html,vue}', // Covers common frontend frameworks/files
    './public/index.html',
  ],

  theme: {
    // Extend the default Tailwind theme
    extend: {
      // --- COLOR PALETTE ---
      // Define semantic color names using Tailwind's rich palettes for flexibility.
      colors: {
        // Primary: Energetic and trustworthy (e.g., Teal or a vibrant Blue)
        primary: {
          light: colors.teal[400], // Lighter shade for hover/accents
          DEFAULT: colors.teal[600], // Main primary color
          dark: colors.teal[700],  // Darker shade for active/borders
        },
        // Secondary: Complementary and action-oriented (e.g., Amber or Orange)
        secondary: {
          light: colors.amber[300],
          DEFAULT: colors.amber[500],
          dark: colors.amber[600],
        },
        // Accent: For highlights, callouts, or specific UI elements (e.g., Pink or Lime)
        accent: {
          light: colors.pink[300],
          DEFAULT: colors.pink[500],
          dark: colors.pink[600],
        },
        // Neutral: Backgrounds, text, borders (Using Slate for a cool, modern feel)
        neutral: colors.slate, // Provides shades 50-900
        // Semantic Colors: For status indicators, validation, etc.
        success: colors.green[500],
        warning: colors.yellow[500], // Changed from Amber for better distinction from secondary
        error: colors.red[500],
        info: colors.sky[500], // Added an info color

        // Custom specific-use colors if needed
        'light-bg': colors.slate[50],   // Very light background
        'muted-text': colors.slate[500], // Softer text color
        
        // --- TAG SELECTION COLORS ---
        'tag-selected': {
          bg: colors.teal[600],
          text: colors.white,
          border: colors.teal[600],
          glow: 'rgba(13, 148, 136, 0.4)'
        },
        'tag-selected-dark': {
          bg: colors.teal[400],
          text: colors.slate[800],
          border: colors.teal[400],
          glow: 'rgba(45, 212, 191, 0.5)'
        },
        'tag-hover': {
          bg: 'rgba(13, 148, 136, 0.15)',
          dark: 'rgba(45, 212, 191, 0.2)'
        }
      },

      // --- BORDER RADIUS ---
      // System for rounded corners, emphasizing softness.
      borderRadius: {
        'sm': '0.25rem',   // Subtle rounding (inputs, tags)
        'md': '0.5rem',    // Default rounding (buttons, smaller elements) - Slightly softer than default
        'lg': '0.75rem',   // Medium rounding (cards, containers)
        'xl': '1.25rem',   // Large rounding (prominent cards, modals)
        '2xl': '2rem',     // Extra large rounding (decorative elements)
        'full': '9999px',  // Circular / Pill shapes
      },

      // --- BOX SHADOW ---
      // System for elevation and floating effects. Softer than default.
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -1px rgba(0, 0, 0, 0.04)', // Softer card shadow
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.04)', // More pronounced
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.07), 0 10px 10px -5px rgba(0, 0, 0, 0.03)', // Strongest lift
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        'interactive': `0 6px 12px -2px ${colors.teal[600]}30`, // Subtle colored shadow on interaction (adjust color/opacity)
        'none': 'none',
        'tag-selected': '0 2px 4px rgba(0, 0, 0, 0.2), 0 0 0 2px rgba(13, 148, 136, 0.25)',
        'tag-selected-dark': '0 2px 4px rgba(0, 0, 0, 0.3), 0 0 12px rgba(45, 212, 191, 0.5)',
      },

      // --- TYPOGRAPHY ---
      // Modern font stack.
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans], // Main body text
        heading: ['Montserrat', ...defaultTheme.fontFamily.sans], // Headings
        mono: ['Fira Code', ...defaultTheme.fontFamily.mono], // Code blocks (Fira Code recommended for ligatures)
      },

      // --- SPACING ---
      // Extend spacing scale for more layout flexibility if needed.
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '30': '7.5rem',
        // Add specific layout spacings if known (e.g., 'sidebar': '16rem')
      },

      // --- TRANSITIONS ---
      // Default timing function and duration for smooth UI interactions.
      transitionTimingFunction: {
        'DEFAULT': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'in': 'cubic-bezier(0.4, 0, 1, 1)',
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
      },
      transitionDuration: {
        'DEFAULT': '200ms', // Slightly faster default
        'fast': '100ms',
        'slow': '300ms',
      },

      // --- OTHER UTILITIES ---
      minHeight: {
        'screen-1/2': '50vh',
        'screen-2/3': '66vh',
      },
      maxWidth: {
        'prose': '70ch', // Good readability width for text blocks
        'screen-3xl': '1920px', // Larger screen support if needed
      },
    },

    // --- RESPONSIVE BREAKPOINTS ---
    // Using default Tailwind breakpoints, generally sufficient. Adjust if needed.
    screens: {
      ...defaultTheme.screens,
      // Example: Add a smaller breakpoint if designing mobile-first very granularly
      // 'xs': '480px',
    },
  },

  // --- PLUGINS ---
  // Essential plugins for modern web development.
  plugins: [
    require('@tailwindcss/forms')({
      // Strategy: 'class' is recommended to avoid global overrides
      // Apply form styles using classes like `form-input`, `form-select`, etc.
      strategy: 'class',
    }),
    require('@tailwindcss/typography'), // Provides `prose` classes for styling markdown/HTML content
    require('@tailwindcss/aspect-ratio'), // Useful for responsive media/visualizations
    
    // Add plugin for CSS variables integration
    function({ addBase, theme }) {
      addBase({
        ':root': {
          '--primary-color': theme('colors.primary.DEFAULT'),
          '--primary-color-rgb': '13, 148, 136', // RGB values for teal-600
          '--primary-light': theme('colors.primary.light'),
          '--primary-light-rgb': '45, 212, 191', // RGB values for teal-400
          '--primary-dark': theme('colors.primary.dark'),
          '--secondary-color': theme('colors.secondary.DEFAULT'),
          '--secondary-light': theme('colors.secondary.light'),
          '--accent-color': theme('colors.accent.DEFAULT'),
          
          // Tag selection specific variables
          '--tag-selected-bg': theme('colors.tag-selected.bg'),
          '--tag-selected-text': theme('colors.tag-selected.text'),
          '--tag-selected-border': theme('colors.tag-selected.border'),
          '--tag-selected-glow': theme('colors.tag-selected.glow'),
          '--tag-hover-bg': theme('colors.tag-hover.bg'),
        },
        '.dark': {
          '--primary-color': theme('colors.primary.light'),
          '--primary-color-rgb': '45, 212, 191', // RGB values for teal-400
          '--primary-light': theme('colors.primary.DEFAULT'),
          '--primary-light-rgb': '13, 148, 136', // RGB values for teal-600
          '--primary-dark': theme('colors.primary.light'),
          '--secondary-color': theme('colors.secondary.light'),
          '--secondary-light': theme('colors.secondary.DEFAULT'),
          '--accent-color': theme('colors.accent.light'),
          
          // Tag selection specific variables for dark mode
          '--tag-selected-bg': theme('colors.tag-selected-dark.bg'),
          '--tag-selected-text': theme('colors.tag-selected-dark.text'),
          '--tag-selected-border': theme('colors.tag-selected-dark.border'),
          '--tag-selected-glow': theme('colors.tag-selected-dark.glow'),
          '--tag-hover-bg': theme('colors.tag-hover.dark'),
        }
      });
    }
  ],
}