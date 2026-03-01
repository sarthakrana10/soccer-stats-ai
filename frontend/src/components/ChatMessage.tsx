import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface Message {
  role: "user" | "assistant";
  content: string;
  tools_used?: string[];
  elapsed_seconds?: number;
}

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} px-4 py-2`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-tr-sm"
            : "bg-gray-700 text-gray-100 rounded-tl-sm"
        }`}
      >
        {isUser ? (
          <p className="text-sm">{message.content}</p>
        ) : (
          <div className="markdown-body text-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        {!isUser && message.tools_used && message.tools_used.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-600 text-xs text-gray-400">
            Tools: {message.tools_used.join(", ")}
            {message.elapsed_seconds != null && (
              <span className="ml-2">· {message.elapsed_seconds}s</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
