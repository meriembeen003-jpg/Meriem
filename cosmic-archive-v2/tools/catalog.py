#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event catalogue: the single source of truth for folders, products and metadata.

Nothing here downloads anything.  Every entry describes *what the official
archive publishes*, where its documented entry point is, and how a downloaded
file must be validated.  `fetch_primary.py` reads this catalogue, `make_derived.py`
consumes what was downloaded, and `tools/make_index.py` renders INDEX.md from it.

Field notes
-----------
kind          "observation" = a measurement recorded by an instrument
              "model"       = a theoretical / simulated product (never evidence)
              "test"        = calibration / demonstration / cropped product
doi           DOI that must resolve to the dataset landing page (checked by
              fetch_primary.py through https://doi.org/ )
license_url   page where the archive states the licence (fetched and stored)
verified_by   callable name used in fetch_primary.py to validate the file
"""

from __future__ import annotations

import textwrap

EVENTS = [
    dict(
        id="E01",
        folder="E01_CMB_SMICA",
        title="أقدم ضوء: خريطة SMICA كاملة وطيف القدرة المقاس (Planck 2018)",
        lookback_years=13.8e9,
        lookback_label="13.8 مليار سنة (z≈1100، 380,000 سنة بعد الانفجار)",
        instrument="Planck — HFI/LFI (SMICA component separation, R3.00 map; R3.01 measured spectra)",
        program="Planck 2018 legacy release (PR3)",
        doi="10.1051/0004-6361/201833880",
        doi_role="ورقة Planck 2018 I — تصف منتجات PR3؛ DOI مجموعة البيانات نفسه غير موجود، انظر السؤال المفتوح",
        license_text="ESA Planck Legacy Archive: بيانات Planck عامة للاستخدام العلمي؛ شرط الاستشهاد بورقة Planck 2018. لا نصّ رخصة مضمَّن في ملفات FITS.",
        license_url="https://pla.esac.esa.int/pla/#home",
        targets=[
            dict(
                name="COM_CMB_IQU-smica_2048_R3.00_full.fits",
                role="خريطة SMICA كاملة (T/Q/U، NSIDE 2048) — 2.0 GB",
                kind="observation",
                candidates=[
                    "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-smica_2048_R3.00_full.fits",
                    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits",
                    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits?__skymap=1",
                ],
                max_bytes=3_000_000_000,
                validation="fits_planck_map",
            ),
            dict(
                name="COM_PowerSpect_CMB-TT-full_R3.01.txt",
                role="طيف TT المقاس (لا النظري) مع الخطأ",
                kind="observation",
                candidates=[
                    "https://pla.esac.esa.int/pla/aio/product-action?SPECTRA.SPECTRA_ID=COM_PowerSpect_CMB-TT-full_R3.01.txt",
                    "https://pla.esac.esa.int/pla/aio/product-action?SPECTRA.SPECTRA_ID=COM_PowerSpect_CMB-TT-full_R3.01",
                    "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/COM_PowerSpect_CMB-TT-full_R3.01.txt",
                ],
                max_bytes=20_000_000,
                validation="planck_spectrum",
            ),
            dict(
                name="COM_PowerSpect_CMB-TE-full_R3.01.txt",
                role="طيف TE المقاس",
                kind="observation",
                candidates=[
                    "https://pla.esac.esa.int/pla/aio/product-action?SPECTRA.SPECTRA_ID=COM_PowerSpect_CMB-TE-full_R3.01.txt",
                    "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/COM_PowerSpect_CMB-TE-full_R3.01.txt",
                ],
                max_bytes=20_000_000,
                validation="planck_spectrum",
            ),
            dict(
                name="COM_PowerSpect_CMB-EE-full_R3.01.txt",
                role="طيف EE المقاس",
                kind="observation",
                candidates=[
                    "https://pla.esac.esa.int/pla/aio/product-action?SPECTRA.SPECTRA_ID=COM_PowerSpect_CMB-EE-full_R3.01.txt",
                    "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/COM_PowerSpect_CMB-EE-full_R3.01.txt",
                ],
                max_bytes=20_000_000,
                validation="planck_spectrum",
            ),
        ],
        derived=["SMICA T-map Mollview PNG (colour assigned, colourbar in µK)",
                  "TT/TE/EE measured spectra PNG with error bars"],
        open_question="PR3 لا يحمل DOI على مستوى المجموعة (فقط DOI الورقة 10.1051/0004-6361/201833880). هل تُدرج المجموعة بمعرّف PLA الداخلي بدل DOI؟",
    ),
    dict(
        id="E02",
        folder="E02_GW150914",
        title="اندماج ثقبين أسودين: GW150914 (H1 + L1 + ملف الحدث + خريطة السماء)",
        lookback_years=1.3e9 / 1.0,
        lookback_label="≈1.3 مليار سنة (D_L ≈ 420 Mpc)",
        instrument="Advanced LIGO — H1 (Hanford) و L1 (Livingston)",
        program="O1 / LOSC — GPS 1126259462.4",
        doi="10.7935/K5MW2F23",
        doi_role="DOI مجموعة بيانات GW150914 على GWOSC (يحلّ إلى صفحة الحدث)",
        license_text="GWOSC: البيانات متاحة للجمهور؛ شرط GWOSC هو الاستشهاد بالورقة وDOI. لا نصّ رخصة صريح على صفحة الحدث.",
        license_url="https://gwosc.org/events/GW150914/",
        targets=[
            dict(name="H-H1_LOSC_16_V1-1126259446-32.hdf5", role="انفعال H1، 16 kHz، 32 ثانية",
                 kind="observation", gwosc=dict(event="GW150914", detector="H1", sampling_rate=16384, duration=32),
                 validation="gwosc_hdf5"),
            dict(name="L-L1_LOSC_16_V1-1126259446-32.hdf5", role="انفعال L1، 16 kHz، 32 ثانية",
                 kind="observation", gwosc=dict(event="GW150914", detector="L1", sampling_rate=16384, duration=32),
                 validation="gwosc_hdf5"),
            dict(name="event_json_GW150914.json", role="ملف الحدث (JSON الرسمي من GWOSC API)",
                 kind="observation", gwosc=dict(event="GW150914", meta_only=True), validation="gwosc_event_json"),
            dict(name="LALInference_skymap.fits.gz", role="خريطة السماء لاحتمال الموضع (P1500227)",
                 kind="observation", gwosc=dict(event="GW150914", skymap=True), validation="healpix_fits"),
        ],
        derived=["strain whitened 20–300 Hz PNG (H1+L1)",
                  "sonification WAV 16 kHz (whitened strain — تحويل صوتي)",
                  "skymap Mollview PNG (colour assigned)"],
        open_question="لا مجموع اختباري منشور رسمياً لملفات GWOSC HDF5؛ التحقق هيكلي + SHA-256 محلي.",
    ),
    dict(
        id="E03",
        folder="E03_EHT_M87",
        title="ظل ثقب أسود: M87* — بيانات EHT 2019 الرسمية + المنتج الصوري",
        lookback_years=5.5e7,
        lookback_label="≈55 مليون سنة ضوئية (16.8 Mpc)",
        instrument="EHT 2017 — 8 محطات، 229 GHz",
        program="EHT 2019-D01-01 (calibrated data) + 2019-D01-02 (imaging pipelines)",
        doi="10.25739/g85n-f134",
        doi_role="DOI مجموعة البيانات (CyVerse Data Commons) — يجب أن يحلّ إلى صفحة المجموعة",
        license_text="ODC-PDDL 1.0 لملفات البيانات، GPLv3 للسكربتات (نصّ الرخصة منشور مع المجموعة)",
        license_url="https://eventhorizontelescope.org/for-astronomers/data",
        targets=[
            dict(name="SR1_M87_2017_096_hi_hops_netcal_StokesI.uvfits",
                 role="بيانات معايرة (Stokes I، hops) — الليلة 096، النطاق العالي",
                 kind="observation", eht=dict(repo_doi="10.25739/g85n-f134", product="SR1_M87_2017_096_hi_hops_netcal_StokesI.uvfits"),
                 validation="uvfits"),
            dict(name="EHT_M87_official_image.fits", role="المنتج الصوري الرسمي (إن نشره التعاون)",
                 kind="observation", eht=dict(repo_doi="10.25739/g85n-f134", image=True), validation="fits_image"),
        ],
        derived=["UV amplitude vs baseline PNG", "closure phase histogram PNG",
                  "official image render PNG (colour assigned) — فقط إن وُجد المنتج الرسمي"],
        open_question="هل يوزّع EHT المنتج الصوري النهائي (FITS/PNG) عبر CyVerse بنفس DOI؟ الصور المنشورة في الأوراق ليست ملفات أرشيف.",
    ),
    dict(
        id="E04",
        folder="E04_EHT_SgrA",
        title="ظل ثقب أسود: Sgr A* — بيانات EHT 2022 الرسمية",
        lookback_years=2.7e4,
        lookback_label="≈27,000 سنة ضوئية (8.2 kpc)",
        instrument="EHT 2017 ER6 — 9 محطات، 227 GHz",
        program="EHT 2022-D02-01 (First Sgr A* Results: calibrated data)",
        doi="10.25739/m140-ct59",
        doi_role="DOI مجموعة بيانات Sgr A* (CyVerse) — يجب أن يحلّ إلى صفحة المجموعة",
        license_text="ODC-PDDL 1.0 لملفات البيانات، GPLv3 للسكربتات",
        license_url="https://eventhorizontelescope.org/for-astronomers/data",
        targets=[
            dict(name="ER6_SGRA_2017_097_lo_hops_netcal-LMTcal_StokesI.uvfits",
                 role="بيانات معايرة — الليلة 097، النطاق المنخفض",
                 kind="observation", eht=dict(repo_doi="10.25739/m140-ct59", product="ER6_SGRA_2017_097_lo_hops_netcal-LMTcal_StokesI.uvfits"),
                 validation="uvfits"),
        ],
        derived=["UV amplitude vs baseline PNG", "closure phase histogram PNG"],
        open_question="هل صورة Sgr A* الرسمية موزّعة كملف بيانات أم فقط كشكل في الورقة؟",
    ),
    dict(
        id="E05",
        folder="E05_HST",
        title="نجم قريب: صورة ACS/WFC3 كاملة + طيف GD153 المرصود (STIS)",
        lookback_years=205.0,
        lookback_label="≈205 سنة ضوئية (63 pc)",
        instrument="HST — ACS/WFC أو WFC3/UVIS (صورة كاملة) و STIS (طيف GD153)",
        program="برنامج GD153 (STIS) وبرنامج الصورة: يُقرأ من ترويسة المنتج (PROPOSID)",
        doi="",
        doi_role="لا DOI لمنتج HST مفرد؛ المعرّف الرسمي هو obs_id + PROPOSID من الترويسة. بادئة MAST (10.17909) لم يُتحقَّق منها هنا فلا تُنسب.",
        license_text="MAST/STScI: منتجات HST عامة؛ MAST تطلب الاستشهاد بمعرّف المنتج وبرنامج الرصد. لا نصّ رخصة في الترويسة.",
        license_url="https://mast.stsci.edu/",
        targets=[
            dict(name="HST_full_frame_flc.fits", role="صورة ACS/WFC أو WFC3/UVIS كاملة (FLT/FLC) بترويسة كاملة",
                 kind="observation", mast=dict(kind="image"), validation="hst_image"),
            dict(name="gd153_stis_x1d.fits", role="طيف GD153 المرصود (STIS x1d) مع PROPOSID",
                 kind="observation", mast=dict(kind="spectrum", target="GD153"), validation="hst_spectrum"),
        ],
        derived=["image PNG cutout of the full frame (colour assigned, log stretch)",
                  "STIS spectrum PNG"],
        open_question="أي برنامج HST يُستخدم للصورة الكاملة (اقتراح محدد)؟ يُختار تلقائياً أكبر منتج WFC3/UVIS أو ACS/WFC متاح في MAST ويُسجَّل PROPOSID.",
    ),
    dict(
        id="E06",
        folder="E06_SDO_AIA171",
        title="الشمس الآن: إطار AIA 171 كامل 4096×4096 + فيديو 120 إطاراً",
        lookback_years=0.0,
        lookback_label="8.3 دقيقة (1 AU)",
        instrument="SDO/AIA — 171 Å، مستوى 1",
        program="AIA lev1 (JSOC/VSO)",
        doi="",
        doi_role="لا DOI لإطار AIA مفرد؛ المعرّف هو T_REC/T_OBS + INSTRUME. لا يُنسب DOI غير محقَّق.",
        license_text="NASA SDO: بيانات عامة بلا قيود (NASA open data, CC0-like policy). لا نصّ رخصة في الترويسة.",
        license_url="https://sdo.gsfc.nasa.gov/data/",
        targets=[
            dict(name="AIA171_fullframe.fits", role="إطار كامل 4096×4096 مستوى 1 لأحدث يوم متاح",
                 kind="observation", sdo=dict(kind="single", wavelength=171), validation="aia_fullframe"),
            dict(name="AIA171_movie.mp4", role="فيديو 120 إطاراً متتالية (تركيب منا، ألوان مُسندة)",
                 kind="observation", sdo=dict(kind="movie", wavelength=171, frames=120), validation="mp4"),
        ],
        derived=["frame PNG (colour assigned)", "MP4 labelled as our composite"],
        open_question="VSO يعطي إطارات 4096؛ JSOC export يحتاج بريداً مسجّلاً (--jsoc-email) لتسلسل زمني أسرع.",
    ),
    dict(
        id="E07",
        folder="E07_IRIS",
        title="الأرض: زلزال كبير بمعرّف USGS + سجلات عدة محطات IRIS",
        lookback_years=0.0,
        lookback_label="دقائق (زمن رحلة الموجات)",
        instrument="IRIS DMC عبر FDSN — محطات متعددة (BHZ/HHZ)",
        program="USGS ComCat event id + IRIS FDSN dataselect",
        doi="",
        doi_role="DOI يُقرأ آلياً من خدمة IRIS fdsnws/doi لكل شبكة مستخدمة ويُحلّ ويُسجَّل مع السجل — لا DOI ثابت مكتوب هنا.",
        license_text="IRIS DMC: بيانات مفتوحة للبحث والتعليم؛ شرط الإقرار بـIRIS والـDOI لكل شبكة.",
        license_url="https://service.iris.edu/",
        targets=[
            dict(name="USGS_event.json", role="ملف الحدث الرسمي من USGS ComCat (المعرّف والمكان والقوة)",
                 kind="observation", usgs=dict(), validation="usgs_event"),
            dict(name="IRIS_multi_station.mseed", role="سجلات ≥5 محطات حول الحدث",
                 kind="observation", usgs=dict(), validation="mseed"),
        ],
        derived=["waveform PNG per station", "spectrogram PNG (colour assigned)", "sonification WAV"],
        open_question="أي زلزال؟ يُختار آلياً أكبر حدث M≥7.5 في آخر 10 سنوات من كتالوج USGS FDSN، ويُسجَّل معرّفه.",
    ),
    dict(
        id="E08",
        folder="E08_CMS_AOD",
        title="LHC: ملف أحداث CMS 2012 حقيقي (AOD) بدل الهستوغرام",
        lookback_years=0.0,
        lookback_label="الحاضر (2012)",
        instrument="CMS — pp 8 TeV، Run2012C DoubleMuParked AOD 22Jan2013-v1",
        program="CERN Open Data record 6030 (DOI 10.7483/OPENDATA.CMS.M5AD.Y3V3)",
        doi="10.7483/OPENDATA.CMS.M5AD.Y3V3",
        doi_role="DOI المجموعة — يجب أن يحلّ إلى سجل 6030",
        license_text="CC0 1.0 (بيانات CERN Open Data) — منصوص على صفحة السجل",
        license_url="https://opendata.cern.ch/record/6030",
        targets=[
            dict(name="CMS_Run2012C_DoubleMuParked_AOD.root", role="ملف AOD واحد (أحداث حقيقية)",
                 kind="observation", cern=dict(recid=6030), validation="cms_aod"),
        ],
        derived=["event-count and muon-kinematics PNGs computed from the AOD file",
                  "dimuon invariant-mass spectrum (calculated by us from AOD)"],
        open_question="ملف AOD واحد ~2 GB؛ إن حُجب xrootd يُستخدم cernopendata-client عبر HTTPS.",
    ),
    dict(
        id="E09",
        folder="E09_OPENNEURO",
        title="الدماغ البشري: T1w + BOLD من OpenNeuro ds000001",
        lookback_years=0.0,
        lookback_label="الحاضر",
        instrument="Siemens 3T، تصوير بالرنين المغناطيسي الوظيفي (BART task)",
        program="OpenNeuro ds000001 (OpenfMRI, Poldrack lab)",
        doi="10.18112/openneuro.ds000001",
        doi_role="DOI مجموعة OpenNeuro (كما تنشره المنصة) — يُحلّ ويُتحقَّق عند التشغيل؛ لم يُتحقَّق منه في هذه البيئة",
        license_text="ODC-PDDL 1.0 (منصوص على صفحة المجموعة)",
        license_url="https://openneuro.org/datasets/ds000001",
        targets=[
            dict(name="sub-01_T1w.nii.gz", role="صورة تشريحية T1w",
                 kind="observation", openneuro=dict(dataset="ds000001", include=["sub-01/anat/sub-01_T1w.nii.gz"]),
                 validation="nifti"),
            dict(name="sub-01_task-balloonanalogrisktask_run-01_bold.nii.gz", role="سلسلة BOLD (fMRI)",
                 kind="observation", openneuro=dict(dataset="ds000001",
                                                    include=["sub-01/func/sub-01_task-balloonanalogrisktask_run-01_bold.nii.gz"]),
                 validation="nifti"),
        ],
        derived=["orthogonal slice PNGs (T1w + BOLD mean) — colours assigned"],
        open_question="OpenNeuro يقدّم SHA-256 لكل ملف عبر API؛ يُقارن تلقائياً بعد التنزيل.",
    ),
    dict(
        id="E10",
        folder="E10_JWST_SMACS0723",
        title="جيمس ويب: SMACS 0723 (صورة MAST)",
        lookback_years=4.6e9,
        lookback_label="≈4.6 مليار سنة (عدسة عنقودية؛ ضوء أقدم)",
        instrument="JWST — NIRCam (F444W/F200W/F150W/F090W)",
        program="JWST ERS 2736 — SMACS J0723.3-7327",
        doi="",
        doi_role="لا DOI لمنتج JWST مفرد؛ المعرّف obs_id + PROPOSID (برنامج ERS يُقرأ من الترويسة ويُسجَّل).",
        license_text="MAST: منتجات JWST عامة بعد انتهاء فترة الملكية الحصرية؛ لا نصّ رخصة في الترويسة",
        license_url="https://mast.stsci.edu/",
        targets=[
            dict(name="JWST_SMACS0723_i2d.fits", role="صورة معالجة i2d لأحد مرشحات NIRCam",
                 kind="observation", mast=dict(kind="jwst", target="SMACS J0723.3-7327"), validation="jwst_image"),
        ],
        derived=["RGB-composite PNG (our composition, channels assigned)"],
        open_question="التركيب RGB يتطلب 3 مرشحات؛ إن لم تتوفر كلها يُنتج PNG أحادي القناة موسوم بوضوح.",
    ),
]

BY_ID = {e["id"]: e for e in EVENTS}
BY_FOLDER = {e["folder"]: e for e in EVENTS}

RECORD_TYPE_AR = {"observation": "رصد", "model": "نموذج", "test": "اختبار"}
