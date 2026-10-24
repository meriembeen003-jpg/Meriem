#!/usr/bin/env python3
"""Build MANIFEST.csv, INDEX.md and one README.md per event folder.

Input:  _download_provenance.json (raw files, verified against GitHub blob SHA-1)
        _derived_checksums.json    (files produced by tools/make_products.py)
Output: MANIFEST.csv, INDEX.md, <event>/README.md
"""
import csv, hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EVENTS = [
 dict(
  id="E01", folder="01_CMB_380ka",
  title="أقدم ضوء: خلفية الميكروويف الكونية",
  lookback="13.8 مليار سنة (z ≈ 1100؛ 380,000 سنة بعد الانفجار)",
  device="Planck (ESA) — HFI/LFI. الملف المحمَّل هو منتج PLA: طيف القدرة النظري الأفضل ملاءمةً R3.01",
  date="رصد 2009–2013 · منتج R3.01 (2018) · ورقة 2020",
  doi="10.1051/0004-6361/201833880",
  license="منتج Planck Legacy Archive (مرآة IRSA)؛ المستودع الحاوي للملف MIT — رخصة المنتج نفسه غير منصوصة داخل الملف",
  strongest="01_CMB_380ka/raw/COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt",
  processing="لا معالجة على البيانات: 2507 صفاً (ℓ = 2…2508) و5 أعمدة (TT, TE, EE, BB, PP) رُسمت كما هي. لا ألوان مُسندة على البيانات (خطوط فقط).",
  colors="لا شيء",
  audio="لا شيء",
  gap="خريطة السماء الكاملة (SMICA، 2.0 GB) وخريطة القناع (0.2 GB) لم تُنزَّل: نقاط PLA/IRSA غير متاحة من شبكة هذه الجلسة.",
  open_q="هل يمكن إدراج خريطة SMICA الكاملة (R3.00، 2048) مع مجموع اختباري رسمي من PLA؟ يلزم مسار شبكة يسمح بالوصول إلى pla.esac.esa.int أو irsa.ipac.caltech.edu.",
 ),
 dict(
  id="E02", folder="02_GW150914_1.3Gyr",
  title="اندماج ثقبين أسودين: GW150914",
  lookback="≈ 1.3 مليار سنة (مسافة 420 Mpc)",
  device="Advanced LIGO — H1 (Hanford) و L1 (Livingston)، سلسلة انفعال 16 kHz",
  date="2015-09-14T09:50:45Z · GPS 1126259462.4",
  doi="10.7935/K5MW2F23",
  license="غير منصوصة في الملف ولا في المستودع المرآة (cranmer/ligo-binder)؛ GWOSC يطلب الاستشهاد بالـDOI",
  strongest="02_GW150914_1.3Gyr/raw/H-H1_LOSC_16_V1-1126259446-32.hdf5",
  processing="تبييض بالطيف (Welch، نوافذ 4 ثوانٍ) ثم مرشّح تمرير نطاقي 20–300 Hz؛ هذا يعالج سلسلة الانفعال الخام 524288 عينة. توزيع كتلة التشيرب من عينات posterior الرسمية.",
  colors="لا شيء (منحنيات زمنية)",
  audio="نعم: 32 ثانية من الانفعال المبيَّض عند 16 kHz → WAV (صوتنة، ليست صوتاً طبيعياً)",
  gap="لا ملف «حدث» منفصل ولا خريطة سماء (FITS skymap) — بيانات السماء على gwosc.org غير متاحة من هذه الشبكة.",
  open_q="هل تُدرج خريطة موضع المصدر (bayestar_skyloc.fits.gz) وملف «حدث» مفرد؟ يلزم الوصول إلى gwosc.org.",
 ),
 dict(
  id="E03", folder="03_EHT_M87_55Mly",
  title="ظل ثقب أسود هائل: M87* (حملة 2017)",
  lookback="≈ 55 مليون سنة ضوئية (16.8 Mpc)",
  device="تلسكوب أفق الحدث EHT 2017 — 8 محطات في المصفوفة (ALMA, APEX, JCMT, SMA, SMT, LMT, PV, SR)، 7 منها في ليلة 096؛ النطاق العالي 229.07 GHz",
  date="2017-04-06 (ليلة SR1-096، MJD 57849)",
  doi="10.25739/g85n-f134",
  license="ODC-PDDL 1.0 (بيانات) وGPLv3 (سكربتات) — منصوصة في LICENSE.txt المؤرشف",
  strongest="03_EHT_M87_55Mly/raw/SR1_M87_2017_096_hi_hops_netcal_StokesI.uvfits",
  processing="قراءة UVFITS (9081 رؤية، 7 محطات، 8.33 Gλ) ثم استخراج: (أ) وسم اتساع المرئية مقابل الطول الأساسي مع النطاق 16–84%، (ب) أنماط طور الإغلاق لـ35 مثلثاً. لم تُنتج صورة معكوسة: النشر لا يحوي طوراً مطلقاً معايراً.",
  colors="لا شيء",
  audio="لا شيء",
  gap="صورة M87* المنشورة (PNG) ليست جزءاً من الأرشيف (بيانات معايرة فقط).",
  open_q="أي منتج صورة رسمي (FITS/PNG) من EHT يمكن أرشفته مع رخصته ومجموعه الاختباري؟ البيانات المنشورة هنا معايرة فقط.",
 ),
 dict(
  id="E04", folder="04_EHT_SgrA_27kly",
  title="ظل ثقب أسود في مركز مجرتنا: Sgr A* (حملة 2017، ER6)",
  lookback="≈ 27,000 سنة ضوئية (8.2 kpc)",
  device="EHT 2017 (ER6) — 9 محطات (AA, AP, AZ, JC, LM, PV, SM, SP, SR)، النطاق المنخفض 227.07 GHz",
  date="2017-04-07 (ليلة ER6-097)",
  doi="10.25739/m140-ct59",
  license="ODC-PDDL 1.0 (بيانات) وGPLv3 (سكربتات) — منصوصة في LICENSE.txt المؤرشف",
  strongest="04_EHT_SgrA_27kly/raw/ER6_SGRA_2017_097_lo_hops_netcal-LMTcal_StokesI.uvfits",
  processing="قراءة UVFITS (17529 رؤية، 8.62 Gλ) ثم استخراج وسم الاتساع وأنماط طور الإغلاق بنفس الطريقة المستخدمة مع M87*.",
  colors="لا شيء",
  audio="لا شيء",
  gap="لا صورة معكوسة؛ ولا بيانات L1 الخام (CyVerse) — الوصول غير متاح.",
  open_q="هل يمكن أرشفة منتج صورة Sgr A* الرسمي؟ وهل توجد نسخة L1 من 2017 قابلة للتنزيل بمجموع اختباري معلن؟",
 ),
 dict(
  id="E05", folder="05_MAST_star_200ly",
  title="ضوء نجم قريب: طيف HST/STIS للقزم الأبيض GD153",
  lookback="≈ 205 سنة ضوئية (63 pc) — عمر النجم نفسه ~5 مليار سنة",
  device="Hubble Space Telescope — STIS (طيف 1150–10300 Å، 75687 نقطة). ومعاينة HST/ACS/WFC (F606W) بترويسة كاملة.",
  date="الطيف: غير موثق داخل الملف (نسخة المستودع منزوعة الترويسة الأولية). معاينة ACS: 2005-03-07T06:51:26",
  doi="لا DOI داخل الملف — المنتج: MAST `gd153_stiswfcnic_003` · المعاينة: `j94f05bgq_flt`",
  license="بيانات HST عامة (NASA/ESA)؛ المستودعان BSD-3-Clause",
  strongest="05_MAST_star_200ly/raw/gd153_stiswfcnic_003.fits",
  processing="قناع DATAQUAL == 0، رسم flux (log) مقابل الطول الموجي. لا تعديل على القيم.",
  colors="لا شيء",
  audio="لا شيء",
  gap="لا صورة HST كاملة بترويسة كاملة، ولا تاريخ رصد موثق للطيف، ولا مجموع اختباري رسمي من MAST (FITS CHECKSUM غير موجود في الملف).",
  open_q="ما تاريخ رصد gd153_stiswfcnic_003 ومعرّف الاقتراح؟ ولماذا حُذفت الترويسة الأولية من نسخة المستودع؟ يلزم استعلام MAST.",
 ),
 dict(
  id="E06", folder="06_SDO_Sun_AIA171",
  title="الشمس: صورة SDO/AIA عند 171 Å",
  lookback="8.3 دقيقة (1 AU)",
  device="SDO/AIA — كاميرا 3، مرشّح 171 Å، تعريض 2.0002 ثانية",
  date="2011-02-15T00:00:00Z (T_OBS 2011-02-15T00:00:01Z) — وليس تاريخ اليوم، انظر «ما ينقص»",
  doi="لا DOI في الملف (منتج JSOC/SDP)",
  license="بيانات NASA عامة؛ المستودع sunpy/sunpy BSD-2-Clause",
  strongest="06_SDO_Sun_AIA171/raw/aia_171_level1.fits",
  processing="قصاصة 128×128 بكسل من الصورة الكاملة، قيم DN كما هي، بلا تصحيح مستوى 1.5.",
  colors="نعم: تدرّج afmhot مُسند (171 Å ليس لوناً بشرياً بل ضوء فوق بنفسجي)",
  audio="لا شيء",
  gap="لا صورة بتاريخ اليوم: JSOC/VSO غير متاحين من شبكة هذه الجلسة. الملف المتاح هو قصاصة اختبار من 2011.",
  open_q="كيف يُؤرشف إطار AIA 171 ليوم التنفيذ مع مجموع اختباري من JSOC؟ وهل تُقبل قصاصة 128×128 كدليل مكان صورة كاملة؟",
 ),
 dict(
  id="E07", folder="07_IRIS_Earth_seismic",
  title="الأرض: سجل زلزالي (شبكة USArray TA + US)",
  lookback="دقائق (زمن رحلة الموجات الزلزالية)",
  device="IRIS DMC — محطة TA.W18A (BHZ، 40 عينة/ث، 612001 عينة) والمحطة US.WMOK",
  date="2014-03-17T04:11:34Z → 08:26:34Z",
  doi="لا DOI داخل الملف؛ معرّف DOI لشبكة TA لم يُتحقَّق منه من مصدره في هذه الجلسة، لذا لا يُذكر",
  license="غير منصوصة في المستودع (iris-edu/noise-toolkit)؛ شروط استخدام IRIS DMC لم تُقرأ هنا",
  strongest="07_IRIS_Earth_seismic/raw/TA.W18A..BHZ.M.2014,076,04:11:34.SAC",
  processing="قراءة SAC، مخطط زمني، STFT (2048 نافذة/1024 تداخل)، وصوتنة WAV عند 4 kHz (تصغير 10× من 40 sps).",
  colors="مطياف التردد: ألوان مُسندة (magma)",
  audio="نعم: صوتنة السجل الزلزالي بـ4 kHz — تحويل صوتي مُعلن",
  gap="هوية الحدث الزلزالي غير موثقة في الملف (لا وسم حدث)، والرخصة غير منصوصة، وDOI الشبكة لم يُتحقَّق.",
  open_q="ما الحدث الزلزالي المقصود بنافذة 2014-03-17T04:11:34Z؟ وما معرّف DOI الرسمي لشبكة TA؟",
 ),
 dict(
  id="E08", folder="08_CERN_LHC_2012",
  title="LHC: تصادمات 2012 وذروة Z→μμ",
  lookback="الحاضر (2012) — زمن التصادم ~10⁻¹⁰ ثانية",
  device="CMS — تصادمات pp عند 8 TeV (Run2012C / DoubleMuParked، AOD 22Jan2013-v1)",
  date="2012 (نطاق التشغيل 198022–203742)",
  doi="10.7483/OPENDATA.CMS.M5AD.Y3V3 (المجموعة) · 10.7483/OPENDATA.CMS.JKB8.RR42 (مثال التحليل)",
  license="CC0 1.0 (البيانات، بحسب بوابة CERN Open Data) · كود المستودع GPL-3.0",
  strongest="08_CERN_LHC_2012/raw/DoubleMu12.root",
  processing="قراءة الهستوغرام demo/massZto2muon من ملف ROOT (uproot) ورسمه كما هو؛ لا إعادة بناء ولا تصفية.",
  colors="لا شيء",
  audio="لا شيء",
  gap="لا ملف حدث واحد (AOD ~GB) — الوصول عبر xrootd/eospublic.cern.ch غير متاح. الملف الموجود هستوغرام مشتق من التحليل، لا بيانات خام.",
  open_q="هل يمكن أرشفة ملف AOD واحد (أو مجموعة الأحداث JSON من السجل 7129) مع مجموعه الاختباري؟",
 ),
 dict(
  id="E09", folder="09_OpenNeuro_brain",
  title="الدماغ البشري الآن — سؤال مفتوح (لا دليل)",
  lookback="الحاضر",
  device="— (لا ملف قياس عصبي مؤرشف)",
  date="—",
  doi="10.18112/openneuro.ds000001 (معرّف المجموعة المستهدفة؛ لم يُتحقَّق منه من المصدر)",
  license="ODC-PDDL 1.0 بحسب صفحة المجموعة ds000001 (لم تُقرأ الرخصة من ملف)",
  strongest="—",
  processing="لا شيء",
  colors="لا شيء",
  audio="لا شيء",
  gap="كل مجموعات OpenNeuro على GitHub (بما فيها ds000001) تخزّن بايتات NIfTI كـ git-annex/LFS: الملف الموجود 140 بايت نص فقط. لا يمكن الحصول على البيانات الفعلية من openneuro.org أو S3 من شبكة هذه الجلسة.",
  open_q="مطلوب: مسار يسمح بتنزيل بايتات NIfTI/FIF من OpenNeuro (أو مفتاح بيانات) لإدراج سجل دماغ حقيقي مع مجموعه الاختباري. حتى ذلك الحين لا يوجد دليل حسي لهذا الحدث.",
 ),
]

ARCHIVES = [
 ("MAST", "HST/STIS, HST/ACS", "https://mast.stsci.edu", "غير متاح (شبكة)", "ملفات منسوخة في مستودعات spacetelescope/astropy"),
 ("Planck / PLA", "Planck HFI-LFI", "https://pla.esac.esa.int", "غير متاح (شبكة)", "منتج رسمي منسوخ في مستودع بحثي + مرآة IRSA"),
 ("SDO", "SDO/AIA", "https://sdo.gsfc.nasa.gov", "غير متاح (شبكة)", "قصاصة اختبار منسوخة في sunpy/data"),
 ("EHT", "EHT 2017/2022", "https://eventhorizontelescope.org/for-astronomers/data", "صفحة الفهرس فقط", "UVFITS رسمي عبر GitHub: eventhorizontelescope/2019-D01-01 و 2022-D02-01"),
 ("GWOSC", "Advanced LIGO H1/L1", "https://gwosc.org/events/GW150914/", "صفحة الحدث فقط", "HDF5 عبر مستودع مرآة cranmer/ligo-binder"),
 ("IRIS", "IRIS DMC / USArray", "https://service.iris.edu", "غير متاح (شبكة)", "SAC منسوخ في iris-edu/noise-toolkit"),
 ("CERN Open Data", "CMS 2012", "https://opendata.cern.ch/record/6030", "صفحة السجل فقط", "ROOT مشتق من cms-opendata-analyses/HiggsExample20112012"),
 ("OpenNeuro", "ds000001", "https://openneuro.org/datasets/ds000001", "البيانات على LFS/S3: غير متاحة", "مؤشر LFS + بيانات وصفية فقط"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    prov = json.load(open(os.path.join(ROOT, "_download_provenance.json")))
    derived = json.load(open(os.path.join(ROOT, "_derived_checksums.json")))
    raw_by_dest = {f["dest"]: f for f in prov["files"]}

    rows = []
    for ev in EVENTS:
        for dest, f in sorted(raw_by_dest.items()):
            if f["event"] != ev["id"]:
                continue
            rows.append(dict(event=ev["id"], folder=ev["folder"], kind="raw",
                             role=f.get("role") or "primary-archive-product", file=dest,
                             bytes=f["bytes"], sha256=f["sha256"],
                             source=f"{f['repo']}@{f['commit'][:12]} :: {f['path']}",
                             archive=f.get("archive") or "", doi=f.get("doi") or "",
                             license=f.get("license") or ev["license"],
                             processing="كما نُزِّل (بايتات مطابقة لمستودع GitHub؛ Git-blob SHA-1 مطابق)"))
        for dest, sh in sorted(derived.items()):
            if not dest.startswith(ev["folder"]):
                continue
            p = os.path.join(ROOT, dest)
            rows.append(dict(event=ev["id"], folder=ev["folder"], kind="derived",
                             role="derived-by-us", file=dest, bytes=os.path.getsize(p),
                             sha256=sha256(p), source="tools/make_products.py",
                             archive="(مشتق من ملفات الأرشيف أعلاه)", doi=ev["doi"].split(" · ")[0],
                             license="إنتاج هذا المستودع", processing="رسم/صوتنة — انظر README الحدث"))

    with open(os.path.join(ROOT, "MANIFEST.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["event", "folder", "kind", "role", "file", "bytes",
                                           "sha256", "source", "archive", "doi", "license", "processing"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ---------------------------------------------------------------- per-event README
    for ev in EVENTS:
        files = [r for r in rows if r["event"] == ev["id"]]
        lines = [f"# {ev['id']} · {ev['title']}", "",
                 f"- **الزمن (زمن رحلة الإشارة):** {ev['lookback']}",
                 f"- **الجهاز:** {ev['device']}",
                 f"- **التاريخ:** {ev['date']}",
                 f"- **DOI:** {ev['doi']}",
                 f"- **الرخصة:** {ev['license']}",
                 f"- **الملف الأقوى:** `{ev['strongest']}`",
                 f"- **المعالجة:** {ev['processing']}",
                 f"- **لون مُسند:** {ev['colors']}",
                 f"- **تحويل صوتي:** {ev['audio']}", "",
                 "## الملفات", "", "| ملف | بايت | SHA-256 (16) | الدور | المصدر |", "|---|---|---|---|---|"]
        for r in files:
            lines.append(f"| `{r['file'].split('/',1)[1]}` | {r['bytes']} | `{r['sha256'][:16]}` | {r['role']} | {r['source']} |")
        lines += ["", "## ما ينقص / سؤال مفتوح", "", f"- {ev['gap']}", f"- **سؤال مفتوح:** {ev['open_q']}", ""]
        open(os.path.join(ROOT, ev["folder"], "README.md"), "w", encoding="utf-8").write("\n".join(lines))

    # ---------------------------------------------------------------- INDEX
    L = []
    L += ["# فهرس أدلة حسية مؤرشفة: من أقدم ضوء إلى اليوم", "",
          "الأرشيفات المصدر: MAST · Planck (PLA) · SDO · Event Horizon Telescope · GWOSC · IRIS · CERN Open Data · OpenNeuro.",
          "قاعدة واحدة: كل ملف أدناه نُزِّل فعلياً إلى هذا المجلد، وله SHA-256، ومطابقته مع مستودع المصدر (Git blob SHA-1) مسجّلة في `MANIFEST.csv`.",
          "الترتيب: **زمن رحلة الإشارة من المصدر إلى الكاشف** (lookback)، من الأقدم إلى الأحدث، دون قفز: لا يُدرج حدث بلا ملف موثق.", "",
          "## المنهجية", "",
          "1. **الترتيب** = زمن رحلة الإشارة من المصدر إلى الكاشف (lookback)، لا زمن الرصد ولا عمر الجرم. «اليوم» = 2026-10-24 (تاريخ التنفيذ) آخر نقطة، ولا يُقفز فوق حدث بلا ملف.",
          "2. **لا رابط مخترع:** كل ملف نُزِّل عبر `api.github.com` من مستودع حقيقي عند commit مثبَّت، والأرشيف الأصلي (MAST/PLA/SDO/EHT/GWOSC/IRIS/CERN/OpenNeuro) مذكور كمصدر للمنتج. كل ما لم يُفتح من هذه الشبكة موسوم «غير متاح» في الجدول الأخير، لا كتنزيل.",
          "3. **الخام مقابل المشتق:** `raw` = بايتات المنتج الأصلي كما نُزِّل؛ `derived` = أنتجناه بأمر واحد `tools/make_products.py`، وكل رسم منها يحمل في عنوانه «our processing».",
          "4. **اللون:** كل صورة كهرومغناطيسية تُرسم بتدرّج مُسند صراحةً؛ لا ادعاء بأن اللون هو ما «يراه» الكاشف (171 Å مثلاً ضوء فوق بنفسجي).",
          "5. **الصوت:** «صوتنة» = تحويل بيانات زمنية إلى WAV بمعدل عينات معلن؛ ليست تسجيلاً صوتياً للحدث.",
          "6. **السلامة:** SHA-256 لكل ملف + مطابقة Git blob SHA-1 لمستودع المصدر؛ إعادة الحساب عبر `python3 tools/verify.py`.",
          "",
          "## الجدول", "",
          "| # | الحدث | زمن الرحلة | الجهاز | تاريخ الرصد | أقوى ملف | DOI | الرخصة |",
          "|---|---|---|---|---|---|---|---|"]
    for ev in EVENTS:
        top = ev["strongest"].split("/", 1)[1] if ev["strongest"].startswith(ev["folder"]) else "—"
        L.append(f"| [{ev['id']}]({ev['folder']}/README.md) | {ev['title']} | {ev['lookback']} | {ev['device'].split('—')[0].strip()} | {ev['date']} | `{top}` | {ev['doi']} | {ev['license'].split('؛')[0]} |")

    L += ["", "## بطاقات الأحداث", ""]
    for ev in EVENTS:
        L += [f"### {ev['id']} — {ev['title']}", "",
              f"- **الجهاز:** {ev['device']}",
              f"- **التاريخ:** {ev['date']}",
              f"- **DOI:** {ev['doi']}",
              f"- **الرخصة:** {ev['license']}",
              f"- **المعالجة:** {ev['processing']}",
              f"- **لون مُسند:** {ev['colors']} · **تحويل صوتي:** {ev['audio']}",
              f"- **ما ينقص:** {ev['gap']}",
              f"- **سؤال مفتوح:** {ev['open_q']}", ""]

    L += ["## أسئلة مفتوحة (بلا تعويض)", "",
          "1. **قبل CMB (التضخم، تخليق النووي، أولى النجوم):** لا أرشيف أولي يقدم ملفاً خاماً لهذه الحقب؛ لا شيء أُدرج. ما الدليل الحسي الممكن؟",
          "2. **E06 — الشمس اليوم:** الملف المتاح إطار من 2011-02-15؛ لا إطار بتاريخ التنفيذ لأن JSOC/VSO غير متاحين.",
          "3. **E07 — هوية الحدث الزلزالي** في نافذة 2014-03-17T04:11:34Z غير موثقة داخل الملف.",
          "4. **E09 — الدماغ البشري:** بايتات OpenNeuro على git-annex/LFS/S3 فقط؛ لا ملف قياس عصبي حقيقي في متناول هذه الجلسة.",
          "5. **E03/E04 — صور EHT الرسمية** غير موجودة في الأرشيف (بيانات معايرة فقط)، ولم نصنع صورة معكوسة كي لا نبدو كأننا أرشفنا دليلاً لم نحمّله.",
          "6. **رخص غير منصوصة:** GWOSC و IRIS (وPlanck داخل الملف) — تحتاج تأكيداً من الأرشيف نفسه.", ""]

    L += ["## الأرشيفات: ما تم الوصول إليه فعلاً", "",
          "| أرشيف | جهاز | واجهة | الوصول | الطريق المستخدم |", "|---|---|---|---|---|"]
    for a in ARCHIVES:
        L.append("| " + " | ".join(a) + " |")

    L += ["", "## التحقق من السلامة", "",
          "- `MANIFEST.csv`: SHA-256 لكل ملف (خام ومشتق).",
          "- الملفات الخام: مطابقة بايت-ببايت لمستودع GitHub عبر حساب Git blob SHA-1 ومقارنته بالمُعلن في واجهة GitHub (28/28 مطابق).",
          "- `python3 tools/verify.py` يعيد الحساب ويقارن؛ أي اختلاف يُبلغ عنه.",
          "- ملفات FITS: لا تحوي CHECKSUM/DATASUM في هذه النسخ؛ لذا الاعتماد على SHA-256 + Git blob SHA-1.",
          "- الاستنساخ في `_download_provenance.json` (مستودع، مسار، commit، blob sha، رخصة المستودع، رابط GitHub).", ""]

    open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8").write("\n".join(L))
    print("wrote MANIFEST.csv (%d rows), INDEX.md, %d event READMEs" % (len(rows), len(EVENTS)))


if __name__ == "__main__":
    main()
