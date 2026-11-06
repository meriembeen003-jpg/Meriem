import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "راصِد | RASED — منظومة الرصد والإنذار المبكر للحروب الجيوسياسية",
  description:
    "تطبيق أندرويد وخادم سحابي دائم التأهب لرصد الأخبار الجيوسياسية والعسكرية من المصادر الأم فقط، التحقق من الفيديوهات والنصوص، وإرسال إشعارات وتفسيرات دقيقة بالعربية.",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#060911",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className="dark">
      <body className="bg-[#060911] text-slate-100 antialiased selection:bg-emerald-500/30 selection:text-emerald-200">
        {children}
      </body>
    </html>
  );
}
