/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Fraunces"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: '#12261F',        // deep pine — primary text
        pine: '#1C4B3A',       // brand green
        moss: '#2F7A5B',       // lighter green accent
        clay: '#D98E4A',       // warm accent (CTAs, highlights)
        cream: '#F6F3EC',      // page background
        card: '#FFFFFF',
        mist: '#EAEAE0',       // borders / dividers
        sage: '#7C9A8E',       // muted text
      },
      boxShadow: {
        soft: '0 1px 2px rgba(18,38,31,0.04), 0 8px 24px rgba(18,38,31,0.06)',
        lift: '0 2px 4px rgba(18,38,31,0.06), 0 14px 40px rgba(18,38,31,0.10)',
      },
      borderRadius: { xl2: '1.25rem' },
    },
  },
  plugins: [],
}
