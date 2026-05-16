# 🌏 Cultural & Linguistic Intelligence Eval

**Do LLMs actually understand Asian cultures — or do they just understand English descriptions of them?**

This benchmark tests 12 frontier LLMs on 20 culturally nuanced questions spanning 9 Asian cultures, asked twice each: once in English, once in the native language. The core metric is **cross-lingual drift** — how much a model's cultural understanding degrades when you stop speaking English.

**[→ View Live Dashboard](https://YOUR-STREAMLIT-APP-URL)**

---

> **Built by Shang Jing Chia · BUSGEN 116 · Stanford University**  
> First published: May 2026

---

## Key Findings

| | Finding |
|---|---|
| 🥇 | **Claude Sonnet 4.6** tops the leaderboard (4.68 / 5.0) — the only model with a 0% trap fall rate |
| 🐋 | **Doubao Seed 2.0** (ByteDance) ranks #2 (4.60 / 5.0), beating both DeepSeek models and every non-Anthropic Western model tested — yet largely unknown in Western AI discourse |
| 📉 | **Every model scores higher in English** than in the native language. Llama 3.1 70B shows the worst collapse (+0.92 drift) |
| 🔇 | **Low-resource languages (Burmese, Khmer, Mongolian)** expose a hard capability cliff — not a gradual slope — across nearly all models |
| 🔒 | **Chinese-origin models show three distinct political sensitivity patterns** absent in all Western models: silent timeouts on Korean/Mongolian identity questions (Doubao), narrative capture on Chinese history in Chinese (DeepSeek R1), and near-total collapse on Burmese (DeepSeek R1: 1.65 / 5.0) |
| 🧭 | **Epistemic calibration** is the weakest dimension across all 12 models — they answer confidently and fluently but rarely hedge appropriately |

---

## What This Measures

Each response is scored on four dimensions (1–5 scale) by Claude Opus acting as judge:

| Dimension | What it captures |
|-----------|-----------------|
| **Cultural Accuracy** | Factual and cultural correctness; whether the model avoided the known trap embedded in each question |
| **Depth & Nuance** | Goes beyond surface stereotypes; demonstrates genuine cultural understanding |
| **Epistemic Calibration** | Confident where warranted, appropriately humble where contested |
| **Language Quality** | Fluency and cultural idiomaticity — penalises "translated-feeling" native-language responses |

**Cross-lingual drift** = `avg(English score) − avg(native language score)` per question, then averaged.  
A positive drift means the model performs better in English. A larger gap reveals reliance on English as a scaffold for cultural knowledge.

---

## Models Evaluated (12)

| Company | Models |
|---------|--------|
| **Anthropic** | Claude Sonnet 4.6, Claude Sonnet 4.5 |
| **OpenAI** | GPT-4.1, GPT-4o |
| **Google** | Gemini 2.5 Flash |
| **ByteDance** | Doubao Seed 2.0 |
| **DeepSeek** | DeepSeek R1, DeepSeek V3-0324 |
| **Alibaba** | Qwen 2.5 72B |
| **Mistral** | Mistral Large |
| **Meta** | Llama 3.3 70B, Llama 3.1 70B |

All models queried via **OpenRouter** at uniform settings (temperature 0.3, 800 max tokens).

---

## 9 Cultures · 3 Language Tiers

| Tier | Cultures | Why it matters |
|------|----------|---------------|
| **High-resource** | Chinese (ZH), Japanese (JA), Korean (KO) | Large web corpora; models trained on abundant text |
| **Mid-resource** | Thai (TH), Vietnamese (VI), Indonesian (ID) | Growing digital presence; moderate training coverage |
| **Low-resource** | Burmese (MY), Khmer (KM), Mongolian (MN) | Underrepresented in most pretraining data; exposes the hard floor |

Each question was designed with a **known trap** — the specific Western-centric mistake a poorly-calibrated model is likely to make. The judge scores whether the model fell into it.

---

## Pipeline

```
questions.json
    ↓
run_eval.py  →  results/raw_responses.json   (~480 API calls, async, resumable)
    ↓
judge.py     →  results/scores.json          (Claude Opus scores each response)
    ↓
leaderboard.py → results/leaderboard.json   (aggregation, drift, trap rates)
    ↓
app.py       →  Streamlit dashboard
```

### Reproduce it

```bash
pip install -r requirements.txt

# Add your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env

# Step 1 — collect model responses (~$8–18, ~480 API calls)
python run_eval.py

# Step 2 — judge each response with Claude Opus (~$10–18)
python judge.py

# Step 3 — aggregate into leaderboard
python leaderboard.py

# Step 4 — launch the dashboard
streamlit run app.py
```

Every step is **resumable** — re-running skips already-completed calls. You can stop and restart at any point.

### Secondary outputs

```bash
python report.py      # results/report.md      — portable markdown summary
python visualize.py   # results/leaderboard.html — self-contained static HTML (no server needed)
```

### Cost estimate

| Step | API calls | Estimated cost |
|------|-----------|---------------|
| `run_eval.py` | ~480 | ~$8–18 |
| `judge.py` | ~480 | ~$10–18 |
| **Total** | | **~$18–36** |

---

## Repo Structure

```
eval/
├── questions.json        # 20 evaluation questions with expected themes and traps
├── run_eval.py           # Step 1 — async model elicitation via OpenRouter
├── judge.py              # Step 2 — LLM-as-judge scoring with Claude Opus
├── leaderboard.py        # Step 3 — aggregation, drift and trap rate calculation
├── report.py             # Step 4a — markdown report generation
├── visualize.py          # Step 4b — static HTML dashboard
├── app.py                # Streamlit interactive dashboard
├── requirements.txt      # Python dependencies
├── .env                  # API key (not committed)
└── results/
    ├── raw_responses.json
    ├── scores.json
    ├── leaderboard.json
    ├── report.md
    └── leaderboard.html
```

---

## About

This project was designed and executed end-to-end for **BUSGEN 116** at **Stanford University** — from question authorship and evaluation design through async model elicitation, LLM-as-judge scoring, statistical aggregation, and interactive dashboard.

**Shang Jing Chia** · Stanford University  
[GitHub](https://github.com/shangjingchia/busgen116-cultural-intelligence-eval)

---

*Methodology, scoring rubric, limitations, and the full question bank are documented in the [live dashboard](https://YOUR-STREAMLIT-APP-URL) under the Methodology tab.*
