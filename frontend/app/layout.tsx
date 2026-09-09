import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "AI Project Architect", description: "Turn software ideas into coherent engineering blueprints." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

