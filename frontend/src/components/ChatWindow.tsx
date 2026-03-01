import { useState, useRef, useEffect } from "react";
import { sendMessage } from "../api/client";
import ChatMessage, { Message } from "./ChatMessage";
import ChatInput from "./ChatInput";
import ExamplePrompts from "./ExamplePrompts";
import LoadingIndicator from "./LoadingIndicator";

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleNewChat = () => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setMessages([]);
    setLoading(false);
  };

  const handleSend = async (text: string) => {
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await sendMessage(text, controller.signal);
      const aiMsg: Message = {
        role: "assistant",
        content: res.answer,
        tools_used: res.tools_used,
        elapsed_seconds: res.elapsed_seconds,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      const errorMsg: Message = {
        role: "assistant",
        content: `Something went wrong. Please try again.\n\n\`${err}\``,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      abortRef.current = null;
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
        <div className="w-20" />
        <h1 className="text-lg font-semibold text-gray-100">Soccer Stats AI</h1>
        {messages.length > 0 || loading ? (
          <button
            onClick={handleNewChat}
            className="w-20 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            New Chat
          </button>
        ) : (
          <div className="w-20" />
        )}
      </header>

      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 && !loading ? (
          <ExamplePrompts onSelect={handleSend} />
        ) : (
          <div className="max-w-4xl mx-auto py-4">
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} />
            ))}
            {loading && <LoadingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="max-w-4xl mx-auto w-full">
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  );
}
