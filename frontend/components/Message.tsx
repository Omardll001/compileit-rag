import SourceList from "./SourceList";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  pending?: boolean;
};

export default function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mr-2 mt-1 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md bg-[#2563eb]">
          <span className="text-xs font-bold text-white">C</span>
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "rounded-tr-sm bg-[#2563eb] text-white"
            : "rounded-tl-sm border border-[#2a2a2a] bg-[#1a1a1a] text-gray-100"
        }`}
      >
        {message.content ? (
          <span className={!isUser && message.pending ? "typing-cursor" : ""}>{message.content}</span>
        ) : message.pending ? (
          <TypingDots />
        ) : null}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceList urls={message.sources} />
        )}
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1 py-1">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-500 [animation-delay:-0.3s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-500 [animation-delay:-0.15s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-500" />
    </span>
  );
}

