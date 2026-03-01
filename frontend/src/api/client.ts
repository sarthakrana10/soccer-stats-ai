const API_URL = "http://localhost:8000";

export interface ChatResponse {
  answer: string;
  tools_used: string[];
  elapsed_seconds: number;
}

export async function sendMessage(
  message: string,
  signal?: AbortSignal
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}
