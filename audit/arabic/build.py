import pathlib, re, sys
import typst, pymupdf
here = pathlib.Path(__file__).resolve().parent
src, pdf = here/"book.typ", here/"book.pdf"
typst.compile(str(src), output=str(pdf), root=str(here),
              font_paths=["/home/user/fonts", "/home/user/.venv-r/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf"])
d = pymupdf.open(str(pdf))
txt = " ".join(re.sub(r"\s+", " ", d[p].get_text()) for p in range(len(d)))
bad = {k: txt.count(k) for k in ["#", "$", "@", "\\", "??", "[", "]"] if txt.count(k)}
print("pages", len(d), "| words", len(txt.split()), "| figures", sum(len(d[p].get_images()) for p in range(len(d))))
print("suspicious chars:", bad)
print("arabic sample:", txt[300:420])
