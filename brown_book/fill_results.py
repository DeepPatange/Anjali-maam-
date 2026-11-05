"""
Insert the measured values into the report.

The chapter sources contain placeholders of the form @@KEY@@. This script
replaces them with values read from finetune/eval_results.json and
finetune/generation_summary.json, so that every number in the text comes from
the measurement files. It fails if a placeholder cannot be resolved.

Usage (from the project root):  finetune/.venv/bin/python brown_book/fill_results.py
"""

import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FT = HERE.parent / "finetune"
ev = json.loads((FT / "eval_results.json").read_text())
gen = json.loads((FT / "generation_summary.json").read_text())


def pval(p):
    if p < 0.001:
        return "< 0.001"
    return f"= {p:.3f}" if p < 0.1 else f"= {p:.2f}"


def num(v, key):
    if key in ("samples", "n", "improved", "names_protagonist_n", "hit_token_limit",
               "words_median", "words_min", "words_max"):
        return f"{int(v):,}"
    if key == "story_tokens":
        return f"{int(v):,}"
    if key in ("loss", "mean_base", "mean_finetuned", "mean_difference", "distinct2_mean"):
        return f"{v:.3f}"
    if key in ("perplexity", "cohens_d", "paired_t"):
        return f"{v:.2f}"
    if key.endswith("_pct"):
        return f"{v:.0f}"
    if key in ("words_mean", "output_tokens_mean"):
        return f"{v:.0f}"
    if key in ("tokens_per_s_mean", "seconds_mean", "seconds_median", "seconds_max"):
        return f"{v:.1f}"
    return str(v)


def resolve(key):
    parts = key.split(":")
    head = parts[0]
    if head == "E":
        if parts[1] == "n_samples":
            return str(ev["test_samples"])
        if parts[1] == "n_stories":
            return str(ev["test_stories"])
        node = ev[parts[1]]
        if len(parts) == 4:                       # E:model:kind:field
            node = node["by_kind"][parts[2]]
        return num(node[parts[-1]], parts[-1])
    if head == "EP":                              # EP:sample|story:field
        node = ev["paired_by_" + parts[1]]
        field = parts[2]
        if field == "ci_lo":
            return f"{node['ci95_bootstrap'][0]:.3f}"
        if field == "ci_hi":
            return f"{node['ci95_bootstrap'][1]:.3f}"
        if field in ("paired_t_p", "wilcoxon_p"):
            return pval(node[field])
        return num(node[field], field)
    if head == "G":                               # G:n  or  G:kind:model:field
        if parts[1] == "n":
            return str(gen["n_prompts"])
        node = gen["by_kind"][parts[1]][parts[2]]
        if parts[3] == "words_range":
            return f"{node['words_min']}--{node['words_max']}"
        return num(node[parts[3]], parts[3])
    if head == "GP":                              # GP:kind:measure
        return pval(gen["paired"][parts[1]][parts[2]]["p"])
    if head == "X":
        b, f = ev["base"], ev["finetuned"]
        if parts[1] == "ppldrop":
            return f"{100 * (1 - f['perplexity'] / b['perplexity']):.0f}"
        if parts[1] == "lossdrop":
            return f"{100 * (1 - f['loss'] / b['loss']):.0f}"
    raise KeyError(key)


def main():
    left = 0
    for path in list((HERE / "chapters").glob("*.tex")) + list((HERE / "front_matter").glob("*.tex")):
        text = path.read_text()
        new = re.sub(r"@@((?:E|EP|G|GP|X):[^@]+)@@", lambda m: resolve(m.group(1)), text)
        if new != text:
            path.write_text(new)
            print("filled", path.name)
        left += len(re.findall(r"@@", new)) // 2
    if left:
        print(f"{left} placeholder(s) still open (hand-written parts)")
        sys.exit(1)


if __name__ == "__main__":
    main()
