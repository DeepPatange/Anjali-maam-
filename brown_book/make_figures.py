"""
Figures for the brown book that describe the fine-tuned model.

Reads the measurement files written by the scripts in finetune/ and saves PDF
and PNG figures into brown_book/images/.

Usage (from the project root):  venv/bin/python brown_book/make_figures.py
"""

import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")
FT = os.path.join(HERE, "..", "finetune")

INK = "#0F172A"
ACC1 = "#2563EB"
ACC2 = "#7C3AED"
ACC3 = "#F59E0B"
ACC4 = "#10B981"
ACC5 = "#EF4444"
GREY = "#94A3B8"


def _save(name):
    for ext in ("pdf", "png"):
        plt.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=240, bbox_inches="tight", facecolor="white")
    plt.close()


def _light(color, amount=0.72):
    """Pastel version of a colour, so that black labels stay readable in print."""
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount)


def _box(ax, x, y, w, h, text, color=ACC1, tc="#111111", fs=8):
    # Light fill with dark text: readable when printed, and no white text in the PDF.
    ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.10",
                                         facecolor=_light(color), edgecolor=color, linewidth=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color="#111111", fontweight="bold")


def _arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#444", lw=1.1))


def architecture():
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.set_xlim(0, 12); ax.set_ylim(0.9, 8); ax.axis("off")
    _box(ax, 0.3, 6.8, 11.4, 0.7, "PRESENTATION  -  HTML5 + CSS3 + JavaScript + D3.js", INK)
    _box(ax, 0.3, 5.7, 11.4, 0.7, "APPLICATION  -  FastAPI / Uvicorn  -  13 REST endpoints", ACC1)
    _box(ax, 0.3, 4.4, 2.0, 0.9, "User Input\nAcquisition", ACC2)
    _box(ax, 2.5, 4.4, 2.0, 0.9, "Context\nExtraction", ACC2)
    _box(ax, 4.7, 4.4, 2.0, 0.9, "Prompt\nEngineering", ACC2)
    _box(ax, 6.9, 4.4, 2.0, 0.9, "Story Flow\nManager", ACC2)
    _box(ax, 9.1, 4.4, 2.6, 0.9, "Knowledge / Memory\n(SQLite)", ACC3, "#111", 7.5)
    _box(ax, 0.3, 3.0, 2.5, 0.9, "Story Generator", ACC5)
    _box(ax, 3.0, 3.0, 2.5, 0.9, "Output Formatter\nHTML / MD / TXT", ACC4)
    _box(ax, 5.7, 3.0, 2.5, 0.9, "Scene Illustration\n(image service)", ACC1)
    _box(ax, 8.4, 3.0, 1.6, 0.9, "Narration\nWeb Speech", ACC2)
    _box(ax, 10.1, 3.0, 1.6, 0.9, "Ambient\nMusic", ACC3, "#111", 7.5)
    _box(ax, 0.3, 1.5, 3.4, 0.9, "Ollama runtime (local)\nllama.cpp, GGUF", INK, "white", 7.5)
    _box(ax, 3.95, 1.5, 3.7, 0.9, "Llama 3.2 3B Instruct\npretrained weights, 4-bit", ACC1, "white", 7.5)
    _box(ax, 7.9, 1.5, 3.8, 0.9, "StoryForge LoRA adapter\nfine-tuned, 2.62 M parameters", ACC4, "white", 7.5)
    for x in [1.3, 3.5, 5.7, 7.9, 10.4]:
        _arrow(ax, x, 5.7, x, 5.3)
    _arrow(ax, 1.3, 4.4, 1.3, 3.9); _arrow(ax, 3.5, 4.4, 3.5, 3.9)
    _arrow(ax, 5.7, 4.4, 6.9, 3.9); _arrow(ax, 7.9, 4.4, 9.2, 3.9)
    _arrow(ax, 1.5, 3.0, 1.5, 2.4)
    ax.text(0.3, 1.15, "MODEL LAYER  (runs on the same machine)", fontsize=7, color="#555", fontweight="bold")
    plt.tight_layout(); _save("n01_architecture")


def dataset_pipeline():
    fig, ax = plt.subplots(figsize=(7.6, 3.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.6); ax.axis("off")
    _box(ax, 0.2, 3.9, 2.4, 1.2, "Public stories\n1,000 stories\n99 genres", INK, "white", 7.5)
    _box(ax, 3.1, 3.9, 2.5, 1.2, "Back-labelling\nanswers to the\n17 questions", ACC2, "white", 7.5)
    _box(ax, 6.1, 3.9, 2.6, 1.2, "Budget sampling\nfirst N answers\n(4 / 8 / 12 / 17)", ACC2, "white", 7.5)
    _box(ax, 9.2, 3.9, 2.6, 1.2, "Application code\nContext Extraction +\nPrompt Engineering", ACC1, "white", 7.5)
    _box(ax, 0.2, 1.9, 2.4, 1.2, "Segmentation\nopening +\nfollow-up parts", ACC3, "#111", 7.5)
    _box(ax, 3.1, 1.9, 5.6, 1.2,
         "Training sample\nsystem prompt + user prompt  ->  story segment\n"
         "(opening, continuation, climax or resolution)", ACC4, "white", 7.2)
    _box(ax, 9.2, 1.9, 2.6, 1.2, "Split by story\n900 / 50 / 50\ntrain / valid / test", ACC5, "white", 7.5)
    _box(ax, 3.1, 0.2, 5.6, 0.9, "3,321 training, 183 validation and 191 test samples", INK, "white", 8)
    _arrow(ax, 2.6, 4.5, 3.1, 4.5); _arrow(ax, 5.6, 4.5, 6.1, 4.5); _arrow(ax, 8.7, 4.5, 9.2, 4.5)
    _arrow(ax, 1.4, 3.9, 1.4, 3.1); _arrow(ax, 2.6, 2.5, 3.1, 2.5)
    _arrow(ax, 10.5, 3.9, 8.0, 3.1); _arrow(ax, 8.7, 2.5, 9.2, 2.5)
    _arrow(ax, 10.5, 1.9, 8.7, 0.75)
    plt.tight_layout(); _save("n02_dataset_pipeline")


def training_curve():
    rows = list(csv.DictReader(open(os.path.join(FT, "training_curve.csv"))))
    tr = [(int(r["step"]), float(r["loss"])) for r in rows if r["split"] == "train"]
    va = [(int(r["step"]), float(r["loss"])) for r in rows if r["split"] == "validation"]
    va[0] = (0, va[0][1])
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    ax.plot(*zip(*tr), color=ACC1, lw=1.4, marker="o", ms=2.5, label="Training loss (mean of 20 steps)")
    ax.plot(*zip(*va), color=ACC5, lw=1.8, marker="s", ms=5, label="Validation loss")
    for s, v in va:
        ax.annotate(f"{v:.3f}", (s, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=7, color=ACC5)
    ax.set_xlabel("Training step"); ax.set_ylabel("Cross-entropy loss on story text")
    ax.set_xlim(-15, 615); ax.set_ylim(1.0, 1.6); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout(); _save("n03_training_curve")


def heldout_loss():
    res = json.load(open(os.path.join(FT, "eval_results.json")))
    kinds = ["init", "continuation", "climax", "resolution"]
    labels = ["Opening", "Continuation", "Climax", "Resolution", "Overall"]
    base = [res["base"]["by_kind"][k]["loss"] for k in kinds] + [res["base"]["loss"]]
    tuned = [res["finetuned"]["by_kind"][k]["loss"] for k in kinds] + [res["finetuned"]["loss"]]
    x = np.arange(len(labels)); w = 0.36
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    b1 = ax.bar(x - w / 2, base, w, label="Pretrained Llama 3.2 3B", color=GREY, edgecolor="white")
    b2 = ax.bar(x + w / 2, tuned, w, label="Fine-tuned (StoryForge)", color=ACC1, edgecolor="white")
    ax.bar_label(b1, fmt="%.3f", padding=2, fontsize=7); ax.bar_label(b2, fmt="%.3f", padding=2, fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Held-out loss (lower is better)"); ax.set_ylim(0, 2.0)
    ax.grid(axis="y", alpha=0.25); ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout(); _save("n04_heldout_loss")


def per_sample_scatter():
    res = json.load(open(os.path.join(FT, "eval_results.json")))
    pts = res["per_sample"]
    colors = {"init": ACC1, "continuation": ACC4, "climax": ACC3, "resolution": ACC2}
    names = {"init": "Opening", "continuation": "Continuation", "climax": "Climax", "resolution": "Resolution"}
    fig, ax = plt.subplots(figsize=(4.4, 4.0))
    for k in colors:
        sub = [p for p in pts if p["kind"] == k]
        ax.scatter([p["base"] for p in sub], [p["finetuned"] for p in sub], s=12, color=colors[k],
                   alpha=0.75, label=names[k], edgecolors="none")
    lo = min(min(p["base"], p["finetuned"]) for p in pts) - 0.05
    hi = max(max(p["base"], p["finetuned"]) for p in pts) + 0.05
    ax.plot([lo, hi], [lo, hi], color="#444", lw=1, ls="--")
    ax.text(hi - 0.02, hi - 0.16, "equal loss", fontsize=7, color="#444", ha="right", rotation=38)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("Loss of pretrained model"); ax.set_ylabel("Loss of fine-tuned model")
    ax.grid(alpha=0.25); ax.legend(fontsize=7, loc="upper left")
    plt.tight_layout(); _save("n05_per_sample")


def generation():
    data = json.load(open(os.path.join(FT, "generation_eval.json")))
    summ = json.load(open(os.path.join(FT, "generation_summary.json")))
    samples = [s for s in data["samples"] if "base" in s and "finetuned" in s]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.3), gridspec_kw={"width_ratios": [1.0, 1.25]})

    ax = axes[0]
    groups, labels, cols = [], [], []
    for kind, name in (("init", "Opening"), ("continuation", "Continuation")):
        for tag, short, c in (("base", "pretrained", GREY), ("finetuned", "fine-tuned", ACC1)):
            groups.append([len(s[tag]["text"].split()) for s in samples if s["kind"] == kind])
            labels.append(f"{name}\n{short}"); cols.append(c)
    bp = ax.boxplot(groups, patch_artist=True, widths=0.6, medianprops=dict(color="#111"))
    for patch, c in zip(bp["boxes"], cols):
        patch.set_facecolor(c); patch.set_alpha(0.85)
    ax.axhspan(300, 400, xmin=0.0, xmax=0.5, color=ACC4, alpha=0.18)
    ax.axhspan(250, 350, xmin=0.5, xmax=1.0, color=ACC4, alpha=0.18)
    ax.set_xticklabels(labels, fontsize=6.5); ax.set_ylabel("Words per generated segment")
    ax.grid(axis="y", alpha=0.25); ax.set_title("Length (shaded: requested range)", fontsize=8)

    ax = axes[1]
    keys = [("length_ok_pct", "Length within\n25% of request"), ("story_text_only_pct", "Story text\nonly"),
            ("names_protagonist_pct", "Names the\nprotagonist"), ("complete_ending_pct", "Ends in a\ncomplete sentence")]
    allk = summ["by_kind"]["all"]
    x = np.arange(len(keys)); w = 0.36
    b1 = ax.bar(x - w / 2, [allk["base"][k] for k, _ in keys], w, color=GREY, edgecolor="white", label="Pretrained")
    b2 = ax.bar(x + w / 2, [allk["finetuned"][k] for k, _ in keys], w, color=ACC1, edgecolor="white", label="Fine-tuned")
    ax.bar_label(b1, fmt="%.0f", padding=2, fontsize=7); ax.bar_label(b2, fmt="%.0f", padding=2, fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels([l for _, l in keys], fontsize=6.5)
    ax.set_ylabel("Share of generated segments (%)"); ax.set_ylim(0, 118)
    ax.grid(axis="y", alpha=0.25); ax.legend(fontsize=7, loc="upper right", ncol=2)
    ax.set_title("Prompt adherence (69 held-out prompts)", fontsize=8)
    plt.tight_layout(); _save("n06_generation")



def image_pipeline():
    fig, ax = plt.subplots(figsize=(7.0, 2.4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 2.3); ax.axis("off")
    _box(ax, 0.2, 1.0, 1.7, 1.0, "Story\nSegment", INK)
    _box(ax, 2.2, 1.0, 1.9, 1.0, "Scene\nExtractor", ACC2)
    _box(ax, 4.4, 1.0, 1.9, 1.0, "Prompt\nBuilder", ACC1)
    _box(ax, 6.6, 1.0, 1.9, 1.0, "Request\nQueue", ACC3)
    _box(ax, 8.8, 1.0, 1.9, 1.0, "Image\nService", ACC5)
    _box(ax, 11.0, 1.0, 1.0, 1.0, "Image", ACC4)
    for x1, x2 in [(1.9, 2.2), (4.1, 4.4), (6.3, 6.6), (8.5, 8.8), (10.7, 11.0)]:
        _arrow(ax, x1, 1.5, x2, 1.5)
    for x, label in [(3.15, "strip dialogue\nscore visual"), (5.35, "<= 200 chars\n+ genre tag"),
                     (7.55, "1.2 s spacing\n+ watchdog"), (9.75, "768 x 432\nseeded")]:
        ax.text(x, 0.35, label, ha="center", fontsize=7, color="#333")
    plt.tight_layout(); _save("f09_imgpipe")


def audio_paths():
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.25); ax.axis("off")
    rows = [(2.8, ["Story Text", "Utterance\nQueue", "Web Speech\nSynthesis", "OS Voice\n(per locale)", "Speakers"],
             "Narration path", 3.95),
            (1.0, ["Detected\nGenre", "Track\nMapper", "HTMLAudio\nLoop + Fade", "Music Stream\n(SoundHelix)", "Speakers"],
             "Ambient music path (8 genre presets)", 0.4)]
    xs = [(0.2, 1.8), (2.2, 2.0), (4.4, 2.4), (7.0, 2.4), (9.6, 2.2)]
    cols = [INK, ACC2, ACC1, ACC4, ACC5]
    for y, labels, title, ty in rows:
        for (x, w), label, c in zip(xs, labels, cols):
            _box(ax, x, y, w, 0.9, label, c)
        for x1, x2 in [(2.0, 2.2), (4.2, 4.4), (6.8, 7.0), (9.4, 9.6)]:
            _arrow(ax, x1, y + 0.45, x2, y + 0.45)
        ax.text(6.0, ty, title, ha="center", fontsize=8, color="#333", fontweight="bold")
    plt.tight_layout(); _save("f10_audio")


def custom_question_path():
    fig, ax = plt.subplots(figsize=(7.0, 2.0))
    ax.set_xlim(0, 12); ax.set_ylim(0.5, 2.1); ax.axis("off")
    labels = ["User adds\nquestion + answer", "Identifier\ncustom_q_N", "/api/response\n(stored)",
              "Context engine\ncustom_elements", "Prompt layer\n+ user preferences"]
    xs = [(0.2, 1.8), (2.2, 2.0), (4.4, 2.0), (6.6, 2.4), (9.2, 2.6)]
    for (x, w), label, c in zip(xs, labels, [INK, ACC2, ACC1, ACC3, ACC4]):
        _box(ax, x, 0.8, w, 1.0, label, c, fs=7.5)
    for x1, x2 in [(2.0, 2.2), (4.2, 4.4), (6.4, 6.6), (9.0, 9.2)]:
        _arrow(ax, x1, 1.3, x2, 1.3)
    plt.tight_layout(); _save("f16_customq")


def _frame(ax, x, y, w, h, title):
    ax.add_patch(mpatches.Rectangle((x, y), w, h, facecolor="#F8FAFC", edgecolor="#475569",
                                    linewidth=1.2, linestyle="--"))
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center", fontsize=8.5,
            fontweight="bold", color="#111111")


def block_diagram():
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9); ax.axis("off")
    # Input
    _frame(ax, 0.15, 3.9, 2.8, 4.75, "INPUT (USER)")
    _box(ax, 0.35, 7.0, 2.4, 0.9, "Story preferences\n(answers to the\n17 questions)", INK, fs=7)
    _box(ax, 0.35, 5.6, 2.4, 0.9, "Custom answers and\nuser-added\nquestions", INK, fs=7)
    _box(ax, 0.35, 4.2, 2.4, 0.9, "Choice of direction\nfor next chapter", INK, fs=7)
    # Proposed system
    _frame(ax, 3.35, 0.75, 6.1, 7.9, "PROPOSED SYSTEM (LOCAL MACHINE)")
    X, W = 3.6, 3.3
    _box(ax, X, 7.0, W, 0.9, "Q&A module\n(question budget 4 / 8 / 12 / 17)", ACC2, fs=7)
    _box(ax, X, 5.6, W, 0.9, "Context extraction\n(story context + custom elements)", ACC2, fs=7)
    _box(ax, X, 3.95, W, 1.2, "Prompt builder\n(phase template + context\n+ previous chapters)", ACC1, fs=7)
    _box(ax, X, 2.45, W, 1.0, "Fine-tuned Llama 3.2 3B\n(QLoRA adapter, Ollama)", ACC4, fs=7)
    _box(ax, X, 1.0, W, 0.95, "Output formatter\n(clean text + four choices)", ACC3, fs=7)
    _box(ax, 7.35, 4.7, 1.95, 0.75, "Story flow manager\n(five phases)", ACC5, fs=6.5)
    _box(ax, 7.35, 3.6, 1.95, 0.75, "Memory (SQLite)\nsessions, chapters", ACC3, fs=6.5)
    cx = X + W / 2
    _arrow(ax, cx, 7.0, cx, 6.5); _arrow(ax, cx, 5.6, cx, 5.15)
    _arrow(ax, cx, 3.95, cx, 3.45); _arrow(ax, cx, 2.45, cx, 1.95)
    _arrow(ax, 7.35, 5.07, X + W, 4.85)
    ax.annotate("", xy=(X + W, 4.2), xytext=(7.35, 3.97),
                arrowprops=dict(arrowstyle="<->", color="#444", lw=1.1))
    # Input arrows
    _arrow(ax, 2.75, 7.45, X, 7.45); _arrow(ax, 2.75, 6.05, X, 6.05); _arrow(ax, 2.75, 4.65, X, 4.65)
    # Output
    _frame(ax, 9.85, 0.75, 3.0, 7.9, "OUTPUT")
    ys = [6.95, 5.65, 4.35, 3.05, 1.75]
    labels = ["Story chapter and\nfour suggested\ndirections", "Scene illustration\n(image service)",
              "Narration\n(Web Speech)", "Background music\n(by genre)", "Story map and\ncharacter graph"]
    cols = [ACC1, ACC2, ACC4, ACC3, INK]
    for y, t, c in zip(ys, labels, cols):
        _box(ax, 10.1, y, 2.5, 0.95, t, c, fs=7)
    _arrow(ax, X + W, 1.47, 9.85, 1.47)
    ax.text(8.35, 1.6, "chapter", ha="center", va="bottom", fontsize=6.5, color="#333")
    # Feedback loop
    ax.plot([11.35, 11.35, 1.55, 1.55], [0.75, 0.3, 0.3, 3.75], color=ACC5, lw=1.3, ls="--")
    ax.annotate("", xy=(1.55, 3.9), xytext=(1.55, 3.6),
                arrowprops=dict(arrowstyle="->", color=ACC5, lw=1.3))
    ax.text(6.4, 0.38, "user reads the chapter and chooses the next direction",
            ha="center", va="bottom", fontsize=6.5, color=ACC5)
    plt.tight_layout(); _save("n07_block_diagram")

if __name__ == "__main__":
    block_diagram()
    architecture()
    dataset_pipeline()
    image_pipeline()
    audio_paths()
    custom_question_path()
    training_curve()
    for fn in (heldout_loss, per_sample_scatter, generation):
        try:
            fn()
        except (FileNotFoundError, KeyError) as e:
            print(f"skipped {fn.__name__}: {e}")
    print("figures written to", OUT)
