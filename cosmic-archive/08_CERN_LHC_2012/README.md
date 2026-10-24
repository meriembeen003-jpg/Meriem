# E08 · LHC: تصادمات 2012 وذروة Z→μμ

- **الزمن (زمن رحلة الإشارة):** الحاضر (2012) — زمن التصادم ~10⁻¹⁰ ثانية
- **الجهاز:** CMS — تصادمات pp عند 8 TeV (Run2012C / DoubleMuParked، AOD 22Jan2013-v1)
- **التاريخ:** 2012 (نطاق التشغيل 198022–203742)
- **DOI:** 10.7483/OPENDATA.CMS.M5AD.Y3V3 (المجموعة) · 10.7483/OPENDATA.CMS.JKB8.RR42 (مثال التحليل)
- **الرخصة:** CC0 1.0 (البيانات، بحسب بوابة CERN Open Data) · كود المستودع GPL-3.0
- **الملف الأقوى:** `08_CERN_LHC_2012/raw/DoubleMu12.root`
- **المعالجة:** قراءة الهستوغرام demo/massZto2muon من ملف ROOT (uproot) ورسمه كما هو؛ لا إعادة بناء ولا تصفية.
- **لون مُسند:** لا شيء
- **تحويل صوتي:** لا شيء

## الملفات

| ملف | بايت | SHA-256 (16) | الدور | المصدر |
|---|---|---|---|---|
| `raw/CMS_Run2012C_DoubleMuParked_AOD_22Jan2013-v1_10000_file_index.txt` | 132264 | `6a7d4e11aca9fe27` | provenance-doc | cms-opendata-analyses/HiggsExample20112012@c05c526a6b75 :: datasets/CMS_Run2012C_DoubleMuParked_AOD_22Jan2013-v1_10000_file_index.txt |
| `raw/DoubleMu12.root` | 74483 | `6311b04d5c53b5fd` | derived-from-archive-product | cms-opendata-analyses/HiggsExample20112012@c05c526a6b75 :: rootfiles/DoubleMu12.root |
| `raw/LICENSE` | 35147 | `8ceb4b9ee5adedde` | license | cms-opendata-analyses/HiggsExample20112012@c05c526a6b75 :: LICENSE |
| `derived/cms_dimuon_z_peak.png` | 51752 | `8b0271b8af5ea7d8` | derived-by-us | tools/make_products.py |

## ما ينقص / سؤال مفتوح

- لا ملف حدث واحد (AOD ~GB) — الوصول عبر xrootd/eospublic.cern.ch غير متاح. الملف الموجود هستوغرام مشتق من التحليل، لا بيانات خام.
- **سؤال مفتوح:** هل يمكن أرشفة ملف AOD واحد (أو مجموعة الأحداث JSON من السجل 7129) مع مجموعه الاختباري؟
