"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken, getRole } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  useEffect(() => {
    const token = getToken();
    const role = getRole();
    if (!token) {
      router.replace("/login");
    } else if (role === "ADMIN") {
      router.replace("/admin");
    } else {
      router.replace("/dashboard");
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin" />
        <p className="text-slate-400 text-sm">Loading CareerAI...</p>
      </div>
    </div>
  );
}
