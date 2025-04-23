/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",   // Flask HTML templates
    "./app/static/js/**/*.js",     // JS files (if you use any)
    "./app/**/*.py"                // Optional: useful if you use Tailwind classes in strings in Python
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}