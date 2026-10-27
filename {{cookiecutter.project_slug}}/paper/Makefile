# Paper build.
#
#   make          build main.pdf
#   make arxiv    package arxiv.tar.gz for submission
#   make format   rewrite main.tex one sentence per line
#   make logo     regenerate the lab logo PDF from its SVG
#   make clean    remove build artifacts

PYTHON ?= python3
LOGO_SVG = figures/ai4g_light.svg
LOGO_PDF = figures/ai4g_light.pdf

.PHONY: all paper arxiv format logo clean

all: paper

paper: main.pdf

main.pdf: main.tex references.bib cup-journal.cls $(LOGO_PDF)
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

arxiv:
	$(PYTHON) arxiv_collector.py main

format:
	$(PYTHON) scripts/sentence_per_line.py main.tex

logo: $(LOGO_SVG)
	uv run --with cairosvg python -c "import cairosvg; cairosvg.svg2pdf(url='$(LOGO_SVG)', write_to='$(LOGO_PDF)')"

clean:
	latexmk -C
	rm -f main.bbl main.run.xml arxiv.tar.gz
