import Gallery from "./Gallery";

export const metadata = { title: "الأرشيف الفلكي الشامل — صور الكون" };

export default function Page() {
  return (
    <main className="min-h-screen bg-[#07080d]">
      <Gallery />
    </main>
  );
}
