# E07 · الأرض: سجل زلزالي (شبكة USArray TA + US)

- **الزمن (زمن رحلة الإشارة):** دقائق (زمن رحلة الموجات الزلزالية)
- **الجهاز:** IRIS DMC — محطة TA.W18A (BHZ، 40 عينة/ث، 612001 عينة) والمحطة US.WMOK
- **التاريخ:** 2014-03-17T04:11:34Z → 08:26:34Z
- **DOI:** لا DOI داخل الملف؛ معرّف DOI لشبكة TA لم يُتحقَّق منه من مصدره في هذه الجلسة، لذا لا يُذكر
- **الرخصة:** غير منصوصة في المستودع (iris-edu/noise-toolkit)؛ شروط استخدام IRIS DMC لم تُقرأ هنا
- **الملف الأقوى:** `07_IRIS_Earth_seismic/raw/TA.W18A..BHZ.M.2014,076,04:11:34.SAC`
- **المعالجة:** قراءة SAC، مخطط زمني، STFT (2048 نافذة/1024 تداخل)، وصوتنة WAV عند 4 kHz (تصغير 10× من 40 sps).
- **لون مُسند:** مطياف التردد: ألوان مُسندة (magma)
- **تحويل صوتي:** نعم: صوتنة السجل الزلزالي بـ4 kHz — تحويل صوتي مُعلن

## الملفات

| ملف | بايت | SHA-256 (16) | الدور | المصدر |
|---|---|---|---|---|
| `raw/README_noise_toolkit.md` | 6666 | `1140088454b24e4c` | doc | iris-edu/noise-toolkit@96f2c25d8192 :: README.md |
| `raw/TA.W18A..BHZ.M.2014,076,04:11:34.SAC` | 2448636 | `dd27222a3ac77c31` | primary-archive-product | iris-edu/noise-toolkit@96f2c25d8192 :: data/SAC/TA.W18A..BHZ.M.2014,076,04:11:34.SAC |
| `raw/US.WMOK.00.BHZ.M.2014,076,04:11:34.SAC` | 2448636 | `ffc68cb54ae917fc` | primary-archive-product | iris-edu/noise-toolkit@96f2c25d8192 :: data/SAC/US.WMOK.00.BHZ.M.2014,076,04:11:34.SAC |
| `derived/audio/ta_w18a_sonification.wav` | 1224046 | `3705fc2cf3896ea8` | derived-by-us | tools/make_products.py |
| `derived/ta_w18a_spectrogram.png` | 626127 | `5062c0e036188cc7` | derived-by-us | tools/make_products.py |
| `derived/ta_w18a_waveform.png` | 64903 | `04282793adb2e248` | derived-by-us | tools/make_products.py |

## ما ينقص / سؤال مفتوح

- هوية الحدث الزلزالي غير موثقة في الملف (لا وسم حدث)، والرخصة غير منصوصة، وDOI الشبكة لم يُتحقَّق.
- **سؤال مفتوح:** ما الحدث الزلزالي المقصود بنافذة 2014-03-17T04:11:34Z؟ وما معرّف DOI الرسمي لشبكة TA؟
