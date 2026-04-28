# CV build: generate vita_generated.tex from YAML, compile to PDF.
#
# Usage:
#   make          # regenerate and compile PDF
#   make tex      # regenerate vita_generated.tex only
#   make pdf      # compile vita_generated.tex -> vita_generated.pdf
#   make diff     # show diff vs. hand-maintained vita.tex
#   make clean    # remove generated artifacts (keeps source vita.tex)
#   make install  # pip install build deps into local .venv
#
# Canonical source: ../_data/cv.yml
# Generated LaTeX:  vita.tex  (regenerated from the YAML every build — never hand-edit)
# Compiled PDF:     vita.pdf
# Legacy reference: vita.tex.legacy (the original hand-written tex, kept for history)

YAML_SRC := ../_data/cv.yml
TEX      := vita.tex
PDF      := vita.pdf
PY       := python3
VENV     := .venv
PIP      := $(VENV)/bin/pip
VENV_PY  := $(VENV)/bin/python

.PHONY: all tex pdf diff clean install

all: pdf

$(TEX): $(YAML_SRC) build_tex.py
	@if [ -d $(VENV) ]; then $(VENV_PY) build_tex.py; else $(PY) build_tex.py; fi

tex: $(TEX)

$(PDF): $(TEX)
	@command -v pdflatex >/dev/null || { echo "pdflatex not found; install a TeX distribution (e.g. BasicTeX: brew install --cask basictex)"; exit 1; }
	pdflatex -interaction=nonstopmode $(TEX) >/dev/null
	pdflatex -interaction=nonstopmode $(TEX) >/dev/null

pdf: $(PDF)

diff: $(TEX)
	@diff -u vita.tex.legacy $(TEX) | head -200 || true

install:
	$(PY) -m venv $(VENV)
	$(PIP) install --quiet --index-url https://pypi.org/simple -r requirements.txt
	@echo "installed build deps into $(VENV)/"

clean:
	rm -f $(PDF) vita.aux vita.log vita.out
