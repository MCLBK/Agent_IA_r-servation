import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GrowUp AI — Assistant Voyage",
  description: "Plateforme SaaS de reservation de voyages assistee par intelligence artificielle",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className="antialiased">{children}</body>
    </html>
  );
}
