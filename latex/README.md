# Final Research Paper — IEEE LaTeX

True IEEE conference-style LaTeX manuscript for *Q&A-Based Interactive Storytelling Using Generative AI: A Multimodal, Provider-Agnostic Framework*.

## Files

- `main.tex` — paper source, uses `IEEEtran` conference class
- `refs.bib` — 47 BibTeX entries (IEEE/Springer/ACM/arXiv, 2017–2025)
- `make_figures.py` — generates all 17 figures into `figures/`
- `figures/` — generated PDFs + PNGs (don't edit by hand; re-run `make_figures.py`)
- `Makefile` — convenience build target

## Compile

### Option A — Overleaf (easiest, no install)

1. Zip the whole `latex/` folder.
2. New Project → Upload Project → drop the zip.
3. Overleaf auto-detects `main.tex` and compiles. Bibliography resolves automatically.

### Option B — Local with full TeX Live (recommended)

```bash
# install once (macOS, ~5 GB)
brew install --cask mactex-no-gui

# or BasicTeX (~80 MB) + install missing classes via tlmgr
brew install --cask basictex
sudo tlmgr install ieeetran cite caption subcaption microtype \
    biber biblatex booktabs hyperref listings algorithmic
```

Then:

```bash
cd latex
python make_figures.py          # generate figures (uses repo venv)
make                            # or run the 4 commands below

# or manually:
pdflatex -interaction=nonstopmode main
bibtex   main
pdflatex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main
```

Output: `main.pdf` (the final paper).

### Option C — Docker (no host TeX install)

```bash
docker run --rm -v "$PWD:/wd" -w /wd texlive/texlive:latest \
  bash -c "python3 make_figures.py && pdflatex main && bibtex main && pdflatex main && pdflatex main"
```

## Adding your screenshots

Drop the PNG into `figures/`, then in `main.tex` add:

```latex
\begin{figure}[!t]
  \centering
  \includegraphics[width=\columnwidth]{screenshot_landing.png}
  \caption{Landing page with question-count selector.}
  \label{fig:screen-landing}
\end{figure}
```

Suggested locations to add UI screenshots:
- after Section III-C (architecture diagram) → landing page + Q&A form
- inside Section IV-D (image pipeline) → a generated story segment with illustration
- inside Section IV-G (reader analytics) → the Story Map and Character Graph modals
- inside Section V-E → the custom-question composer in action

## Section / figure map

| Sect. | Content                                    | Figures              |
| ----- | ------------------------------------------ | -------------------- |
| I     | Intro, problem, contributions              | —                    |
| II    | Related work                               | —                    |
| III   | Architecture, modules, tech stack          | Fig. 7, 8 + screenshots s01 (landing), s02 (Q\&A form) + Tables I,II |
| IV    | Methodology + multimodal pipelines         | Fig. 4, 9, 10, 16 + screenshots s03 (loading), s04 (story with image) |
| V     | Implementation, REST, DB schema            | Tables III,IV + screenshot s05 (settings panel) |
| VI    | Experimental results (10 subsections)      | Fig. 1, 2, 3, 6, 11, 12, 13, 14, 15, 17 + Table V |
| VII   | Comparative evaluation                     | Fig. 5               |
| VIII  | Limitations                                | —                    |
| IX    | Future work                                | —                    |
| X     | Conclusion                                 | —                    |
| —     | References                                 | (IEEEtran .bbl)      |

## Screenshots

The five UI screenshots in `figures/` (`s01_landing.png` …
`s05_settings.png`) are referenced from `main.tex` as
`Fig.~\ref{fig:landing}` (III-C), `\ref{fig:questions}` (III-C),
`\ref{fig:loading}` (IV-D), `\ref{fig:storyimage}` (IV-D) and
`\ref{fig:settings}` (V-C) respectively. Replace any of them by
overwriting the PNG of the same name; no `.tex` edit needed.
