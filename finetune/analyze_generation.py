"""
Summarise the generation benchmark (generation_eval.json).

For the pretrained base model and the fine-tuned model the script reports, per
prompt type, the prompt-adherence measures, lexical variety and speed of the
generated text, and compares the two models on the same prompts with paired
tests (McNemar's exact test for yes/no measures, Wilcoxon signed-rank test for
numeric measures).

Usage:  finetune/.venv/bin/python finetune/analyze_generation.py
Output: finetune/generation_summary.json
"""

import json
import re
from pathlib import Path
from statistics import mean, median

from scipy import stats

HERE = Path(__file__).resolve().parent
TARGET = {"init": (300, 400), "continuation": (250, 350)}       # words requested by the prompt
TOLERANCE = 0.25

ADDED_START = re.compile(
    r"^\s*(#|\*\*|\*|here('s| is| are)\b|sure\b|certainly\b|of course\b|okay\b|title\s*:|chapter\s+\w+|"
    r"story\s*:|opening\s*:|continuation\s*:)", re.I)
ADDED_END = re.compile(
    r"(word count|let me know|i hope (this|you)|would you like|feel free|\(\s*\d+\s*words?\s*\)|^note\s*:|"
    r"to be continued|what (will|would|should) \w+ do next\?)", re.I)


def measures(text, kind, protagonist):
    words = text.split()
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    first, last = (lines[0], lines[-1]) if lines else ("", "")
    heading = len(first.split()) <= 8 and not re.search(r"[.!?\"”]$", first)
    lo, hi = TARGET[kind]
    lower = [w.lower().strip(".,;:!?\"'()“”’") for w in words]
    pairs = list(zip(lower, lower[1:]))
    return {
        "words": len(words),
        "length_ok": lo * (1 - TOLERANCE) <= len(words) <= hi * (1 + TOLERANCE),
        "story_text_only": not (ADDED_START.search(first) or heading or ADDED_END.search(last)),
        "names_protagonist": (protagonist in text) if protagonist else None,
        "complete_ending": bool(re.search(r"[.!?][\"”’)*]*$", text.strip())),
        "distinct2": len(set(pairs)) / max(1, len(pairs)),
    }


def mcnemar_exact(a, b):
    """Two-sided exact McNemar test for paired yes/no outcomes."""
    only_a = sum(1 for x, y in zip(a, b) if x and not y)
    only_b = sum(1 for x, y in zip(a, b) if y and not x)
    n = only_a + only_b
    p = 1.0 if n == 0 else float(stats.binomtest(min(only_a, only_b), n, 0.5).pvalue)
    return {"base_only": only_a, "finetuned_only": only_b, "p": p}


def wilcoxon(a, b):
    if all(x == y for x, y in zip(a, b)):
        return {"p": 1.0}
    return {"p": float(stats.wilcoxon(a, b).pvalue)}


def summarise(samples, tag):
    m = [s[tag + "_m"] for s in samples]
    named = [x["names_protagonist"] for x in m if x["names_protagonist"] is not None]
    gen = [s[tag] for s in samples]
    return {
        "n": len(samples),
        "words_mean": round(mean(x["words"] for x in m), 1),
        "words_median": median(x["words"] for x in m),
        "words_min": min(x["words"] for x in m),
        "words_max": max(x["words"] for x in m),
        "length_ok_pct": round(100 * mean(x["length_ok"] for x in m), 1),
        "story_text_only_pct": round(100 * mean(x["story_text_only"] for x in m), 1),
        "names_protagonist_pct": round(100 * mean(named), 1) if named else None,
        "names_protagonist_n": len(named),
        "complete_ending_pct": round(100 * mean(x["complete_ending"] for x in m), 1),
        "distinct2_mean": round(mean(x["distinct2"] for x in m), 3),
        "output_tokens_mean": round(mean(g["output_tokens"] for g in gen), 1),
        "tokens_per_s_mean": round(mean(g["output_tokens"] / g["output_s"] for g in gen), 1),
        "seconds_mean": round(mean(g["wall_s"] for g in gen), 1),
        "seconds_median": round(median(g["wall_s"] for g in gen), 1),
        "seconds_max": round(max(g["wall_s"] for g in gen), 1),
        "hit_token_limit": sum(g.get("done_reason") == "length" for g in gen),
    }


def main():
    data = json.loads((HERE / "generation_eval.json").read_text())
    samples = [s for s in data["samples"] if "base" in s and "finetuned" in s]
    for s in samples:
        for tag in ("base", "finetuned"):
            s[tag + "_m"] = measures(s[tag]["text"], s["kind"], s["protagonist"])

    out = {"n_prompts": len(samples), "tolerance": TOLERANCE, "targets": TARGET, "by_kind": {}, "paired": {}}
    for kind in ["init", "continuation", "all"]:
        sub = [s for s in samples if kind == "all" or s["kind"] == kind]
        if not sub:
            continue
        out["by_kind"][kind] = {tag: summarise(sub, tag) for tag in ("base", "finetuned")}
        b = [s["base_m"] for s in sub]
        f = [s["finetuned_m"] for s in sub]
        named = [(x["names_protagonist"], y["names_protagonist"]) for x, y in zip(b, f)
                 if x["names_protagonist"] is not None]
        out["paired"][kind] = {
            "length_ok": mcnemar_exact([x["length_ok"] for x in b], [y["length_ok"] for y in f]),
            "story_text_only": mcnemar_exact([x["story_text_only"] for x in b], [y["story_text_only"] for y in f]),
            "names_protagonist": mcnemar_exact([x for x, _ in named], [y for _, y in named]),
            "complete_ending": mcnemar_exact([x["complete_ending"] for x in b], [y["complete_ending"] for y in f]),
            "words": wilcoxon([x["words"] for x in b], [y["words"] for y in f]),
            "distinct2": wilcoxon([x["distinct2"] for x in b], [y["distinct2"] for y in f]),
            "seconds": wilcoxon([s["base"]["wall_s"] for s in sub], [s["finetuned"]["wall_s"] for s in sub]),
        }
    (HERE / "generation_summary.json").write_text(json.dumps(out, indent=1))
    for kind, v in out["by_kind"].items():
        print("==", kind)
        for tag in ("base", "finetuned"):
            print("  ", tag, v[tag])
        print("   paired", {k: (round(x["p"], 4)) for k, x in out["paired"][kind].items()})


if __name__ == "__main__":
    main()
