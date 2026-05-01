/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        apple: {
          bg: "#F5F5F7",
          card: "#FFFFFF",
          accent: "#007AFF",
          text: "#1D1D1F",
          secondary: "#6E6E73",
          disabled: "#C7C7CC",
          divider: "#E5E5EA",
          green: "#34C759",
          orange: "#FF9500",
          red: "#FF3B30",
        },
      },
      borderRadius: {
        apple: "20px",
        "apple-sm": "12px",
        "apple-xs": "10px",
      },
      fontFamily: {
        apple: [
          '-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"',
          '"SF Pro Text"', '"Helvetica Neue"', 'Helvetica', 'Arial', 'sans-serif',
        ],
      },
      boxShadow: {
        apple: "0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)",
        "apple-lg": "0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06)",
      },
      backdropBlur: {
        apple: "20px",
      },
    },
  },
  plugins: [],
};
