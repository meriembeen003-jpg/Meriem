"""Build the archive manifest.

Each entry describes one independent observation (an object seen in one waveband by
one instrument). Duplicates are collapsed by ``dedupe_key`` so that the same press
image shipped in several resolutions/repos is stored only once at its highest
resolution, while genuinely different wavelengths of the same object are kept.
"""
import hashlib
import os
import json
from texts import TEXTS

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

FOLDERS = {
    "galaxies": "1seHJAsLW3K0v3gfNF2fTjdBatJGwhQm0",
    "bh": "1c45o4b510WaxRC74qzoqWNoN1mHEyDCf",
    "stars": "1B18KNLQXwUtkfBh-Vnv6uOSYtEFBPTws",
    "nebulae": "1xUX8RNnj3uI7VPVb0mCSrsASUHlHXlhe",
    "exo": "1y6G8Mhw0mdPg-w28Bo5Ai9IloSFUzdVy",
    "clusters": "1yItH7fnCvEbVoEvNkJwoNV8SMRFPhgPx",
    "deep": "1SuharM5HeGjJDKPZNasGDJEKDTyjTR05",
    "snr": "1MMa2IKhGONwrzXVyEGu2ruvxZjq3Wj8R",
    "fits": "1tlnIfkjFiIK5ByUgzHauZVFueN4w1dsn",
    "sun": "1CeqQ3F4xz-mcrekkgWchnE-N2ara-rA1",
}

# ---------------------------------------------------------------------------
# Webb: NASA/ESA/CSA/STScI press images (webbtelescope.org), credits STScI
WEBB_BASE = dict(
    telescope="James Webb Space Telescope (JWST) — 6.5 m, نقطة L2",
    credit="NASA, ESA, CSA, STScI (معالجة الصور: STScI/JWST ERO)",
    license="مشاع إبداعي CC BY 4.0 (NASA/ESA/CSA/STScI) — الصور العلمية متاحة للعامة",
    archive="https://webbtelescope.org",
)

WEBB = [
    dict(key="smacs", obs="smacs", file="raw/space-wallpapers/webb_first_deep_field_4K.png",
         name="SMACS 0723 أول حقل عميق من ويب", folder="deep", wl="أشعة تحت حمراء قريبة-متوسطة (0.9–4.8 µm) — NIRCam",
         instrument="NIRCam (6 مرشحات)", date="2022-07-11",
         src="WEBB 2022/038", extra="First Deep Field"),
    dict(key="carina_nircam", obs="carina_nir", file="raw/space-wallpapers/webb_carina_4K.png",
         name="سد كارينا — منحدرات الكون الصخرية", folder="nebulae", wl="أشعة تحت حمراء قريبة (1.4–4.4 µm) — NIRCam",
         instrument="NIRCam", date="2022-07-12", src="WEBB 2022/031", extra="Carina Nebula Cosmic Cliffs"),
    dict(key="carina_miri", file="raw/space-wallpapers/webb_carina_miri_4K.png",
         name="سد كارينا بالأشعة تحت الحمراء المتوسطة", folder="nebulae", wl="أشعة تحت حمراء متوسطة (7.7–18 µm) — MIRI",
         instrument="MIRI", date="2022-07-12", src="WEBB 2022/031", extra="Carina MIRI"),
    dict(key="tarantula", obs="tarantula_nir", file="raw/space-wallpapers/webb_tarantula.png",
         name="سد الرتيلاء (30 Doradus) في سحابة ماجلان الكبرى", folder="nebulae",
         wl="أشعة تحت حمراء قريبة (0.9–4.4 µm) — NIRCam", instrument="NIRCam",
         date="2022-09-06", src="WEBB 2022/041", extra="Tarantula Nebula"),
    dict(key="cartwheel", obs="cartwheel_nir", file="raw/space-wallpapers/webb_cartwheel.png",
         name="مجرة عجلة العربة (ESO 350-40)", folder="galaxies",
         wl="أشعة تحت حمراء قريبة-متوسطة (0.9–18 µm) — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2022-08-02", src="WEBB 2022/039", extra="Cartwheel Galaxy"),
    dict(key="quintet", obs="quintet_nir", file="raw/space-wallpapers/webb_stephans_quintet_4K.png",
         name="خماسية ستيفان (HCG 92)", folder="clusters",
         wl="أشعة تحت حمراء قريبة-متوسطة (0.9–21 µm) — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2022-07-12", src="WEBB 2022/034", extra="Stephan's Quintet"),
    dict(key="southern_ring", obs="sring_nir", file="raw/space-wallpapers/webb_southern_ring_4K.png",
         name="سد الحلقة الجنوبية (NGC 3132)", folder="nebulae",
         wl="أشعة تحت حمراء قريبة (2.12 + 4.7 µm) — NIRCam", instrument="NIRCam",
         date="2022-07-12", src="WEBB 2022/033", extra="Southern Ring Nebula"),
    dict(key="ring", file="raw/space-wallpapers/webb_ring.png",
         name="سد الحلقة (M57، NGC 6720)", folder="nebulae",
         wl="أشعة تحت حمراء قريبة-متوسطة (0.9–18 µm) — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2023-08-21", src="STScI 01H82G0PP38P6PBXQ11BEVSMY0", extra="Ring Nebula M57"),
    dict(key="pillars", file="raw/space-wallpapers/webb_pillars.png",
         name="أعمدة الخلق (M16, سد النسر)", folder="nebulae",
         wl="أشعة تحت حمراء قريبة (1.87–4.44 µm) — NIRCam", instrument="NIRCam",
         date="2022-10-19", src="STScI 01GK2KKTR81SGYF24YBGYG7TAP", extra="Pillars of Creation"),
    dict(key="casa", file="raw/space-wallpapers/webb_cassiopeia_a.png",
         name="ذات الكرسي أ (Cassiopeia A) — بقايا مستعر أعظم", folder="snr",
         wl="أشعة تحت حمراء قريبة-متوسطة (1.6–21 µm) — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2023-12-10", src="WEBB 2023/149", extra="Cassiopeia A"),
    dict(key="ic348", file="raw/space-wallpapers/webb_ic_348.png",
         name="سد IC 348 وحزام الكويكبات في العنقود الشاب", folder="stars",
         wl="أشعة تحت حمراء قريبة-متوسطة — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2023-12-13", src="WEBB 2023/151", extra="IC 348"),
    dict(key="chamaeleon", file="raw/space-wallpapers/webb_chamaeleon.png",
         name="الحرباء I — منطقة تكوّن نجوم قريبة", folder="stars",
         wl="أشعة تحت حمراء قريبة-متوسطة — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2023-11-20", src="WEBB 2023/106", extra="Chamaeleon I"),
    dict(key="ice", file="raw/space-wallpapers/webb_ice_1440p.png",
         name="سد الحرباء: خريطة جليد الماء والجزيئات العضوية", folder="stars",
         wl="أشعة تحت حمراء متوسطة (طيف 3 µm) — MIRI/NIRSpec", instrument="NIRSpec + MIRI",
         date="2023-01-23", src="NASA Webb Flickr 52638633506", extra="Ice mapping"),
    dict(key="aww", obs="sring_nir", file="raw/WebbCompare/webb/southern_nebula.png",
         name="سد الحلقة الجنوبية — تفصيل عالي الدقة (NIRCam)", folder="nebulae",
         wl="أشعة تحت حمراء قريبة (2.12 + 4.7 µm) — NIRCam", instrument="NIRCam",
         date="2022-07-12", src="WEBB 2022/033 (full frame)", extra="Southern Ring high-res"),
    dict(key="aww_df", obs="smacs", file="raw/WebbCompare/webb/deep_field.png",
         name="SMACS 0723 — إطار كامل غير مُقتطع", folder="deep",
         wl="أشعة تحت حمراء قريبة-متوسطة (0.9–4.8 µm) — NIRCam", instrument="NIRCam",
         date="2022-07-11", src="WEBB 2022/038 (full frame)", extra="SMACS 0723 full frame"),
    dict(key="aww_quintet", obs="quintet_nir", file="raw/WebbCompare/webb/stephans_quintet.jpg",
         name="خماسية ستيفان — إطار كامل", folder="clusters",
         wl="أشعة تحت حمراء قريبة-متوسطة — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2022-07-12", src="WEBB 2022/034 (full frame)", extra="Stephan's Quintet full frame"),
    dict(key="aww_tarantula", obs="tarantula_nir", file="raw/WebbCompare/webb/tarantula.png",
         name="سد الرتيلاء — إطار كامل", folder="nebulae",
         wl="أشعة تحت حمراء قريبة — NIRCam", instrument="NIRCam", date="2022-09-06",
         src="WEBB 2022/041 (full frame)", extra="Tarantula full frame"),
    dict(key="aww_carina", obs="carina_nir", file="raw/WebbCompare/webb/carina.jpg",
         name="سد كارينا — إطار كامل لـ NIRCam", folder="nebulae",
         wl="أشعة تحت حمراء قريبة — NIRCam", instrument="NIRCam", date="2022-07-12",
         src="WEBB 2022/031 (full frame)", extra="Carina full frame"),
    dict(key="aww_cartwheel", obs="cartwheel_nir", file="raw/WebbCompare/webb/cartwheel.png",
         name="عجلة العربة — إطار كامل", folder="galaxies",
         wl="أشعة تحت حمراء قريبة-متوسطة — NIRCam + MIRI", instrument="NIRCam + MIRI",
         date="2022-08-02", src="WEBB 2022/039 (full frame)", extra="Cartwheel full frame"),
    # Hubble
    dict(key="h_carina", file="raw/WebbCompare/hubble/carina.png",
         name="سد كارينا — ضوء مرئي (هابل)", folder="nebulae", telescope="Hubble Space Telescope (2.4 m)",
         wl="ضوء مرئي/أشعة تحت حمراء قريبة (0.4–0.9 µm) — ACS/WFC",
         instrument="ACS/WFC", date="2007-04-24", src="NASA/STScI Hubble",
         credit="NASA, ESA, N. Smith (UC Berkeley) and the Hubble Heritage Team (STScI/AURA)", license="CC BY 4.0 (NASA/ESA)",
         extra="Carina visible"),
    dict(key="h_southern", file="raw/WebbCompare/hubble/southern_nebula.png",
         name="سد الحلقة الجنوبية — ضوء مرئي (هابل)", folder="nebulae", telescope="Hubble Space Telescope (2.4 m)",
         wl="ضوء مرئي (0.4–0.7 µm) — WFPC2", instrument="WFPC2", date="1998-05-28",
         src="NASA/STScI Hubble", credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Southern Ring visible"),
    dict(key="h_tarantula", file="raw/WebbCompare/hubble/tarantula.png",
         name="سد الرتيلاء — ضوء مرئي/هيدروجين (هابل)", folder="nebulae", telescope="Hubble Space Telescope (2.4 m)",
         wl="ضوء مرئي (Hα + [O III] + [S II]) — WFC3/UVIS", instrument="WFC3/UVIS",
         date="2011-06-01", src="NASA/STScI Hubble", credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Tarantula visible"),
    dict(key="h_cartwheel", file="raw/WebbCompare/hubble/cartwheel.png",
         name="عجلة العربة — ضوء مرئي (هابل)", folder="galaxies", telescope="Hubble Space Telescope (2.4 m)",
         wl="ضوء مرئي (0.4–0.7 µm) — WFC3", instrument="WFC3", date="2014-10-15",
         src="NASA/STScI Hubble", credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Cartwheel visible"),
    dict(key="h_deep", file="raw/WebbCompare/hubble/deep_field.png",
         name="حقل SMACS 0723 — ضوء مرئي (هابل، قبل ويب)", folder="deep", telescope="Hubble Space Telescope (2.4 m)",
         wl="ضوء مرئي (0.4–0.9 µm) — ACS/WFC", instrument="ACS/WFC", date="2017-06-01",
         src="NASA/STScI Hubble", credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="SMACS 0723 Hubble"),
]

# ---------------------------------------------------------------------------
# NASA/JPL/STScI imagery re-hosted by unit511/space-wallpapers (README maps each file
# back to its original NASA asset id)
WP = [
    dict(key="andromeda", file="raw/space-wallpapers/andromeda_4K.png", folder="galaxies",
         name="مجرة أندروميدا (M31) في الأشعة تحت الحمراء",
         telescope="Wide-field Infrared Survey Explorer (WISE) — NASA", instrument="WISE (IR)",
         wl="أشعة تحت حمراء متوسطة (3.4–22 µm)", date="2010-01-05", src="PIA15416",
         credit="NASA/JPL-Caltech/WISE Team", license="ملكية عامة (NASA) — تُنسب إلى NASA/JPL-Caltech",
         extra="Andromeda M31"),
    dict(key="whirlpool", file="raw/space-wallpapers/whirlpool_galaxy_1440p.png", folder="galaxies",
         name="مجرة الدوّامة (M51a) ورفيقتها NGC 5195",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC",
         wl="ضوء مرئي + Hα (0.4–0.8 µm)", date="2005-04-01", src="NASA GSFC 20171208 Archive e001925",
         credit="NASA, ESA, S. Beckwith (STScI) and the Hubble Heritage Team", license="CC BY 4.0 (NASA/ESA)",
         extra="Whirlpool M51"),
    dict(key="m81", file="raw/space-wallpapers/m81_galaxy_1440p.png", folder="galaxies",
         name="مجرة M81 (NGC 3031) — القرص والذراعان الحلزونيتان",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC + قرار مرئي ضيق",
         wl="أشعة تحت حمراء (3.6–8 µm) + ضوء مرئي", date="2003-12-01", src="PIA09579",
         credit="NASA/JPL-Caltech/SST", license="ملكية عامة (NASA)",
         extra="M81"),
    dict(key="spiral", file="raw/space-wallpapers/spiral_galaxy_4K.png", folder="galaxies",
         name="مجرة حلزونية ضلعية (NGC 1300)",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC",
         wl="ضوء مرئي (0.4–0.7 µm، أربعة مرشحات)", date="2005-02-01", src="NASA GSFC 20171208 Archive e002154",
         credit="NASA, ESA, and The Hubble Heritage Team (STScI/AURA)", license="CC BY 4.0 (NASA/ESA)",
         extra="NGC 1300 barred spiral"),
    dict(key="two_galaxies", file="raw/space-wallpapers/two_galaxies_4K.png", folder="galaxies",
         name="زوج مجري متفاعل (NGC 2336/2276)",
         telescope="Galaxy Evolution Explorer (GALEX) + قرار أرضي", instrument="GALEX NUV/FUV",
         wl="فوق بنفسجي (0.15–0.28 µm) مع ضوء مرئي", date="2006-07-01", src="NASA GSFC 20171208 Archive e000097",
         credit="NASA/JPL-Caltech/GALEX", license="ملكية عامة (NASA)",
         extra="Interacting galaxy pair"),
    dict(key="rainbow", file="raw/space-wallpapers/rainbow_galaxy_4K.png", folder="galaxies",
         name="مجرة «قوس قزح» — NGC 4725 الضلعية",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC (24 µm + قرار مرئي)",
         wl="أشعة تحت حمراء (8 + 24 µm) فوق صورة مرئية", date="2005-05-01", src="PIA08093",
         credit="NASA/JPL-Caltech", license="ملكية عامة (NASA)",
         extra="Deep Space 1 / NGC 4725"),
    dict(key="ufo", file="raw/space-wallpapers/ufo_galaxy_4K.png", folder="galaxies",
         name="مجرة «الطبق الطائر» NGC 2787",
         telescope="Hubble Space Telescope (2.4 m)", instrument="WFPC2",
         wl="ضوء مرئي (0.4–0.7 µm)", date="2002-01-01", src="NASA GSFC 20171208 Archive e001757",
         credit="NASA/STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="NGC 2787"),
    dict(key="faint_compact", file="raw/space-wallpapers/faint_compact_galaxy_4K.png", folder="galaxies",
         name="مجرة حديثة النشأة في العنقود المجري A1689",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC + عدسة جاذبية",
         wl="ضوء مرئي (0.4–0.9 µm)", date="2009-01-01", src="PIA20054",
         credit="NASA, ESA/L. Bradley (JHU)", license="CC BY 4.0 (NASA/ESA)",
         extra="Faint compact galaxy A1689"),
    dict(key="galaxy_pair", file="raw/space-wallpapers/galaxy_pair_1080p.png", folder="galaxies",
         name="زوج NGC 2207 و IC 2163 المتفاعلان",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC + Spitzer",
         wl="ضوء مرئي + أشعة تحت حمراء", date="2006-07-01", src="NASA 0203049",
         credit="NASA, ESA, STScI, and JPL-Caltech", license="CC BY 4.0 (NASA/ESA)",
         extra="NGC 2207 IC 2163"),
    dict(key="crab", file="raw/space-wallpapers/crab_nebula_4K.png", folder="snr",
         name="سد السلطعون (M1) — بقايا مستعر أعظم 1054",
         telescope="Hubble Space Telescope (2.4 m)", instrument="WFPC2",
         wl="ضوء مرئي (0.4–0.7 µm) + الأشعة السينية (Chandra)", date="1999-11-01", src="PIA03606",
         credit="NASA/CXC/ASU/J. Hester et al.", license="ملكية عامة (NASA/CXC)",
         extra="Crab Nebula M1"),
    dict(key="cats_paw", file="raw/space-wallpapers/cats_paw_nebula_1080p.png", folder="nebulae",
         name="سد «قدم القط» (NGC 6334) — مصنع نجوم",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC/MIPS",
         wl="أشعة تحت حمراء (8–70 µm)", date="2005-11-01", src="PIA22567",
         credit="NASA/JPL-Caltech", license="ملكية عامة (NASA)",
         extra="Cat's Paw NGC 6334"),
    dict(key="carina_vis", file="raw/space-wallpapers/carina_nebula_4K.png", folder="nebulae",
         name="سد كارينا — خريطة هيدروجين عريضة (صورة أرضية/هابل)",
         telescope="مقراب أرضي واسع المجال + معالجة NASA", instrument="CCD تصوير واسع المجال",
         wl="ضوء مرئي (Hα 656 nm)", date="2007-01-01", src="NASA GSFC 20171208 Archive e002076",
         credit="NASA/STScI", license="ملكية عامة (NASA)",
         extra="Carina wide field"),
    dict(key="lagoon", file="raw/space-wallpapers/lagoon_nebula_1440p.png", folder="nebulae",
         name="سد البحيرة (M8) — ولادة العناقيد",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC",
         wl="ضوء مرئي (0.4–0.7 µm: Hα, [O III])", date="2004-01-01", src="NASA GSFC 20171208 Archive e001955",
         credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Lagoon M8"),
    dict(key="na_nebula", file="raw/space-wallpapers/na_nebula_4K.png", folder="nebulae",
         name="سد N11 في سحابة ماجلان الكبرى — كتلة نجمية",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC",
         wl="أشعة تحت حمراء (3.6–8 µm)", date="2004-12-01", src="PIA13845",
         credit="NASA/JPL-Caltech", license="ملكية عامة (NASA)",
         extra="N11 nebula LMC"),
    dict(key="na_nebula2", file="raw/space-wallpapers/na_nebula_2_4K.png", folder="nebulae",
         name="سد NGC 602 — أطراف سحابة ماجلان",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC/MIPS",
         wl="أشعة تحت حمراء (8 + 24 µm)", date="2005-01-12", src="PIA13844",
         credit="NASA/JPL-Caltech/STScI", license="ملكية عامة (NASA)",
         extra="NGC 602"),
    dict(key="cepheus_bc", file="raw/space-wallpapers/cepheus_bc_4K.png", folder="stars",
         name="سد قيفاوس B — انبعاث CO حول نجوم شابة",
         telescope="Spitzer Space Telescope", instrument="Spitzer (طيف CO)",
         wl="أشعة تحت حمراء بعيدة (~5–35 µm)", date="2007-03-01", src="PIA23126",
         credit="NASA/JPL-Caltech/Harvard-Smithsonian CfA", license="ملكية عامة (NASA)",
         extra="Cepheus B"),
    dict(key="life_death", file="raw/space-wallpapers/life_and_death_4K.png", folder="stars",
         name="حياة وموت النجوم: NGC 281 (سحابة باكمان) وأصدافها",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC/MIPS",
         wl="أشعة تحت حمراء (3.6–24 µm)", date="2011-08-24", src="PIA17019",
         credit="NASA/JPL-Caltech/Harvard-Smithsonian CfA", license="ملكية عامة (NASA)",
         extra="NGC 281 Pacman"),
    dict(key="cygnus_x", file="raw/space-wallpapers/cygnus_x_4K.png", folder="stars",
         name="منطقة تشكّل النجوم Cygnus X",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC/MIPS",
         wl="أشعة تحت حمراء (3.6–24 µm)", date="2009-01-01", src="PIA15253",
         credit="NASA/JPL-Caltech/CfA", license="ملكية عامة (NASA)",
         extra="Cygnus X"),
    dict(key="w5", file="raw/space-wallpapers/w5_4K.png", folder="stars",
         name="منطقة W5 (Westerhout 5) — تجاويف الرياح النجمية",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC/MIPS",
         wl="أشعة تحت حمراء (3.6–24 µm)", date="2007-04-25", src="PIA11046",
         credit="NASA/JPL-Caltech", license="ملكية عامة (NASA)",
         extra="W5 star formation"),
    dict(key="lmc", file="raw/space-wallpapers/lmc_4K.png", folder="galaxies",
         name="سحابة ماجلان الكبرى — سد الرتيلاء بالأشعة تحت الحمراء",
         telescope="Spitzer Space Telescope", instrument="Spitzer IRAC",
         wl="أشعة تحت حمراء (3.6–8 µm)", date="2005-01-01", src="NASA/JPL-Caltech (LMC)",
         credit="NASA/JPL-Caltech", license="ملكية عامة (NASA)",
         extra="Large Magellanic Cloud"),
    dict(key="milkyway", file="raw/space-wallpapers/milky_way_4K.png", folder="stars",
         name="مركز مجرة درب التبانة (Sgr B2 / Sgr A*)",
         telescope="Hubble Space Telescope (2.4 m)", instrument="WFC3/IR",
         wl="أشعة تحت حمراء قريبة (1.1–1.6 µm)", date="2009-11-10", src="PIA12348",
         credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Galactic centre"),
    dict(key="orion_hearth", file="raw/space-wallpapers/orion_hearth_4K.png", folder="nebulae",
         name="سد الجبّار (M42) — «موقد» النجوم",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC",
         wl="ضوء مرئي (0.4–0.7 µm)", date="2006-01-11", src="PIA01322",
         credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Orion Nebula M42"),
    dict(key="orion_dreamy", file="raw/space-wallpapers/orion_dreamy_4K.png", folder="nebulae",
         name="سد الجبّار — سد مظلم أمام نجومه",
         telescope="Hubble Space Telescope (2.4 m)", instrument="ACS/WFC",
         wl="ضوء مرئي (Hα)", date="2004-06-01", src="PIA13005",
         credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Orion dark nebula"),
    dict(key="orion_sword", file="raw/space-wallpapers/orion_sword_4K.png", folder="nebulae",
         name="سيف الجبّار — سد الجبار الضيق",
         telescope="Hubble Space Telescope (2.4 m)", instrument="WFPC2",
         wl="ضوء مرئي (0.4–0.7 µm)", date="2001-06-01", src="PIA08653",
         credit="NASA, ESA, STScI", license="CC BY 4.0 (NASA/ESA)",
         extra="Orion's sword"),
    dict(key="superbubble", file="raw/space-wallpapers/superbubble_4K.png", folder="clusters",
         name="الفقاعة الفائقة N44 في سحابة ماجلان",
         telescope="Hubble Space Telescope (2.4 m)", instrument="WFC3/UVIS + تصوير واسع",
         wl="ضوء مرئي (Hα, [O III], [S II])", date="2011-12-01", src="SVS 14018",
         credit="NASA/STScI/Goddard SVS", license="CC BY 4.0 (NASA)",
         extra="N44 superbubble"),
    dict(key="triton", file="raw/space-wallpapers/triton.png", folder="nebulae",
         name="ترايتون (قمر نبتون) — سطح جليدي مُعاد معالجته",
         telescope="Voyager 2 (NASA/STScI)", instrument="Voyager ISS",
         wl="ضوء مرئي (0.4–0.6 µm)", date="1989-08-25", src="STScI 4767-Image (2020/54)",
         credit="NASA/JPL/USGS", license="ملكية عامة (NASA)",
         extra="Triton Voyager"),
    dict(key="pluto", file="raw/space-wallpapers/pluto.png", folder="nebulae",
         name="بلوتو — خريطة عالم جليدي (كويبر)",
         telescope="New Horizons (NASA) / معالجة STScI", instrument="LORRI + Ralph",
         wl="ضوء مرئي (0.4–0.9 µm)", date="2015-07-14", src="STScI 4766-Image (2020/54)",
         credit="NASA/JHUAPL/SwRI", license="ملكية عامة (NASA)",
         extra="Pluto global map"),
    dict(key="tycho", file="raw/NASA-3D-Resources/Tycho Supernova Remnant.png", folder="snr",
         name="بقايا المستعر الأعظم تيخو (SN 1572)",
         telescope="Chandra X-ray Observatory + مركّب بصري", instrument="ACIS (أشعة سينية) + DSS",
         wl="أشعة سينية (0.5–7 keV) فوق صورة مرئية", date="2000–2009",
         src="NASA/CXC/SAO (مركّب NASA 3D Resources)", credit="NASA/CXC/SAO",
         license="ملكية عامة (NASA)", extra="Tycho SNR"),
    dict(key="ic443", file="raw/NASA-3D-Resources/IC 443 (Jellyfish Nebula).png", folder="snr",
         name="سد قنديل البحر (IC 443) — بقايا مستعر أعظم",
         telescope="Chandra + Spitzer + مركّب بصري", instrument="ACIS + IRAC",
         wl="أشعة سينية + تحت حمراء + خط Hα", date="2009–2011",
         src="NASA/CXC/JPL-Caltech (مركّب NASA 3D Resources)", credit="NASA/CXC/SAO & JPL-Caltech",
         license="ملكية عامة (NASA)", extra="IC443 Jellyfish"),
]

# ---------------------------------------------------------------------------
# CMB (Planck)
PLANCK = [
    dict(key="cmb0", file="raw/planck_cmb_cubemaps/0_cmb_planck_1024.png", folder="clusters",
         name="الخلفية الكونية الميكروية — وجه 0 من مكعّب السماء (Planck)",
         telescope="Planck (ESA) — HFI/LFI", instrument="HFI 100–857 GHz",
         wl="ميكروية/تحت مليمترية (1.4–10 مم، 30–857 GHz)", date="2015-02-05",
         src="Planck 2015 SMICA (ESA)", credit="ESA/Planck Collaboration",
         license="CC BY-SA 3.0 IGO (ESA)", extra="CMB face 0"),
    dict(key="cmb2", file="raw/planck_cmb_cubemaps/2_cmb_planck_1024.png", folder="clusters",
         name="الخلفية الكونية الميكروية — وجه 2 من مكعّب السماء (Planck)",
         telescope="Planck (ESA) — HFI/LFI", instrument="HFI 100–857 GHz",
         wl="ميكروية/تحت مليمترية (1.4–10 مم، 30–857 GHz)", date="2015-02-05",
         src="Planck 2015 SMICA (ESA)", credit="ESA/Planck Collaboration",
         license="CC BY-SA 3.0 IGO (ESA)", extra="CMB face 2"),
]

# ---------------------------------------------------------------------------
# Products rendered from calibrated FITS (see renders.md for the recipe)
FITS_RENDERED = [
    dict(key="meerkat", file="final/09_NGC1044_MeerKAT_Lband_radio.png", folder="galaxies",
         name="NGC 1044 — مجرة راديوية بنفاثات (MeerKAT، نطاق L)",
         telescope="MeerKAT (64 هوائي، جنوب أفريقيا)", instrument="MeerKAT L-band",
         wl="راديوي — 1.28 GHz (λ ≈ 23 سم)", date="2024-10-10",
         src="Clews et al. 2026 (مخرجات MeerKAT، Stokes I MFS)",
         credit="J. Croston et al. / MeerKAT (SARAO) — بيانات عامة",
         license="CC BY 4.0 (بيانات SARAO العامة)", extra="NGC1044 MeerKAT 1.28 GHz"),
    dict(key="chandra", file="final/10_HCG62_Chandra_ACIS_xray.png", folder="clusters",
         name="HCG 62 — غاز ساخن بين مجرات العنقود (Chandra)",
         telescope="Chandra X-ray Observatory", instrument="ACIS-S",
         wl="أشعة سينية لينة (0.5–8 كيلو إلكترون فولت)", date="2000–2009 (7 رصدات مدمجة)",
         src="Chandra ObsID 921/922/923/… (الاندماج)", credit="NASA/CXC/SAO",
         license="ملكية عامة (NASA/CXC)", extra="HCG62 Chandra 0.5-8 keV"),
    dict(key="soho", file="final/11_SOHO_EIT_195A_corona.png", folder="sun",
         name="هالة الشمس عند 195 أنغستروم (SOHO/EIT)",
         telescope="SOHO (ESA/NASA)", instrument="EIT",
         wl="فوق بنفسجي متطرف — 19.5 نانومتر (Fe XII، ~1.5 مليون كلفن)", date="2004-03-01",
         src="SOHO/EIT level-1", credit="ESA/NASA/SOHO", license="ملكية عامة (ESA/NASA)",
         extra="SOHO EIT 195 A"),
    dict(key="aia", file="final/12_SDO_AIA_171A_corona.png", folder="sun",
         name="هالة الشمس عند 171 أنغستروم (SDO/AIA)",
         telescope="Solar Dynamics Observatory (NASA)", instrument="AIA",
         wl="فوق بنفسجي متطرف — 17.1 نانومتر (Fe IX، ~0.6 مليون كلفن)", date="2011-02-15",
         src="SDO/AIA level-1", credit="NASA/SDO/AIA", license="ملكية عامة (NASA)",
         extra="SDO AIA 171 A"),
    dict(key="herschel", file="final/13_Herschel_SPIRE_350um_submm.png", folder="stars",
         name="حقل تشكّل نجوم في السحب الماجلانية عند 350 ميكرومتر (Herschel/SPIRE)",
         telescope="Herschel Space Observatory (ESA)", instrument="SPIRE",
         wl="تحت مليمتري — 350 ميكرومتر (857 GHz)", date="2010-06-18",
         src="Herschel SPIRE map (HSC/ESA)", credit="ESA/Herschel/SPIRE (HSC)",
         license="CC BY-SA 3.0 IGO (ESA)",
         extra="Herschel SPIRE 350um (LMC field)"),
    dict(key="hi4pi", file="final/14_HI4PI_21cm_channelmap.png", folder="stars",
         name="HI4PI — خريطة هيدروجين محايد في درب التبانة (خط 21 سم)",
         telescope="Effelsberg 100 m + Parkes 64 m (HI4PI)", instrument="مستقبلات خط 21 سم",
         wl="راديوي — 21 سم (1420 MHz)، سرعة −543 كم/ث", date="2016 (إصدار HI4PI)",
         src="HI4PI Collaboration 2016, A&A 594, A116",
         credit="HI4PI Collaboration (AIfA/MPIfR Bonn, ATNF Sydney)",
         license="CC BY 4.0 (استخدام علمي عام)", extra="HI4PI 21cm channel map"),
    dict(key="fermi", file="final/15_FermiLAT_gamma_ray_sky_map.png", folder="clusters",
         name="خريطة السماء كاملة في أشعة غاما (Fermi-LAT، 3FHL)",
         telescope="Fermi Gamma-ray Space Telescope (NASA)", instrument="LAT",
         wl="أشعة غاما — 10 غيغا إلكترون فولت إلى 2 تيرا إلكترون فولت", date="2008–2015 (7 سنوات)",
         src="3FHL — Ajello et al. 2017, ApJS 232, 18",
         credit="NASA/Fermi-LAT Collaboration", license="ملكية عامة (NASA)",
         extra="Fermi-LAT 3FHL all-sky"),
]

# ---------------------------------------------------------------------------
# Black-hole / EHT imagery
EHT = [
    dict(key="m87", file="fits/m87_eht.png", folder="bh",
         name="M87* — أول صورة لثقب أسود (EHT)",
         telescope="Event Horizon Telescope (شبكة 8 مقاريب)", instrument="VLBI 230 GHz",
         wl="راديوي مليمتري — 1.3 مم (230 GHz)", date="2017-04-11",
         src="EHT Collaboration 2019, ApJL 875, L1", credit="EHT Collaboration",
         license="CC BY 4.0", extra="M87* EHT 2019"),
]


# ---------------------------------------------------------------------------
# Ground-based / space observatories, open data products (press imagery)
OTHER = [
    dict(key="hr8799", obs="hr8799", file="raw/jwst/hr8799.png", folder="exo",
         name="HR 8799 — أربعة كواكب خارجية عملاقة مصوّرة مباشرة (JWST/NIRCam)",
         telescope="James Webb Space Telescope (JWST)", instrument="NIRCam (تعليق كوروناغرافي)",
         wl="أشعة تحت حمراء قريبة (2.1 + 4.1 µm)",
         date="2023-07 (بيانات) / 2025-03 (إصدار)",
         src="NASA/ESA/CSA/STScI — Balmer et al. 2025",
         credit="NASA, ESA, CSA, STScI, L. Pueyo (STScI), W. Balmer (JHU), M. Perrin (STScI)",
         license="CC BY 4.0 (NASA/ESA/CSA)", extra="HR 8799 b/c/d/e"),
    dict(key="sgra", file="fits/sgra_eht.png", folder="bh",
         name="Sgr A* — الثقب الأسود المركزي لدرب التبانة (EHT)",
         telescope="Event Horizon Telescope (شبكة 8 مقاريب)", instrument="VLBI 230 GHz",
         wl="راديوي مليمتري — 1.3 مم (230 GHz)", date="2017-04-06/07",
         src="EHT Collaboration 2022, ApJL 930, L12",
         credit="EHT Collaboration", license="CC BY 4.0",
         extra="Sgr A* EHT 2022"),
]

# ---------------------------------------------------------------------------
# Original-quality FITS delivered beside the renders
FITS_FILES = [
    ("raw/NGC1044-MeerKAT-data-products/L_7arc-StokesI-MFS-image.fits", "16_NGC1044_MeerKAT_1.28GHz_StokesI.fits",
     "صورة Stokes I المعايرة (JY/BEAM) لمجرة NGC 1044 من MeerKAT عند 1.28 GHz — ملف FITS أصلي 2000×2000 بيكسل، دقة 7″."),
    ("raw/astropy-data/chandra_events.fits", "17_HCG62_Chandra_ACIS_events.fits",
     "قائمة فوتونات Chandra/ACIS المعايرة لعنقود HCG 62 (483,964 حدثاً، 0.5–8 keV) — تُستخدم لعمل الصورة السينية."),
    ("raw/astropy-data/herschel-350.fits.gz", "18_Herschel_SPIRE_350um_map.fits.gz",
     "خريطة Herschel/SPIRE عند 350 ميكرومتر بوحدة MJy/sr مع WCS كامل — ملف FITS أصلي مضغوط."),
    ("raw/gammapy-data/fermi_3fhl_events_selected.fits.gz", "19_FermiLAT_3FHL_events.fits.gz",
     "قائمة فوتونات Fermi-LAT عالية الطاقة (3FHL، 697,317 حدثاً، 10 GeV–2 TeV) — ملف FITS أصلي مضغوط."),
    ("raw/astropy-data/reduced_TAN_C14.fits", "20_HI4PI_21cm_cube.fits",
     "مكعّب بيانات HI4PI لخط الهيدروجين 21 سم (450 قناة سرعة × 150×150 بيكسل)."),
]


# Redundant encodings of exactly the same observation: the surviving copy is the one
# with the most original pixels. Logged to dedupe_report.md, never uploaded.
DROP = {
    "aww_df": "smacs (3840×2160 مقابل 2798×2856)",
    "aww_carina": "carina_nircam (3840×2160 مقابل 3600×2085)",
    "aww_tarantula": "tarantula (3840×2160 مقابل 2000×1157)",
    "aww_cartwheel": "cartwheel (3840×2160 مقابل 2000×1841)",
    "aww_quintet": "quintet (3840×2160 مقابل 3500×3355)",
    "southern_ring": "aww (4833×4501 هو الإطار الكامل الأصلي)",
}


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build():
    entries = []
    for group in (WEBB, WP, PLANCK, EHT, OTHER):
        for e in group:
            e = dict(e)
            e.setdefault("telescope", "James Webb Space Telescope (JWST)")
            e.setdefault("credit", "NASA/ESA/CSA/STScI")
            e.setdefault("license", "CC BY 4.0 (NASA/ESA/CSA)")
            e.setdefault("instrument", "—")
            e.setdefault("src", "NASA/STScI")
            if e["key"] in DROP:
                print("dedupe-dropped", e["key"], "→", DROP[e["key"]])
                continue
            path = os.path.join(HERE, e["file"])
            if not os.path.exists(path):
                print("MISSING", e["file"])
                continue
            e["path"] = path
            e["bytes"] = os.path.getsize(path)
            e["sha1"] = sha1(path)
            e["science"], e["props"] = TEXTS[e["key"]]
            entries.append(e)
    return entries


if __name__ == "__main__":
    ents = build()
    print(len(ents), "entries")
    for e in ents:
        print(f"{e['bytes']/1e6:7.2f}MB {e['folder']:9} {e['file']}")
    json.dump([{k: v for k, v in e.items() if k != 'path'} for e in ents],
              open(os.path.join(HERE, "manifest.json"), "w"), indent=1, ensure_ascii=False)
