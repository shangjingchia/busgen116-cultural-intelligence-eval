"""
run_eval.py — Fan out all 20 questions × 2 languages × 12 models via OpenRouter
Saves raw responses to results/raw_responses.json
"""

import json
import os
import time
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    # Original models
    "openai/gpt-4o",
    "anthropic/claude-sonnet-4-5",
    "meta-llama/llama-3.1-70b-instruct",
    "deepseek/deepseek-chat-v3-0324",
    "qwen/qwen-2.5-72b-instruct",
    "mistralai/mistral-large",
    # Latest additions
    "openai/gpt-4.1",
    "anthropic/claude-sonnet-4-6",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-r1",
    "bytedance-seed/seed-2.0-lite",
]

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
RAW_OUTPUT = RESULTS_DIR / "raw_responses.json"

CONCURRENCY = 5          # parallel requests at once
RETRY_LIMIT = 3
RETRY_DELAY = 5          # seconds between retries

# ── Prompt wrapper ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a knowledgeable assistant with deep expertise in world cultures, languages, and social norms. Answer the following question thoughtfully and in detail. Do not hedge excessively — share your genuine understanding even for nuanced cultural topics."""

def build_prompt(question: dict, lang: str) -> str:
    """Return the question text in the requested language."""
    if lang == "en":
        return question["english"]
    else:
        return question["native"]

# ── API call ───────────────────────────────────────────────────────────────────

async def call_model(session: aiohttp.ClientSession, model: str, prompt: str, question_id: str, lang: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cultural-eval",
        "X-Title": "Cultural LLM Eval",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 800,
        "temperature": 0.3,
    }

    for attempt in range(RETRY_LIMIT):
        try:
            async with session.post(OPENROUTER_URL, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "question_id": question_id,
                        "model": model,
                        "lang": lang,
                        "response": content,
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": None,
                    }
                elif resp.status == 429:
                    wait = RETRY_DELAY * (attempt + 1)
                    print(f"  ! Rate limited on {model}, waiting {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    err_text = await resp.text()
                    print(f"  !! {model} [{question_id}/{lang}] HTTP {resp.status}: {err_text[:200]}")
                    return {
                        "question_id": question_id, "model": model, "lang": lang,
                        "response": None, "tokens_used": 0,
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": f"HTTP {resp.status}: {err_text[:200]}",
                    }
        except asyncio.TimeoutError:
            print(f"  !! Timeout on {model} [{question_id}/{lang}], attempt {attempt+1}")
            await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"  !! Exception on {model} [{question_id}/{lang}]: {e}")
            await asyncio.sleep(RETRY_DELAY)

    return {
        "question_id": question_id, "model": model, "lang": lang,
        "response": None, "tokens_used": 0,
        "timestamp": datetime.utcnow().isoformat(),
        "error": "Max retries exceeded",
    }

# ── Semaphore-limited fan-out ──────────────────────────────────────────────────

async def run_all(questions: list, completed: set, existing_keys: dict) -> dict:
    sem = asyncio.Semaphore(CONCURRENCY)
    lock = asyncio.Lock()
    total_new = sum(
        1 for q in questions
        for lang in ["en", q["language"]]
        for model in MODELS
        if (q["id"], model, lang) not in completed
    )
    done = 0

    async def bounded_call(session, model, prompt, qid, lang):
        nonlocal done
        async with sem:
            result = await call_model(session, model, prompt, qid, lang)
            async with lock:
                done += 1
                status = "ok" if result["error"] is None else "!!"
                print(f"  {status} [{done}/{total_new}] {model.split('/')[1]} | {qid} | {lang}")
                key = (result["question_id"], result["model"], result["lang"])
                if key not in existing_keys or existing_keys[key]["error"] is not None:
                    existing_keys[key] = result
                # Save after every completed call
                with open(RAW_OUTPUT, "w", encoding="utf-8") as f:
                    json.dump(list(existing_keys.values()), f, indent=2, ensure_ascii=False)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for q in questions:
            for lang in ["en", q["language"]]:
                if (q["id"], MODELS[0], lang) in completed:
                    # Check per-model below
                    pass
                prompt = build_prompt(q, lang)
                for model in MODELS:
                    if (q["id"], model, lang) not in completed:
                        tasks.append(bounded_call(session, model, prompt, q["id"], lang))
        await asyncio.gather(*tasks)

    return existing_keys

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("Set OPENROUTER_API_KEY environment variable first.")

    with open("questions.json", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"\nCultural LLM Eval")
    print(f"   {len(questions)} questions x 2 languages x {len(MODELS)} models = {len(questions)*2*len(MODELS)} calls\n")

    existing_keys = {}
    if RAW_OUTPUT.exists():
        with open(RAW_OUTPUT, encoding="utf-8") as f:
            for r in json.load(f):
                existing_keys[(r["question_id"], r["model"], r["lang"])] = r
        completed = {k for k, r in existing_keys.items() if r["error"] is None}
        print(f"   Resuming — {len(completed)} calls already done\n")
    else:
        completed = set()

    final_keys = asyncio.run(run_all(questions, completed, existing_keys))
    final = list(final_keys.values())
    success = sum(1 for r in final if r["error"] is None)
    print(f"\nDone. {success}/{len(final)} responses saved to {RAW_OUTPUT}")


if __name__ == "__main__":
    main()
