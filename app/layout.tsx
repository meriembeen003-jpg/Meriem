import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Console — recherche & audit scientifiques",
  description:
    "Recherche fédérée (OpenAlex, Crossref, Europe PMC) et audit statistique d'articles : recalcul APA, GRIM, GRIMMER, SPRITE. 142 outils GitHub vérifiés.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body className="antialiased">{children}</body>
    </html>
  );
}
