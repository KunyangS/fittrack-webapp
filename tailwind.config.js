/** 
 * tailwind.config.js
 * Config for Sports Data Analytics Web App
 * Modern, consistent style with soft rounded corners, color system, and best practices.
 */

module.exports = {
    // Purge unused styles in production for performance.
    content: [
      './src/**/*.{js,jsx,ts,tsx,html,vue}',
      './public/index.html',
    ],
  
    theme: {
      // Design tokens for unified and reusable style
      extend: {
        // Main color palette for the site
        colors: {
          primary:   '#2563eb', // Blue-600, modern tech feeling
          secondary: '#22d3ee', // Cyan-400, vibrant accent
          accent:    '#f472b6', // Pink-400, for highlights
          muted:     '#f1f5f9', // Slate-100, background/light sections
          dark:      '#0f172a', // Slate-900, text/contrast blocks
          success:   '#22c55e', // Green-500, e.g. completed uploads
          warning:   '#fbbf24', // Amber-400, e.g. caution info
          error:     '#ef4444', // Red-500, error status
        },
  
        // Soft, modern rounded corners system
        borderRadius: {
          md:  '0.75rem',  // For cards and main blocks
          lg:  '1.2rem',
          xl:  '2rem',     // For highlighted blocks, modals, etc.
          full: '9999px',  // For avatars, pills, chips, etc.
        },
  
        // Spacing scale extension (for comfortable padding/margin)
        spacing: {
          '18': '4.5rem',
          '22': '5.5rem',
          '30': '7.5rem',
        },
  
        // Custom font families for a modern appearance
        fontFamily: {
          sans:   ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
          heading:['Montserrat', 'ui-sans-serif', 'system-ui', 'sans-serif'],
          mono:   ['Fira Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        },
  
        // Box shadows for cards and elevated components, keeping them soft
        boxShadow: {
          card: '0 2px 16px rgba(37, 99, 235, 0.07)',
          soft: '0 4px 24px 0 rgba(0,0,0,0.06)',
        },
  
        // Minimum height for hero and visualization sections
        minHeight: {
          'screen-1/2': '50vh',
          'screen-2/3': '66vh',
        },
  
        // Custom max-widths for cards/layouts
        maxWidth: {
          'xs': '20rem',
          'md': '32rem',
          'screen-2xl': '1440px',
        },
      },
  
      // Responsive breakpoints (modern device-centric)
      screens: {
        'sm': '480px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  
    plugins: [
      // Best-practice plugins for form/typography etc.
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('@tailwindcss/aspect-ratio'),
    ],
  }