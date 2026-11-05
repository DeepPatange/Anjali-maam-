"""
Held-out evaluation: pretrained base model vs. fine-tuned model.

For every sample of finetune/data/test.jsonl the cross-entropy loss of the story
text is computed (prompt tokens masked, as in training) with the base model and
with the base model plus the LoRA adapter. The script reports

  * token-weighted loss and perplexity per prompt type and overall, and
  * paired comparisons of the two models: per sample, and per story (the
    samples of one story are averaged first, because they are not independent).

Usage:  finetune/.venv/bin/python finetune/evaluate.py
Output: finetune/eval_results.json
"""

import json
import math
import random
from collections import defaultdict
from pathlib import Path

from mlx_lm import load
from mlx_lm.tuner.datasets import CacheDataset, ChatDataset
from mlx_lm.tuner.trainer import evaluate
from scipy import stats

HERE = Path(__file__).resolve().parent
BASE = "mlx-community/Llama-3.2-3B-Instruct-4bit"
MAX_SEQ = 1344
KINDS = ["init", "continuation", "climax", "resolution"]


def per_sample_losses(model, tokenizer, rows):
    chat = ChatDataset(rows, tokenizer, mask_prompt=True)
    losses, tokens = [], []
    for i in range(len(chat)):
        toks, offset = chat.process(chat[i])
        one = CacheDataset(ChatDataset([rows[i]], tokenizer, mask_prompt=True))
        losses.append(float(evaluate(model=model, dataset=one, batch_size=1, num_batches=-1,
                                     max_seq_length=MAX_SEQ)))
        tokens.append(min(len(toks), MAX_SEQ) - offset)
        if (i + 1) % 20 == 0:
            print(f"   {i + 1}/{len(chat)}", flush=True)
    return losses, tokens


def weighted(losses, tokens, idx):
    total = sum(tokens[i] for i in idx)
    loss = sum(losses[i] * tokens[i] for i in idx) / total
    return {"samples": len(idx), "story_tokens": total, "loss": round(loss, 4),
            "perplexity": round(math.exp(loss), 3)}


def paired(base, tuned, seed=7):
    """Paired comparison of two lists of losses (base minus fine-tuned)."""
    diff = [b - t for b, t in zip(base, tuned)]
    n = len(diff)
    mean = sum(diff) / n
    rng = random.Random(seed)
    boots = sorted(sum(rng.choices(diff, k=n)) / n for _ in range(10000))
    t = stats.ttest_rel(base, tuned)
    w = stats.wilcoxon(base, tuned)
    sd = (sum((d - mean) ** 2 for d in diff) / (n - 1)) ** 0.5
    return {
        "n": n,
        "mean_base": round(sum(base) / n, 4),
        "mean_finetuned": round(sum(tuned) / n, 4),
        "mean_difference": round(mean, 4),
        "ci95_bootstrap": [round(boots[249], 4), round(boots[9749], 4)],
        "improved": sum(d > 0 for d in diff),
        "cohens_d": round(mean / sd, 3),
        "paired_t": round(float(t.statistic), 3),
        "paired_t_p": float(t.pvalue),
        "wilcoxon_p": float(w.pvalue),
    }


def main():
    rows = [json.loads(line) for line in open(HERE / "data" / "test.jsonl")]
    metas = [json.loads(line) for line in open(HERE / "data" / "test_meta.jsonl")]
    results = {"test_stories": len({m["story_id"] for m in metas}), "test_samples": len(rows)}

    per = {}
    for tag, adapter in (("base", None), ("finetuned", str(HERE / "adapters"))):
        print(f"== {tag}", flush=True)
        model, tokenizer = load(BASE, adapter_path=adapter)
        losses, tokens = per_sample_losses(model, tokenizer, rows)
        per[tag] = losses
        by_kind = {k: weighted(losses, tokens, [i for i, m in enumerate(metas) if m["kind"] == k]) for k in KINDS}
        results[tag] = dict(weighted(losses, tokens, list(range(len(rows)))), by_kind=by_kind)
        print(f"   overall loss {results[tag]['loss']}  perplexity {results[tag]['perplexity']}", flush=True)
        del model

    results["paired_by_sample"] = paired(per["base"], per["finetuned"])
    stories = defaultdict(lambda: ([], []))
    for i, m in enumerate(metas):
        stories[m["story_id"]][0].append(per["base"][i])
        stories[m["story_id"]][1].append(per["finetuned"][i])
    results["paired_by_story"] = paired([sum(b) / len(b) for b, _ in stories.values()],
                                        [sum(t) / len(t) for _, t in stories.values()])
    results["per_sample"] = [
        {"story_id": m["story_id"], "kind": m["kind"], "budget": m["budget"],
         "base": round(per["base"][i], 4), "finetuned": round(per["finetuned"][i], 4)}
        for i, m in enumerate(metas)
    ]
    (HERE / "eval_results.json").write_text(json.dumps(results, indent=1))
    print("paired by sample:", results["paired_by_sample"])
    print("paired by story:", results["paired_by_story"])
    print("saved eval_results.json")


if __name__ == "__main__":
    main()
