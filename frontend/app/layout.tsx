import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShopSphere Analytics",
  description: "Association matrix dashboard and recommendation demo"
};

const nav = [
  { href: "/", label: "Overview" },
  { href: "/rules", label: "Rules" },
  { href: "/clusters", label: "Clusters" },
  { href: "/recommendations", label: "Demo Cart" }
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
            <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 md:flex-row md:items-center md:justify-between">
              <Link href="/" className="text-xl font-semibold tracking-tight text-ink">
                ShopSphere Analytics
              </Link>
              <nav className="flex flex-wrap gap-2 text-sm text-slate-600">
                {nav.map((item) => (
                  <Link key={item.href} href={item.href} className="rounded-full px-3 py-1.5 hover:bg-slate-100 hover:text-ink">
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
