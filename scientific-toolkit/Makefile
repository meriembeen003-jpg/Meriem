.PHONY: test demo audit review catalogue install clean

test:
	python3 -m unittest discover -s tests -v

demo:
	bash demos/run_all.sh

audit:
	python3 -m scitk audit data/article_exemple.txt --biblio data/references_exemple.bib \
		--descriptifs data/descriptifs_exemple.json --out demos/out/audit_article

review:
	python3 -m scitk review data/corpus_exemple.csv --nom "Remédiation en lecture" \
		--inclusion "lecture|reading" --exclusion "rodent|animal" --sortie demos/out/revue

catalogue:
	python3 scripts/build_catalog.py
	cp catalog/outils.json ../public/catalogue.json
	cp catalog/outils.json ../public/catalogue.json

install:
	bash scripts/install.sh

clean:
	rm -rf demos/out/*.md demos/out/*.html demos/out/*.json demos/out/revue __pycache__ */__pycache__ */*/__pycache__
