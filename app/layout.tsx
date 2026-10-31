import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "مدار | أطلس الدليل العلمي",
  description: "مسار زمني عربي موثق من الكون المبكر إلى نشأة الحياة والتطور البيولوجي، مع أوراق علمية وأدلة رصدية ومحاكاة.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
