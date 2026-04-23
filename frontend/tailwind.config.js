/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f17",
        panel: "#111827",
        panel2: "#1f2937",
        border: "#1f2937",
        accent: "#22d3ee",
        accent2: "#a78bfa",
        danger: "#ef4444",
        warn: "#f59e0b",
        ok: "#10b981",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(34, 211, 238, 0.15), 0 8px 32px rgba(34, 211, 238, 0.08)",
      },
    },
  },
  plugins: [],
};
