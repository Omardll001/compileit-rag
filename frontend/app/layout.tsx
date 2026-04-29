import "./globals.css";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "Compileit Chat – AI-assistent",
  description: "Ställ frågor om Compileits tjänster, branscher och kontaktuppgifter.",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="sv" className="h-full">
      <body className="h-full bg-[#111111] text-[#f5f5f5]">{children}</body>
    </html>
  );
}
