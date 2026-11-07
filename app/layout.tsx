import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "الأرشيف الفلكي الشامل — صور الكون",
  description:
    "أرشيف متجدد لصور الكون العلمية عبر كامل الطيف الكهرومغناطيسي: راديوي، تحت مليمتري، تحت أحمر، مرئي، فوق بنفسجي، سيني وغاما.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl">
      <body className="antialiased bg-[#07080d] text-white">{children}</body>
    </html>
  );
}
