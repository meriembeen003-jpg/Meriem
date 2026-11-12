# تقرير التدقيق العلمي والتصحيحات
## The Complete History of the Universe — النسخة الكاملة (247 كيلوبايت، ~40,000 كلمة)

**المنهج:** قراءة النص كاملاً، ثم التحقق من كل رقم وتاريخ وإسناد مقابل المصادر الأولية: Planck 2018، Particle Data Group، CODATA/NIST، أوراق النشر الأصلية (PRL/PRD/Nature/ApJ)، وأرشيفات جوائز نوبل. الحكم لا يُطلق إلا بعد تطابق المصدرين على الأقل.

**النتيجة:** 55 تصحيحاً مؤكداً، موزعة على 27 نوعاً من الخطأ. لم يُمسّ أي مقطع سليم، والصياغة الأصلية محفوظة حرفياً في كل ما عدا المقاطع المصححة.

> **ملاحظة تقنية:** أداة قراءة Google Drive تحدّ كل استدعاء بنحو 16 ألف حرف، فقُرئ الملف كاملاً عبر نوافذ متداخلة (31 نافذة تغطي الفصول 1–25 والخاتمة). التصحيحات أدناه جاهزة للتطبيق آلياً عبر `revise_universe.py` دون أي تعديل يدوي.

---

## 1. جدول التصحيحات (ملخّص)

| # | الموضع | نوع الخطأ | الأصل ← الصواب |
|---|---|---|---|
| C01 | طول بلانك/البروتون | خطأ حسابي | 10⁻²³ ← 10⁻²⁰ |
| C02 | مرسوم 1277 وسيجيه دو برابان | خطأ تاريخي | «مرسوم On the Heaven» ← قائمة تامبييه 1277 |
| C03 | معامل التضخم | خطأ رياضي | 10⁷⁸ ← 10²⁶–10²⁷ |
| C04 | كتلة W مقابل الكوارك القمي | خطأ قاطع (مقلوب) | W أثقل 40,000 مرة ← W أخفّ بنحو النصف |
| C05 | نصيب هيغز من كتلة النوية | خطأ في النسبة | 9% ← ~1% |
| C06 | مطيافية الهايدروجين المضاد | خطأ زمني | 1995 ← 2016–2017 |
| C07 | حفظ الكتلة | إسناد خاطئ | سانتوريو ← لافوازييه |
| C08 | PSR J0740+6620 | خطأ تاريخي ورقمي | 2012 و10¹³ كغ/سم³ ← 2019 و~10¹² |
| C09 | نهاية التخليق النووي | تناقض داخلي | 200 ثانية ← ~1,200 ثانية |
| C10 | IceCube | رقم قديم | 80 حبلاً/4,000 ← 86 حبلاً/5,160 |
| C11 | إعادة اتحاد الهيليوم | تقدير زمني خاطئ | 100 ألف سنة/4000 K ← 30–40 ألف/6000–7000 K |
| C12 | حجة واينبرغ الأنثروبية | خطأ تاريخي | 1997 ← 1987 |
| C13 | الذرّية الهندية | إسناد ومصطلح خاطئان | Ājīvika/anūkara ← Vaiśeṣika/aṇu |
| C14 | القمي/الساحر | خطأ حسابي | 75,000 ← ~136 |
| C15 | اقتباس جويس | اقتباس ناقص | for Mark ← for Muster Mark |
| C16 | طاقة سلاك 1968 | رقم غير دقيق | 50 GeV ← ~20 GeV |
| C17 | مقياس الذرة | خطأ حسابي | 63,000 ← ~31,000 |
| C18 | فريدمان | خطأ تاريخي | 1925 لينينغراد ← 1922 بيتروغراد |
| C19 | انتهاك التكافؤ | خطأ في التجربة | تحلل الميون ← كوبالت-60 |
| C20 | طاقة السوبرنوفا | خطأ بمراتب قدرية | 10¹⁹ ← ~10²⁷ |
| C21 | خزان هومستيك | خطأ بمعامل ~10 | 40,000 لتر ← ~380,000 لتر |
| C22 | Jun Ye | خطأ في الاسم | John Ye ← Jun Ye |
| C23 | سكوت كيلي | خطأ رقمي | 520 يوماً ← 340 يوماً |
| C24 | ميليخين | خطأ في الاسم | Milovanov ← Milekhin |
| C25 | NANOGrav | رقم غير دقيق | 67 نباضاً ← 68 |
| C26 | الاقتباس الختامي | إسناد خاطئ | بورخيس ← تايسون |
| C27 | سداسي زحل/فوياجر | خطأ تاريخي | فوياجر-1 1981 ← 1980 |
| C28 | لوتين | خطأ في الاسم | William ← Willem |
| C29 | معجون نووي | خطأ في الاسم | Kaplan ← Caplan |
| C30 | انفجارات غاما | خطأ في الاسم | Klebasadel ← Klebesadel |
| C31 | الكوكب التاسع | خطأ في الاسمين | Schultz/Owen ← Scholtz/Unwin |
| C32 | كتلة الكوكب التاسع | خطأ بوحدة القياس | 5–6 M☉ ← 5–6 M⊕ |
| C33 | بيرلماتر | خطأ في الاسم | Perlmatter ← Perlmutter |
| C34 | جون بيل | خطأ في السيرة | أمريكي/قُتل ← بلفاستي/1990 |
| C35 | كلاوزر | خطأ في التجربة | إلكترونات ← فوتونات |
| C36 | نوبل التشابك | خطأ تاريخي | 2018 ← 2022 |
| C37 | المحّاء الكمومي | إسناد خاطئ | Zeilinger/Smullin ← Kim/Shih |
| C38 | المشاهد | إسناد خاطئ | تجربة بنروز 1996 ← لا وجود لها |
| C39 | التباعد الكمومي | إسناد خاطئ | Brassard-Bennett-Toffoli ← Bennett et al. 1993 |
| C40 | ER = EPR | إسناد خاطئ | Mahndré/Schulman ← Maldacena & Susskind |
| C41 | مالداسينا | خطأ في الجنسية | فلبيني ← أرجنتيني |
| C42 | سوسكند | خطأ في الجنسية | مكسيكي نووي ← أمريكي |
| C43 | عطية | خطأ في الجنسية | سويسري ← بريطاني-لبناني |
| C44 | يانغ–ميلز | إسناد خاطئ | John Cowper Ward ← Robert Mills |
| C45 | نوبل يانغ 1957 | إسناد خاطئ | نظرية المقياس ← انتهاك التكافؤ |
| C46 | التايجي | خطأ تاريخي | القرن 18 ق.م ← سونغ |
| C47 | جسيم Λ | خطأ تاريخي | 1975 ← 1950–51 |
| C48 | انتهاك CPT | خطأ مفهومي | CPT ← CP |
| C49 | سوبر-كاميوكاندي | رقم غير دقيق | 225 كيلوطناً ← 50 كيلوطناً |
| C50 | جسيم Oh-My-God | خطأ في الوحدة | 3.2 EeV ← 320 EeV |
| C51 | لانداور | تحديد زمني غير دقيق | الستينيات ← 1961 |
| C52 | Summit | خطأ في الوحدة | 3 MWh ← ~13 MW |
| C53 | الجدار الناري | خطأ مفهومي | خلط التكامل بالجدار ← تصحيح مفهومي |
| C54 | Enceladus (1) | خطأ إملائي | Enceledus ← Enceladus |
| C55 | Enceladus (2) | خطأ إملائي | Enceledus ← Enceladus |

---

## 1. Ch. 3 — Higgs mechanism — خطأ قاطع (مقلوب)  `C04`

**النص الأصلي:**

> W bosons became about 40,000 times heavier than the top quark

**التصحيح المعتمد:**

> W bosons became about 157,000 times heavier than the electron, while the top quark is in turn about twice as heavy as the W boson

**لماذا:** كتلة W ≈ 80.38 GeV وكتلة الكوارك القمي ≈ 172.7 GeV، أي أن W أخفّ من القمي بنحو النصف؛ ولا وجود لأي نسبة 40,000 بينهما (النسبة 157,000 هي W/الإلكترون).

**المصدر:** Particle Data Group, *Review of Particle Physics* (2022/2024): m_W = 80.377 GeV, m_t = 172.69 GeV

---

## 2. Ch. 1 — Planck Era — خطأ حسابي  `C01`

**النص الأصلي:**

> The Planck length is one hundred thousand quintillionth of the diameter of a proton

**التصحيح المعتمد:**

> The Planck length is about one hundred quintillionth of the diameter of a proton (a ratio of 10⁻²⁰)

**لماذا:** نسبة طول بلانك (1.6×10⁻³⁵ م) إلى قطر البروتون (1.7×10⁻¹⁵ م) هي 10⁻²⁰، أي «واحد من مئة كوينتيليون»، لا 10⁻²³.

**المصدر:** CODATA 2018 (NIST); PDG — proton rms charge radius 0.841 fm

---

## 3. Ch. 7 — Quark masses — خطأ حسابي  `C14`

**النص الأصلي:**

> where the top quark exceeds the charm quark's mass by 75,000 times

**التصحيح المعتمد:**

> where the top quark is about 136 times heavier than the charm quark

**لماذا:** m_t ≈ 172.7 GeV وm_c ≈ 1.27 GeV، والنسبة ≈ 136. والرقم 75,000 لا يوافق أي مقارنة معروفة.

**المصدر:** PDG (2024): m_c(m_c) = 1.27 ± 0.02 GeV, m_t = 172.69 ± 0.30 GeV

---

## 4. Ch. 7 — Atomic scale — خطأ حسابي  `C17`

**النص الأصلي:**

> the electron cloud is separated from the proton by a distance exceeding 63,000 times the proton's diameter

**التصحيح المعتمد:**

> the electron cloud is separated from the proton by a distance about 31,000 times the proton's diameter

**لماذا:** نصف قطر بور 5.29×10⁻¹¹ م ÷ قطر البروتون 1.7×10⁻¹⁵ م ≈ 31,000.

**المصدر:** CODATA 2018: a₀ = 5.29177210903×10⁻¹¹ m

---

## 5. Ch. 8 — Supernova energy — خطأ بمراتب قدرية  `C20`

**النص الأصلي:**

> but a supernova observed that same year at 45 million light-years released 10¹⁹ times more energy

**التصحيح المعتمد:**

> but a core-collapse supernova at a comparable distance releases about 10²⁷ times more energy

**لماذا:** طاقة السوبرنوفا النموذجية ~10⁴⁴ جول مقابل ~2×10¹⁷ جول لقنبلة القيصر (50 ميغاطن) → النسبة ~5×10²⁶ لا 10¹⁹.

**المصدر:** Woosley & Janka (2005) Nature Physics 1, 147; DOE/NNSA — yield of Tsar Bomba (50 Mt ≈ 2.1×10¹⁷ J)

---

## 6. Ch. 9 — Homestake — خطأ بمعامل ~10  `C21`

**النص الأصلي:**

> using 40,000 liters of cleaning fluid rich in chlorine

**التصحيح المعتمد:**

> using a 615-tonne tank of perchloroethylene (about 380,000 litres) rich in chlorine

**لماذا:** خزان تجربة هومستيك كان 100,000 غالون ≈ 380,000 لتر (615 طناً من C₂Cl₄) وليس 40,000 لتر.

**المصدر:** R. Davis Jr. (1964) Phys. Rev. Lett. 12, 303; Nobel Prize 2002 (advanced information)

---

## 7. Ch. 12 — Twin astronauts — خطأ رقمي  `C23`

**النص الأصلي:**

> increased by a few extra milliseconds for Scott's 520 days aboard the International Space Station at 27,600 km/h

**التصحيح المعتمد:**

> increased by a few extra milliseconds for Scott's 340 days aboard the International Space Station at 27,600 km/h

**لماذا:** مهمة سكوت كيلي «Year in Space» استمرت 340 يوماً (2015–2016) لا 520.

**المصدر:** NASA Twins Study (2019) Science 364, 6435

---

## 8. Ch. 1 — Discovery of expansion — خطأ تاريخي  `C02`

**النص الأصلي:**

> This was the idea the philosopher Siger of Brabant had proposed in the thirteenth century in his book *Summary of the Universe*, which the Church condemned in 1277 in the decree *On the Heaven and the Earth* — a decree Galileo later used to confess his forced recantation.

**التصحيح المعتمد:**

> This was among the Aristotelian propositions condemned in 1277 by Stephen Tempier, Bishop of Paris — a condemnation that also targeted the philosopher Siger of Brabant. (*On the Heavens*, *De Caelo*, is the title of Aristotle's treatise, not of any Church decree, and no such decree featured in Galileo's 1633 abjuration.)

**لماذا:** لا وجود لمرسوم كنسي باسم «On the Heaven and the Earth»؛ هذا عنوان كتاب أرسطو (De Caelo). الإدانة الصادرة في 7 مارس 1277 هي قائمة 219 أطروحة أصدرها الأسقف إتيان تامبييه، وكان سيجيه دو برابان من المستهدفين بها، ولم تُذكر في تنازل جاليليو 1633.

**المصدر:** H. Denifle & É. Châtelain, *Chartularium Universitatis Parisiis* I (1889), 543–558; J. F. Wippel, «The Condemnation of 1277» (in *The Stanford Encyclopedia of Philosophy / SEP*)

---

## 9. Ch. 6 — Cosmological constant — خطأ تاريخي  `C12`

**النص الأصلي:**

> as Steven Weinberg argued in 1997

**التصحيح المعتمد:**

> as Steven Weinberg argued in 1987

**لماذا:** ورقة واينبرغ المرجعية عن الحد الأنثروبي للثابت الكوني نُشرت في Physical Review Letters عام 1987.

**المصدر:** S. Weinberg (1987) Phys. Rev. Lett. 59, 2607

---

## 10. Ch. 7 — Friedmann — خطأ تاريخي  `C18`

**النص الأصلي:**

> after Alexander Friedmann predicted the expansion of the universe in 1925 in Leningrad

**التصحيح المعتمد:**

> after Alexander Friedmann predicted the expansion of the universe in 1922 in Petrograd

**لماذا:** ورقة فريدمان الأولى نُشرت عام 1922 (والثانية 1924)، وكانت المدينة قد صارت لينينغراد عام 1924 فقط.

**المصدر:** A. Friedmann (1922) Z. Phys. 10, 377; (1924) Z. Phys. 21, 326

---

## 11. Ch. 15 — Saturn — خطأ تاريخي  `C27`

**النص الأصلي:**

> a hexagonal jet stream crowns the north pole observed by the Voyager-1 probe in 1981

**التصحيح المعتمد:**

> a hexagonal jet stream crowns the north pole, imaged by Voyager 1 in 1980 and re-observed by Voyager 2 in 1981

**لماذا:** فوياجر 1 حلّق قرب زحل في 12 نوفمبر 1980، وفوياجر 2 في أغسطس 1981؛ فأي نسبة للعام 1981 يجب أن تكون لفوياجر 2.

**المصدر:** NASA/JPL Voyager mission timeline; Godfrey (1988) Icarus 76, 335

---

## 12. Ch. 21 — Nobel 2022 — خطأ تاريخي  `C36`

**النص الأصلي:**

> Then in 2018, the "Nobel Prize for the Death of Local Reality" was awarded

**التصحيح المعتمد:**

> Then in 2022, the Nobel Prize in Physics was awarded

**لماذا:** جائزة نوبل لأسبر وكلاوزر وزيلينغر مُنحت في أكتوبر 2022 لا 2018.

**المصدر:** Nobel Prize in Physics 2022 (nobelprize.org)

---

## 13. Ch. 22 — Taiji — خطأ تاريخي  `C46`

**النص الأصلي:**

> From Chinese Taoist philosophy's Taiji diagram (eighteenth century BC)

**التصحيح المعتمد:**

> From Chinese Taoist philosophy's Taiji diagram (a Song-dynasty symbol, 11th–12th century AD)

**لماذا:** رمز التايجيtu نشأ في عهد أسرة سونغ، ولا يعود إلى الألف الثاني قبل الميلاد.

**المصدر:** Needham, *Science and Civilisation in China*, vol. 2

---

## 14. Ch. 22 — Strange baryons — خطأ تاريخي  `C47`

**النص الأصلي:**

> gives physical explanation for the 1975 discovery of the "strange Lambda baryon" at the Brookhaven Laboratory

**التصحيح المعتمد:**

> is a separate matter from the discovery of the strange Lambda baryon in cosmic rays in 1950–51, and of the Ω⁻ at Brookhaven in 1964

**لماذا:** جسيم Λ اكتُشف في الأشعة الكونية عام 1950–51، وΩ⁻ في بروكهافن عام 1964؛ ولا وجود لاكتشاف «1975».

**المصدر:** Rochester & Butler (1947) Nature 160, 855; Barnes et al. (1964) PRL 12, 204

---

## 15. Ch. 3 — Antimatter — خطأ زمني  `C06`

**النص الأصلي:**

> then the assembly of 9 antihydrogen atoms in CERN's LEAR ring in 1995 and proof of the exact matching of its light spectrum with ordinary hydrogen

**التصحيح المعتمد:**

> then the assembly of 9 antihydrogen atoms in CERN's LEAR ring in 1995 — while the exact matching of antihydrogen's light spectrum with ordinary hydrogen was only achieved in 2016–2017 by the ALPHA experiment

**لماذا:** إنتاج 9 ذرات في 1995 صحيح، لكن مطيافية الهايدروجين المضاد (انتقال 1S–2S) لم تُنجز إلا عام 2016 (ALPHA) ثم بقياس أدق 2017.

**المصدر:** ALPHA Collaboration, Nature 541, 506 (2017); Ahmadi et al., Nature 557, 71 (2018)

---

## 16. Ch. 3 — Higgs mechanism — خطأ في النسبة  `C05`

**النص الأصلي:**

> However, the Higgs field generates only about 9% of the proton and neutron mass

**التصحيح المعتمد:**

> However, the Higgs field accounts for only about 1% of the proton and neutron mass

**لماذا:** كتل الكواركات الحالية لا تساهم في كتلة النوية إلا بنحو 1%؛ والباقي (>99%) طاقة ربط QCD وتحرّك الغلوونات والكواركات الافتراضية.

**المصدر:** PDG (2024) — proton mass decomposition; Yang et al. (2018) Phys. Rev. Lett. 121, 212001

---

## 17. Ch. 2 — Inflation — خطأ رياضي  `C03`

**النص الأصلي:**

> increasing the universe's size by a factor of about 10⁷⁸

**التصحيح المعتمد:**

> increasing the universe's size by a factor of about 10²⁶–10²⁷ (roughly e⁶⁰, i.e. 60 e-folds)

**لماذا:** مضاعفة الحجم 80–90 مرة تعني 2⁸⁰–2⁹⁰ ≈ 10²⁴–10²⁷، والتضخم القياسي يمنح نحو 60 e-fold أي e⁶⁰ ≈ 10²⁶. أما 10⁷⁸ فتوازي نحو 260 مضاعفة.

**المصدر:** Guth (1981) Phys. Rev. D 23, 347; Baumann, *TASI Lectures on Inflation* (2009), §3

---

## 18. Ch. 3 — Mass conservation — إسناد خاطئ  `C07`

**النص الأصلي:**

> The principle of mass conservation in chemical reactions had been firmly established since the experiments of the Italian physician Santorio Santorio in the seventeenth century

**التصحيح المعتمد:**

> The principle of mass conservation in chemical reactions was firmly established by Antoine Lavoisier's quantitative experiments in the 1770s and 1780s

**لماذا:** سانتوريو سانتوريو (1561–1636) معروف بتجاربه على «العرق غير المحسوس»، وليس بمبدأ حفظ الكتلة في التفاعلات الكيميائية؛ الصياغة الكمية للمبدأ تُنسب إلى لافوازييه.

**المصدر:** A. Lavoisier, *Traité élémentaire de chimie* (1789); Encyclopaedia Britannica, «Antoine Lavoisier»

---

## 19. Final page — Epigraph — إسناد خاطئ  `C26`

**النص الأصلي:**

> Jorge Luis Borges, after Hawking's remark that the universe does not owe us an explanation

**التصحيح المعتمد:**

> Neil deGrasse Tyson (2011); the line is widely misattributed to Borges and has no source in his work

**لماذا:** العبارة «The universe is under no obligation to make sense to you» منسوبة خطأً لبورخيس؛ وهي من نيل ديغراس تايسون.

**المصدر:** N. deGrasse Tyson, *Space Chronicles* (2012) / Twitter, 2011; Quote Investigator

---

## 20. Ch. 21 — Quantum eraser — إسناد خاطئ  `C37`

**النص الأصلي:**

> The "Delayed-Choice Quantum Eraser" experiment of 1999 by Anton Zeilinger and Jacques Smullin at the University of Innsbruck decided this

**التصحيح المعتمد:**

> The delayed-choice quantum eraser experiment of 1999 by Yoon-Ho Kim, Yanhua Shih and colleagues (with a related delayed-choice test by Anton Zeilinger's group in Innsbruck) decided this

**لماذا:** تجربة المحّاء الكمومي المؤخَّر الشهيرة (1999) أجراها كيم وشيه وزملاؤهما، و«Jacques Smullin» ليس من مؤلفيها.

**المصدر:** Kim, Kulik, Shih et al. (2000) Phys. Rev. Lett. 84, 1

---

## 21. Ch. 21 — Observer — إسناد خاطئ  `C38`

**النص الأصلي:**

> (as proven by Roger Penrose in 1996 with the "Parity Inversion Delayed Choice Experiment" where the choice to measure polarization of a flying photon happens after the photon is inside the Michelson-Morley beamsplitter!)

**التصحيح المعتمد:**

> (delayed-choice experiments demand no conscious observer — only classical information recorded by the apparatus)

**لماذا:** لا وجود لتجربة بهذا الاسم لروجر بنروز عام 1996؛ وبنروز فيزيائي جاذبية لا تجريبي في البصريات الكمومية.

**المصدر:** Aspect et al. (1982) PRL 49, 91; Jacques et al. (2007) Science 315, 966

---

## 22. Ch. 21 — Teleportation — إسناد خاطئ  `C39`

**النص الأصلي:**

> The teleportation protocol (Brassard-Benneti-Toffoli)

**التصحيح المعتمد:**

> The teleportation protocol (Bennett, Brassard, Crépeau, Jozsa, Peres and Wootters, 1993)

**لماذا:** البروتوكول الأصلي للتباعد الكمومي (1993) من ستة مؤلفين، وليس «Brassard-Bennett-Toffoli».

**المصدر:** Bennett et al. (1993) Phys. Rev. Lett. 70, 1895

---

## 23. Ch. 21 — ER = EPR — إسناد خاطئ  `C40`

**النص الأصلي:**

> "ER = EPR" Conjecture (Mahndré, Schulman, & Maldacena, 2013)

**التصحيح المعتمد:**

> "ER = EPR" Conjecture (Maldacena & Susskind, 2013)

**لماذا:** اسمًان مُختلقان؛ الفرضية لمالداسينا وسوسكند (arXiv:1306.0533).

**المصدر:** Maldacena & Susskind (2013) Fortschr. Phys. 61, 781

---

## 24. Ch. 22 — Yang–Mills — إسناد خاطئ  `C44`

**النص الأصلي:**

> physicist John Cowper Ward and Chen-Ning Yang proved that the internal geometric symmetry of interactions underlies the entire dynamics of particle physics

**التصحيح المعتمد:**

> physicists Chen-Ning Yang and Robert Mills (1954) showed that local internal gauge symmetry underlies the dynamics of particle physics

**لماذا:** نظرية يانغ–ميلز (1954) لـ يانغ وروبرت ميلز؛ ولا وجود لفيزيائي باسم «John Cowper Ward».

**المصدر:** Yang & Mills (1954) Phys. Rev. 96, 191

---

## 25. Ch. 22 — Yang Nobel — إسناد خاطئ  `C45`

**النص الأصلي:**

> whose mathematical mastery earned Yang the Nobel Prize of 1957 for Minakshisundaram and Plebanski and Sidney Coleman's pioneering work in 1974

**التصحيح المعتمد:**

> a framework whose consequences shaped all later particle physics (Yang's 1957 Nobel, however, was for parity violation with T. D. Lee, not for gauge theory)

**لماذا:** نوبل 1957 ليانغ كان مع تسونغ داو لي على انتهاك التكافؤ، لا على نظرية المقياس؛ والأسماء المذكورة لا علاقة لها بالجائزة.

**المصدر:** Nobel Prize in Physics 1957 (nobelprize.org)

---

## 26. Ch. 7 — Indian atomism — إسناد ومصطلح خاطئان  `C13`

**النص الأصلي:**

> The reductionist conception of matter appeared in Indian philosophy in the eighth century BCE (the Ājīvika school in Kashmir assumed two possible compositions of the world: the internal principle "anūkara," an indivisible accumulation of fundamental units, and the external accumulation "aṭṭara")

**التصحيح المعتمد:**

> The reductionist conception of matter appeared in Indian philosophy in the first millennium BCE (the Vaiśeṣika school attributed to Kaṇāda, and earlier the Ājīvika current, conceived of indivisible ultimate units called aṇu / paramāṇu, whose combinations compose all bodies)

**لماذا:** المدرسة الذرّية الهندية هي «فايشيشيكا» (کانادا)، والمصطلح المتداول هو aṇu / paramāṇu. أما «anūkara» و«aṭṭara» وربط الآجيفيكا بكشمير فلا سند موثوق لهما.

**المصدر:** SEP, «Atomism, Indian»; *Encyclopaedia of Indian Philosophy* (Vaiśeṣika, Kaṇāda)

---

## 27. Ch. 10 — JILA — خطأ في الاسم  `C22`

**النص الأصلي:**

> In February 2022, John Ye's team at JILA

**التصحيح المعتمد:**

> In February 2022, Jun Ye's team at JILA

**لماذا:** الباحث هو جون يي (Jun Ye) لا «John Ye».

**المصدر:** Bothwell et al. (2022) Nature 602, 420 (JILA/NIST)

---

## 28. Ch. 12 — Traversable wormholes — خطأ في الاسم  `C24`

**النص الأصلي:**

> then Juan Maldacena and Alexey Milovanov

**التصحيح المعتمد:**

> then Juan Maldacena and Alexey Milekhin

**لماذا:** الاسم الصحيح أليكسي ميليخين (Alexey Milekhin).

**المصدر:** Maldacena & Milekhin (2021) Phys. Rev. D 103, 066007

---

## 29. Ch. 15 — White dwarfs — خطأ في الاسم  `C28`

**النص الأصلي:**

> William Luyten named these stellar corpses

**التصحيح المعتمد:**

> Willem Luyten named these stellar corpses

**لماذا:** الاسم الصحيح فيليم ياكوب لوتين (Willem Jacob Luyten) لا «William».

**المصدر:** Luyten (1922) Proc. Natl. Acad. Sci.; Holberg, *Sirius* (2007)

---

## 30. Ch. 16 — Nuclear pasta — خطأ في الاسم  `C29`

**النص الأصلي:**

> Matthew Kaplan and Charles Horowitz named

**التصحيح المعتمد:**

> Matthew Caplan and Charles Horowitz named

**لماذا:** الباحث هو ماثيو كابلان (Matthew Caplan) لا «Kaplan».

**المصدر:** Caplan & Horowitz (2017) Rev. Mod. Phys. 89, 041002

---

## 31. Ch. 16 — GRBs — خطأ في الاسم  `C30`

**النص الأصلي:**

> declassified in 1973 by Ray Klebasadel at Los Alamos

**التصحيح المعتمد:**

> declassified in 1973 by Ray Klebesadel at Los Alamos

**لماذا:** الاسم الصحيح راي كليبيزيدل (Ray Klebesadel).

**المصدر:** Klebesadel, Strong & Olson (1973) ApJL 182, L85

---

## 32. Ch. 19 — Dark energy — خطأ في الاسم  `C33`

**النص الأصلي:**

> the Supernova Cosmology Project led by Saul Perlmatter

**التصحيح المعتمد:**

> the Supernova Cosmology Project led by Saul Perlmutter

**لماذا:** الاسم الصحيح سول بيرلماتر (Saul Perlmutter).

**المصدر:** Nobel Prize in Physics 2011 (nobelprize.org)

---

## 33. Ch. 8 — Parity violation — خطأ في التجربة  `C19`

**النص الأصلي:**

> after Wu, Yang, and Lee (1956) proved parity breaking (P) in the decay of the muon (π → μ + ν)

**التصحيح المعتمد:**

> after Lee and Yang (1956) proposed and Wu (1957) proved parity breaking (P) in the beta decay of polarised cobalt-60 — the same asymmetry later seen in pion decay (π → μ + ν)

**لماذا:** تجربة وو الحاسمة كانت على تحلل بيتا لنوى الكوبالت-60 المستقطبة، لا على «تحلل الميون»؛ وπ → μ + ν تحلل بيون لا ميون.

**المصدر:** Wu et al. (1957) Phys. Rev. 105, 1413; Lee & Yang (1956) Phys. Rev. 104, 254

---

## 34. Ch. 21 — Clauser — خطأ في التجربة  `C35`

**النص الأصلي:**

> John Clauser performed the first actual tests of this inequality at Lawrence Berkeley Laboratory using entangled pairs of electrons

**التصحيح المعتمد:**

> John Clauser performed the first actual tests of this inequality at Lawrence Berkeley Laboratory using entangled pairs of photons

**لماذا:** تجربة فريدمان–كلاوزر (1972) استخدمت فوتوناتٍ متشابكة من كالسيوم، لا زوج إلكترونات؛ وأول اختبار بإلكترونات جاء لاحقاً وبصعوبة أكبر.

**المصدر:** Freedman & Clauser (1972) Phys. Rev. Lett. 28, 938

---

## 35. Ch. 4 — BBN timing — تناقض داخلي  `C09`

**النص الأصلي:**

> The cosmic nuclear furnace stopped completely at the twentieth minute (t ≈ 200 seconds)

**التصحيح المعتمد:**

> The cosmic nuclear furnace stopped completely at about the twentieth minute (t ≈ 1,200 seconds)

**لماذا:** الدقيقة العشرون تساوي 1200 ثانية لا 200 ثانية؛ والانطفاء الكامل يُؤرَّخ عادةً بنحو 20 دقيقة (بعد تفكيك الديوتيريوم عند ~200 ثانية).

**المصدر:** PdG / Planck 2018 VI (A&A 641, A6), §Big Bang Nucleosynthesis

---

## 36. Ch. 5 — Helium recombination — تقدير زمني خاطئ  `C11`

**النص الأصلي:**

> At an age of about 100,000 years and a temperature drop to about 4000 K, helium nuclei captured electrons first

**التصحيح المعتمد:**

> At an age of roughly 30,000–40,000 years and temperatures of about 6,000–7,000 K, helium nuclei captured electrons first

**لماذا:** إعادة اتحاد الهيليوم (He III → He II) تحدث عند z ≈ 5000–6000، أي عند عمر ~30–40 ألف سنة ودرجة ~6000–7000 كلفن، لا 100 ألف سنة/4000 كلفن (وهي أرقام إعادة اتحاد الهيدروجين تقريباً).

**المصدر:** Seager, Sasselov & Scott (2000) ApJS 128, 407; Planck 2018 VI

---

## 37. Ch. 4 — IceCube — رقم قديم  `C10`

**النص الأصلي:**

> equipped with over 4,000 optical units distributed on 80 strings

**التصحيح المعتمد:**

> equipped with 5,160 digital optical modules distributed on 86 strings

**لماذا:** العدد النهائي لمرصد IceCube هو 5160 وحدة بصرية على 86 حبلاً (النسخة المؤقتة IceCube-79 كانت 79 حبلاً/4860 وحدة).

**المصدر:** IceCube Collaboration, J. Phys. Conf. Ser. 60, 012002; icecube.wisc.edu

---

## 38. Ch. 7 — SLAC — رقم غير دقيق  `C16`

**النص الأصلي:**

> when electrons at 50 GeV were fired at protons and neutrons

**التصحيح المعتمد:**

> when electrons at about 20 GeV were fired at protons and neutrons

**لماذا:** طاقة المسرّع الخطي في تجارب سلاك الحاسمة (1968–1969) كانت قريبة من 20 GeV؛ الوصول إلى 50 GeV جاء لاحقاً في السبعينيات.

**المصدر:** SLAC (1968) «Deep Inelastic Scattering»; Nobel Prize 1990 (Friedman, Kendall, Taylor)

---

## 39. Ch. 12 — NANOGrav — رقم غير دقيق  `C25`

**النص الأصلي:**

> after monitoring the timing of 67 millisecond pulsars in the Milky Way for fifteen years

**التصحيح المعتمد:**

> after monitoring the timing of 68 millisecond pulsars in the Milky Way for fifteen years

**لماذا:** مجموعة بيانات NANOGrav الممتدة 15 سنة تضم 68 نباضاً مليثانياً.

**المصدر:** Agazie et al. (2023) ApJL 951, L8 (NANOGrav 15-yr data set)

---

## 40. Ch. 22 — Proton decay — رقم غير دقيق  `C49`

**النص الأصلي:**

> or the vast mass of liquid water (225 kilotons as in the Kamioka ND experiment in Japan

**التصحيح المعتمد:**

> or the vast mass of liquid water (50 kilotons in Super-Kamiokande, Japan

**لماذا:** سوبر-كاميوكاندي يحتوي 50,000 طن من الماء؛ و«225 كيلوطناً» لا توافق أي كاشف قائم.

**المصدر:** Super-Kamiokande Collaboration, Nucl. Instrum. Methods A 501, 418 (2003)

---

## 41. Ch. 7 — Joyce quote — اقتباس ناقص  `C15`

**النص الأصلي:**

> borrowing its spelling from the phrase "three quarks for Mark" in James Joyce's novel *Finnegans Wake*

**التصحيح المعتمد:**

> borrowing its spelling from the phrase "Three quarks for Muster Mark!" in James Joyce's novel *Finnegans Wake*

**لماذا:** نص جويس الحرفي هو «Three quarks for Muster Mark!».

**المصدر:** J. Joyce, *Finnegans Wake* (1939), Book II, ch. 4

---

## 42. Ch. 4 — Neutron star — خطأ تاريخي ورقمي  `C08`

**النص الأصلي:**

> like the pulsar PSR J0740 observed by the Green Bank Telescope in 2012 with a mass of 2.1 M☉ compressed into a 27 km diameter, a density of 10¹³ kg/cm³

**التصحيح المعتمد:**

> like the pulsar PSR J0740+6620, discovered with the Green Bank Telescope in 2019, with a mass of 2.14 M☉ compressed into roughly a 25–30 km diameter and a mean density of about 10¹² kg/cm³

**لماذا:** PSR J0740+6620 أُعلن عام 2019 لا 2012. والكثافة المتوسطة للنجوم النيوترونية ≈ 5×10¹⁷ كغ/م³ أي ≈ 5×10¹¹ كغ/سم³، فالمذكور 10¹³ مبالغ فيه نحو 20 مرة.

**المصدر:** Cromartie et al. (2019) Nature Astronomy 4, 72; Lattimer & Prakash (2004) Science 304, 536

---

## 43. Ch. 17 — Planet Nine — خطأ في الاسمين  `C31`

**النص الأصلي:**

> Jacob Schultz and James Owen even proposed in 2019

**التصحيح المعتمد:**

> Jakub Scholtz and James Unwin even proposed in 2019

**لماذا:** صاحبا فرضية «الثقب الأسود البدائي ككوكب تاسع» هما ياكوب شولتز وجيمس أنوين.

**المصدر:** Scholtz & Unwin (2020) Phys. Rev. Lett. 125, 051103 (arXiv 2019)

---

## 44. Ch. 17 — Planet Nine — خطأ بوحدة القياس  `C32`

**النص الأصلي:**

> ("Planet Nine" with a mass of 5–6 M☉ at 400–500 AU)

**التصحيح المعتمد:**

> ("Planet Nine" with a mass of 5–6 Earth masses at 400–500 AU)

**لماذا:** كتلة الكوكب التاسع المفترض هي 5–6 كتل أرضية (M⊕) لا شمسية؛ والفقرة نفسها تذكر لاحقاً «خمس كتل أرضية».

**المصدر:** Batygin & Brown (2016) AJ 151, 22; Scholtz & Unwin (2020)

---

## 45. Ch. 21 — Bell — خطأ في السيرة  `C34`

**النص الأصلي:**

> the late John Stewart Bell (an American-born physicist working in explosion mechanics at CERN, killed by 2000)

**التصحيح المعتمد:**

> the late John Stewart Bell (a Belfast-born physicist who worked on accelerator design at CERN, and died in 1990)

**لماذا:** جون ستيوارت بيل وُلد في بلفاست (إيرلندا الشمالية) وتوفي في 1 أكتوبر 1990؛ وليس أمريكياً ولا «قُتل».

**المصدر:** Royal Society Biographical Memoirs; Bell, *Speakable and Unspeakable in QM* (1987)

---

## 46. Ch. 21 — Maldacena — خطأ في الجنسية  `C41`

**النص الأصلي:**

> a visiting Filipino student named Juan Maldacena

**التصحيح المعتمد:**

> a visiting Argentine physicist named Juan Maldacena

**لماذا:** خوان مالداسينا أرجنتيني، وكان زميلاً مبتدئاً في هارفارد (1998–2001).

**المصدر:** Harvard Society of Fellows (1998–2001); IAS faculty biography of J. Maldacena

---

## 47. Ch. 21 — Susskind — خطأ في الجنسية  `C42`

**النص الأصلي:**

> former Mexican nuclear physicist Leonard Susskind

**التصحيح المعتمد:**

> American theoretical physicist Leonard Susskind

**لماذا:** سوسكند أمريكي وُلد في نيويورك، ولم يكن فيزيائياً نووياً مكسيكياً.

**المصدر:** Stanford University faculty biography; Susskind, *The Black Hole War* (2008)

---

## 48. Ch. 22 — Atiyah — خطأ في الجنسية  `C43`

**النص الأصلي:**

> Swiss-born mathematician Michael Atiyah

**التصحيح المعتمد:**

> British-Lebanese mathematician Michael Atiyah

**لماذا:** مايكل عطية وُلد في لندن لأب لبناني وأم إنجليزية، وحمل الجنسية البريطانية.

**المصدر:** Royal Society Biographical Memoirs of M. F. Atiyah (1929–2019)

---

## 49. Ch. 22 — CPT — خطأ مفهومي  `C48`

**النص الأصلي:**

> but strangely violates the "CPT theorem" in the decay of B-mesons as observed in the BaBar experiment

**التصحيح المعتمد:**

> but CP itself is violated in the decay of B-mesons, as observed by the BaBar experiment

**لماذا:** CPT مبدأ مصون في نظرية الحقل الكمومي؛ المنتهَك هو CP لا CPT.

**المصدر:** BaBar Collaboration (2001) PRL 87, 091801; CPLEAR/PDG review on CPT invariance

---

## 50. Ch. 23 — Complementarity — خطأ مفهومي  `C53`

**النص الأصلي:**

> But from the perspective of an infalling observer, the information never crosses the horizon, because it is "reflected" from the firewall at the event horizon (a barrier of enormous energy that forms at the horizon and destroys anyone who tries to enter!)

**التصحيح المعتمد:**

> From the infalling observer's perspective, complementarity says the information crosses the horizon unharmed — which is exactly what the 2012 AMPS "firewall" argument challenged: it claimed that unitarity, the equivalence principle and effective field theory cannot all hold, so a wall of high-energy quanta must form at the horizon

**لماذا:** الفقرة تخلط بين «التكامل» (complementarity) و«الجدار الناري» (firewall) وهما متعارضان: الجدار الناري نتيجة تناقض، لا وصف لوجهة نظر الساقط.

**المصدر:** Almheiri, Marolf, Polchinski & Sully (2013) JHEP 02, 062; Susskind (1995) J. Math. Phys. 36, 6377

---

## 51. Ch. 23 — Oh-My-God particle — خطأ في الوحدة  `C50`

**النص الأصلي:**

> the Oh-My-God Particle (3.2 EeV)

**التصحيح المعتمد:**

> the Oh-My-God Particle (320 EeV)

**لماذا:** الطاقة 3.2×10²⁰ eV = 320 EeV؛ و«3.2 EeV» تصغير بمئة ضعف.

**المصدر:** Bird et al. (1995) ApJ 441, 144 (Fly's Eye)

---

## 52. Ch. 23 — Summit — خطأ في الوحدة  `C52`

**النص الأصلي:**

> achieved 1.1 × 10¹⁸ operations per second (over 1 exaflop) in 2018 with a power consumption approaching 3 megawatt hours

**التصحيح المعتمد:**

> achieved 1.1 × 10¹⁸ operations per second (over 1 exaflop) in 2018 with a power consumption of about 13 megawatts

**لماذا:** القدرة الكهربائية تُقاس بالميغاواط لا «ميغاواط·ساعة»؛ واستهلاك Summit نحو 13 ميغاواط.

**المصدر:** TOP500 list (June 2018); ORNL Summit specifications

---

## 53. Ch. 23 — Landauer — تحديد زمني غير دقيق  `C51`

**النص الأصلي:**

> A long time ago in the 1960s, physicist Rolf Landauer proved

**التصحيح المعتمد:**

> In 1961, physicist Rolf Landauer proved

**لماذا:** مبدأ لانداور نُشر عام 1961 في IBM Journal.

**المصدر:** Landauer (1961) IBM J. Res. Dev. 5, 183

---

## 54. Ch. 15–16 — Enceladus (1) — خطأ إملائي  `C54`

**النص الأصلي:**

> the moon Enceledus

**التصحيح المعتمد:**

> the moon Enceladus

**لماذا:** الاسم الصحيح Enceladus.

**المصدر:** IAU planetary nomenclature

---

## 55. Ch. 14–15 — Enceladus (2) — خطأ إملائي  `C55`

**النص الأصلي:**

> like Enceledus without metals

**التصحيح المعتمد:**

> like Enceladus without metals

**لماذا:** الاسم الصحيح Enceladus.

**المصدر:** IAU planetary nomenclature

---

## 2. ما تم التحقق من صحته (لم يُعدّل)

توثيقاً للحياد: هذه المقاطع راجعتها مقابل المصادر ووجدتها دقيقة كما هي.

| العبارة | المرجع |
|---|---|
| عمر الكون 13.787 ± 0.020 مليار سنة | Planck 2018 (A&A 641, A6) — مطابق تماماً |
| نصف قطر الكون المرصود 46.5 مليار سنة ضوئية (قطر ~93) | Planck 2018؛ Gott et al. (2005) — صحيح |
| درجة حرارة الخلفية الميكروية 2.725 كلفن | COBE/FIRAS — صحيح |
| ثابت هابل القانوني v = H₀d ونسبته إلى لومتر 1927 | Lemaître (1927) Ann. Soc. Sci. Brux. 47, 49 — صحيح |
| تسمية «الانفجار العظيم» ساخرةً في برنامج بي بي سي 1949 | Hoyle, BBC Third Programme, 28 March 1949 — صحيح |
| تضخم Guth في ديسمبر 1979 في SLAC | Guth (1981) PRD 23, 347 — صحيح |
| التضخم الخالد: Linde / Albrecht–Steinhardt 1982 | PRD 49 (1994) / PRL 48 (1982) — صحيح |
| نموذج Hartle–Hawking 1983 ومحاضرة الفاتيكان 1981 | Hartle & Hawking (1983) PRD 28, 2960 — صحيح |
| إيكبايروتيك 2001 (Khoury, Ovrut, Steinhardt, Turok) | PRD 64, 123522 — صحيح |
| الكسر CP: Fitch & Cronin 1964 (1 من 500 كاون، 301/300) | PRL 13, 138 (1964) — صحيح |
| GW150914: 14 سبتمبر 2015، 36+29 → 62 كتلة شمسية | Abbott et al. (2016) PRL 116, 061102 — صحيح |
| هفيلي–كيتنغ 1971 وفارق بضع مئات من النانوثانية | Science 177, 166 (1972) — صحيح |
| PSR B1913+16: 1974، تقلّص المدار 3.5 م/سنة | Hulse & Taylor (1975) ApJL 195, L51 — صحيح |
| إنتروبيا الكون 10⁸⁸ → 10¹⁰⁴ k_B | Egan & Lineweaver (2010) ApJ 710, 1825 — صحيح |
| خط 21 سم: 1420.405 MHz، ΔE ≈ 5.87×10⁻⁶ eV، انتظار 11 مليون سنة | Ewen & Purcell (1951) Nature 168, 356 — صحيح |
| NIF: 2.05 MJ → 3.15 MJ في 5 ديسمبر 2022 | DOE/NNSA & LLNL announcement (Dec 2022) — صحيح |
| GW170817 وتشكّل السترونشيوم | Watson et al. (2019) Nature 574, 497 — صحيح |
| SMSS J0313–6708 بـ [Fe/H] < −7.1 (2014) | Keller et al. (2014) Nature 506, 463 — صحيح |
| JWST: إطلاق 25 ديسمبر 2021، مرآة 6.5 م، نقطة L2 | NASA/ESA — صحيح |
| مضاعف g للإلكترون 2.00231930436 وتطابق 10⁻¹² | Fan et al. (2023) PRL 130, 071801 — صحيح |

---

## 3. كيف تُطبَّق التصحيحات

```bash
python corrections/revise_universe.py "The Complete History of the Universe (English - Full Translation).md"
```

يُنتج الملف: `The Complete History of the Universe (English - Full Translation) — REVISED.md`
بكل التصحيحات مطبّقة، مع بقاء كل حرف آخر كما هو. السكربت لا يستبدل مقطعاً إلا إذا وُجد **مرة واحدة** بالضبط، ويطبع تقريراً بكل تصحيح طُبّق أو تُخطّي، فلا خطر من إفساد النص.

**ملاحظة إضافية غير مصحّحة آلياً:** أرقام مثل «17 حقلاً كمومياً» و«61 جسيماً» و«10⁸⁰ بروتوناً» و«6.7×10⁶¹ طن TNT» تحققتُ منها ووجدتها متوافقة مع المصادر (PDG، Planck) فتُركت كما هي.