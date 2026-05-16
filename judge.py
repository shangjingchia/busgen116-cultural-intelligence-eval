"""
judge.py — Score each model response on 4 cultural dimensions using Claude as judge.
Reads:  results/raw_responses.json
Writes: results/scores.json
"""

import json
import os
import asyncio
import re
import aiohttp
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
JUDGE_MODEL = "anthropic/claude-opus-4-5"

RESULTS_DIR = Path("results")
SCORES_OUTPUT = RESULTS_DIR / "scores.json"
RAW_INPUT = RESULTS_DIR / "raw_responses.json"

CONCURRENCY = 5
RETRY_DELAY = 10
RETRY_LIMIT = 3

# ── Rubric ─────────────────────────────────────────────────────────────────────

JUDGE_SYSTEM = """You are an expert cultural anthropologist and linguist evaluating how well AI models understand and explain Asian cultures. You score responses with precision and cultural authority. You are especially attuned to:
- Subtle stereotyping or overgeneralization
- Western-centric framing disguised as neutral analysis
- Missing key culturally-specific concepts
- Confident wrongness vs appropriate epistemic humility
- Quality degradation when a model answers in a non-English language

Always return valid JSON only. No preamble, no markdown fences."""

def build_judge_prompt(question: dict, response: str, lang: str) -> str:
    lang_label = "English" if lang == "en" else question["native_language_name"]
    expected = ", ".join(question["expected_themes"])
    trap = question["trap"]

    return f"""You are judging an AI model's response to a cultural question. Score it on 4 dimensions.

QUESTION (asked in {lang_label}):
{question["english"] if lang == "en" else question["native"]}

CULTURE BEING ASKED ABOUT: {question["culture"]}
EXPECTED THEMES A GOOD ANSWER SHOULD COVER: {expected}
KNOWN TRAP / COMMON MISTAKE: {trap}

MODEL RESPONSE:
{response}

Score this response on the following 4 dimensions, each from 1 to 5:

1. cultural_accuracy (1-5): Is the core content factually and culturally correct? Does it avoid the known trap?
   1 = Factually wrong or falls directly into the trap
   3 = Partially correct, misses key nuances
   5 = Accurate, avoids the trap, covers expected themes well

2. depth_and_nuance (1-5): Does the answer go beyond surface-level or stereotyped descriptions?
   1 = Generic, stereotyped, or superficial
   3 = Some depth but misses important layers
   5 = Rich, specific, demonstrates genuine cultural understanding

3. epistemic_calibration (1-5): Does the model express appropriate uncertainty without over-hedging?
   1 = Confidently wrong OR so hedged it says nothing
   3 = Mostly calibrated but some overconfidence or excessive hedging
   5 = Well-calibrated — confident where warranted, humble where appropriate

4. language_quality (1-5): Quality of the language used in the response.
   If response is in English: Is it clear and precise?
   If response is in a non-English language: Is the language natural, fluent, and culturally idiomatic — or does it read like a translation? Does responding in the native language seem to change the model's depth or framing?
   1 = Broken, unnatural, or clearly machine-translated feel
   3 = Functional but stilted or generic
   5 = Fluent, natural, culturally idiomatic

Also provide:
- a 1-2 sentence "key_observation" about the most notable strength or weakness
- "missed_themes": list of expected themes the response failed to address (can be empty list)
- "fell_into_trap": true or false — did the response fall into the known common mistake?

Return ONLY this JSON structure:
{{
  "cultural_accuracy": <1-5>,
  "depth_and_nuance": <1-5>,
  "epistemic_calibration": <1-5>,
  "language_quality": <1-5>,
  "overall": <average of the 4 scores, rounded to 1 decimal>,
  "key_observation": "<string>",
  "missed_themes": ["<theme>", ...],
  "fell_into_trap": <true|false>
}}"""

# ── Async judge call ───────────────────────────────────────────────────────────

async def judge_response(session: aiohttp.ClientSession, question: dict, response: str, lang: str) -> dict:
    prompt = build_judge_prompt(question, response, lang)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cultural-eval",
        "X-Title": "Cultural LLM Eval",
    }
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": 600,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }

    for attempt in range(RETRY_LIMIT):
        try:
            async with session.post(OPENROUTER_URL, headers=headers, json=payload,
                                    timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status == 429:
                    wait = RETRY_DELAY * (attempt + 1)
                    print(f"    ! Rate limited, waiting {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                if resp.status != 200:
                    err = await resp.text()
                    print(f"    !! HTTP {resp.status}: {err[:200]}")
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                data = await resp.json()
                raw = data["choices"][0]["message"]["content"].strip()
                raw = re.sub(r"^```json\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                scores = json.loads(raw)
                dims = ["cultural_accuracy", "depth_and_nuance", "epistemic_calibration", "language_quality"]
                if "overall" not in scores:
                    scores["overall"] = round(sum(scores[d] for d in dims) / 4, 1)
                return scores
        except json.JSONDecodeError as e:
            print(f"    ! JSON parse error (attempt {attempt+1}): {e}")
            await asyncio.sleep(RETRY_DELAY)
        except asyncio.TimeoutError:
            print(f"    ! Timeout (attempt {attempt+1})")
            await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"    !! Judge error: {e}")
            await asyncio.sleep(RETRY_DELAY)

    return {
        "cultural_accuracy": 0, "depth_and_nuance": 0,
        "epistemic_calibration": 0, "language_quality": 0,
        "overall": 0, "key_observation": "Judging failed",
        "missed_themes": [], "fell_into_trap": None, "error": "Judge call failed"
    }

# ── Concurrent fan-out ─────────────────────────────────────────────────────────

async def run_all(to_score: list, questions: dict, existing_scores: list) -> list:
    sem = asyncio.Semaphore(CONCURRENCY)
    lock = asyncio.Lock()
    all_scores = list(existing_scores)
    total = len(to_score)
    done = 0

    async def bounded_judge(session, record):
        nonlocal done
        async with sem:
            qid = record["question_id"]
            model = record["model"]
            lang = record["lang"]
            question = questions[qid]

            scores = await judge_response(session, question, record["response"], lang)
            entry = {
                "question_id": qid,
                "model": model,
                "lang": lang,
                "culture": question["culture"],
                "tier": question["tier"],
                "topic": question["topic"],
                **scores,
            }

            async with lock:
                done += 1
                status = "ok" if not scores.get("error") else "!!"
                print(f"  {status} [{done}/{total}] {model.split('/')[1]} | {qid} | {lang}")
                all_scores.append(entry)
                with open(SCORES_OUTPUT, "w", encoding="utf-8") as f:
                    json.dump(all_scores, f, indent=2, ensure_ascii=False)

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_judge(session, r) for r in to_score]
        await asyncio.gather(*tasks)

    return all_scores

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("Set OPENROUTER_API_KEY environment variable first.")

    with open("questions.json", encoding="utf-8") as f:
        questions = {q["id"]: q for q in json.load(f)}

    with open(RAW_INPUT, encoding="utf-8") as f:
        raw_responses = json.load(f)

    existing_scores = []
    if SCORES_OUTPUT.exists():
        with open(SCORES_OUTPUT, encoding="utf-8") as f:
            existing_scores = json.load(f)
    scored_keys = {(s["question_id"], s["model"], s["lang"]) for s in existing_scores}

    to_score = [r for r in raw_responses
                if r["error"] is None
                and (r["question_id"], r["model"], r["lang"]) not in scored_keys]

    print(f"\nCultural LLM Judge")
    print(f"   {len(to_score)} responses to score ({len(scored_keys)} already done)\n")

    if not to_score:
        print("Nothing to do.")
        return

    all_scores = asyncio.run(run_all(to_score, questions, existing_scores))
    print(f"\nDone. {len(all_scores)} total scores in {SCORES_OUTPUT}")


if __name__ == "__main__":
    main()
