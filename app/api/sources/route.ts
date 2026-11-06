import { NextResponse } from "next/server";
import { getDb, saveDb } from "@/lib/server/db";
import { SECONDARY_RUMOR_PATTERNS } from "@/lib/data/root-sources";
import { RootSource, SourceCategory } from "@/lib/types/geointel";

export const dynamic = "force-dynamic";

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const db = getDb();

    if (body.action === "toggle" && body.sourceId) {
      const target = db.rootSources.find((s) => s.id === body.sourceId);
      if (!target) {
        return NextResponse.json(
          { ok: false, error: "المصدر غير موجود" },
          { status: 404 }
        );
      }
      target.enabled = Boolean(body.enabled);
      saveDb(db);
      return NextResponse.json({ ok: true, rootSources: db.rootSources });
    }

    if (body.action === "add") {
      const rssUrl = String(body.rssUrl || "").trim();
      const nameAr = String(body.nameAr || "").trim();
      const shortCode = String(body.shortCode || "ROOT")
        .trim()
        .toUpperCase()
        .slice(0, 8);

      if (!rssUrl || !nameAr) {
        return NextResponse.json(
          { ok: false, error: "اسم المصدر الأم ورابط RSS الرسمي مطلوبان." },
          { status: 400 }
        );
      }

      let hostname = "";
      try {
        const parsed = new URL(rssUrl);
        if (parsed.protocol !== "https:" && parsed.protocol !== "http:") {
          throw new Error("Invalid protocol");
        }
        hostname = parsed.hostname.toLowerCase().replace(/^www\./, "");
      } catch {
        return NextResponse.json(
          { ok: false, error: "يرجى إدخال رابط RSS رسمي صالح (HTTPS)." },
          { status: 400 }
        );
      }

      // Enforce Root-Source Gatekeeper: block social/blog secondary aggregators
      const blocked = [
        ...SECONDARY_RUMOR_PATTERNS,
        "t.me",
        "telegram.me",
        "x.com",
        "twitter.com",
        "facebook.com",
        "youtube.com",
      ].some((b) => hostname.includes(b));

      if (blocked) {
        db.rejectedNoise.unshift({
          id: `rej-${Date.now()}`,
          timestampUtc: new Date().toISOString(),
          originDomainOrHandle: hostname,
          rawHeadline: `محاولة إضافة مصدر غير أولي: ${nameAr} (${rssUrl})`,
          rejectionReasonAr:
            "رفضته بوابة المصادر الأم الصارمة: يُمنع إدراج منصات التواصل أو المدونات الثانوية؛ يُقبل فقط النطاق الرسمي لوكالة أنباء أم أو وزارة دفاع أو منظمة دولية.",
          ruleCode: "NON_ROOT_AGGREGATOR",
        });
        saveDb(db);

        return NextResponse.json(
          {
            ok: false,
            error:
              "رفضت بوابة الدقة هذا الرابط لأنه منصة تواصل/تجميع ثانوي وليس نطاقًا رسميًا لمصدر أم معتمد.",
          },
          { status: 422 }
        );
      }

      const category: SourceCategory = body.category || "GLOBAL_WIRE_AGENCY";
      const newSource: RootSource = {
        id: `custom-${Date.now()}`,
        shortCode,
        nameAr,
        nameOriginal: body.nameOriginal || nameAr,
        category,
        countryOrOrgAr: body.countryOrOrgAr || hostname,
        officialDomain: hostname,
        rssUrl,
        language: body.language || "en",
        reliabilityBaseScore: category === "DEFENSE_MINISTRY" ? 89 : 93,
        biasNatureAr:
          body.biasNatureAr ||
          "مصدر رسمي مضاف يدويًا — يخضع لفلتر التقاطع الميداني في راصد",
        requiresCrossCheck: category === "DEFENSE_MINISTRY",
        enabled: true,
        capturedCount: 0,
      };

      db.rootSources.unshift(newSource);
      saveDb(db);

      return NextResponse.json({
        ok: true,
        rootSources: db.rootSources,
      });
    }

    return NextResponse.json(
      { ok: false, error: "عملية غير معروفة" },
      { status: 400 }
    );
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: String(err) },
      { status: 500 }
    );
  }
}
