import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerAI — Explainable AI Career Recommendation System",
  description:
    "AI-powered, explainable career recommendation platform for B.Tech students. Powered by SHAP, LIME, and Skill Analytics.",
  keywords: "career recommendation, explainable AI, SHAP, LIME, skill gap analysis, student career guidance",
  openGraph: {
    title: "CareerAI — Explainable Career Recommendations",
    description: "Personalized AI career recommendations with transparent SHAP & LIME explanations.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light bg-white">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="antialiased bg-white text-slate-900">
        {children}
      </body>
    </html>
  );
}
