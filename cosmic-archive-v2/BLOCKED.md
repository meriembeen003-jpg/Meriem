# BLOCKED — ما حُجب في بيئة التنفيذ هذه، بالدليل

تاريخ الاختبار: 2026-10-24 (UTC) · المضيف: حاوية Arena للتنفيذ.

## الخلاصة

بيئة التنفيذ تسمح بالخروج إلى **قائمة مضيفين محدودة فقط** (GitHub + PyPI/npm). كل نطاقات
الأرشيفات الأولية التي يتطلبها هذا المشروع تفشل عند مصافحة TLS: الاتصال TCP يُفتح ثم
يُقطع خلال مصافحة TLS (‍`SSL_ERROR_SYSCALL`)، أو يُغلق على المنفذ 80 بردّ فارغ.
لذلك **لا يوجد في هذه النسخة أي ملف أولي**، ولا نُعوّض عنه بشيء: كل حدث بلا ملف مكتوب
كسؤال مفتوح في `INDEX.md`.

## الطرق الثلاث التي جُرِّبت لكل نطاق

1. `curl -sS -v https://<host>/` → `OpenSSL SSL_connect: SSL_ERROR_SYSCALL … curl: (35)`
2. `curl -sS -v http://<host>/` → `Empty reply from server … curl: (52)`
3. `python3 urllib.request.urlopen('https://<host>')` → `URLError: TLS/SSL connection has been closed (EOF)`

طرق إضافية (كلها فشلت بنفس النمط): `curl --tls-max 1.2`، `curl --http1.1 --tlsv1.2 -k`،
`curl -6`، `openssl s_client -connect <host>:443 -servername <host>`
(النتيجة: `New, (NONE), Cipher is (NONE)` = لم تُكتمل المصافحة)، و`/dev/tcp/<host>/443`
(يفتح TCP لكن لا يمرّ TLS).

## النطاقات المحجوبة (أرشيفات مطلوبة)

| النطاق | الأرشيف | الخطأ الحرفي |
|---|---|---|
| gwosc.org (+www) | GWOSC — E02 | `SSL_ERROR_SYSCALL in connection to gwosc.org:443` · http: `Empty reply from server` |
| mast.stsci.edu | MAST — E05, E10 | `SSL_ERROR_SYSCALL` · `getent` يحلّ إلى 130.167.220.{32,33,111,112} |
| pla.esac.esa.int | Planck PLA — E01 | `SSL_ERROR_SYSCALL` |
| irsa.ipac.caltech.edu | مرآة Planck — E01 | `SSL_ERROR_SYSCALL` |
| sdo.gsfc.nasa.gov / jsoc.stanford.edu | SDO/AIA — E06 | `SSL_ERROR_SYSCALL` |
| service.iris.edu / ds.iris.edu | IRIS DMC — E07 | `SSL_ERROR_SYSCALL` |
| opendata.cern.ch | CERN Open Data — E08 | `SSL_ERROR_SYSCALL` (IPv6 فقط في DNS؛ `curl -6` → `Couldn't connect`) |
| openneuro.org (+ s3.amazonaws.com) | OpenNeuro — E09 | `SSL_ERROR_SYSCALL` |
| eventhorizontelescope.org / doi.org / almascience.org | EHT + حلّ DOI — E03/E04 | `SSL_ERROR_SYSCALL` |
| earthquake.usgs.gov | كتالوج USGS — E07 | `SSL_ERROR_SYSCALL` |

## ما يعمل فعلاً (ولذلك لم يُستخدم كدليل)

| المضيف | الحالة |
|---|---|
| github.com · api.github.com · codeload.github.com | 200 |
| pypi.org · files.pythonhosted.org | 200 |
| registry.npmjs.org | 200 |

هذه تسمح بتثبيت المكتبات (astroquery, gwosc, sunpy, obspy, cernopendata-client,
openneuro-py) — وقد فُعل ذلك — لكنها **ليست** أرشيفاً أولياً، ولهذا لا يُنزَّل منها أي دليل.

## أثر الحجب على كل حدث

| الحدث | المطلوب | الحالة | البديل المتخذ |
|---|---|---|---|
| E01 | SMICA R3.00 (2.0 GB) + أطياف TT/TE/EE المقاسة | محجوب (PLA/IRSA) | مسار تنزيل جاهز + سؤال مفتوح |
| E02 | H1/L1 + ملف الحدث + خريطة السماء | محجوب (GWOSC/doi) | `gwosc` client جاهز |
| E03/E04 | UVFITS رسمي + حلّ DOI + صورة رسمية | محجوب (doi.org/CyVerse) | مسار DOI→landing→ملف جاهز |
| E05 | صورة ACS/WFC3 كاملة + STIS GD153 | محجوب (MAST) | `astroquery.mast` جاهز |
| E06 | إطار 4096×4096 + MP4 120 إطاراً | محجوب (VSO/JSOC) | `sunpy.Fido` + مُرمِّز MP4 جاهز |
| E07 | زلزال USGS + محطات IRIS + DOI شبكات | محجوب (USGS/IRIS) | `obspy` + خدمة DOI جاهزة |
| E08 | ملف AOD حقيقي | محجوب (CERN) | `cernopendata-client` + adler32 جاهز |
| E09 | NIfTI T1w + BOLD | محجوب (OpenNeuro/S3) | `openneuro-py` جاهز |
| E10 | SMACS 0723 من MAST | محجوب (MAST) | `astroquery` جاهز |

## كيف تُكمل في بيئة غير محجوبة

```bash
pip install -r requirements.txt
python fetch_primary.py --all          # ينزّل ويتحقق ويسجّل
python tools/make_derived.py --all     # يبني الرسوم/الصوتنة المعلنة
python tools/make_index.py             # يعيد بناء INDEX/MANIFEST/README
python verify.py                       # يعيد الحساب ويكتب VERIFY_REPORT.md
```

أو من Colab: افتح `colab_quickstart.ipynb` (خلية واحدة تشغّل السلسلة كاملة).
كل مسار تنزيل في `fetch_primary.py` يستعمل واجهة الأرشيف نفسها (لا عنوان مخترع):
`gwosc.locate.get_event_urls` · `astroquery.mast.Observations` · `sunpy.net.Fido` ·
`obspy.clients.fdsn.Client` · `cernopendata-client` · `openneuro.download` ·
نقاط PLA/IRSA وCyVerse المعلنة في صفحات الأرشيف.
