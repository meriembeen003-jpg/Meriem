import Uploader from "./Uploader";

export const metadata = { title: "رفع الأرشيف الفلكي — Google Drive" };

export default function Page() {
  return (
    <main className="min-h-screen bg-[#07080d]">
      <Uploader />
    </main>
  );
}
