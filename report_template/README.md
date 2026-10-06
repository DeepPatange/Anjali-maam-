# M.Tech Dissertation — Q&A Based Interactive Storytelling Using Generative AI

LaTeX source built on the SAKEC B.Tech/M.Tech project report template.

## Author
- **Student:** Anjali Madan Jha (Roll No. 124MTCM1008)
- **Department:** Computer Engineering, SAKEC
- **Supervisor:** Dr. Vidyullata Devmane
- **Date:** January 2026

## Layout

```
report_template/
├── thesis.tex              # Main document — \include's everything
├── references.bib          # natbib bibliography (~50 entries, 2017–2025)
├── front_matter/
│   ├── title_page.tex
│   ├── certificate.tex
│   ├── candidate's_declaration.tex
│   ├── Certificate_of_Plag_Check.tex
│   ├── dedication.tex
│   ├── acknowledgements.tex
│   └── Abstract.tex
├── chapters/
│   ├── introduction.tex            # Ch. 1
│   ├── literature_review.tex       # Ch. 2 (survey + research gap)
│   ├── problem_statement.tex       # Ch. 3 (problem, objectives, scope)
│   ├── scheduling.tex              # Ch. 4 (Gantt chart)
│   ├── proposed_system.tex         # Ch. 5 (feasibility, framework, h/w, design, methodology)
│   ├── implementation.tex          # Ch. 6 (modules + UI snapshots)
│   ├── testing.tex                 # Ch. 7
│   ├── results_and_discussions.tex # Ch. 8
│   ├── conclusions.tex             # Ch. 9 (conclusion + future scope)
│   └── appendix.tex
└── images/
    ├── SAKEC_logo.png
    ├── gantt.{pdf,png}
    ├── f01_latency.pdf … f17_breakdown.pdf   # 17 generated charts
    └── s01_landing.png … s05_settings.png    # 5 UI screenshots
```

The chapter order exactly follows the SAKEC project-report format
(Abstract → Introduction → Literature Survey → Problem Statement →
Scheduling → Proposed System → Implementation → Testing → Results →
Conclusion → Bibliography).

## Compile

### Option A — Overleaf (recommended, no install needed)

1. Zip the entire `report_template/` folder.
2. New Project → Upload Project → drop the zip.
3. Overleaf detects `thesis.tex` and compiles in one click.
4. Run again after `BibTeX` resolves the bibliography.

### Option B — Local with TeX Live

```bash
# install once (macOS)
brew install --cask mactex-no-gui

cd report_template
pdflatex -interaction=nonstopmode thesis
bibtex   thesis
pdflatex -interaction=nonstopmode thesis
pdflatex -interaction=nonstopmode thesis
```

Output: `thesis.pdf`.

### Option C — Docker

```bash
docker run --rm -v "$PWD:/wd" -w /wd texlive/texlive:latest \
  bash -c "pdflatex thesis && bibtex thesis && pdflatex thesis && pdflatex thesis"
```

## Customisation hooks

All author / title / supervisor data is centralised at the top of
[`thesis.tex`](thesis.tex):

```tex
\def\mytitle{Q\&A Based Interactive Storytelling Using Generative AI}
\def\myname{Anjali Madan Jha}
\def\mydegree{MASTER OF TECHNOLOGY}
\def\branch{Computer Engineering}
\def\mysupervisor{Dr. Vidyullata Devmane}
\def\myrollno{124MTCM1008}
\def\mydep{Department of Computer Engineering}
\def\mydegreedate{JANUARY 2026}
```

Edit these, recompile, and the title page, certificate, declaration
and plagiarism check page all pick up the new values automatically.

## Adding / swapping figures

1. Drop the PNG/PDF into `images/`.
2. Use `\includegraphics[width=0.8\textwidth]{images/your_file}`.

The five screenshots in the manuscript live at:

| File                        | Used in                          |
| --------------------------- | -------------------------------- |
| `images/s01_landing.png`    | Implementation §6.1 (Fig.\ ui-landing) |
| `images/s02_questions.png`  | Implementation §6.1 (Fig.\ ui-form) |
| `images/s03_loading.png`    | Implementation §6.8 (Fig.\ ui-loading) |
| `images/s04_story_image.png`| Implementation §6.8 (Fig.\ ui-story) |
| `images/s05_settings.png`   | Implementation §6.5 (Fig.\ ui-settings) |

To swap any one of them, overwrite the PNG with a new screenshot of
the same name — no `.tex` edit required.
