# الأرشيف الفلكي الشامل — صور الكون

أرشيف صور كونية علمية (لا صور تلسكوبات ولا أجهزة) مأخوذ من بيانات عامة، مع تعليق علمي لكل صورة.

- **الوجهة في Google Drive:** مجلد «Unknown Universe / الأرشيف الفلكي الشامل — صور الكون»
  <https://drive.google.com/drive/folders/1JTJwVP-dhjA1_pAb2k1psJPCNrUiqt-i>
- **العدد:** 63 ملفاً (58 صورة/رصد + 5 منتجات FITS معايرة) بحجم ~671 ميجابايت.
- **التغطية الطيفية:** راديوي (MeerKAT 1.28 GHz، HI4PI 21 سم، EHT 1.3 مم)، تحت مليمتري (Herschel/SPIRE 350 µm)،
  ميكروي (Planck CMB)، تحت أحمر (JWST NIRCam/MIRI، Spitzer، WISE)، مرئي (Hubble، مركّبات NASA)،
  فوق بنفسجي متطرف (SDO/AIA 171 Å، SOHO/EIT 195 Å)، سيني (Chandra/ACIS)، غاما (Fermi-LAT 3FHL).

## المجلدات

| المجلد | المحتوى |
| --- | --- |
| 01 — المجرات | JWST Cartwheel، Hubble M51/M81/NGC1300/NGC2787، WISE M31، GALEX، MeerKAT NGC 1044 |
| 02 — الثقوب السوداء والنوى النشطة | M87* (EHT 2019)، Sgr A* (EHT 2022) |
| 03 — النجوم والعناقيد | IC 348، Chamaeleon I، Westerlund 2، Cygnus X، W5، NGC 281، Herschel 350 µm |
| 04 — السدم | Carina (NIRCam + MIRI + Hubble)، Tarantula، Ring M57، Southern Ring، Pillars، Orion، Lagoon ... |
| 05 — الكواكب الخارجية | HR 8799 b/c/d/e (JWST NIRCam) |
| 06 — العناقيد والبنية الكونية | Stephan's Quintet، HCG 62 (Chandra)، CMB (Planck)، Fermi-LAT all-sky، N44 superbubble |
| 07 — حقول الرصد العميق | SMACS 0723 (JWST مقابل Hubble) |
| 08 — البقايا النجمية | Cas A، Crab، Tycho، IC 443 |
| 09 — منتجات FITS | MeerKAT Stokes I، Chandra events، Herschel SPIRE، Fermi 3FHL، HI4PI cube |
| 10 — الشمس | AIA 171 Å، EIT 195 Å |

## الملفات

- `catalog.py` — قائمة الرصدات (كائن واحد = رصد واحد بطول موجي واحد) مع المصدر والرخصة.
- `texts.py` — التعليقات العلمية العربية (تفسير + خصائص مرصودة).
- `fetch.py` — تنزيل البايتات الأصلية من الأرشيفات العامة (GitHub blobs API).
- `render_fits.py` — تحويل منتجات FITS المعايرة إلى صور بألوان كاذبة موثقة (asinh / log stretch).
- `make_tasks.py` — توليد `tasks.json` (أسماء نهائية + تعليقات) وحشد الملفات في `upload/`.
- `state.json` — سجل المرفوع فعلياً إلى Drive (المعرّف والرابط).

## إزالة التكرار

كل رصد موجود مرة واحدة فقط. عند ورود نفس الصورة بأحجام مختلفة (مثلاً إطار كامل 4833×4501 مقابل نسخة 3840×2160
مقتطعة) تُحفظ النسخة الأعلى دقة، وتُسجَّل القرارات في `catalog.DROP`. الأطوال الموجية المختلفة لنفس الجسم
(Carina NIRCam مقابل MIRI مقابل Hubble) تُحفظ كلها لأنها رصدات مستقلة.

## إعادة التوليد

```bash
python3 archive/fetch.py          # تنزيل المصادر
python3 archive/render_fits.py    # صور من FITS
python3 archive/make_tasks.py     # tasks.json + upload/
npm run dev                       # ثم /upload لدفع الملفات إلى Drive
```
