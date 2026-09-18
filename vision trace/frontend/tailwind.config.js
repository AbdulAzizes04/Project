/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        forensic: {
          bg: "#050b18",
          panel: "#0a1628",
          card: "#0f1f3d",
          border: "#1a2a4a",
          accent: "#00d4ff",
          cyan: "#00d4ff",
          green: "#00ff88",
          yellow: "#ffc107",
          red: "#ff4444",
          navy: "#0c1a35",
          "text-primary": "#e2e8f0",
          "text-secondary": "#94a3b8",
          "text-muted": "#4a5568",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "monospace"],
        sans: ["'Inter'", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
        "scan": "scan 3s linear infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-in": "slideIn 0.3s ease-out",
      },
      keyframes: {
        glow: {
          from: { textShadow: "0 0 10px #00d4ff, 0 0 20px #00d4ff" },
          to: { textShadow: "0 0 20px #00d4ff, 0 0 40px #00d4ff, 0 0 60px #00d4ff" },
        },
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        fadeIn: {
          from: { opacity: 0, transform: "translateY(8px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
        slideIn: {
          from: { opacity: 0, transform: "translateX(-12px)" },
          to: { opacity: 1, transform: "translateX(0)" },
        },
      },
      boxShadow: {
        "cyan-glow": "0 0 20px rgba(0,212,255,0.3)",
        "green-glow": "0 0 20px rgba(0,255,136,0.3)",
        "card": "0 4px 24px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
};
