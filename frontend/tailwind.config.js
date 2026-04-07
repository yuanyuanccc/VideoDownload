/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-bg': '#0f0f23',
        'deep-card': '#1a1a2e',
        'deep-border': '#2a2a4a',
        'accent-cyan': '#00d4ff',
        'accent-purple': '#7c3aed',
        'text-primary': '#e5e7eb',
        'text-secondary': '#9ca3af',
      }
    },
  },
  plugins: [],
}
