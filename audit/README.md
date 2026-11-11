Audit sources, third pass (Companion A).

- companion_A.tex  the paper source (15 pp, 6,934 words, 5 figures)
- deepen.py        recomputes every number and draws all 5 figures from the raw Pantheon bins
- build.py         tex -> typst -> pdf, with a markup-leak and unresolved-ref check
- logs/            the raw computation log, plus every number in machine form (deepen.json)
                 and every caption exactly as typeset (deepen_figures_manifest.json)
- Companion_A.pdf  the built deliverable

Figure PNGs (paper/figures/f19..f23) and the raw data files are intentionally not committed:
regenerate with `python deepen.py` after placing data/lcparam_DS17f.txt and data/sys_DS17f.txt
(from github.com/dscolnic/Pantheon, Binned_data/).
