#!/usr/bin/env python
"""tex -> typst -> pdf, with the two checks that matter: leaked markup and unresolved refs.
(Re-created after the sandbox reset; same three steps as the first two passes.)"""
import re, sys, pathlib
here = pathlib.Path(__file__).resolve().parent
tex, typ, pdf = here / "main.tex", here / "main.typ", here / "main.pdf"
import pypandoc, typst
pypandoc.convert_file(str(tex), "typst", outputfile=str(typ),
                      extra_args=["--standalone", "--wrap=none"])
s = typ.read_text()
if 'sectionnumbering' not in s:
    s = re.sub(r"(#show: doc => conf\()", r'\1\n  sectionnumbering: "1.1",', s, count=1)
    typ.write_text(s)
typst.compile(str(typ), output=str(pdf))
import pymupdf
d = pymupdf.open(str(pdf))
txt = " ".join(re.sub(r"\s+", " ", d[p].get_text()) for p in range(len(d)))
leaks = {k: txt.count(k) for k in [r"\textbf", r"\emph", r"\item", r"\cite", r"\S", r"\mu", r"\alpha", r"\beta", r"\to", r"\pm", "\\_", r"\rm", r"\label", r"\ref", r"\includegraphics", "$"]}
leaks = {k: v for k, v in leaks.items() if v}
words = len(txt.split())
print(f"pages={len(d)} words={words} leaks={leaks}")
unres = txt.count("??")
print("unresolved references:", unres)
print("figures embedded:", sum(len(d[p].get_images()) for p in range(len(d))))
if leaks or unres:
    print("WARNING: LaTeX leakage or unresolved refs"); sys.exit(1)
print(f"wrote {pdf}")
