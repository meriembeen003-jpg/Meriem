# -*- coding: utf-8 -*-
"""يولّد main.tex (XeLaTeX + polyglossia/bidi + Amiri) من نفس محتوى النسخة العربية."""
import os, re
import content_a as A
import content_b as B
import content_c as C
import content_d as D
import render as R

HERE = os.path.dirname(os.path.abspath(__file__))


def esc(t):
    t = t.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        t = t.replace(a, b)
    return t


def paras_for(sec):
    return (list(sec["paras"]) + list(C.EXTRA_PARAS.get(sec["title"], []))
            + list(D.EXTRA2.get(sec["title"], [])))


out = []
w = out.append

w(r"""% !TEX program = xelatex
% النسخة العربية من «التاريخ الكامل للكون» — مصدر LaTeX
% التحويل إلى PDF:
%   xelatex main.tex && xelatex main.tex
% المتطلبات: محرّك XeLaTeX، حزمة polyglossia، خطّ Amiri (مجلد fonts/ مرفق)،
%             وحزمة fancyhdr وgraphicx وbooktabs وhyperref.
\documentclass[12pt,a4paper,openany]{book}

\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{arabic}
\setotherlanguage{english}

\newfontfamily\arabicfont[Path=fonts/,Script=Arabic]{Amiri-Regular.ttf}
\newfontfamily\arabicfontsf[Path=fonts/,Script=Arabic]{Amiri-Regular.ttf}
\newfontfamily\arabicfontbf[Path=fonts/,Script=Arabic]{Amiri-Bold.ttf}
\newfontfamily\arabicfonttt[Path=fonts/,Script=Arabic]{Amiri-Regular.ttf}

\usepackage[a4paper,margin=2.4cm]{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{booktabs}
\usepackage[hidelinks]{hyperref}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\fancyfoot[L]{\footnotesize THE COMPLETE HISTORY OF THE UNIVERSE · ARABIC}
\renewcommand{\headrulewidth}{0pt}

\setlength{\parindent}{1.2em}
\setlength{\parskip}{0.45em}
\linespread{1.35}

\newcommand{\plate}[3]{%
  \begin{figure}[htbp]\centering
    \includegraphics[width=0.92\textwidth,height=0.42\textheight,keepaspectratio]{#1}%
    \par\vspace{0.25em}{\small #2\par}
    \vspace{0.15em}{\footnotesize\textcolor[HTML]{8a5a2b}{المصدر: #3}}
  \end{figure}}

\begin{document}

% ---------- الغلاف ----------
\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\bfseries """ + esc(A.TITLE) + r"""\par}
\vspace{0.9cm}
{\Large """ + esc(A.SUBTITLE) + r"""\par}
\vspace{0.6cm}
\rule{8cm}{0.6pt}\par
\vspace{0.9cm}
\end{titlepage}

\tableofcontents
\clearpage

% ---------- المقدمة ----------
\chapter*{""" + esc(A.INTRO["title"]) + r"""}
\addcontentsline{toc}{chapter}{""" + esc(A.INTRO["title"]) + r"""}
""")

for p in A.INTRO["paras"]:
    w(esc(p) + "\n\n")

n = 0
for sec in R.ordered_sections():
    n += 1
    w(r"\chapter*{" + esc(sec["title"]) + "}\n")
    w(r"\addcontentsline{toc}{chapter}{" + esc(sec["title"]) + "}\n")
    w(r"\markboth{" + esc(sec["title"]) + "}{}\n\n")
    paras = paras_for(sec)
    w(esc(paras[0]) + "\n\n")
    for i, p in enumerate(paras[1:]):
        w(esc(p) + "\n\n")
        if i == 1 and sec.get("img"):
            w(r"\plate{" + sec["img"] + "}{" + esc(sec["cap"]) + "}{" + esc(sec["credit"]) + "}\n\n")
    if sec.get("img") and len(paras) <= 2:
        w(r"\plate{" + sec["img"] + "}{" + esc(sec["cap"]) + "}{" + esc(sec["credit"]) + "}\n\n")
    for rel, cap, credit in R.EXTRAS.get(sec["title"], []):
        w(r"\plate{" + rel + "}{" + esc(cap) + "}{" + esc(credit) + "}\n\n")

# ---------- الخاتمة ----------
w(r"\chapter*{" + esc(B.AFTERWORD["title"]) + "}\n")
w(r"\addcontentsline{toc}{chapter}{" + esc(B.AFTERWORD["title"]) + "}\n\n")
for p in B.AFTERWORD["paras"]:
    w(esc(p) + "\n\n")

# ---------- الخط الزمني ----------
w(r"\chapter*{خطّ زمني للكون}\n")
w(r"\addcontentsline{toc}{chapter}{خطّ زمني للكون}\n\n")
w(esc("كل ما في هذا الكتاب يمكن اختصاره في جدول واحد؛ لكن الجدول لا يشرح، ولذلك كُتب الكتاب.") + "\n\n")
w(r"\begin{description}" + "\n")
for lab, txt in R.TIMELINE:
    w(r"\item[{" + esc(lab) + "}] " + esc(txt) + "\n")
w(r"\end{description}" + "\n\n")

# ---------- ألبوم الصور ----------
w(r"\chapter*{ألبوم الصور: ثماني عشرة صورة}\n")
w(r"\addcontentsline{toc}{chapter}{ألبوم الصور}\n\n")
w(esc("تُجمع هنا كل صورة استُخدمت في هذا الكتاب أو وُجدت في أرشيف البحث، ومنها نسختان لكل موضوع؛ "
      "لم تُحذف صورة واحدة.") + "\n\n")
w(r"\begin{figure}[htbp]\centering" + "\n")
for i, (rel, label, credit) in enumerate(R.GALLERY):
    w(r"\begin{minipage}{0.31\textwidth}\centering"
      r"\includegraphics[width=\linewidth,height=4cm,keepaspectratio]{" + rel + "}"
      r"\par\footnotesize " + esc(label) + r"\par"
      r"{\scriptsize\textcolor[HTML]{8a5a2b}{" + esc(credit) + r"}}" +
      ("\n\\end{minipage}\\hfill\n" if i % 3 != 2 else "\n\\end{minipage}\n\\vspace{0.6em}\n"))
w(r"\end{figure}" + "\n\n")

# ---------- الإسناد ----------
w(r"\chapter*{إسناد الصور والمصادر}" + "\n")
for p in R.CREDITS_PARAS:
    w(esc(p) + "\n\n")
w(r"\begin{description}" + "\n")
for name, role in R.CREDITS_LIST:
    w(r"\item[" + esc(name) + r"] " + esc(role) + "\n")
w(r"\end{description}" + "\n\n")
w(r"\vfill\begin{center}\large تمّ بحمد الله\end{center}" + "\n\n")
w(r"\end{document}" + "\n")

tex = "\n".join(out)
open(os.path.join(HERE, "main.tex"), "w", encoding="utf-8").write(tex)
print("main.tex written:", len(tex), "bytes;", n, "chapters")
