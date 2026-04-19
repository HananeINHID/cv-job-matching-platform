export default function ResultCard({ decisionFinale, confiance, audioValide }) {
  const confidence = confiance ?? null;
  const percent = confidence !== null ? Math.round(confidence * 100) : null;

  if (!audioValide) {
    return (
      <div className="w-full max-w-sm mx-auto">
        <div className="rounded-xl border border-red-100 bg-red-50 px-5 py-4">
          <p className="text-sm font-medium text-red-600">Invalid audio file</p>
          <p className="text-xs text-red-400 mt-0.5">Please try again with a different file.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm mx-auto">
      <div className="rounded-xl border border-gray-100 bg-white px-5 py-5">

        <p className="text-[11px] font-medium text-gray-400 uppercase tracking-widest mb-3">
          Detected Language
        </p>

        <p className="text-3xl font-semibold text-gray-900 tracking-tight leading-none">
          {decisionFinale ?? "—"}
        </p>

        {percent !== null && (
          <div className="flex items-center gap-2 mt-4">
            <div className="flex-1 h-1 rounded-full bg-gray-100">
              <div
                className="h-1 rounded-full bg-violet-500 transition-all duration-500"
                style={{ width: `${percent}%` }}
              />
            </div>
            <span className="text-xs text-gray-400 tabular-nums">{percent}%</span>
          </div>
        )}

      </div>
    </div>
  );
}
