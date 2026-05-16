"""
leaderboard.py — Aggregate scores into ranked leaderboard with cross-lingual drift analysis.
Reads:  results/scores.json
Writes: results/leaderboard.json
"""

import json
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path("results")
SCORES_INPUT = RESULTS_DIR / "scores.json"
LEADERBOARD_OUTPUT = RESULTS_DIR / "leaderboard.json"

MODELS_SHORT = {
    "openai/gpt-4o": "GPT-4o",
    "anthropic/claude-sonnet-4-5": "Claude Sonnet 4.5",
    "google/gemini-2.5-flash": "Gemini 2.5 Flash",
    "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B",
    "deepseek/deepseek-chat-v3-0324": "DeepSeek V3-0324",
    "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B",
    "mistralai/mistral-large": "Mistral Large",
    "openai/gpt-4.1": "GPT-4.1",
    "anthropic/claude-sonnet-4-6": "Claude Sonnet 4.6",
    "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
    "deepseek/deepseek-r1": "DeepSeek R1",
    "bytedance-seed/seed-2.0-lite": "Doubao Seed 2.0",
}

DIMS = ["cultural_accuracy", "depth_and_nuance", "epistemic_calibration", "language_quality"]
TIERS = ["high", "mid", "low"]
CULTURES = ["Chinese", "Japanese", "Korean", "Thai", "Vietnamese", "Indonesian", "Burmese", "Khmer", "Mongolian"]


def safe_avg(vals):
    vals = [v for v in vals if v is not None and v > 0]
    return round(sum(vals) / len(vals), 2) if vals else None


def main():
    with open(SCORES_INPUT, encoding="utf-8") as f:
        scores = json.load(f)

    # ── Per-model aggregation ──────────────────────────────────────────────────
    model_data = defaultdict(lambda: {
        "overall": [], "cultural_accuracy": [], "depth_and_nuance": [],
        "epistemic_calibration": [], "language_quality": [],
        "trap_falls": 0, "trap_total": 0,
        "by_tier": {t: [] for t in TIERS},
        "by_culture": {c: [] for c in CULTURES},
        "by_lang": {"en": [], "native": []},
        "drift_pairs": {},  # qid -> {en_score, native_score}
    })

    for s in scores:
        if s.get("error"):
            continue
        m = s["model"]
        d = model_data[m]

        d["overall"].append(s["overall"])
        for dim in DIMS:
            d[dim].append(s[dim])

        if s["fell_into_trap"] is not None:
            d["trap_total"] += 1
            if s["fell_into_trap"]:
                d["trap_falls"] += 1

        tier = s.get("tier")
        if tier in TIERS:
            d["by_tier"][tier].append(s["overall"])

        culture = s.get("culture")
        if culture in CULTURES:
            d["by_culture"][culture].append(s["overall"])

        lang_key = "en" if s["lang"] == "en" else "native"
        d["by_lang"][lang_key].append(s["overall"])

        # Track pairs for drift calculation
        qid = s["question_id"]
        if qid not in d["drift_pairs"]:
            d["drift_pairs"][qid] = {}
        d["drift_pairs"][qid][lang_key] = s["overall"]

    # ── Build leaderboard ──────────────────────────────────────────────────────
    leaderboard = []
    for model, d in model_data.items():
        if model not in MODELS_SHORT:
            continue
        # Cross-lingual drift: avg(en_score - native_score) per question
        drifts = []
        for qid, pair in d["drift_pairs"].items():
            if "en" in pair and "native" in pair:
                drifts.append(pair["en"] - pair["native"])
        avg_drift = round(sum(drifts) / len(drifts), 2) if drifts else None
        # Positive drift = better in English, Negative = better in native

        trap_rate = round(d["trap_falls"] / d["trap_total"], 2) if d["trap_total"] > 0 else None

        entry = {
            "model": model,
            "model_short": MODELS_SHORT.get(model, model),
            "overall_score": safe_avg(d["overall"]),
            "dimensions": {dim: safe_avg(d[dim]) for dim in DIMS},
            "by_tier": {t: safe_avg(d["by_tier"][t]) for t in TIERS},
            "by_culture": {c: safe_avg(d["by_culture"][c]) for c in CULTURES if d["by_culture"][c]},
            "english_score": safe_avg(d["by_lang"]["en"]),
            "native_lang_score": safe_avg(d["by_lang"]["native"]),
            "cross_lingual_drift": avg_drift,
            "trap_fall_rate": trap_rate,
            "n_responses": len(d["overall"]),
        }
        leaderboard.append(entry)

    # Sort by overall score descending
    leaderboard.sort(key=lambda x: x["overall_score"] or 0, reverse=True)

    # Add rank
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1

    output = {
        "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
        "n_questions": 20,
        "n_models": len(leaderboard),
        "leaderboard": leaderboard,
    }

    with open(LEADERBOARD_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # ── Print summary ──────────────────────────────────────────────────────────
    print("\nCultural LLM Leaderboard\n")
    print(f"{'Rank':<5} {'Model':<22} {'Overall':<9} {'Eng':<7} {'Native':<9} {'Drift':<8} {'Trap%'}")
    print("─" * 70)
    for e in leaderboard:
        drift_str = f"{e['cross_lingual_drift']:+.2f}" if e['cross_lingual_drift'] is not None else " N/A"
        trap_str = f"{e['trap_fall_rate']*100:.0f}%" if e['trap_fall_rate'] is not None else " N/A"
        print(f"#{e['rank']:<4} {e['model_short']:<22} {e['overall_score']:<9.2f} "
              f"{e['english_score']:<7.2f} {e['native_lang_score']:<9.2f} "
              f"{drift_str:<8} {trap_str}")

    print(f"\nSaved to {LEADERBOARD_OUTPUT}")

    # ── Tier breakdown ─────────────────────────────────────────────────────────
    print("\n\nScore by Language Tier (avg across all models)")
    print(f"{'Model':<22} {'High-resource':<16} {'Mid-resource':<15} {'Low-resource'}")
    print("─" * 65)
    for e in leaderboard:
        h = e['by_tier'].get('high', 0) or 0
        m = e['by_tier'].get('mid', 0) or 0
        l = e['by_tier'].get('low', 0) or 0
        print(f"{e['model_short']:<22} {h:<16.2f} {m:<15.2f} {l:.2f}")


if __name__ == "__main__":
    main()
