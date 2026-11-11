# Arabic facts edition (pass 5)

`make_facts.py` is the whole build: it re-runs the supernova fit from `data/`,
assembles every number into `logs/facts_numbers.json`, writes `facts.typ`, compiles
`facts.pdf` and audits it (no markup leaks, 11 figures, 11 ordered captions, no
unresolved placeholder — an unknown key raises instead of printing a zero).

Run order: `python figs.py` → `python deepen.py` → `python make_facts.py`, with
`data/lcparam_DS17f.txt` and `data/sys_DS17f.txt` next to the scripts and
`paper/figures/` holding the eleven PNGs (g01–g06 from figs.py, f19–f23 from
deepen.py; MD5s of the PNGs are recorded in the two manifests).

The text never carries a hand-typed figure: numbers reach it only as `§key:spec§`.
Two sentences carry their own weakness rather than hiding it — the cross-check in
block (٤) quotes the size of the disagreement between the two fits, and block (٢٦)
lists the three wrong arXiv ids found in this project's earlier drafts, one
fabricated record, four ids that could not be opened, and the three plotting bugs.
