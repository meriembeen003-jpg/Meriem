# E02 · اندماج ثقبين أسودين: GW150914 (H1 + L1 + ملف الحدث + خريطة السماء)

- **زمن الرحلة:** ≈1.3 مليار سنة (D_L ≈ 420 Mpc)
- **الجهاز:** Advanced LIGO — H1 (Hanford) و L1 (Livingston)
- **البرنامج:** O1 / LOSC — GPS 1126259462.4
- **DOI:** `10.7935/K5MW2F23` (DOI مجموعة بيانات GW150914 على GWOSC (يحلّ إلى صفحة الحدث))
- **الرخصة:** GWOSC: البيانات متاحة للجمهور؛ شرط GWOSC هو الاستشهاد بالورقة وDOI. لا نصّ رخصة صريح على صفحة الحدث.
- **صفحة الرخصة:** https://gwosc.org/events/GW150914/

## الحالة

**لا ملف أولي في هذه النسخة.**

## محاولات فاشلة

- `H-H1_LOSC_16_V1-1126259446-32.hdf5` ← get_event_urls failed: SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /api/v2/event-versions/GW150914/strain-files?detector=H1&sample-rate=16&file-format=hdf&duration=32 (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))
- `L-L1_LOSC_16_V1-1126259446-32.hdf5` ← get_event_urls failed: SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /api/v2/event-versions/GW150914/strain-files?detector=L1&sample-rate=16&file-format=hdf&duration=32 (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))
- `event_json_GW150914.json` ← SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /eventapi/json/allevents/ (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))
- `LALInference_skymap.fits.gz` ← SSLError: HTTPSConnectionPool(host='gwosc.org', port=443): Max retries exceeded with url: /eventapi/json/allevents/ (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:992)')))

## سؤال مفتوح

لا مجموع اختباري منشور رسمياً لملفات GWOSC HDF5؛ التحقق هيكلي + SHA-256 محلي.
