import React from "react";
import { AlertCircle } from "lucide-react";

export default function DisclaimerBanner({ text }) {
  return (
    <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200/90 text-xs">
      <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-amber-300 mr-1">Medical Research Disclaimer:</span>
        <span>
          {text ||
            "This software is developed strictly for final-year engineering research and educational purposes. It has not been clinically certified by regulatory authorities (FDA/CE) and must never be utilized for patient diagnosis or medical treatment decisions."}
        </span>
      </div>
    </div>
  );
}
