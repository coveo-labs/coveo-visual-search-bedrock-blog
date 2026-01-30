/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        luxury: {
          gold: '#D4AF37',
          darkGold: '#B8941F',
          cream: '#F5F5DC',
          charcoal: '#2C2C2C',
          black: '#0A0A0A',
          white: '#FAFAFA'
        }
      },
      fontFamily: {
        serif: ['Playfair Display', 'serif'],
        sans: ['Inter', 'sans-serif']
      }
    },
  },
  plugins: [],
}
