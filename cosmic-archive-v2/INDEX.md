# فهرس أدلة حسية مؤرشفة — من أقدم ضوء إلى اليوم (v2)

**مصادر أولية فقط.** كل ملف في `MANIFEST.csv` نُزِّل من نطاق الأرشيف الرسمي (PLA/IRSA · GWOSC · MAST · SDO/JSOC-VSO · IRIS DMC · CERN Open Data · OpenNeuro · أرشيف EHT) باستعمال واجهاته البرمجية، ومعه SHA-256 ومقارنة بالمجموع الرسمي إن نُشر، وحلّ DOI، ونصّ رخصة، وتاريخ رصد وجهاز ومعرّف برنامج. الملفات المشتقة (رسوم/صوتنة) موسومة «مصدر أولي: لا».

## الحالة في هذه النسخة

- أحداث فيها ملفات أولية مؤرشفة: **0/10**
- أحداث بلا ملف أولي (سؤال مفتوح معلن): **E01, E02, E03, E04, E05, E06, E07, E08, E09, E10**
- تفاصيل الحجب والخطأ لكل نطاق: `BLOCKED.md`. القرارات: `LOG.md`. نتيجة التحقق: `VERIFY_REPORT.md`.
- الاختبار الذاتي الشامل (ملفات اصطناعية، ليست دليلاً): `_selftest/e2e/selftest_summary.json`.
- إعادة التنزيل من أي جهاز أو Colab: `python fetch_primary.py --all` ثم `python tools/make_derived.py --all` و`python tools/make_index.py` و`python verify.py`.

## المنتجات المستهدفة ومصدرها الرسمي

المنتج المطلوب لكل حدث، والواجهة الرسمية التي ينزّله منها `fetch_primary.py`. الغائب منها الآن محجوب عن بيئة التنفيذ (BLOCKED.md) لا متروك سهواً.

| الحدث | المنتج | النوع | الواجهة الرسمية | الحالة |
|---|---|---|---|---|
| E01 | `COM_CMB_IQU-smica_2048_R3.00_full.fits` — خريطة SMICA كاملة (T/Q/U، NSIDE 2048) — 2.0 GB | رصد | PLA (pla.esac.esa.int) ثم مرآة IRSA | مطلوب — لم يُنزَّل |
| E01 | `COM_PowerSpect_CMB-TT-full_R3.01.txt` — طيف TT المقاس (لا النظري) مع الخطأ | رصد | PLA (pla.esac.esa.int) ثم مرآة IRSA | مطلوب — لم يُنزَّل |
| E01 | `COM_PowerSpect_CMB-TE-full_R3.01.txt` — طيف TE المقاس | رصد | PLA (pla.esac.esa.int) ثم مرآة IRSA | مطلوب — لم يُنزَّل |
| E01 | `COM_PowerSpect_CMB-EE-full_R3.01.txt` — طيف EE المقاس | رصد | PLA (pla.esac.esa.int) ثم مرآة IRSA | مطلوب — لم يُنزَّل |
| E02 | `H-H1_LOSC_16_V1-1126259446-32.hdf5` — انفعال H1، 16 kHz، 32 ثانية | رصد | gwosc.locate.get_event_urls + GWOSC event API | مطلوب — لم يُنزَّل |
| E02 | `L-L1_LOSC_16_V1-1126259446-32.hdf5` — انفعال L1، 16 kHz، 32 ثانية | رصد | gwosc.locate.get_event_urls + GWOSC event API | مطلوب — لم يُنزَّل |
| E02 | `event_json_GW150914.json` — ملف الحدث (JSON الرسمي من GWOSC API) | رصد | gwosc.locate.get_event_urls + GWOSC event API | مطلوب — لم يُنزَّل |
| E02 | `LALInference_skymap.fits.gz` — خريطة السماء لاحتمال الموضع (P1500227) | رصد | gwosc.locate.get_event_urls + GWOSC event API | مطلوب — لم يُنزَّل |
| E03 | `SR1_M87_2017_096_hi_hops_netcal_StokesI.uvfits` — بيانات معايرة (Stokes I، hops) — الليلة 096، النطاق العالي | رصد | DOI 10.25739/g85n-f134 → CyVerse (أرشيف EHT) | مطلوب — لم يُنزَّل |
| E03 | `EHT_M87_official_image.fits` — المنتج الصوري الرسمي (إن نشره التعاون) | رصد | DOI 10.25739/g85n-f134 → CyVerse (أرشيف EHT) | مطلوب — لم يُنزَّل |
| E04 | `ER6_SGRA_2017_097_lo_hops_netcal-LMTcal_StokesI.uvfits` — بيانات معايرة — الليلة 097، النطاق المنخفض | رصد | DOI 10.25739/m140-ct59 → CyVerse (أرشيف EHT) | مطلوب — لم يُنزَّل |
| E05 | `HST_full_frame_flc.fits` — صورة ACS/WFC أو WFC3/UVIS كاملة (FLT/FLC) بترويسة كاملة | رصد | astroquery.mast.Observations (MAST) | مطلوب — لم يُنزَّل |
| E05 | `gd153_stis_x1d.fits` — طيف GD153 المرصود (STIS x1d) مع PROPOSID | رصد | astroquery.mast.Observations (MAST) | مطلوب — لم يُنزَّل |
| E06 | `AIA171_fullframe.fits` — إطار كامل 4096×4096 مستوى 1 لأحدث يوم متاح | رصد | sunpy.net.Fido (VSO/JSOC) + ترميز MP4 محلي | مطلوب — لم يُنزَّل |
| E06 | `AIA171_movie.mp4` — فيديو 120 إطاراً متتالية (تركيب منا، ألوان مُسندة) | رصد | sunpy.net.Fido (VSO/JSOC) + ترميز MP4 محلي | مطلوب — لم يُنزَّل |
| E07 | `USGS_event.json` — ملف الحدث الرسمي من USGS ComCat (المعرّف والمكان والقوة) | رصد | obspy FDSN (USGS) + obspy FDSN (IRIS) + fdsnws/doi | مطلوب — لم يُنزَّل |
| E07 | `IRIS_multi_station.mseed` — سجلات ≥5 محطات حول الحدث | رصد | obspy FDSN (USGS) + obspy FDSN (IRIS) + fdsnws/doi | مطلوب — لم يُنزَّل |
| E08 | `CMS_Run2012C_DoubleMuParked_AOD.root` — ملف AOD واحد (أحداث حقيقية) | رصد | cernopendata-client (opendata.cern.ch record 6030) | مطلوب — لم يُنزَّل |
| E09 | `sub-01_T1w.nii.gz` — صورة تشريحية T1w | رصد | openneuro-py (openneuro.org ds000001) | مطلوب — لم يُنزَّل |
| E09 | `sub-01_task-balloonanalogrisktask_run-01_bold.nii.gz` — سلسلة BOLD (fMRI) | رصد | openneuro-py (openneuro.org ds000001) | مطلوب — لم يُنزَّل |
| E10 | `JWST_SMACS0723_i2d.fits` — صورة معالجة i2d لأحد مرشحات NIRCam | رصد | astroquery.mast.Observations (MAST, JWST) | مطلوب — لم يُنزَّل |

## الجدول

| # | الحدث | زمن الرحلة | الجهاز | تاريخ الرصد | أقوى ملف | DOI | الرخصة | مصدر أولي | رصد/نموذج/اختبار |
|---|---|---|---|---|---|---|---|---|---|
| [E01](E01_CMB_SMICA/README.md) | أقدم ضوء: خريطة SMICA كاملة وطيف القدرة المقاس (Planck 2018) | 13.8 مليار سنة (z≈1100، 380,000 سنة بعد الانفجار) | Planck | — | `— (سؤال مفتوح)` | 10.1051/0004-6361/201833880 | ESA Planck Legacy Archive: بيانات Planck عامة للاستخدام العل… | لا | — |
| [E02](E02_GW150914/README.md) | اندماج ثقبين أسودين: GW150914 (H1 + L1 + ملف الحدث + خريطة السماء) | ≈1.3 مليار سنة (D_L ≈ 420 Mpc) | Advanced LIGO | — | `— (سؤال مفتوح)` | 10.7935/K5MW2F23 | GWOSC: البيانات متاحة للجمهور؛ شرط GWOSC هو الاستشهاد بالورق… | لا | — |
| [E03](E03_EHT_M87/README.md) | ظل ثقب أسود: M87* — بيانات EHT 2019 الرسمية + المنتج الصوري | ≈55 مليون سنة ضوئية (16.8 Mpc) | EHT 2017 | — | `— (سؤال مفتوح)` | 10.25739/g85n-f134 | ODC-PDDL 1.0 لملفات البيانات، GPLv3 للسكربتات (نصّ الرخصة من… | لا | — |
| [E04](E04_EHT_SgrA/README.md) | ظل ثقب أسود: Sgr A* — بيانات EHT 2022 الرسمية | ≈27,000 سنة ضوئية (8.2 kpc) | EHT 2017 ER6 | — | `— (سؤال مفتوح)` | 10.25739/m140-ct59 | ODC-PDDL 1.0 لملفات البيانات، GPLv3 للسكربتات… | لا | — |
| [E05](E05_HST/README.md) | نجم قريب: صورة ACS/WFC3 كاملة + طيف GD153 المرصود (STIS) | ≈205 سنة ضوئية (63 pc) | HST | — | `— (سؤال مفتوح)` |  | MAST/STScI: منتجات HST عامة؛ MAST تطلب الاستشهاد بمعرّف المن… | لا | — |
| [E06](E06_SDO_AIA171/README.md) | الشمس الآن: إطار AIA 171 كامل 4096×4096 + فيديو 120 إطاراً | 8.3 دقيقة (1 AU) | SDO/AIA | — | `— (سؤال مفتوح)` |  | NASA SDO: بيانات عامة بلا قيود (NASA open data, CC0-like pol… | لا | — |
| [E07](E07_IRIS/README.md) | الأرض: زلزال كبير بمعرّف USGS + سجلات عدة محطات IRIS | دقائق (زمن رحلة الموجات) | IRIS DMC عبر FDSN | — | `— (سؤال مفتوح)` |  | IRIS DMC: بيانات مفتوحة للبحث والتعليم؛ شرط الإقرار بـIRIS و… | لا | — |
| [E08](E08_CMS_AOD/README.md) | LHC: ملف أحداث CMS 2012 حقيقي (AOD) بدل الهستوغرام | الحاضر (2012) | CMS | — | `— (سؤال مفتوح)` | 10.7483/OPENDATA.CMS.M5AD.Y3V3 | CC0 1.0 (بيانات CERN Open Data) — منصوص على صفحة السجل… | لا | — |
| [E09](E09_OPENNEURO/README.md) | الدماغ البشري: T1w + BOLD من OpenNeuro ds000001 | الحاضر | Siemens 3T، تصوير بالرنين المغناطيسي الوظيفي (BART task) | — | `— (سؤال مفتوح)` | 10.18112/openneuro.ds000001 | ODC-PDDL 1.0 (منصوص على صفحة المجموعة)… | لا | — |
| [E10](E10_JWST_SMACS0723/README.md) | جيمس ويب: SMACS 0723 (صورة MAST) | ≈4.6 مليار سنة (عدسة عنقودية؛ ضوء أقدم) | JWST | — | `— (سؤال مفتوح)` |  | MAST: منتجات JWST عامة بعد انتهاء فترة الملكية الحصرية؛ لا ن… | لا | — |

## بطاقات الأحداث

### E01 — أقدم ضوء: خريطة SMICA كاملة وطيف القدرة المقاس (Planck 2018)

- **الزمن (زمن رحلة الإشارة):** 13.8 مليار سنة (z≈1100، 380,000 سنة بعد الانفجار)
- **الجهاز:** Planck — HFI/LFI (SMICA component separation, R3.00 map; R3.01 measured spectra)
- **البرنامج:** Planck 2018 legacy release (PR3)
- **DOI:** `10.1051/0004-6361/201833880` — ورقة Planck 2018 I — تصف منتجات PR3؛ DOI مجموعة البيانات نفسه غير موجود، انظر السؤال المفتوح
- **الرخصة:** ESA Planck Legacy Archive: بيانات Planck عامة للاستخدام العلمي؛ شرط الاستشهاد بورقة Planck 2018. لا نصّ رخصة مضمَّن في ملفات FITS.
- **صفحة الرخصة:** https://pla.esac.esa.int/pla/#home
- **المشتقات المعلنة:** SMICA T-map Mollview PNG (colour assigned, colourbar in µK)؛ TT/TE/EE measured spectra PNG with error bars

- **سؤال مفتوح:** PR3 لا يحمل DOI على مستوى المجموعة (فقط DOI الورقة 10.1051/0004-6361/201833880). هل تُدرج المجموعة بمعرّف PLA الداخلي بدل DOI؟

### E02 — اندماج ثقبين أسودين: GW150914 (H1 + L1 + ملف الحدث + خريطة السماء)

- **الزمن (زمن رحلة الإشارة):** ≈1.3 مليار سنة (D_L ≈ 420 Mpc)
- **الجهاز:** Advanced LIGO — H1 (Hanford) و L1 (Livingston)
- **البرنامج:** O1 / LOSC — GPS 1126259462.4
- **DOI:** `10.7935/K5MW2F23` — DOI مجموعة بيانات GW150914 على GWOSC (يحلّ إلى صفحة الحدث)
- **الرخصة:** GWOSC: البيانات متاحة للجمهور؛ شرط GWOSC هو الاستشهاد بالورقة وDOI. لا نصّ رخصة صريح على صفحة الحدث.
- **صفحة الرخصة:** https://gwosc.org/events/GW150914/
- **المشتقات المعلنة:** strain whitened 20–300 Hz PNG (H1+L1)؛ sonification WAV 16 kHz (whitened strain — تحويل صوتي)؛ skymap Mollview PNG (colour assigned)

**لم يُنزَّل:** H-H1_LOSC_16_V1-1126259446-32.hdf5 ← get_event_urls failed: SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /api/v2/event-versions/GW150914/strain-files?detector=H1&sample-rate=16&file-format=hdf&duration=32 (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))؛ L-L1_LOSC_16_V1-1126259446-32.hdf5 ← get_event_urls failed: SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /api/v2/event-versions/GW150914/strain-files?detector=L1&sample-rate=16&file-format=hdf&duration=32 (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))؛ LALInference_skymap.fits.gz ← SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /eventapi/json/allevents/ (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))؛ event_json_GW150914.json ← SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /eventapi/json/allevents/ (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))

- **سؤال مفتوح:** لا مجموع اختباري منشور رسمياً لملفات GWOSC HDF5؛ التحقق هيكلي + SHA-256 محلي.

### E03 — ظل ثقب أسود: M87* — بيانات EHT 2019 الرسمية + المنتج الصوري

- **الزمن (زمن رحلة الإشارة):** ≈55 مليون سنة ضوئية (16.8 Mpc)
- **الجهاز:** EHT 2017 — 8 محطات، 229 GHz
- **البرنامج:** EHT 2019-D01-01 (calibrated data) + 2019-D01-02 (imaging pipelines)
- **DOI:** `10.25739/g85n-f134` — DOI مجموعة البيانات (CyVerse Data Commons) — يجب أن يحلّ إلى صفحة المجموعة
- **الرخصة:** ODC-PDDL 1.0 لملفات البيانات، GPLv3 للسكربتات (نصّ الرخصة منشور مع المجموعة)
- **صفحة الرخصة:** https://eventhorizontelescope.org/for-astronomers/data
- **المشتقات المعلنة:** UV amplitude vs baseline PNG؛ closure phase histogram PNG؛ official image render PNG (colour assigned) — فقط إن وُجد المنتج الرسمي

- **سؤال مفتوح:** هل يوزّع EHT المنتج الصوري النهائي (FITS/PNG) عبر CyVerse بنفس DOI؟ الصور المنشورة في الأوراق ليست ملفات أرشيف.

### E04 — ظل ثقب أسود: Sgr A* — بيانات EHT 2022 الرسمية

- **الزمن (زمن رحلة الإشارة):** ≈27,000 سنة ضوئية (8.2 kpc)
- **الجهاز:** EHT 2017 ER6 — 9 محطات، 227 GHz
- **البرنامج:** EHT 2022-D02-01 (First Sgr A* Results: calibrated data)
- **DOI:** `10.25739/m140-ct59` — DOI مجموعة بيانات Sgr A* (CyVerse) — يجب أن يحلّ إلى صفحة المجموعة
- **الرخصة:** ODC-PDDL 1.0 لملفات البيانات، GPLv3 للسكربتات
- **صفحة الرخصة:** https://eventhorizontelescope.org/for-astronomers/data
- **المشتقات المعلنة:** UV amplitude vs baseline PNG؛ closure phase histogram PNG

- **سؤال مفتوح:** هل صورة Sgr A* الرسمية موزّعة كملف بيانات أم فقط كشكل في الورقة؟

### E05 — نجم قريب: صورة ACS/WFC3 كاملة + طيف GD153 المرصود (STIS)

- **الزمن (زمن رحلة الإشارة):** ≈205 سنة ضوئية (63 pc)
- **الجهاز:** HST — ACS/WFC أو WFC3/UVIS (صورة كاملة) و STIS (طيف GD153)
- **البرنامج:** برنامج GD153 (STIS) وبرنامج الصورة: يُقرأ من ترويسة المنتج (PROPOSID)
- **DOI:** `` — لا DOI لمنتج HST مفرد؛ المعرّف الرسمي هو obs_id + PROPOSID من الترويسة. بادئة MAST (10.17909) لم يُتحقَّق منها هنا فلا تُنسب.
- **الرخصة:** MAST/STScI: منتجات HST عامة؛ MAST تطلب الاستشهاد بمعرّف المنتج وبرنامج الرصد. لا نصّ رخصة في الترويسة.
- **صفحة الرخصة:** https://mast.stsci.edu/
- **المشتقات المعلنة:** image PNG cutout of the full frame (colour assigned, log stretch)؛ STIS spectrum PNG

- **سؤال مفتوح:** أي برنامج HST يُستخدم للصورة الكاملة (اقتراح محدد)؟ يُختار تلقائياً أكبر منتج WFC3/UVIS أو ACS/WFC متاح في MAST ويُسجَّل PROPOSID.

### E06 — الشمس الآن: إطار AIA 171 كامل 4096×4096 + فيديو 120 إطاراً

- **الزمن (زمن رحلة الإشارة):** 8.3 دقيقة (1 AU)
- **الجهاز:** SDO/AIA — 171 Å، مستوى 1
- **البرنامج:** AIA lev1 (JSOC/VSO)
- **DOI:** `` — لا DOI لإطار AIA مفرد؛ المعرّف هو T_REC/T_OBS + INSTRUME. لا يُنسب DOI غير محقَّق.
- **الرخصة:** NASA SDO: بيانات عامة بلا قيود (NASA open data, CC0-like policy). لا نصّ رخصة في الترويسة.
- **صفحة الرخصة:** https://sdo.gsfc.nasa.gov/data/
- **المشتقات المعلنة:** frame PNG (colour assigned)؛ MP4 labelled as our composite

- **سؤال مفتوح:** VSO يعطي إطارات 4096؛ JSOC export يحتاج بريداً مسجّلاً (--jsoc-email) لتسلسل زمني أسرع.

### E07 — الأرض: زلزال كبير بمعرّف USGS + سجلات عدة محطات IRIS

- **الزمن (زمن رحلة الإشارة):** دقائق (زمن رحلة الموجات)
- **الجهاز:** IRIS DMC عبر FDSN — محطات متعددة (BHZ/HHZ)
- **البرنامج:** USGS ComCat event id + IRIS FDSN dataselect
- **DOI:** `` — DOI يُقرأ آلياً من خدمة IRIS fdsnws/doi لكل شبكة مستخدمة ويُحلّ ويُسجَّل مع السجل — لا DOI ثابت مكتوب هنا.
- **الرخصة:** IRIS DMC: بيانات مفتوحة للبحث والتعليم؛ شرط الإقرار بـIRIS والـDOI لكل شبكة.
- **صفحة الرخصة:** https://service.iris.edu/
- **المشتقات المعلنة:** waveform PNG per station؛ spectrogram PNG (colour assigned)؛ sonification WAV

- **سؤال مفتوح:** أي زلزال؟ يُختار آلياً أكبر حدث M≥7.5 في آخر 10 سنوات من كتالوج USGS FDSN، ويُسجَّل معرّفه.

### E08 — LHC: ملف أحداث CMS 2012 حقيقي (AOD) بدل الهستوغرام

- **الزمن (زمن رحلة الإشارة):** الحاضر (2012)
- **الجهاز:** CMS — pp 8 TeV، Run2012C DoubleMuParked AOD 22Jan2013-v1
- **البرنامج:** CERN Open Data record 6030 (DOI 10.7483/OPENDATA.CMS.M5AD.Y3V3)
- **DOI:** `10.7483/OPENDATA.CMS.M5AD.Y3V3` — DOI المجموعة — يجب أن يحلّ إلى سجل 6030
- **الرخصة:** CC0 1.0 (بيانات CERN Open Data) — منصوص على صفحة السجل
- **صفحة الرخصة:** https://opendata.cern.ch/record/6030
- **المشتقات المعلنة:** event-count and muon-kinematics PNGs computed from the AOD file؛ dimuon invariant-mass spectrum (calculated by us from AOD)

- **سؤال مفتوح:** ملف AOD واحد ~2 GB؛ إن حُجب xrootd يُستخدم cernopendata-client عبر HTTPS.

### E09 — الدماغ البشري: T1w + BOLD من OpenNeuro ds000001

- **الزمن (زمن رحلة الإشارة):** الحاضر
- **الجهاز:** Siemens 3T، تصوير بالرنين المغناطيسي الوظيفي (BART task)
- **البرنامج:** OpenNeuro ds000001 (OpenfMRI, Poldrack lab)
- **DOI:** `10.18112/openneuro.ds000001` — DOI مجموعة OpenNeuro (كما تنشره المنصة) — يُحلّ ويُتحقَّق عند التشغيل؛ لم يُتحقَّق منه في هذه البيئة
- **الرخصة:** ODC-PDDL 1.0 (منصوص على صفحة المجموعة)
- **صفحة الرخصة:** https://openneuro.org/datasets/ds000001
- **المشتقات المعلنة:** orthogonal slice PNGs (T1w + BOLD mean) — colours assigned

- **سؤال مفتوح:** OpenNeuro يقدّم SHA-256 لكل ملف عبر API؛ يُقارن تلقائياً بعد التنزيل.

### E10 — جيمس ويب: SMACS 0723 (صورة MAST)

- **الزمن (زمن رحلة الإشارة):** ≈4.6 مليار سنة (عدسة عنقودية؛ ضوء أقدم)
- **الجهاز:** JWST — NIRCam (F444W/F200W/F150W/F090W)
- **البرنامج:** JWST ERS 2736 — SMACS J0723.3-7327
- **DOI:** `` — لا DOI لمنتج JWST مفرد؛ المعرّف obs_id + PROPOSID (برنامج ERS يُقرأ من الترويسة ويُسجَّل).
- **الرخصة:** MAST: منتجات JWST عامة بعد انتهاء فترة الملكية الحصرية؛ لا نصّ رخصة في الترويسة
- **صفحة الرخصة:** https://mast.stsci.edu/
- **المشتقات المعلنة:** RGB-composite PNG (our composition, channels assigned)

- **سؤال مفتوح:** التركيب RGB يتطلب 3 مرشحات؛ إن لم تتوفر كلها يُنتج PNG أحادي القناة موسوم بوضوح.

## أسئلة مفتوحة عامة

1. Planck PR3 لا DOI على مستوى المجموعة؛ المستخدم هو DOI الورقة. هل يُقبل معرّف PLA كمعرّف مجموعة؟
2. GWOSC وIRIS وPLA لا تنشر مجاميع اختبارية لكل ملف؛ التحقق هيكلي + SHA-256 محلي موسوم بذلك صراحةً.
3. صور EHT الرسمية: هل تُوزّع كملفات بيانات أم أشكال في الأوراق فقط؟
4. نطاقات الأرشيف الرئيسية محجوبة في بيئة التنفيذ الحالية (انظر BLOCKED.md)؛ الحزمة تعمل عند تشغيلها خارجها.

## ما تم استبعاده (غير دليل)

`_non_evidence_git_mirrors/v1_snapshot/` يحوي نسخة v1 السابقة: ملفات نُزِّلت من GitHub أو قصاصات اختبار أو طيفاً نظرياً أو هستوغرامات جاهزة. لا تدخل MANIFEST ولا INDEX كأدلة؛ مجاميعها في `MANIFEST_NON_EVIDENCE.csv` للتدقيق فقط.
