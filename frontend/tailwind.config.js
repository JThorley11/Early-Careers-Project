/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // Scan all your React components
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#3b82f6",   // Example custom color
        secondary: "#fbbf24",
      },
      borderRadius: {
        xl: "1rem",
      },
    },
  },
  plugins: [],
};