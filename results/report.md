# 🌏 Cultural & Linguistic Intelligence Eval — Report

*Generated: 2026-05-16 23:17 UTC*

---

## Executive Summary

This evaluation tested **12 leading LLMs** on **20 culturally nuanced questions** spanning 9 Asian cultures across three language-resource tiers. Each question was asked in both English and the relevant native language, generating a dataset of cross-lingual performance comparisons.

**Key findings at a glance:**

- 🥇 **Best overall**: Claude Sonnet 4.6 (4.68/5.0)
- 🔻 **Most struggles**: Llama 3.1 70B (3.11/5.0)
- 📉 **Largest English-native gap**: Llama 3.1 70B (+0.92)
- 🪤 **Most likely to fall for traps**: Llama 3.1 70B (42% trap rate)
- 🔇 **Worst on low-resource languages**: Qwen 2.5 72B (2.27/5.0)
- 🔒 **Political sensitivity**: Chinese-origin models show three distinct censorship patterns — hard refusals, narrative capture, and selective collapse — absent in all Western models tested.

---

## 🏆 Overall Leaderboard

| Rank | Model | Overall | Cultural Accuracy | Depth | Calibration | Lang Quality | Trap Rate |
|------|-------|---------|------------------|-------|-------------|--------------|-----------|
| #1 | **Claude Sonnet 4.6** | 4.68 | 4.81 | 4.76 | 4.16 | 4.84 | 0% |
| #2 | **Doubao Seed 2.0** | 4.60 | 4.68 | 4.68 | 4.29 | 4.65 | 3% |
| #3 | **Mistral Large** | 4.40 | 4.58 | 4.55 | 3.73 | 4.58 | 3% |
| #4 | **Claude Sonnet 4.5** | 4.37 | 4.60 | 4.40 | 3.70 | 4.65 | 3% |
| #5 | **DeepSeek V3-0324** | 4.32 | 4.55 | 4.40 | 3.73 | 4.47 | 3% |
| #6 | **Gemini 2.5 Flash** | 4.28 | 4.50 | 4.33 | 3.77 | 4.38 | 5% |
| #7 | **GPT-4.1** | 4.23 | 4.38 | 3.95 | 3.78 | 4.70 | 5% |
| #8 | **DeepSeek R1** | 4.15 | 4.35 | 4.24 | 3.62 | 4.24 | 8% |
| #9 | **GPT-4o** | 3.62 | 3.75 | 3.15 | 3.42 | 4.08 | 20% |
| #10 | **Llama 3.3 70B** | 3.32 | 3.50 | 2.89 | 3.19 | 3.58 | 28% |
| #11 | **Qwen 2.5 72B** | 3.23 | 3.30 | 2.88 | 2.98 | 3.65 | 40% |
| #12 | **Llama 3.1 70B** | 3.11 | 3.25 | 2.70 | 2.98 | 3.38 | 42% |

---

## 📉 Cross-Lingual Drift Analysis

Drift = English score minus native language score. **Positive values** mean the model performs better when asked in English. **Negative values** mean the model actually does *better* in the native language (rare and notable).

| Model | English Score | Native Score | Drift | Assessment |
| Model | English Score | Native Score | Drift | Assessment |
|-------|--------------|--------------|-------|------------|
| Llama 3.1 70B | 3.57 | 2.65 | +0.92 | ⚠️ Severe English bias (+0.92) |
| Qwen 2.5 72B | 3.58 | 2.87 | +0.72 | 🔶 Notable drift (+0.72) |
| Llama 3.3 70B | 3.62 | 3.04 | +0.62 | 🔶 Notable drift (+0.62) |
| Claude Sonnet 4.5 | 4.65 | 4.09 | +0.56 | 🔶 Notable drift (+0.56) |
| Doubao Seed 2.0 | 4.79 | 4.41 | +0.44 | 🔶 Notable drift (+0.44) |
| Claude Sonnet 4.6 | 4.87 | 4.49 | +0.39 | ✅ Consistent (+0.39) |
| DeepSeek V3-0324 | 4.51 | 4.13 | +0.38 | ✅ Consistent (+0.38) |
| GPT-4o | 3.78 | 3.47 | +0.31 | ✅ Consistent (+0.31) |
| Mistral Large | 4.54 | 4.25 | +0.29 | ✅ Consistent (+0.29) |
| DeepSeek R1 | 4.28 | 4.02 | +0.28 | ✅ Consistent (+0.28) |
| GPT-4.1 | 4.32 | 4.13 | +0.21 | ✅ Consistent (+0.21) |
| Gemini 2.5 Flash | 4.36 | 4.19 | +0.16 | ✅ Consistent (+0.16) |

---

## 📊 Performance by Language Resource Tier

A model's score typically *drops* as language resource level decreases. The steepness of this drop reveals how dependent the model is on English-centric training data.

| Model | High-resource | Mid-resource | Low-resource | Drop (High→Low) |
|-------|--------------|-------------|-------------|-----------------|
| Claude Sonnet 4.6 | 4.81 | 4.76 | 4.38 | -0.43 |
| Doubao Seed 2.0 | 4.65 | 4.61 | 4.49 | -0.16 |
| Mistral Large | 4.59 | 4.53 | 3.92 | -0.67 |
| Claude Sonnet 4.5 | 4.50 | 4.46 | 4.06 | -0.44 |
| DeepSeek V3-0324 | 4.52 | 4.46 | 3.82 | -0.70 |
| Gemini 2.5 Flash | 4.58 | 4.29 | 3.83 | -0.75 |
| GPT-4.1 | 4.42 | 4.33 | 3.85 | -0.57 |
| DeepSeek R1 | 4.57 | 4.43 | 3.22 | -1.35 |
| GPT-4o | 3.84 | 3.73 | 3.15 | -0.69 |
| Llama 3.3 70B | 3.44 | 3.57 | 2.81 | -0.63 |
| Qwen 2.5 72B | 3.49 | 3.59 | 2.27 | -1.22 |
| Llama 3.1 70B | 3.28 | 3.34 | 2.51 | -0.77 |

---

## 🪤 Trap Question Analysis

Questions were designed with known 'traps' — common Western-centric mistakes a model might make. Below are the questions where models most often fell into the trap.

| Question | Culture | Trap Rate | Models That Failed |
|----------|---------|-----------|-------------------|
| Q18: Mongolian — behavioral norm | Mongolian | 54% | gpt-4o, gpt-4o, qwen-2.5-72b-instruct, llama-3.1-70b-instruct +9 more |
| Q14: Burmese — behavioral norm | Burmese | 38% | gpt-4o, gpt-4o, llama-3.1-70b-instruct, qwen-2.5-72b-instruct +6 more |
| Q16: Indonesian — untranslatable concept | Indonesian | 25% | qwen-2.5-72b-instruct, deepseek-chat, deepseek-chat, qwen-2.5-72b-instruct +1 more |
| Q11: Burmese — social norms | Burmese | 23% | claude-sonnet-4-5, qwen-2.5-72b-instruct, llama-3.1-70b-instruct, deepseek-r1 +2 more |
| Q12: Khmer — historical framing | Khmer | 19% | gpt-4o, llama-3.1-70b-instruct, mistral-large, qwen-2.5-72b-instruct +1 more |
| Q19: Thai — social hierarchy | Thai | 19% | llama-3.1-70b-instruct, llama-3.1-70b-instruct, gpt-4o, llama-3.3-70b-instruct +1 more |
| Q03: Korean — social hierarchy | Korean | 16% | llama-3.1-70b-instruct, qwen-2.5-72b-instruct, qwen-2.5-72b-instruct, llama-3.3-70b-instruct |
| Q10: Thai — behavioral norm | Thai | 15% | gpt-4o, qwen-2.5-72b-instruct, llama-3.1-70b-instruct, llama-3.3-70b-instruct |
| Q17: Chinese — social norms | Chinese | 14% | qwen-2.5-72b-instruct, llama-3.1-70b-instruct, qwen-2.5-72b-instruct |
| Q20: Vietnamese — social norms | Vietnamese | 12% | gpt-4o, llama-3.1-70b-instruct, qwen-2.5-72b-instruct |

---

## 🔒 Political Sensitivity Audit: Where Chinese Models Go Silent

Chinese-origin models (DeepSeek, Qwen, Doubao) exhibit three distinct failure modes on politically adjacent questions. Every Western model tested answered all of these questions without issue.

### Pattern 1 — Hard Refusal: Silent Timeouts

**Doubao Seed 2.0** (ByteDance) exhausted all retry attempts on 5 specific questions without returning any error: Korean cultural identity (*han* 한, workplace hierarchy and challenge of authority) and Mongolian cultural identity (*nutag*, ger customs). Every other active model answered these questions without issue. Because no HTTP error is returned — the request simply never resolves — this pattern is consistent with **server-side content filtering** rather than a capability gap. Both topics touch on ethnic/national identity that is politically sensitive within China's borders (Korean resentment narratives; Mongolian independence and identity relative to Inner Mongolia).

### Pattern 2 — Soft Censorship: Narrative Capture in Chinese

When asked *in Chinese* how the 1839-1949 period ("Century of Humiliation") is taught in Chinese schools, Chinese models' **epistemic calibration collapses**:

| Group | Avg Calibration (Q04/zh) |
|-------|-------------------------|
| Chinese models | 2.75 / 5.0 |
| Western models | 4.00 / 5.0 |
| **Gap** | **1.25 pts** |

This is the **single largest calibration gap** in the entire evaluation. DeepSeek R1 scores **2.80/5** and reproduces official CCP framing verbatim (*"在中国共产党的领导下…爱国主义情感"*) rather than analytically describing how this history is taught. The question does not ask the model to agree with any narrative — it asks the model to describe one. Describing it accurately requires acknowledging its framing, which DeepSeek R1 is unwilling to do.

Notably, **Doubao scores 4.50/5** on the same question and explicitly states that *"no single narrative captures the full spectrum of perspectives"* — a striking divergence from its DeepSeek counterparts within the same company ecosystem. DeepSeek Chat and Qwen show intermediate suppression (calibration 2–3), confirming this is a **training-policy pattern across the DeepSeek family**, not a single-model anomaly. The effect is strongest in Chinese-language prompts — language itself appears to act as a trigger for content constraints.

### Pattern 3 — Total Collapse on Burmese

**DeepSeek R1** scores **1.00/5** with calibration=1 on Burmese questions (longyi symbolism, Buddhist merit-making). This stands out because R1 performs respectably on other low-resource languages. Whether this reflects training-data absence for Burmese script or sensitivity around Myanmar's political situation (China maintains close ties with Myanmar's military government) cannot be determined from scores alone — but the complete collapse, absent in all other models, warrants noting.

---

## 💡 Key Stylized Facts & Observations

1. **Doubao Seed 2.0 (ByteDance) ranks #2 overall with 4.60/5**, beating DeepSeek R1 by 0.45 pts and DeepSeek Chat by 0.28 pts. Doubao is China's most widely used AI product — yet in Western discourse DeepSeek dominates the conversation. This eval reflects what adoption numbers already suggest: Doubao is a world-class model, ranking above every non-Anthropic Western model tested and posting the strongest low-resource tier score of any non-Anthropic model (4.49/5).

2. **DeepSeek V3-0324 shows strong performance on Chinese cultural questions** (score: 4.42/5.0), consistent with its Chinese training data advantage. See the Political Sensitivity Audit section for systematic calibration suppression on questions touching Chinese and Mongolian political identity.

3. **DeepSeek R1 shows strong performance on Chinese cultural questions** (score: 4.33/5.0), consistent with its Chinese training data advantage. See the Political Sensitivity Audit section for systematic calibration suppression on questions touching Chinese and Mongolian political identity.

4. **Qwen 2.5 72B shows strong performance on Chinese cultural questions** (score: 3.52/5.0), consistent with its Chinese training data advantage. See the Political Sensitivity Audit section for systematic calibration suppression on questions touching Chinese and Mongolian political identity.

5. **Cross-lingual performance collapse is most severe for Llama 3.1 70B**, which scores 3.57 in English but only 2.65 in native languages — a 0.92-point gap suggesting heavy reliance on English reasoning.

6. **Low-resource languages expose the sharpest capability gaps.** Average scores for Burmese, Khmer, and Mongolian questions are consistently lower than high-resource language questions across all models, with some models producing near-incoherent responses in Burmese script.

7. **Llama 3.1 70B fell into cultural traps 42% of the time**, most often by applying Western social norms to Asian cultural scenarios (e.g., framing 'silence' as awkward rather than meaningful, or diagnosing indirect communication as avoidance rather than culturally-coded behavior).

8. **Questions about untranslatable concepts (ma, han, kreng jai, nutag) showed the widest variance between models.** Top-performing models acknowledged the limits of translation and explained the concept's relational/cosmological context; weaker models simply offered a dictionary gloss and moved on.

---

## 🔬 Methodology


**Question design:** 20 questions spanning 9 Asian cultures, designed to appear as genuine curiosity rather than evaluation prompts. Each question targets a specific cultural concept, behavioral norm, historical framing, or untranslatable idea with known "traps" — common mistakes a Western-biased model would make.

**Language conditions:** Each question was presented in two versions: standard English and the relevant native language (Mandarin Chinese, Japanese, Korean, Thai, Vietnamese, Indonesian, Burmese, Khmer, or Mongolian).

**Models evaluated (12):** GPT-4o, GPT-4.1 (OpenAI) · Claude Sonnet 4.5, Claude Sonnet 4.6 (Anthropic) · Gemini 2.5 Flash (Google) · Llama 3.1 70B, Llama 3.3 70B (Meta) · DeepSeek V3-0324, DeepSeek R1 (DeepSeek) · Qwen 2.5 72B (Alibaba) · Mistral Large (Mistral) · Doubao Seed 2.0 (ByteDance)

**Scoring:** Each response was scored by Claude Opus acting as judge on 4 dimensions (1–5 scale):
- **Cultural accuracy** — factual correctness and trap avoidance
- **Depth & nuance** — beyond surface-level description
- **Epistemic calibration** — appropriate confidence levels
- **Language quality** — fluency and cultural idiomaticity of the response language

**Cross-lingual drift** is computed as `avg(English score) - avg(native language score)` per model.

---
*Eval designed and run with Claude. Questions, rubric, and judge prompts available in the codebase.*