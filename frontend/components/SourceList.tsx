export default function SourceList({ urls }: { urls: string[] }) {
  if (!urls?.length) return null;
  return (
    <div className="mt-3 border-t border-[#2a2a2a] pt-2">
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
        Källor
      </p>
      <ul className="space-y-1">
        {urls.map((url) => (
          <li key={url} className="flex items-start gap-1">
            <span className="mt-1 h-1 w-1 flex-shrink-0 rounded-full bg-[#2563eb]" />
            <a
              href={url}
              target="_blank"
              rel="noreferrer"
              className="break-all text-[11px] text-[#3b82f6] hover:text-[#60a5fa] hover:underline"
            >
              {url}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
