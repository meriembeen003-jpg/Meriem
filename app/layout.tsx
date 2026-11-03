import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "مِرصد — من المصدر، لا من الصدى",
  description: "مساحة عربية لمتابعة المصادر العامة والتحقق من سياقها، مع دفتر ملاحظات خاص على جهازك.",
  applicationName: "مِرصد",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, title: "مِرصد", statusBarStyle: "default" },
  icons: { icon: "/icon.svg", apple: "/icon.svg" },
};

export const viewport: Viewport = {
  themeColor: "#176b50",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
