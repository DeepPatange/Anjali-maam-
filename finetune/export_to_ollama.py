"""
Register the fine-tuned adapter with Ollama as the model `storyforge`.

The LoRA adapter trained by mlx_lm (finetune/adapters) is written as a GGUF
adapter file and layered on the pretrained base model through a Modelfile:

    FROM llama3.2:3b
    ADAPTER ./storyforge-lora.gguf

Two conversions are needed between the training layout and the GGUF layout:

  * mlx_lm stores lora_a as (in, r) and lora_b as (r, out) and applies
    W + scale * (lora_a @ lora_b)^T. GGUF expects lora_a as (r, in), lora_b as
    (out, r) and applies W + (alpha / r) * lora_b @ lora_a, so both matrices are
    transposed and alpha is set to scale * r.
  * GGUF Llama models keep the query and key projection rows in the original
    Meta order, while the Hugging Face / MLX weights use a permuted order. The
    same row permutation is therefore applied to lora_b of q_proj and k_proj.
    (Checked against the base weights: correlation 0.99 with the permutation,
    0.01 without.)

Usage (from the project root, with `ollama serve` running):
    finetune/.venv/bin/python finetune/export_to_ollama.py
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

import gguf
import mlx.core as mx
import numpy as np

HERE = Path(__file__).resolve().parent

# Llama 3.2 3B attention layout
N_HEAD, N_HEAD_KV = 24, 8
GGUF_NAME = {"q_proj": "attn_q", "k_proj": "attn_k", "v_proj": "attn_v", "o_proj": "attn_output"}


def permute_rows(w, n_head):
    """Row permutation used by llama.cpp when converting Hugging Face Llama weights."""
    return w.reshape(n_head, 2, w.shape[0] // n_head // 2, *w.shape[1:]).swapaxes(1, 2).reshape(w.shape)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter-dir", default=str(HERE / "adapters"))
    ap.add_argument("--adapter-file", default="adapters.safetensors",
                    help="file inside --adapter-dir (use a checkpoint name to export an earlier step)")
    ap.add_argument("--base", default="llama3.2:3b")
    ap.add_argument("--name", default="storyforge")
    ap.add_argument("--no-create", action="store_true", help="write the files but do not call ollama")
    args = ap.parse_args()

    src = Path(args.adapter_dir)
    cfg = json.loads((src / "adapter_config.json").read_text())
    rank = int(cfg["lora_parameters"]["rank"])
    scale = float(cfg["lora_parameters"]["scale"])
    alpha = scale * rank

    weights = mx.load(str(src / args.adapter_file))
    out_path = HERE / "storyforge-lora.gguf"
    writer = gguf.GGUFWriter(str(out_path), arch="llama")
    writer.add_type("adapter")
    writer.add_string("adapter.type", "lora")
    writer.add_float32("adapter.lora.alpha", alpha)
    writer.add_name("StoryForge LoRA (Llama 3.2 3B Instruct)")

    count = 0
    for key in sorted(k for k in weights if k.endswith(".lora_a")):
        m = re.fullmatch(r"model\.layers\.(\d+)\.self_attn\.(\w+)\.lora_a", key)
        if not m:
            raise ValueError(f"unexpected adapter tensor: {key}")
        layer, proj = int(m.group(1)), m.group(2)
        a = np.array(weights[key].astype(mx.float32)).T                                  # (r, in)
        b = np.array(weights[key[:-1] + "b"].astype(mx.float32)).T                       # (out, r)
        if proj == "q_proj":
            b = permute_rows(b, N_HEAD)
        elif proj == "k_proj":
            b = permute_rows(b, N_HEAD_KV)
        base = f"blk.{layer}.{GGUF_NAME[proj]}.weight"
        writer.add_tensor(base + ".lora_a", np.ascontiguousarray(a, dtype=np.float32))
        writer.add_tensor(base + ".lora_b", np.ascontiguousarray(b, dtype=np.float32))
        count += 1

    writer.write_header_to_file()
    writer.write_kv_data_to_file()
    writer.write_tensors_to_file()
    writer.close()
    print(f"wrote {out_path.name}: {count} adapted weight matrices, rank {rank}, alpha {alpha:g}")

    modelfile = HERE / "Modelfile"
    modelfile.write_text(
        f"# Fine-tuned story model: {args.base} + LoRA adapter trained on the Q&A-to-story dataset\n"
        f"FROM {args.base}\n"
        f"ADAPTER ./{out_path.name}\n"
        f"PARAMETER temperature 0.8\n"
        f"PARAMETER top_p 0.9\n"
        f"PARAMETER num_ctx 4096\n"
    )
    print(f"wrote {modelfile.name}")

    if not args.no_create:
        subprocess.run(["ollama", "create", args.name, "-f", "Modelfile"], check=True, cwd=HERE)
        print(f"created Ollama model '{args.name}'")


if __name__ == "__main__":
    main()
