# StoryForge: the fine-tuned story model

The application's own language model. It is Llama 3.2 3B Instruct (open weights)
fine-tuned with LoRA on a Q&A-to-story dataset, and it runs locally through
Ollama under the name `storyforge`. No external API is used for story text.

## What was done

| Stage | Detail |
|---|---|
| Base model | Llama 3.2 3B Instruct, 4-bit quantised (3.2 billion parameters) |
| Method | QLoRA: rank 16, alpha 32, dropout 0.05, on the query, key, value and output projections of the top 8 of 28 transformer blocks |
| Trainable parameters | 2.62 million (0.082% of the model) |
| Dataset source | "Thousand Stories, Hundred Genres" (`FareedKhan/1k_stories_100_genre`, CC-BY-2.0): 1,000 stories, 99 genres |
| Training samples | 3,321 from 900 stories (893 openings, 1,122 continuations, 501 climaxes, 805 resolutions) |
| Validation / test | 183 samples from 50 stories / 191 samples from 49 stories, held out by story |
| Training | 600 steps, batch size 1, gradient accumulation 2, Adam, learning rate 1e-4, loss on the story text only |
| Hardware and time | Apple M2, 8 GB RAM; about 1 hour |

Each training sample uses the exact prompts the application sends at run time.
A story is labelled with answers to the application's 17 questions by keyword
rules, a question budget (4, 8, 12 or 17) is sampled, and the answers are passed
through the application's `ContextExtractionEngine` and `PromptEngineeringLayer`.
The story is cut into an opening and follow-up segments, which become the targets
of the init, continuation, climax and resolution prompts.

## Results

Loss on the story text (lower is better). Validation during training:

| Step | 0 | 150 | 300 | 450 | 600 |
|---|---|---|---|---|---|
| Validation loss | 1.476 | 1.207 | 1.164 | 1.151 | 1.107 |

Held-out test set, pretrained base against fine-tuned (`eval_results.json`):

| Prompt type | Samples | Base loss | Fine-tuned loss |
|---|---|---|---|
| Opening (init) | 49 | 1.705 | 1.370 |
| Continuation | 71 | 1.464 | 1.151 |
| Climax | 25 | 1.534 | 1.174 |
| Resolution | 46 | 1.377 | 1.052 |
| **Overall** | **191** | **1.521** (perplexity 4.58) | **1.194** (perplexity 3.30) |

The fine-tuned model has the lower loss on all 191 test samples and all 49 test
stories (paired tests, p < 0.001). Perplexity measures how well the model predicts
held-out stories written in the dataset's style. It is not a human rating of story
quality.

Generated text for 69 held-out prompts (49 openings, 20 continuations), both models
run through Ollama with the application's settings (`generation_summary.json`):

| Measure | Pretrained | Fine-tuned |
|---|---|---|
| Story text only (no added title or comment) | 75% | 100% |
| Length within 25% of the requested range | 100% | 90% |
| Words per segment, mean | 344 | 275 |
| Names the protagonist (60 prompts) | 97% | 88% (not significant) |
| Ends in a complete sentence | 99% | 99% |
| Tokens per second | 38.0 | 37.3 |
| Seconds per segment, mean | 12.9 | 10.2 |

The result is mixed. Fine-tuning removes the titles the pretrained model adds, at
the same speed, but the fine-tuned model writes shorter segments than the prompt
asks for, because the training targets average 292 words for openings and about
255 for the other prompt types.

In the application on the same Mac a full turn, with the request for four
choices, took 22 to 28 seconds.

## Reproduce

Run from the project root. Needs an Apple-silicon Mac, Python 3.10+ and Ollama.

```bash
python3 -m venv finetune/.venv
finetune/.venv/bin/pip install mlx-lm gguf scipy pydantic httpx

finetune/.venv/bin/python finetune/build_dataset.py                    # data/*.jsonl
finetune/.venv/bin/python -m mlx_lm lora -c finetune/lora_config.yaml  # adapters/
finetune/.venv/bin/python finetune/evaluate.py                         # eval_results.json

ollama serve &                                                         # if not already running
ollama pull llama3.2:3b
finetune/.venv/bin/python finetune/export_to_ollama.py                 # creates `storyforge`
finetune/.venv/bin/python finetune/generation_eval.py                  # generation_eval.json
finetune/.venv/bin/python finetune/analyze_generation.py               # generation_summary.json
```

Then set `LLM_PROVIDER=ollama` and `OLLAMA_MODEL=storyforge` in `.env`, or pick
"Llama 3.2 – fine-tuned for storytelling" in the application's settings panel.

To install the model on another machine without retraining, copy
`storyforge-lora.gguf` and `Modelfile`, run `ollama pull llama3.2:3b`, then
`ollama create storyforge -f Modelfile` in that folder.

## Files

| File | Purpose |
|---|---|
| `build_dataset.py` | Builds the training, validation and test sets |
| `lora_config.yaml` | Training configuration |
| `adapters/` | Trained LoRA adapter and its configuration |
| `training_curve.csv`, `train_log.txt` | Loss during training |
| `evaluate.py`, `eval_results.json` | Held-out loss of base and fine-tuned model, with paired tests |
| `generation_eval.py`, `analyze_generation.py` | Generation benchmark and its summary |
| `export_to_ollama.py` | Writes `storyforge-lora.gguf` and `Modelfile`, registers the model with Ollama |
