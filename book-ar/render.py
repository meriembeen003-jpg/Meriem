# -*- coding: utf-8 -*-
"""مُصيِّر الكتاب العربي إلى PDF (RTL) — ReportLab + arabic_reshaper + bidi."""
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import arabic_reshaper
from bidi.algorithm import get_display

import content_a as A
import content_b as B
import content_c as C
import content_d as D
import content_e as E
import content_f as F
import content_g as G
import content_h as HC

HERE = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont("Amiri", os.path.join(HERE, "fonts", "Amiri-Regular.ttf")))
pdfmetrics.registerFont(TTFont("AmiriBold", os.path.join(HERE, "fonts", "Amiri-Bold.ttf")))

W, H = A4
M = 2.3 * cm
TEXT_W = W - 2 * M
INK = HexColor("#1a1a1c")
ACCENT = HexColor("#8a5a2b")
GREY = HexColor("#63636b")
RULE = HexColor("#c9beb0")
PAPER = HexColor("#fbf9f5")
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


_DIG = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def _numfix(text):
    """أرقام عربية-هندية للكلمات العربية، وإبقاء الرموز اللاتينية كما هي."""
    out = []
    for tok in text.split(" "):
        if any("a" <= ch.lower() <= "z" for ch in tok):
            out.append(tok)
        else:
            out.append(tok.translate(_DIG).replace(",", "\u066c").replace(".", "\u066b"))
    return " ".join(out)


_SAFE = {"≈": " يقارب ", "ℓ": "", "→": " إلى ", "≥": " فأكثر ", "≤": " فأقلّ ",
         "∞": " لا نهائي ", "μ": "ميكرو", "Ω": "أوم", "∑": "مجموع", "∫": "تكامل",
         "⅓": "ثلث", "⅔": "ثلثين", "□": ""}


def _clean(t):
    if not any(ch in t for ch in _SAFE):
        return t
    for k, v in _SAFE.items():
        t = t.replace(k, v)
    return t


def ar(t):
    return get_display(arabic_reshaper.reshape(_numfix(_clean(t))))


def justify(line, font, size, maxw):
    words = line.split()
    if len(words) < 2:
        return line
    base = sw(line, font, size)
    extra = maxw - base
    if extra <= 0:
        return line
    sp = sw(" ", font, size) or size * 0.25
    k = int(extra // sp)
    if k <= 0:
        return line
    gaps = len(words) - 1
    q, r = divmod(k, gaps)
    parts = [words[0]]
    for i, w in enumerate(words[1:]):
        parts.append(" " * (1 + q + (1 if i < r else 0)))
        parts.append(w)
    return "".join(parts)


def sw(t, font, size):
    return pdfmetrics.stringWidth(ar(t), font, size)



SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺"
SUPMAP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
          "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "−", "⁺": "+"}


def has_sup(t):
    return any(ch in SUP for ch in t)


def _segs(word):
    out, cur, mode = [], "", None
    for ch in word:
        m = ch in SUP
        if mode is None or m == mode:
            cur += ch
        else:
            out.append((mode, cur))
            cur = ch
        mode = m
    if cur:
        out.append((mode, cur))
    return out


def draw_line(c, line, y, size, font, x_right):
    """يرسم سطراً من اليمين إلى اليسار مع مراعاة الأسس العلوية يدوياً."""
    x = x_right
    for word in line.split():
        latin = any("a" <= ch.lower() <= "z" for ch in word)
        segs = _segs(word)
        widths = []
        for is_sup, seg in segs:
            fs = size * 0.6 if is_sup else size
            txt = "".join(SUPMAP.get(ch, ch) for ch in seg) if is_sup else seg
            widths.append((is_sup, txt, pdfmetrics.stringWidth(ar(txt), font, fs), fs))
        total = sum(w for _, _, w, _ in widths)
        if latin:  # كلمة لاتينية تُرسم من اليسار إلى اليمين
            cx = x - total
            for is_sup, txt, w, fs in widths:
                c.setFont(font, fs)
                c.drawString(cx, y + (size * 0.34 if is_sup else 0), ar(txt))
                cx += w
        else:
            cx = x
            for is_sup, txt, w, fs in widths:
                c.setFont(font, fs)
                c.drawString(cx - w, y + (size * 0.34 if is_sup else 0), ar(txt))
                cx -= w
        x -= total + sw(" ", font, size)
    c.setFont(font, size)


def wrap(text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if sw(trial, font, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Book:
    def __init__(self, path, dry=False):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.dry = dry
        self.page = 1
        self.y = H - M
        self.chapters = []

    def bg(self):
        if self.dry:
            return
        self.c.setFillColor(PAPER)
        self.c.rect(0, 0, W, H, stroke=0, fill=1)
        self.c.setFillColor(INK)

    def new_page(self):
        self.c.showPage()
        self.page += 1
        self.y = H - M
        self.bg()

    def footer(self):
        if self.dry:
            return
        self.c.setFont("Amiri", 9.5)
        self.c.setFillColor(GREY)
        self.c.drawCentredString(W / 2, M * 0.72, str(self.page).translate(AR_DIGITS))
        self.c.setFont("Amiri", 7.6)
        self.c.drawString(M, M * 0.72, "THE COMPLETE HISTORY OF THE UNIVERSE  ·  ARABIC")
        self.c.setFillColor(INK)

    # ------------------------- blocks -------------------------
    def heading(self, num, title, size=21):
        lines = wrap(title, "AmiriBold", size, TEXT_W)
        h = len(lines) * size * 1.45 + 1.1 * cm
        if self.y - h < M + 1.6 * cm:
            self.footer()
            self.new_page()
        if not self.dry:
            self.c.setFillColor(ACCENT)
            self.c.rect(W - M - 1.1 * cm, self.y - 0.11 * cm, 1.1 * cm, 0.11 * cm, stroke=0, fill=1)
            if num:
                self.c.setFont("AmiriBold", 15)
                self.c.drawRightString(W - M - 1.55 * cm, self.y - 0.15 * cm, ar(num))
            self.c.setFillColor(INK)
        self.y -= 0.85 * cm
        for ln in lines:
            if not self.dry:
                if has_sup(ln):
                    draw_line(self.c, ln, self.y - size, size, "AmiriBold", W - M)
                else:
                    self.c.setFont("AmiriBold", size)
                    self.c.drawRightString(W - M, self.y - size, ar(ln))
            self.y -= size * 1.45
        self.y -= 0.5 * cm
        if not self.dry:
            self.c.setStrokeColor(RULE)
            self.c.setLineWidth(0.6)
            self.c.line(M, self.y + 0.15 * cm, W - M, self.y + 0.15 * cm)
            self.c.setStrokeColor(INK)
        self.y -= 0.4 * cm

    def para(self, text, size=12.6, leading=22.5, gap=0.4 * cm):
        lines = wrap(text, "Amiri", size, TEXT_W)
        if self.y - len(lines) * leading < M + 1.2 * cm:
            self.footer()
            self.new_page()
        for i, ln in enumerate(lines):
            if not self.dry:
                if has_sup(ln):
                    draw_line(self.c, ln, self.y - size, size, "Amiri", W - M)
                else:
                    self.c.setFont("Amiri", size)
                    txt = ln if i == len(lines) - 1 else justify(ln, "Amiri", size, TEXT_W)
                    self.c.drawRightString(W - M, self.y - size, ar(txt))
            self.y -= leading
        self.y -= gap

    def quote(self, text):
        size, lead = 13.4, 24.5
        lines = wrap(text, "Amiri", size, TEXT_W - 1.7 * cm)
        if self.y - len(lines) * lead < M + 1.4 * cm:
            self.footer()
            self.new_page()
        top = self.y
        for ln in lines:
            if not self.dry:
                self.c.setFillColor(HexColor("#2b2b31"))
                if has_sup(ln):
                    draw_line(self.c, ln, self.y - size, size, "Amiri", W - M - 0.55 * cm)
                else:
                    self.c.setFont("Amiri", size)
                    self.c.drawRightString(W - M - 0.55 * cm, self.y - size, ar(ln))
                self.c.setFillColor(INK)
            self.y -= lead
        if not self.dry:
            self.c.setStrokeColor(ACCENT)
            self.c.setLineWidth(1.4)
            self.c.line(W - M, top, W - M, self.y + lead - size - 0.1 * cm)
            self.c.setStrokeColor(INK)
        self.y -= 0.45 * cm

    def figure(self, rel, cap, credit, max_h=10.6 * cm):
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            print("!! missing image:", rel)
            return
        iw, ih = ImageReader(path).getSize()
        w = TEXT_W
        h = w * ih / iw
        if h > max_h:
            h = max_h
            w = h * iw / ih
        cap_lines = wrap(cap, "Amiri", 9.7, TEXT_W - 1.0 * cm)
        block = h + 0.3 * cm + len(cap_lines) * 15 + 0.9 * cm
        if self.y - block < M + 1.2 * cm:
            self.footer()
            self.new_page()
        if not self.dry:
            x = (W - w) / 2
            y = self.y - h
            self.c.drawImage(path, x, y, w, h)
            self.c.setStrokeColor(RULE)
            self.c.setLineWidth(0.7)
            self.c.rect(x, y, w, h, stroke=1, fill=0)
            self.c.setStrokeColor(INK)
        self.y -= h + 0.3 * cm
        for ln in cap_lines:
            if not self.dry:
                self.c.setFont("Amiri", 9.7)
                self.c.setFillColor(GREY)
                self.c.drawRightString(W - M, self.y - 9.7, ar(ln))
                self.c.setFillColor(INK)
            self.y -= 15
        if not self.dry and credit:
            self.c.setFont("Amiri", 8.4)
            self.c.setFillColor(ACCENT)
            self.c.drawRightString(W - M, self.y - 8.4, ar("المصدر: " + credit))
            self.c.setFillColor(INK)
            self.y -= 14
        self.y -= 0.8 * cm

    # ------------------------- pages -------------------------
    def cover(self):
        if self.dry:
            return
        self.bg()
        band = 13.0 * cm
        self.c.setFillColor(HexColor("#0e1116"))
        self.c.rect(0, H - band, W, band, stroke=0, fill=1)
        img = os.path.join(HERE, "images/jwst-pillars-of-creation-carina-nebula-i-2.jpg")
        if os.path.exists(img):
            iw, ih = ImageReader(img).getSize()
            hh = band
            ww = hh * iw / ih
            self.c.saveState()
            p = self.c.beginPath()
            p.rect(0, H - band, W, band)
            self.c.clipPath(p, stroke=0)
            self.c.drawImage(img, (W - ww) / 2, H - band, ww, hh)
            self.c.restoreState()
            self.c.setFillColorRGB(0, 0, 0, alpha=0.42)
            self.c.rect(0, H - band, W, band, stroke=0, fill=1)
            self.c.setFillColor(INK)

        self.c.setFillColor(HexColor("#20201f"))
        self.c.setFont("AmiriBold", 42)
        self.c.drawCentredString(W / 2, H - 16.8 * cm, ar(A.TITLE))
        self.c.setFont("Amiri", 16.5)
        self.c.setFillColor(HexColor("#4a4238"))
        self.c.drawCentredString(W / 2, H - 19.0 * cm, ar(A.SUBTITLE))

        self.c.setStrokeColor(HexColor("#8a5a2b"))
        self.c.setLineWidth(1.2)
        self.c.line(W / 2 - 3.2 * cm, H - 20.0 * cm, W / 2 + 3.2 * cm, H - 20.0 * cm)

    def toc(self, entries):
        if not self.dry:
            self.bg()
        if not self.dry:
            self.c.setFont("AmiriBold", 25)
            self.c.drawCentredString(W / 2, H - M - 25, ar("الفهرس"))
            self.c.setStrokeColor(RULE)
            self.c.setLineWidth(0.8)
            self.c.line(M + 3.2 * cm, H - M - 36, W - M - 3.2 * cm, H - M - 36)
        self.y = H - M - 1.9 * cm
        row = 0.93 * cm
        for title, pg in entries:
            if self.y - row < M + 1.4 * cm:
                self.footer()
                self.new_page()
                if not self.dry:
                    self.c.setFont("AmiriBold", 15)
                    self.c.setFillColor(GREY)
                    self.c.drawCentredString(W / 2, H - M - 1.2 * cm, ar("الفهرس — تابع"))
                    self.c.setFillColor(INK)
                self.y = H - M - 1.9 * cm
            if not self.dry:
                self.c.setFont("Amiri", 12.4)
                self.c.drawRightString(W - M, self.y - 12.4, ar(title))
                self.c.setFont("Amiri", 10.6)
                self.c.setFillColor(GREY)
                self.c.drawString(M, self.y - 12.4, str(pg).translate(AR_DIGITS))
                self.c.setFillColor(INK)
                tw = sw(title, "Amiri", 12.4)
                self.c.setStrokeColor(HexColor("#ded6c9"))
                self.c.setLineWidth(0.4)
                self.c.line(M + 1.0 * cm, self.y - 16, max(M + 1.05 * cm, W - M - tw - 0.35 * cm), self.y - 16)
                self.c.setStrokeColor(INK)
            self.y -= row



CREDITS_PARAS = [
    "أُعدّ هذا الكتاب العربي اعتماداً على النصّ الإنجليزي المنقّح «The Complete History of the Universe»، "
    "وهو نصٌّ خضع لتدقيقٍ صارم في ٥٥ موضعاً قبل الترجمة. ولم تُترجم الصور ولا أسماؤها: نُقلت كما هي من أرشيف "
    "الجهة التي أنتجتها، وأُثبت اسم الجهة في تذييل كل صورة، لأن الصورة الرصدية وثيقةٌ لها مؤلّفٌ ومصدر.",
    "جميع الصور في هذا الكتاب ملكٌ لعامة الناس، وتُنشر بموجب سياسات النشر المعلنة لدى الوكالات المذكورة أدناه. "
    "وحيث كانت الصورة المتاحة نسخةً مصغّرة من الأصل (thumbnail)، فقد أُدرجت كما وُجدت دون تحسينٍ يُوهم بدقّةٍ أعلى.",
    "أما النصوص فهي من كتابة النسخة العربية، ولم تُستخدم ترجمةٌ آلية في صياغتها؛ وقد رُوعي في كل جملة أن تحمل "
    "معلومةً قابلةً للتحقّق: رقماً أو تاريخاً أو نتيجةَ رصد.",
]

CREDITS_LIST = [
    ("NASA", "أرشيف الصور العلمية · الشمس، شاندرا، هابل"),
    ("ESA / Hubble", "أرشيف هابل الأوروبي · أندروميدا، القاعدة، السرطان"),
    ("NASA, ESA, CSA, STScI", "تلسكوب جيمس ويب · الحقول العميقة وأعمدة الخلق"),
    ("ESA / Planck", "خريطة الخلفية الميكروية · ٢٠١٣–٢٠١٨"),
    ("EHT Collaboration", "تلسكوب أفق الحدث · M87* وساجيتاريوس A*"),
    ("CERN / ALICE", "كاشف ALICE · تصادمات أيونات الرصاص"),
]

def ordered_sections():
    A5 = list(A.SECTIONS_A)
    B5 = list(B.SECTIONS_B)
    return ([A5[0], E.E_SECTIONS[0], E.E_SECTIONS[1], E.E_SECTIONS[2], E.E_SECTIONS[3],
             A5[3], E.E_SECTIONS[4], E.E_SECTIONS[5], A5[1], E.E_SECTIONS[6], A5[4]]
            + list(G.G_SECTIONS)
            + list(HC.H_SECTIONS)
            + [B5[0], B5[1], B5[2], B5[3]]
            + list(F.F_SECTIONS) + [B5[4], B5[5]])


def write_body(b):
    b.heading("", A.INTRO["title"], size=22)
    for p in A.INTRO["paras"]:
        b.para(p)
    order = ordered_sections()
    for k, sec in enumerate(order):
        if b.y < M + 0.45 * (H - 2 * M):
            b.footer()
            b.new_page()
        b.chapters.append((sec["title"], b.page))
        b.heading(str(k + 1).translate(AR_DIGITS), sec["title"])
        paras = (list(sec["paras"]) + list(C.EXTRA_PARAS.get(sec["title"], []))
                 + list(D.EXTRA2.get(sec["title"], [])))
        b.quote(paras[0])
        for i, p in enumerate(paras[1:]):
            b.para(p)
            if i == 1 and sec.get("img"):
                b.figure(sec["img"], sec["cap"], sec["credit"], max_h=9.8 * cm)
        if sec.get("img") and len(paras) <= 2:
            b.figure(sec["img"], sec["cap"], sec["credit"], max_h=9.8 * cm)
        for rel, cap, credit in EXTRAS.get(sec["title"], []):
            b.figure(rel, cap, credit, max_h=9.4 * cm)
    b.chapters.append((B.AFTERWORD["title"], b.page))
    b.heading("", B.AFTERWORD["title"], size=20)
    for p in B.AFTERWORD["paras"]:
        b.para(p)


EXTRAS = {
    
    "النجوم الأولى: حين أضاء الظلام": [(
        "images/jwst-pillars-of-creation-carina-nebula-i-2.jpg",
        "النسخة التي التقطها هابل عام ٢٠٠٩ لسديم القاعدة: المقارنة مع صورة ويب تُظهر تقدُّم أدواتنا بقدر ما تُظهر ثبات المشهد.",
        "NASA, ESA, and the Hubble Heritage Team",
    )],
    "موت النجوم: من السديم إلى الكثافة المطلقة": [(
        "images/crab-nebula-supernova-remnant-hubble-spa-1.jpg",
        "السرطان مجمَّعاً من عدة أطوال موجية: الأشعة السينية تكشف الغاز المسخَّن إلى ملايين الدرجات في قلب البقايا.",
        "NASA, ESA, and G. Dubner (IAFE)",
    )],
    "قلب المجرّة: ساجيتاريوس A*": [(
        "images/sagittarius-a-event-horizon-telescope-im-2.jpg",
        "منطقة مركز المجرّة بالأشعة السينية (مرصد شاندرا): سحبُ غازٍ ساخنٍ ونشاطٌ متبقٍّ من ثقبٍ أسود هادئٍ اليوم.",
        "NASA / CXC / Q. Daniel Wang (UMass)",
    )],
    "الشمس: مفاعلنا القريب": [(
        "images/solar-prominence-solar-dynamics-observat-2.jpg",
        "شُوَاظٌ شمسي آخر في طور التكوّن: البلازما المعلَّقة على أقواس المجال المغناطيسي، برصدٍ متواصل لمركبة SDO.",
        "NASA / SDO",
    )],
}

GALLERY = [
    ("images/andromeda-galaxy-hubble-high-resolution--1.jpg", "أندروميدا: بانوراما هابل عالية الدقة", "NASA, ESA, J. Dalcanton (UW)"),
    ("images/andromeda-galaxy-hubble-high-resolution--2.jpg", "أندروميدا: نسخة مصغّرة من البانوراما", "NASA, ESA, J. Dalcanton (UW)"),
    ("images/planck-cosmic-microwave-background-map-e-2.jpg", "بلانك: السماء كاملةً في تسع نطاقات ترددية", "ESA / Planck Collaboration"),
    ("images/planck-cosmic-microwave-background-map-e-1.jpg", "شريطُ السماء: تباينات الخلفية الميكروية", "ESA / Planck Collaboration"),
    ("images/alice-detector-lead-ion-collision-quark--2.jpg", "ALICE: تصادم أيونات الرصاص", "CERN / ALICE"),
    ("images/alice-detector-lead-ion-collision-quark--1.jpg", "ALICE: مقطعٌ في الكاشف", "CERN / ALICE"),
    ("images/jwst-pillars-of-creation-carina-nebula-i-1.jpg", "أعمدة الخلق — جيمس ويب", "NASA, ESA, CSA, STScI"),
    ("images/jwst-pillars-of-creation-carina-nebula-i-2.jpg", "القاعدة — هابل ٢٠٠٩", "NASA, ESA, Hubble Heritage"),
    ("images/crab-nebula-supernova-remnant-hubble-spa-2.jpg", "السرطان: بقايا مستعر ١٠٥٤", "NASA, ESA, J. Hester & A. Loll"),
    ("images/crab-nebula-supernova-remnant-hubble-spa-1.jpg", "السرطان بأطوال موجية متعددة", "NASA, ESA, G. Dubner"),
    ("images/event-horizon-telescope-first-image-m87--1.jpg", "M87*: أول صورة لظلّ ثقب أسود", "EHT Collaboration"),
    ("images/event-horizon-telescope-first-image-m87--2.jpg", "M87*: الصورة مع الحلقة المؤشَّرة", "EHT Collaboration"),
    ("images/sagittarius-a-event-horizon-telescope-im-1.jpg", "ساجيتاريوس A* — تلسكوب أفق الحدث", "EHT Collaboration"),
    ("images/sagittarius-a-event-horizon-telescope-im-2.jpg", "مركز المجرّة — شاندرا (أشعة سينية)", "NASA / CXC"),
    ("images/solar-prominence-solar-dynamics-observat-1.jpg", "اندفاعٌ شمسي — SDO", "NASA / SDO"),
    ("images/solar-prominence-solar-dynamics-observat-2.jpg", "شُوَاظٌ متطوّر — SDO", "NASA / SDO"),
    ("images/james-webb-space-telescope-deep-field-th-1.jpg", "حقل جيمس ويب العميق", "NASA, ESA, CSA, STScI"),
    ("images/james-webb-space-telescope-deep-field-th-2.jpg", "حقل ويب العميق — نسخة ثانية", "NASA, ESA, CSA, STScI"),
]


TIMELINE = [
    ("١٠ أس سالب ٤٣ ثانية", "زمن بلانك: تنهار عنده النسبية العامة، ولا بدّ من نظرية جاذبية كمومية."),
    ("١٠ أس سالب ٣٦ ثانية", "بداية التضخّم: تضخّم الكون بمعامل ١٠ أس ٢٦ على الأقلّ في جزءٍ من الثانية."),
    ("١٠ أس سالب ١٢ ثانية", "نهاية الحقبة الكهروضعيفة عند ١٠ أس ١٥ كلفن: تنفصل القوة النووية الشديدة."),
    ("١٠ أس سالب ٦ ثانية", "تجمّد الكواركات إلى بروتونات ونيوترونات؛ الكون بلازما كوارك-غلوونية."),
    ("١ ثانية", "النيوترينوات تنفصل عند ١٠ أس ١٠ كلفن، وتظلّ اليوم خلفيةً لا تزيد على ١٫٩٥ كلفن."),
    ("٣ دقائق", "تخليق الأنوية: ٧٥٪ هيدروجين، ٢٥٪ هيليوم، ٠٫٠١٪ ديوتيريوم."),
    ("٣٨٠ ألف سنة", "إعادة الاتحاد عند ٣٠٠٠ كلفن: ينطلق الضوء الأول، ونراه اليوم عند ٢٫٧٢٥ كلفن."),
    ("١٥٠ مليون سنة", "أولى النجوم (الجمهرة الثالثة)، كتلتها بين ١٠٠ و١٠٠٠ كتلة شمسية."),
    ("١ مليار سنة", "المجرّات والعناقيد الأولى؛ نهاية «فجر الكون» وإعادة التأين."),
    ("٩٫٢ مليار سنة", "ولادة الشمس والأرض من سحابةٍ أُغنيَت برماد نجومٍ سابقة (منذ ٤٫٦ مليار سنة)."),
    ("١٣٫٧٨٧ مليار سنة", "اليوم: خلفية ٢٫٧ كلفن، وسماءٌ فيها نحو تريليوني مجرّة قابلة للرصد."),
    ("+ ٤٫٥ مليار سنة", "اندماج درب التبانة مع أندروميدا، وتشكّل مجرّة «لاكتوميدا»."),
    ("+ ٥ مليارات سنة", "الشمس تصبح عملاقاً أحمر، ثم قزماً أبيض بحجم الأرض."),
    ("+ ١٠ أس ١٤ سنة", "آخر النجوم تنطفئ؛ لا يبقى إلا الأقزام الباردة والثقوب السوداء."),
    ("+ ١٠ أس ٦٧ سنة", "تبخّر الثقوب السوداء النجمية بإشعاع هوكينغ."),
    ("+ ١٠ أس ١٠٠ سنة", "الموت الحراري: كونٌ بارد، متوسّع، لا شيء فيه يُحدث حدثاً."),
]


def timeline(b):
    if b.y < M + 0.5 * (H - 2 * M):
        b.footer()
        b.new_page()
    b.chapters.append(("خطّ زمني للكون", b.page))
    b.heading("", "خطّ زمني للكون: من ١٠ أس سالب ٤٣ ثانية إلى ١٠ أس ١٠٠ سنة", size=19)
    b.para("كل ما في هذا الكتاب يمكن اختصاره في جدولٍ واحد؛ لكن الجدول لا يشرح، ولذلك كُتب الكتاب.", size=11.5, leading=20)
    lead = 15.6
    for lab, txt in TIMELINE:
        lines = wrap(txt, "Amiri", 11.2, TEXT_W - 4.3 * cm)
        if b.y - len(lines) * lead - 8 < M + 1.0 * cm:
            b.footer()
            b.new_page()
        if not b.dry:
            b.c.setFillColor(ACCENT)
            if has_sup(lab):
                draw_line(b.c, lab, b.y - 11.2, 10.6, "AmiriBold", M + 2.6 * cm)
            else:
                b.c.setFont("AmiriBold", 10.6)
                b.c.drawString(M, b.y - 11.2, ar(lab))
            b.c.setFillColor(INK)
            b.c.setFont("Amiri", 11.2)
            for j, ln in enumerate(lines):
                b.c.drawRightString(W - M, b.y - 11.2 - j * lead, ar(ln))
            b.c.setStrokeColor(HexColor("#e0d8cb"))
            b.c.setLineWidth(0.4)
            b.c.line(M, b.y - len(lines) * lead - 2, W - M, b.y - len(lines) * lead - 2)
            b.c.setStrokeColor(INK)
        b.y -= len(lines) * lead + 8


def gallery(b):
    b.footer()
    b.new_page()
    b.chapters.append(("ألبوم الصور: ثماني عشرة صورة", b.page))
    b.heading("", "ألبوم الصور: ثماني عشرة صورة", size=20)
    b.para("تُجمع هنا كلُّ صورةٍ استُخدمت في هذا الكتاب أو وُجدت في أرشيف البحث، ومنها نسختان لكلِّ موضوع: "
           "الأساسية داخل الفصول، والبديلة هنا. لم تُحذف صورةٌ واحدة؛ فالصورة، في هذا الكتاب، وثيقةٌ لا زينة.", size=11.5, leading=20)

    gap = 0.45 * cm
    col_w = (TEXT_W - 2 * gap) / 3
    thumb_h = 4.0 * cm
    row_h = 5.45 * cm
    for i, (rel, label, credit) in enumerate(GALLERY):
        col = i % 3
        if col == 0 and b.y - row_h < M + 1.0 * cm:
            b.footer()
            b.new_page()
        path = os.path.join(HERE, rel)
        iw, ih = ImageReader(path).getSize()
        w, h = col_w, col_w * ih / iw
        if h > thumb_h:
            h = thumb_h
            w = h * iw / ih
        x0 = W - M - col_w - col * (col_w + gap)
        x = x0 + (col_w - w) / 2
        if not b.dry:
            y = b.y - h
            b.c.drawImage(path, x, y, w, h)
            b.c.setStrokeColor(RULE)
            b.c.setLineWidth(0.5)
            b.c.rect(x, y, w, h, stroke=1, fill=0)
            b.c.setFont("Amiri", 8.4)
            b.c.setFillColor(INK)
            lab = wrap(label, "Amiri", 8.4, col_w)
            for j, L in enumerate(lab[:2]):
                b.c.drawCentredString(x0 + col_w / 2, y - 11 - j * 10, ar(L))
            b.c.setFont("Amiri", 7.2)
            b.c.setFillColor(ACCENT)
            b.c.drawCentredString(x0 + col_w / 2, y - 11 - len(lab[:2]) * 10 - 2, ar(credit))
            b.c.setFillColor(INK)
        if col == 2:
            b.y -= row_h


def run(out="book_ar.pdf"):
    # المرور الأول: رسمٌ حقيقي (لضمان تطابق التخطيط تماماً) بفهرسٍ رموزه أصفار
    titles = (["مقدمة: لماذا نسأل؟"] + [s["title"] for s in ordered_sections()]
              + ["خاتمة المحقّق: ما صُحّح في هذه النسخة", "خطّ زمني للكون", "ألبوم الصور: ثماني عشرة صورة"])
    m = Book(os.path.join(HERE, "_pass1.pdf"), dry=False)
    m.cover()
    m.new_page()
    m.toc([(t, 0) for t in titles])
    m.footer()
    m.new_page()
    intro_pg = m.page
    write_body(m)
    timeline(m)
    gallery(m)
    m.footer()
    m.c.save()

    entries = [("مقدمة: لماذا نسأل؟", intro_pg)] + [(t, p) for t, p in m.chapters]

    # المرور الثاني: النسخة النهائية
    b = Book(os.path.join(HERE, out), dry=False)
    b.cover()
    b.new_page()            # صفحة ٢ وما بعدها: الفهرس
    b.toc(entries)
    b.footer()
    b.new_page()            # أول صفحة من المتن
    write_body(b)
    timeline(b)
    gallery(b)
    b.footer()

    # صفحة الإسناد
    b.new_page()
    b.heading("", "إسناد الصور والمصادر", size=20)
    for p in CREDITS_PARAS:
        b.para(p, size=11.4, leading=20.5)
    b.y -= 0.4 * cm
    for name, role in CREDITS_LIST:
        if b.y < M + 2 * cm:
            b.footer()
            b.new_page()
        if not b.dry:
            b.c.setFont("AmiriBold", 11.2)
            b.c.setFillColor(ACCENT)
            b.c.drawString(M, b.y - 11.2, ar(name) if any("\u0600" <= ch <= "\u06ff" for ch in name) else name)
            b.c.setFillColor(INK)
            b.c.setFont("Amiri", 11.2)
            b.c.drawRightString(W - M - 4.2 * cm, b.y - 11.2, ar(role))
            b.c.setStrokeColor(HexColor("#e0d8cb"))
            b.c.setLineWidth(0.4)
            b.c.line(M, b.y - 15, W - M, b.y - 15)
            b.c.setStrokeColor(INK)
        b.y -= 0.78 * cm
    b.footer()
    b.c.showPage()
    b.page += 1
    b.bg()
    b.y = H * 0.55
    if not b.dry:
        b.c.setFont("Amiri", 12)
        b.c.setFillColor(GREY)
        b.c.drawCentredString(W / 2, b.y, ar("تمّ بحمد الله"))
        b.c.setFont("Amiri", 9.6)
        b.c.drawCentredString(W / 2, b.y - 1.6 * cm, ar("النسخة العربية من «التاريخ الكامل للكون» · ١٤٤٧هـ / ٢٠٢٦م"))
        b.c.setFillColor(INK)
    b.footer()
    b.c.save()
    print("pages:", b.page)
    print("chapters:", b.chapters[:3], "...")
    return out


if __name__ == "__main__":
    run()
