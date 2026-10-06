.PHONY: all figures clean

PYTHON ?= ../venv/bin/python
TEX    ?= pdflatex
BIB    ?= bibtex
FLAGS  := -interaction=nonstopmode -halt-on-error

all: figures main.pdf

figures:
	$(PYTHON) make_figures.py

main.pdf: main.tex refs.bib $(wildcard figures/*.pdf)
	$(TEX) $(FLAGS) main
	$(BIB) main
	$(TEX) $(FLAGS) main
	$(TEX) $(FLAGS) main

clean:
	rm -f main.aux main.bbl main.blg main.log main.out main.toc
	rm -f main.fdb_latexmk main.fls main.synctex.gz

distclean: clean
	rm -f main.pdf
	rm -rf figures/
