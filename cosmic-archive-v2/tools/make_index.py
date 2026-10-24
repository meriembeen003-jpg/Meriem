#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_index.py — render INDEX.md, MANIFEST.csv, per-event README.md and
BLOCKED.md from the catalogue + what fetch_primary.py actually downloaded.

Only files listed in _fetch_records.json (raw, from official archives) and
_derived_records.json (products we computed from them) enter MANIFEST.csv.
Files kept in _non_evidence_git_mirrors/ never do.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "tools"))
from catalog import EVENTS, RECORD_TYPE_AR  # noqa: E402

FIELDS = ["event", "event_title", "record_type", "record_type_ar", "primary_source",
          "primary_source_ar", "file", "bytes", "sha256", "official_checksum",
          "checksum_match", "archive", "archive_product", "doi", "doi_resolves",
          "doi_landing", "license_declared", "license_url", "instrument",
          "program_id", "obs_date", "processing", "colour", "audio", "validator", "validation", "notes"]

AR_YES, AR_NO = "نعم", "لا"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(name):
    p = ROOT / name
    return json.loads(p.read_text()) if p.exists() else []


def rows():
    out = []
    for r in load("_fetch_records.json"):
        f = ROOT / r["file"]
        if not f.exists():
            continue
        oc = r.get("official_checksum") or {}
        doi_res = r.get("doi_resolution") or {}
        out.append(dict(
            event=r["event"], event_title=r["event_title"],
            record_type=r["kind"], record_type_ar=RECORD_TYPE_AR.get(r["kind"], r["kind"]),
            primary_source=AR_YES, primary_source_ar=AR_YES,
            file=r["file"], bytes=f.stat().st_size, sha256=sha256(f),
            official_checksum=(f"{oc.get('algorithm')}:{oc.get('value')}"
                               if oc.get("value") else "غير منشور"),
            checksum_match=("نعم" if oc.get("match") is True else
                            "لا" if oc.get("match") is False else "لا ينطبق"),
            archive=r.get("archive", ""), archive_product=r.get("product", ""),
            doi=r.get("doi", ""),
            doi_resolves=("نعم" if doi_res.get("resolves") else
                          "لا" if doi_res.get("resolves") is False else "لم يُختبر"),
            doi_landing=doi_res.get("landing") or "",
            license_declared=r.get("license_declared", ""),
            license_url=r.get("license_url", ""),
            instrument=r.get("instrument", ""), program_id=str(r.get("program_id") or ""),
            obs_date=str(r.get("obs_date") or ""),
            processing=r.get("processing", "none"), colour="لا شيء",
            audio="لا", validator=r.get("validator", ""), validation=json.dumps(r.get("validation", {}), ensure_ascii=False),
            notes=r.get("role", "")))
    for d in load("_derived_records.json"):
        f = ROOT / d["file"]
        if not f.exists():
            continue
        ev = next((e for e in EVENTS if d["file"].startswith(e["folder"] + "/")), None)
        out.append(dict(
            event=ev["id"] if ev else "", event_title=ev["title"] if ev else "",
            record_type="observation", record_type_ar="رصد (مشتق)",
            primary_source=AR_NO, primary_source_ar=AR_NO,
            file=d["file"], bytes=f.stat().st_size, sha256=sha256(f),
            official_checksum="لا ينطبق", checksum_match="لا ينطبق",
            archive="مشتق داخل هذا المستودع", archive_product=Path(d["file"]).name,
            doi=ev["doi"] if ev else "", doi_resolves="لا ينطبق", doi_landing="",
            license_declared="إنتاج هذا المستودع", license_url="",
            instrument=ev["instrument"] if ev else "",
            program_id=str(d.get("proposer_id") or ""), obs_date=str(d.get("date") or ""),
            processing=d.get("processing", ""), colour=d.get("colour", "لا شيء"),
            audio=("نعم" if d.get("audio") else "لا"), validator="", validation="", notes="derived-by-us"))
    return out


def main():
    R = rows()
    with open(ROOT / "MANIFEST.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in R:
            w.writerow(r)

    fail = load("_fetch_failures.json")
    by_event = {e["id"]: [r for r in R if r["event"] == e["id"]] for e in EVENTS}
    fails = {}
    for f in fail:
        fails.setdefault(f["event"], []).append(f)

    L = ["# فهرس أدلة حسية مؤرشفة — من أقدم ضوء إلى اليوم (v2)", "",
         "**مصادر أولية فقط.** كل ملف في `MANIFEST.csv` نُزِّل من نطاق الأرشيف الرسمي "
         "(PLA/IRSA · GWOSC · MAST · SDO/JSOC-VSO · IRIS DMC · CERN Open Data · OpenNeuro · أرشيف EHT) "
         "باستعمال واجهاته البرمجية، ومعه SHA-256 ومقارنة بالمجموع الرسمي إن نُشر، وحلّ DOI، "
         "ونصّ رخصة، وتاريخ رصد وجهاز ومعرّف برنامج. الملفات المشتقة (رسوم/صوتنة) موسومة «مصدر أولي: لا».",
         "", "## الحالة في هذه النسخة", ""]

    have = sum(1 for e in EVENTS if by_event[e["id"]])
    missing = [e["id"] for e in EVENTS if not by_event[e["id"]]]
    L += [f"- أحداث فيها ملفات أولية مؤرشفة: **{have}/{len(EVENTS)}**",
          f"- أحداث بلا ملف أولي (سؤال مفتوح معلن): **{', '.join(missing) if missing else 'لا شيء'}**",
          "- تفاصيل الحجب والخطأ لكل نطاق: `BLOCKED.md`. القرارات: `LOG.md`. نتيجة التحقق: `VERIFY_REPORT.md`.",
          "- الاختبار الذاتي الشامل (ملفات اصطناعية، ليست دليلاً): `_selftest/e2e/selftest_summary.json`.",
          "- إعادة التنزيل من أي جهاز أو Colab: `python fetch_primary.py --all` ثم "
          "`python tools/make_derived.py --all` و`python tools/make_index.py` و`python verify.py`.", ""]

    L += ["## المنتجات المستهدفة ومصدرها الرسمي", "",
          "المنتج المطلوب لكل حدث، والواجهة الرسمية التي ينزّله منها `fetch_primary.py`. "
          "الغائب منها الآن محجوب عن بيئة التنفيذ (BLOCKED.md) لا متروك سهواً.", "",
          "| الحدث | المنتج | النوع | الواجهة الرسمية | الحالة |",
          "|---|---|---|---|---|"]
    entry = {"E01": "PLA (pla.esac.esa.int) ثم مرآة IRSA",
             "E02": "gwosc.locate.get_event_urls + GWOSC event API",
             "E03": "DOI 10.25739/g85n-f134 → CyVerse (أرشيف EHT)",
             "E04": "DOI 10.25739/m140-ct59 → CyVerse (أرشيف EHT)",
             "E05": "astroquery.mast.Observations (MAST)",
             "E06": "sunpy.net.Fido (VSO/JSOC) + ترميز MP4 محلي",
             "E07": "obspy FDSN (USGS) + obspy FDSN (IRIS) + fdsnws/doi",
             "E08": "cernopendata-client (opendata.cern.ch record 6030)",
             "E09": "openneuro-py (openneuro.org ds000001)",
             "E10": "astroquery.mast.Observations (MAST, JWST)"}
    for e in EVENTS:
        for t in e["targets"]:
            status = "مؤرشف" if any(r["archive_product"] == t["name"] for r in by_event[e["id"]]) else "مطلوب — لم يُنزَّل"
            L.append(f"| {e['id']} | `{t['name']}` — {t['role']} | "
                     f"{RECORD_TYPE_AR.get(t['kind'], t['kind'])} | {entry[e['id']]} | {status} |")
    L.append("")

    L += ["## الجدول", "",
          "| # | الحدث | زمن الرحلة | الجهاز | تاريخ الرصد | أقوى ملف | DOI | الرخصة | مصدر أولي | رصد/نموذج/اختبار |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for e in EVENTS:
        rows_e = by_event[e["id"]]
        best = max(rows_e, key=lambda r: r["bytes"])["file"].split("/", 1)[-1] if rows_e else "— (سؤال مفتوح)"
        rtype = sorted({r["record_type_ar"] for r in rows_e}) or ["—"]
        L.append(f"| [{e['id']}]({e['folder']}/README.md) | {e['title']} | {e['lookback_label']} | "
                 f"{e['instrument'].split('—')[0].strip()} | "
                 f"{', '.join(sorted({r['obs_date'] for r in rows_e if r['obs_date']})) or '—'} | "
                 f"`{best}` | {e['doi']} | {e['license_text'][:60]}… | "
                 f"{AR_YES if rows_e else AR_NO} | {'/'.join(rtype)} |")
    L.append("")

    L += ["## بطاقات الأحداث", ""]
    for e in EVENTS:
        rows_e = by_event[e["id"]]
        L += [f"### {e['id']} — {e['title']}", "",
              f"- **الزمن (زمن رحلة الإشارة):** {e['lookback_label']}",
              f"- **الجهاز:** {e['instrument']}",
              f"- **البرنامج:** {e['program']}",
              f"- **DOI:** `{e['doi']}` — {e['doi_role']}",
              f"- **الرخصة:** {e['license_text']}",
              f"- **صفحة الرخصة:** {e['license_url']}",
              f"- **المشتقات المعلنة:** {'؛ '.join(e['derived'])}", ""]
        if rows_e:
            L += ["| ملف | بايت | SHA-256 (16) | مصدر أولي | نوع | تاريخ الرصد | المجموع الرسمي |",
                  "|---|---|---|---|---|---|---|"]
            for r in rows_e:
                L.append(f"| `{r['file'].split('/', 1)[-1]}` | {r['bytes']} | `{r['sha256'][:16]}` | "
                         f"{r['primary_source_ar']} | {r['record_type_ar']} | {r['obs_date'] or '—'} | "
                         f"{r['official_checksum']} ({r['checksum_match']}) |")
            L.append("")
        if fails.get(e["id"]):
            L += ["**لم يُنزَّل:** " + "؛ ".join(sorted({f"{f['product']} ← {f['reason']}" for f in fails[e['id']]})), ""]
        L += [f"- **سؤال مفتوح:** {e['open_question']}", ""]

    L += ["## أسئلة مفتوحة عامة", "",
          "1. Planck PR3 لا DOI على مستوى المجموعة؛ المستخدم هو DOI الورقة. هل يُقبل معرّف PLA كمعرّف مجموعة؟",
          "2. GWOSC وIRIS وPLA لا تنشر مجاميع اختبارية لكل ملف؛ التحقق هيكلي + SHA-256 محلي موسوم بذلك صراحةً.",
          "3. صور EHT الرسمية: هل تُوزّع كملفات بيانات أم أشكال في الأوراق فقط؟",
          "4. نطاقات الأرشيف الرئيسية محجوبة في بيئة التنفيذ الحالية (انظر BLOCKED.md)؛ الحزمة تعمل عند تشغيلها خارجها.", ""]

    L += ["## ما تم استبعاده (غير دليل)", "",
          "`_non_evidence_git_mirrors/v1_snapshot/` يحوي نسخة v1 السابقة: ملفات نُزِّلت من GitHub "
          "أو قصاصات اختبار أو طيفاً نظرياً أو هستوغرامات جاهزة. لا تدخل MANIFEST ولا INDEX كأدلة؛ "
          "مجاميعها في `MANIFEST_NON_EVIDENCE.csv` للتدقيق فقط.", ""]

    (ROOT / "INDEX.md").write_text("\n".join(L), encoding="utf-8")

    # ---------------- per-event README
    for e in EVENTS:
        rows_e = by_event[e["id"]]
        out = [f"# {e['id']} · {e['title']}", "",
               f"- **زمن الرحلة:** {e['lookback_label']}",
               f"- **الجهاز:** {e['instrument']}",
               f"- **البرنامج:** {e['program']}",
               f"- **DOI:** `{e['doi']}` ({e['doi_role']})",
               f"- **الرخصة:** {e['license_text']}",
               f"- **صفحة الرخصة:** {e['license_url']}", ""]
        if rows_e:
            out += ["## الملفات", "",
                    "| ملف | بايت | SHA-256 | مصدر أولي | نوع | تاريخ الرصد | معرّف البرنامج |",
                    "|---|---|---|---|---|---|---|"]
            for r in rows_e:
                out.append(f"| `{r['file'].split('/', 1)[-1]}` | {r['bytes']} | `{r['sha256'][:24]}…` | "
                           f"{r['primary_source_ar']} | {r['record_type_ar']} | {r['obs_date'] or '—'} | "
                           f"{r['program_id'] or '—'} |")
        else:
            out += ["## الحالة", "", "**لا ملف أولي في هذه النسخة.**", ""]
        if fails.get(e["id"]):
            out += ["## محاولات فاشلة", ""]
            for f in fails[e["id"]]:
                out.append(f"- `{f['product']}` ← {f['reason']}")
            out.append("")
        out += [f"## سؤال مفتوح", "", e["open_question"], ""]
        d = ROOT / e["folder"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "raw").mkdir(exist_ok=True)
        (d / "derived").mkdir(exist_ok=True)
        (d / "README.md").write_text("\n".join(out), encoding="utf-8")

    # ---------------- BLOCKED appendix (network facts are static, kept in BLOCKED.md)
    print(f"INDEX.md, MANIFEST.csv ({len(R)} rows), {len(EVENTS)} READMEs")
    if missing:
        print("بلا ملفات:", ", ".join(missing))


if __name__ == "__main__":
    main()
