"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Message, { ChatMessage } from "./Message";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hej! Jag svarar på frågor om compileit.com. Fråga t.ex. om tjänster, branscher eller hur du kontaktar oss.",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // Use ref for sessionId so it's always current inside async callbacks without needing it as a dep
  const sessionIdRef = useRef<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  /** Append a token to the last assistant message (proper immutable update). */
  const appendToken = (text: string) => {
    setMessages((prev) => {
      const copy = [...prev];
      const last = copy[copy.length - 1];
      if (last?.role === "assistant") {
        copy[copy.length - 1] = { ...last, content: last.content + text };
      }
      return copy;
    });
  };

  /** Add source URLs to the last assistant message (proper immutable update). */
  const appendSources = (urls: string[]) => {
    setMessages((prev) => {
      const copy = [...prev];
      const last = copy[copy.length - 1];
      if (last?.role === "assistant") {
        copy[copy.length - 1] = {
          ...last,
          sources: Array.from(new Set([...(last.sources ?? []), ...urls])),
        };
      }
      return copy;
    });
  };

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput("");
    setIsLoading(true);

    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "", sources: [], pending: true },
    ]);

    try {
      const resp = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionIdRef.current }),
      });
      if (!resp.ok || !resp.body) throw new Error(`HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // SSE parser: split on blank lines, parse "event:" + "data:".
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // Normalise line endings: sse-starlette sends \r\n
        buffer = buffer.replace(/\r\n/g, "\n");
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const evt of events) {
          const lines = evt.split("\n");
          let eventType = "message";
          let dataLine = "";
          for (const line of lines) {
            if (line.startsWith("event:")) eventType = line.slice(6).trim();
            else if (line.startsWith("data:")) dataLine = line.slice(5).trim();
          }
          if (!dataLine) continue;
          let payload: Record<string, unknown>;
          try {
            payload = JSON.parse(dataLine);
          } catch {
            continue;
          }

          if (eventType === "session") {
            sessionIdRef.current = payload.session_id as string;
          } else if (eventType === "token") {
            appendToken(payload.text as string);
          } else if (
            eventType === "tool" &&
            payload.status === "end" &&
            payload.name === "search_compileit"
          ) {
            const urls = Array.from(
              new Set<string>(
                String(payload.output)
                  .split(/\s+/)
                  .filter((t) => t.startsWith("http"))
                  .map((u) => u.replace(/[)\].,]+$/, ""))
              )
            );
            if (urls.length) appendSources(urls);
          }
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setMessages((prev) => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last?.role === "assistant") {
          copy[copy.length - 1] = { ...last, content: `Något gick fel: ${msg}`, pending: false };
        }
        return copy;
      });
    } finally {
      setIsLoading(false);
      setMessages((prev) => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last?.role === "assistant") {
          copy[copy.length - 1] = { ...last, pending: false };
        }
        return copy;
      });
    }
  }, [input, isLoading]);

  return (
    <section className="mx-auto flex w-full max-w-3xl flex-1 flex-col overflow-hidden px-4 py-4">
      {/* Messages */}
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto pr-1 pb-2">
        {messages.map((m, i) => (
          <Message key={i} message={m} />
        ))}
      </div>

      {/* Input */}
      <form
        className="mt-3 flex gap-2 rounded-2xl border border-[#2a2a2a] bg-[#1a1a1a] p-2"
        onSubmit={(e) => {
          e.preventDefault();
          void send();
        }}
      >
        <input
          className="flex-1 rounded-xl border-0 bg-transparent px-3 py-2 text-sm text-white outline-none placeholder:text-gray-600"
          placeholder="Ställ en fråga om compileit.com..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="rounded-xl bg-[#2563eb] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#1d4ed8] disabled:opacity-40"
        >
          {isLoading ? (
            <span className="flex items-center gap-1.5">
              <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              Tänker
            </span>
          ) : "Skicka"}
        </button>
      </form>
    </section>
  );
}
