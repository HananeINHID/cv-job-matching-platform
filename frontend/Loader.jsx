import { useEffect, useState } from "react";

const STAGES = [
  "Routing audio...",
  "Identifying language family...",
  "Detecting dialect...",
];

export default function Loader() {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    if (stage >= STAGES.length - 1) return;
    const t = setTimeout(() => setStage((s) => s + 1), 1800);
    return () => clearTimeout(t);
  }, [stage]);

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm text-center">

        <div className="flex justify-center mb-8">
          <div className="relative w-10 h-10">
            <div className="absolute inset-0 rounded-full border-2 border-gray-100" />
            <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-violet-500 animate-spin" />
          </div>
        </div>

        <p className="text-sm font-medium text-gray-700 mb-1">Processing audio</p>
        <p className="text-xs text-gray-400 transition-all duration-300">
          {STAGES[stage]}
        </p>

        <div className="flex justify-center gap-1.5 mt-6">
          {STAGES.map((_, i) => (
            <div
              key={i}
              className={[
                "h-1 rounded-full transition-all duration-500",
                i <= stage ? "w-6 bg-violet-500" : "w-2 bg-gray-200",
              ].join(" ")}
            />
          ))}
        </div>

      </div>
    </div>
  );
}
