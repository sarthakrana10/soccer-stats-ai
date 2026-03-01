import { useState, useEffect } from "react";

export default function LoadingIndicator() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-start gap-3 px-4 py-3">
      <div className="bg-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 text-gray-300">
        <div className="flex items-center gap-2">
          <span className="text-sm">Thinking</span>
          <div className="flex gap-1">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
          <span className="text-xs text-gray-500 ml-1">{seconds}s</span>
        </div>
      </div>
    </div>
  );
}
