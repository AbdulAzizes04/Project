import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import TopHeader from "@/components/layout/TopHeader";
import DisclaimerBanner from "@/components/layout/DisclaimerBanner";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "VisionTrace AI | Intelligent Forensic Surveillance & Evidence Analysis",
  description: "Advanced AI-assisted surveillance platform for crime investigation, person-of-interest tracking, gait kinematics, and rapid evidence synthesis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} bg-[#07090e] text-slate-100 min-h-screen font-sans antialiased bg-surveillance-grid flex`}>
        {/* Sidebar Navigation */}
        <Sidebar />

        {/* Main Content Viewport (offset by 64 = 256px on md+) */}
        <div className="flex-1 flex flex-col min-h-screen md:pl-64 transition-all duration-300">
          <TopHeader />
          <DisclaimerBanner />
          <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="w-full border-t border-white/10 bg-[#07090e] py-5 px-6 text-center text-xs text-slate-500 font-mono no-print">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
              <p>© 2026 VisionTrace AI Forensic System. All analytical conclusions require certified human verification.</p>
              <div className="flex items-center space-x-4">
                <span className="text-[#00e5ff]">v1.0.0-PRO</span>
                <span>•</span>
                <span>YOLOv8 + MediaPipe Pose + ByteTrack</span>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
