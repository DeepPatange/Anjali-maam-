"""
Generation benchmark on held-out prompts: pretrained base vs. fine-tuned model.

Both models are run through Ollama with the application's own generation
settings (temperature 0.8, top-p 0.9, up to 1000 new tokens, 4096-token context)
on prompts built from held-out test stories: every story-opening prompt and the
first 20 continuation prompts. For each generation the text and the timings
reported by Ollama are stored.

Usage (with `ollama serve` running and nothing else using the GPU):
    finetune/.venv/bin/python finetune/generation_eval.py
Output: finetune/generation_eval.json
"""

import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS = {"base": "llama3.2:3b", "finetuned": "storyforge"}
OPTIONS = {"temperature": 0.8, "top_p": 0.9, "num_predict": 1000, "num_ctx": 4096}
N_CONTINUATION = 20


def chat(model, messages, seed):
    body = {"model": model, "messages": messages, "stream": False, "options": dict(OPTIONS, seed=seed)}
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    return {
        "text": d["message"]["content"],
        "wall_s": round(time.time() - t0, 2),
        "prompt_tokens": d.get("prompt_eval_count", 0),
        "prompt_s": round(d.get("prompt_eval_duration", 0) / 1e9, 3),
        "output_tokens": d["eval_count"],
        "output_s": round(d["eval_duration"] / 1e9, 3),
        "done_reason": d.get("done_reason"),
    }


def protagonist(user_prompt):
    m = re.search(r"\*\*Main Character:\*\* (.+)", user_prompt) or re.search(r"- Protagonist: (\S+)", user_prompt)
    name = m.group(1).strip() if m else None
    return None if name in (None, "the protagonist") else name


def main():
    rows = [json.loads(line) for line in open(HERE / "data" / "test.jsonl")]
    metas = [json.loads(line) for line in open(HERE / "data" / "test_meta.jsonl")]
    picked = [i for i, m in enumerate(metas) if m["kind"] == "init"]
    picked += [i for i, m in enumerate(metas) if m["kind"] == "continuation"][:N_CONTINUATION]

    results = {"options": OPTIONS, "models": MODELS, "samples": []}
    for i in picked:
        results["samples"].append({
            "index": i, "kind": metas[i]["kind"], "budget": metas[i]["budget"], "genre": metas[i]["genre"],
            "protagonist": protagonist(rows[i]["messages"][1]["content"]),
            "reference_words": len(rows[i]["messages"][2]["content"].split()),
        })

    for tag, model in MODELS.items():
        chat(model, [{"role": "user", "content": "Say ready."}], seed=0)      # load the model, not timed
        for n, sample in enumerate(results["samples"]):
            sample[tag] = chat(model, rows[sample["index"]]["messages"][:2], seed=1000 + sample["index"])
            print(f"{tag} {n + 1}/{len(results['samples'])} {sample['kind']:12} "
                  f"{sample[tag]['output_tokens']:4} tok {sample[tag]['wall_s']:6.1f}s", flush=True)
            (HERE / "generation_eval.json").write_text(json.dumps(results, indent=1))
    print("saved generation_eval.json")


if __name__ == "__main__":
    main()
