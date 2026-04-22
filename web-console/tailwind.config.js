/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        violet: {
          400: '#9F4FFF',
          500: '#7F00FF',
          600: '#6600CC',
          700: '#4D0099',
        },
      },
    },
  },
  plugins: [],
}
