export default function PipelineStepper({ steps = [], activeStep = null }) {
  const visible = steps.slice(0, 3);

  return (
    <div className="w-full max-w-sm mx-auto py-2">
      {visible.map((step, index) => {
        const isActive = activeStep === step.etape;
        const isDone = activeStep !== null && step.etape < activeStep;
        const isLast = index === visible.length - 1;
        const percent = Math.round((step.confiance ?? 0) * 100);

        return (
          <div key={step.etape} className="flex gap-4">

            <div className="flex flex-col items-center">
              <div
                className={[
                  "w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-colors duration-200 text-[10px] font-semibold",
                  isActive
                    ? "bg-violet-600 text-white"
                    : isDone
                    ? "bg-violet-100 text-violet-600"
                    : "bg-gray-100 text-gray-400",
                ].join(" ")}
              >
                {isDone ? (
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5l2.5 2.5L8 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : (
                  step.etape
                )}
              </div>

              {!isLast && (
                <div className={["w-px flex-1 my-1", isDone ? "bg-violet-200" : "bg-gray-100"].join(" ")} />
              )}
            </div>

            <div className={["pb-5 flex-1", isLast ? "pb-0" : ""].join(" ")}>
              <div className="flex items-baseline justify-between gap-2">
                <div>
                  <span className="text-[11px] text-gray-400 font-medium">{step.modele}</span>
                  <p
                    className={[
                      "text-sm font-medium mt-0.5",
                      isActive ? "text-gray-900" : "text-gray-500",
                    ].join(" ")}
                  >
                    {step.prediction}
                  </p>
                </div>
                <span
                  className={[
                    "text-xs tabular-nums flex-shrink-0",
                    isActive ? "text-violet-600 font-medium" : "text-gray-300",
                  ].join(" ")}
                >
                  {percent}%
                </span>
              </div>
            </div>

          </div>
        );
      })}
    </div>
  );
}
