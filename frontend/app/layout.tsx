import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Transcriber App" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <main className="mx-auto max-w-3xl p-6">{children}</main>
      </body>
    </html>
  );
}
