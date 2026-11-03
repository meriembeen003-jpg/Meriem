import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "مِرصد — تصريحات من المصادر الأصلية",
    short_name: "مِرصد",
    description: "نشرة مباشرة للمواد المنشورة من الجهات العامة.",
    lang: "ar",
    dir: "rtl",
    start_url: "/",
    display: "standalone",
    background_color: "#f6f8f5",
    theme_color: "#176b50",
    orientation: "portrait-primary",
    icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any" }],
  };
}
