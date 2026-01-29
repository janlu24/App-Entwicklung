/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './**/forms.py',
    './**/views.py',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

