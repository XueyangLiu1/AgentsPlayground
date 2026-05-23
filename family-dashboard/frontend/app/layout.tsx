import "./globals.css";
import type { Metadata, Viewport } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Family Dashboard",
  description: "Track credit card benefits for the family",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#3b82f6",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="font-semibold text-lg">
              🏠 Family Dashboard
            </Link>
            <nav className="flex gap-3 text-sm">
              <Link href="/" className="hover:text-blue-600">Overview</Link>
              <Link href="/holder/all" className="hover:text-blue-600">Holders</Link>
              <Link href="/new" className="btn btn-primary">+ New</Link>
            </nav>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
