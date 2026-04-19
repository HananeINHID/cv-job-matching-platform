import { Mic, Upload } from "lucide-react";

export default function HomePage({ onRecord, onUpload }) {
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm text-center">

        <div className="mb-10">
          <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-violet-50 mb-6">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="7" y="1" width="6" height="11" rx="3" fill="#7C3AED" />
              <path d="M3 9a7 7 0 0 0 14 0" stroke="#7C3AED" strokeWidth="1.5" strokeLinecap="round" />
              <line x1="10" y1="16" x2="10" y2="19" stroke="#7C3AED" strokeWidth="1.5" strokeLinecap="round" />
              <line x1="7" y1="19" x2="13" y2="19" stroke="#7C3AED" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>

          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight mb-2">
            LangDetect
          </h1>
          <p className="text-sm text-gray-400 leading-relaxed">
            Identify spoken language and dialect<br />from any audio file or recording.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <button
            onClick={onRecord}
            className="flex items-center justify-center gap-2.5 w-full py-3 px-5 bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium rounded-xl transition-colors duration-150"
          >
            <Mic size={15} strokeWidth={2} />
            Record Audio
          </button>

          <button
            onClick={onUpload}
            className="flex items-center justify-center gap-2.5 w-full py-3 px-5 bg-white hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-xl border border-gray-200 transition-colors duration-150"
          >
            <Upload size={15} strokeWidth={2} />
            Upload File
          </button>
        </div>

        <p className="mt-8 text-xs text-gray-300">
          Supports MP3, WAV, M4A · Max 25MB
        </p>

      </div>
    </div>
  );
}
