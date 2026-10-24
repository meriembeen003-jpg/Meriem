# E02 · اندماج ثقبين أسودين: GW150914

- **الزمن (زمن رحلة الإشارة):** ≈ 1.3 مليار سنة (مسافة 420 Mpc)
- **الجهاز:** Advanced LIGO — H1 (Hanford) و L1 (Livingston)، سلسلة انفعال 16 kHz
- **التاريخ:** 2015-09-14T09:50:45Z · GPS 1126259462.4
- **DOI:** 10.7935/K5MW2F23
- **الرخصة:** غير منصوصة في الملف ولا في المستودع المرآة (cranmer/ligo-binder)؛ GWOSC يطلب الاستشهاد بالـDOI
- **الملف الأقوى:** `02_GW150914_1.3Gyr/raw/H-H1_LOSC_16_V1-1126259446-32.hdf5`
- **المعالجة:** تبييض بالطيف (Welch، نوافذ 4 ثوانٍ) ثم مرشّح تمرير نطاقي 20–300 Hz؛ هذا يعالج سلسلة الانفعال الخام 524288 عينة. توزيع كتلة التشيرب من عينات posterior الرسمية.
- **لون مُسند:** لا شيء (منحنيات زمنية)
- **تحويل صوتي:** نعم: 32 ثانية من الانفعال المبيَّض عند 16 kHz → WAV (صوتنة، ليست صوتاً طبيعياً)

## الملفات

| ملف | بايت | SHA-256 (16) | الدور | المصدر |
|---|---|---|---|---|
| `raw/H-H1_LOSC_16_V1-1126259446-32.hdf5` | 4069531 | `9abec849134cdd1f` | primary-archive-product | cranmer/ligo-binder@cecb27c3c824 :: H-H1_LOSC_16_V1-1126259446-32.hdf5 |
| `raw/L-L1_LOSC_16_V1-1126259446-32.hdf5` | 3876039 | `855d08b7924dbdfa` | primary-archive-product | cranmer/ligo-binder@cecb27c3c824 :: L-L1_LOSC_16_V1-1126259446-32.hdf5 |
| `raw/README_ligo_binder.md` | 825 | `48c5d9520f0946f1` | doc | cranmer/ligo-binder@cecb27c3c824 :: README.md |
| `raw/gw150914_posteriors_thinned.hdf` | 1086688 | `5df979972a28fba2` | derived-official-product | gwastro/pycbc-inference-paper@ddbbdfa068d4 :: posteriors/GW150914/gw150914_posteriors_thinned.hdf |
| `derived/audio/gw150914_H1_sonification.wav` | 1048620 | `94dca79ca49b2a30` | derived-by-us | tools/make_products.py |
| `derived/gw150914_chirpmass_posterior.png` | 43133 | `d9f1edd87e375172` | derived-by-us | tools/make_products.py |
| `derived/gw150914_whitened_H1_L1.png` | 175830 | `155ab49ed07a265e` | derived-by-us | tools/make_products.py |

## ما ينقص / سؤال مفتوح

- لا ملف «حدث» منفصل ولا خريطة سماء (FITS skymap) — بيانات السماء على gwosc.org غير متاحة من هذه الشبكة.
- **سؤال مفتوح:** هل تُدرج خريطة موضع المصدر (bayestar_skyloc.fits.gz) وملف «حدث» مفرد؟ يلزم الوصول إلى gwosc.org.
