import ChatWindow from "@/components/ChatWindow";

export default function Page() {
  return (
    <main className="flex h-full flex-col bg-[#111111]">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-[#2a2a2a] bg-[#111111]">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            {/* Compileit logo mark */}
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[#2563eb]">
              <span className="text-sm font-bold text-white">C</span>
            </div>
            <span className="text-base font-semibold tracking-tight text-white">Compileit</span>
            <span className="ml-1 rounded border border-[#2a2a2a] px-1.5 py-0.5 text-[10px] font-medium text-gray-400">
              AI Chat
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className="flex h-2 w-2 rounded-full bg-green-500" title="Backend online" />
            <span className="text-gray-600">online</span>
          </div>
        </div>
      </header>

      <ChatWindow />

      {/* Footer */}
      <footer className="flex-shrink-0 border-t border-[#2a2a2a] py-2 text-center text-[11px] text-gray-600">
        © Compileit 2026 · Svar baserade på indexerat innehåll från{" "}
        <a href="https://compileit.com" target="_blank" rel="noreferrer" className="text-[#2563eb] hover:underline">
          compileit.com
        </a>
      </footer>
    </main>
  );
}
