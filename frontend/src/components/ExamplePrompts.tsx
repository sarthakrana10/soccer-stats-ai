const PROMPTS = [
  "Show me the Premier League standings",
  "How many goals has Salah scored this season?",
  "Compare Arsenal and Chelsea team stats",
  "Who are the top scorers in La Liga?",
  "Liverpool vs Man United head to head",
  "How has Lamine Yamal performed in his last 5 games?",
];

interface Props {
  onSelect: (prompt: string) => void;
}

export default function ExamplePrompts({ onSelect }: Props) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 px-4">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-100 mb-2">Soccer Stats AI</h1>
        <p className="text-gray-400">Ask anything about football statistics</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
        {PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSelect(prompt)}
            className="text-left px-4 py-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-sm text-gray-300 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
