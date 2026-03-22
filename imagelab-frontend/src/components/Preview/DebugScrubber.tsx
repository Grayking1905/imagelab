import { usePipelineStore } from "../../store/pipelineStore";
import { ChevronLeft, ChevronRight, X, Play } from "lucide-react";

export default function DebugScrubber() {
  const { debugStates, debugCursor, stepForward, stepBackward, exitDebug } = usePipelineStore();

  if (!debugStates || debugStates.length === 0) return null;

  const currentState = debugStates[debugCursor];

  return (
    <div className="flex flex-col h-full bg-gray-50 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px]">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-white border-b border-amber-200">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-5 h-5 rounded bg-amber-100 text-amber-700 text-xs font-bold font-mono">
            {debugCursor}
          </span>
          <span className="text-sm font-semibold text-gray-700 font-mono">
            {currentState.operator_type}
          </span>
        </div>
        <button
          onClick={exitDebug}
          className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600 transition-colors"
          title="Exit Debug Mode (Esc)"
        >
          <X size={16} />
        </button>
      </div>

      {/* Image Display */}
      <div className="flex-1 flex items-center justify-center p-4 min-h-0 overflow-auto">
        <img
          src={`data:image/jpeg;base64,${currentState.image}`}
          alt={`Debug step ${debugCursor}`}
          className="max-w-full max-h-full object-contain shadow-sm border border-gray-200 rounded"
        />
      </div>

      {/* Footer / Scrubber Controls */}
      <div className="p-3 bg-white border-t border-gray-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <div className="flex items-center gap-3">
          <button
            onClick={stepBackward}
            disabled={debugCursor === 0}
            className="p-1.5 rounded hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent text-gray-600 transition-colors"
            title="Previous Step (Left Arrow)"
          >
            <ChevronLeft size={20} />
          </button>

          <div className="flex-1 relative flex items-center group cursor-pointer h-6">
            {/* Scrubber track */}
            <div className="absolute left-0 right-0 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-400 rounded-full transition-all duration-200"
                style={{
                  width: `${(debugCursor / Math.max(1, debugStates.length - 1)) * 100}%`,
                }}
              />
            </div>
            {/* Interactive ticks */}
            <div className="absolute inset-x-0 inset-y-0 flex justify-between items-center px-1">
              {debugStates.map((_, i) => (
                <div
                  key={i}
                  className={`w-1.5 h-1.5 rounded-full z-10 transition-colors duration-200 ${
                    i <= debugCursor ? "bg-amber-600" : "bg-gray-300"
                  } ${i === debugCursor ? "ring-4 ring-amber-100 scale-150" : ""}`}
                />
              ))}
            </div>
          </div>

          <button
            onClick={stepForward}
            disabled={debugCursor === debugStates.length - 1}
            className="p-1.5 rounded hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent text-gray-600 transition-colors"
            title="Next Step (Right Arrow)"
          >
            {debugCursor === debugStates.length - 1 ? (
              <Play size={20} />
            ) : (
              <ChevronRight size={20} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
