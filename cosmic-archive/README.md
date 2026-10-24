# cosmic-archive

فهرس Markdown + مجلد منظم لأدلة حسية من أرشيفات أولية مفتوحة (MAST · Planck/PLA · SDO · EHT · GWOSC · IRIS · CERN Open Data · OpenNeuro).

- **الفهرس:** `INDEX.md`
- **كل ملف + SHA-256 + مصدره (مستودع/commit/مسار):** `MANIFEST.csv`
- **الاستنساخ الكامل للتنزيلات:** `_download_provenance.json`
- **إعادة الحساب:** `python3 tools/verify.py`
- **إعادة إنتاج المشتقات (رسوم/صوتنة):** `python3 tools/make_products.py` ثم `python3 tools/build_index.py`
  (يتطلب numpy, astropy, matplotlib, scipy, h5py, obspy, uproot)
