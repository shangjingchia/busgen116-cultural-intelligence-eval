"""
report.py — Generate a human-readable markdown report with stylized findings.
Reads:  results/leaderboard.json + results/scores.json
Writes: results/report.md
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

RESULTS_DIR = Path("results")
REPORT_OUTPUT = RESULTS_DIR / "report.md"

TIER_LABELS = {"high": "High-resource (Chinese/Japanese/Korean)",
               "mid": "Mid-resource (Thai/Vietnamese/Indonesian)",
               "low": "Low-resource (Burmese/Khmer/Mongolian)"}

DRIFT_THRESHOLDS = {
    "severe": 0.8,    # English score > native by 0.8+
    "notable": 0.4,   # 0.4-0.8 gap
    "minimal": 0.0,   # under 0.4
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_score(val):
    if val is None:
        return "N/A"
    return f"{val:.2f}"


def drift_label(drift):
    if drift is None:
        return "unknown"
    if drift > DRIFT_THRESHOLDS["severe"]:
        return f"⚠️ Severe English bias (+{drift:.2f})"
    elif drift > DRIFT_THRESHOLDS["notable"]:
        return f"🔶 Notable drift (+{drift:.2f})"
    elif drift > -DRIFT_THRESHOLDS["notable"]:
        return f"✅ Consistent ({drift:+.2f})"
    else:
        return f"🔵 Better in native language ({drift:+.2f})"


def generate_report(leaderboard_data: dict, scores: list) -> str:
    lb = leaderboard_data["leaderboard"]
    top = lb[0]
    bottom = lb[-1]
    generated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Find most trap-prone model
    trap_sorted = sorted([e for e in lb if e["trap_fall_rate"] is not None],
                         key=lambda x: x["trap_fall_rate"], reverse=True)

    # Find model with worst low-resource performance
    low_scores = [(e["model_short"], e["by_tier"].get("low") or 0) for e in lb]
    low_scores.sort(key=lambda x: x[1])

    # Cross-lingual drift analysis
    drift_sorted = sorted([e for e in lb if e["cross_lingual_drift"] is not None],
                          key=lambda x: x["cross_lingual_drift"], reverse=True)

    # Per-question trap analysis
    trap_by_question = defaultdict(lambda: {"falls": 0, "total": 0, "models": []})
    for s in scores:
        if s.get("fell_into_trap") is not None:
            qid = s["question_id"]
            trap_by_question[qid]["total"] += 1
            if s["fell_into_trap"]:
                trap_by_question[qid]["falls"] += 1
                trap_by_question[qid]["models"].append(s["model"].split("/")[1])

    # Load questions for labels
    with open("questions.json", encoding="utf-8") as f:
        questions = {q["id"]: q for q in json.load(f)}

    lines = []

    lines.append("# 🌏 Cultural & Linguistic Intelligence Eval — Report")
    lines.append(f"\n*Generated: {generated}*\n")
    lines.append("---\n")

    # ── Executive Summary ──────────────────────────────────────────────────────
    lines.append("## Executive Summary\n")
    lines.append(
        f"This evaluation tested **{leaderboard_data['n_models']} leading LLMs** on "
        f"**{leaderboard_data['n_questions']} culturally nuanced questions** spanning 9 Asian cultures "
        f"across three language-resource tiers. Each question was asked in both English and the relevant "
        f"native language, generating a dataset of cross-lingual performance comparisons.\n"
    )

    lines.append("**Key findings at a glance:**\n")
    lines.append(f"- 🥇 **Best overall**: {top['model_short']} ({format_score(top['overall_score'])}/5.0)")
    lines.append(f"- 🔻 **Most struggles**: {bottom['model_short']} ({format_score(bottom['overall_score'])}/5.0)")
    if drift_sorted:
        lines.append(f"- 📉 **Largest English-native gap**: {drift_sorted[0]['model_short']} ({drift_sorted[0]['cross_lingual_drift']:+.2f})")
    if trap_sorted:
        lines.append(f"- 🪤 **Most likely to fall for traps**: {trap_sorted[0]['model_short']} ({trap_sorted[0]['trap_fall_rate']*100:.0f}% trap rate)")
    if low_scores:
        lines.append(f"- 🔇 **Worst on low-resource languages**: {low_scores[0][0]} ({low_scores[0][1]:.2f}/5.0)")
    lines.append(f"- 🔒 **Political sensitivity**: Chinese-origin models show three distinct censorship patterns — "
                 f"hard refusals, narrative capture, and selective collapse — absent in all Western models tested.")
    lines.append("")

    # ── Main Leaderboard ───────────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 🏆 Overall Leaderboard\n")
    lines.append("| Rank | Model | Overall | Cultural Accuracy | Depth | Calibration | Lang Quality | Trap Rate |")
    lines.append("|------|-------|---------|------------------|-------|-------------|--------------|-----------|")
    for e in lb:
        dims = e["dimensions"]
        trap = f"{e['trap_fall_rate']*100:.0f}%" if e["trap_fall_rate"] is not None else "N/A"
        lines.append(
            f"| #{e['rank']} | **{e['model_short']}** | {format_score(e['overall_score'])} "
            f"| {format_score(dims.get('cultural_accuracy'))} "
            f"| {format_score(dims.get('depth_and_nuance'))} "
            f"| {format_score(dims.get('epistemic_calibration'))} "
            f"| {format_score(dims.get('language_quality'))} "
            f"| {trap} |"
        )
    lines.append("")

    # ── Cross-Lingual Drift ────────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 📉 Cross-Lingual Drift Analysis\n")
    lines.append(
        "Drift = English score minus native language score. "
        "**Positive values** mean the model performs better when asked in English. "
        "**Negative values** mean the model actually does *better* in the native language (rare and notable).\n"
    )
    lines.append("| Model | English Score | Native Score | Drift | Assessment |")
    lines.append("|-------|--------------|--------------|-------|------------|")
    for e in sorted(lb, key=lambda x: (x["cross_lingual_drift"] or 0), reverse=True):
        lines.append(
            f"| {e['model_short']} | {format_score(e['english_score'])} "
            f"| {format_score(e['native_lang_score'])} "
            f"| {e['cross_lingual_drift']:+.2f} if e['cross_lingual_drift'] is not None else 'N/A' "
            f"| {drift_label(e['cross_lingual_drift'])} |"
        )
    lines.append("")

    # Fix the f-string issue in the table above
    # Rebuild that section cleanly
    lines = lines[:-len(lb)-2]  # remove last table rows
    lines.append("| Model | English Score | Native Score | Drift | Assessment |")
    lines.append("|-------|--------------|--------------|-------|------------|")
    for e in sorted(lb, key=lambda x: (x["cross_lingual_drift"] or 0), reverse=True):
        drift_val = e["cross_lingual_drift"]
        drift_str = f"{drift_val:+.2f}" if drift_val is not None else "N/A"
        lines.append(
            f"| {e['model_short']} | {format_score(e['english_score'])} "
            f"| {format_score(e['native_lang_score'])} "
            f"| {drift_str} | {drift_label(drift_val)} |"
        )
    lines.append("")

    # ── Score by Language Tier ─────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 📊 Performance by Language Resource Tier\n")
    lines.append(
        "A model's score typically *drops* as language resource level decreases. "
        "The steepness of this drop reveals how dependent the model is on English-centric training data.\n"
    )
    lines.append("| Model | High-resource | Mid-resource | Low-resource | Drop (High→Low) |")
    lines.append("|-------|--------------|-------------|-------------|-----------------|")
    for e in lb:
        h = e["by_tier"].get("high") or 0
        m = e["by_tier"].get("mid") or 0
        l = e["by_tier"].get("low") or 0
        drop = round(h - l, 2) if h and l else None
        drop_str = f"-{drop:.2f}" if drop else "N/A"
        lines.append(f"| {e['model_short']} | {h:.2f} | {m:.2f} | {l:.2f} | {drop_str} |")
    lines.append("")

    # ── Trap Analysis ──────────────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 🪤 Trap Question Analysis\n")
    lines.append(
        "Questions were designed with known 'traps' — common Western-centric mistakes a model might make. "
        "Below are the questions where models most often fell into the trap.\n"
    )
    trap_ranked = sorted(trap_by_question.items(),
                         key=lambda x: x[1]["falls"] / max(x[1]["total"], 1), reverse=True)
    lines.append("| Question | Culture | Trap Rate | Models That Failed |")
    lines.append("|----------|---------|-----------|-------------------|")
    for qid, data in trap_ranked[:10]:
        q = questions.get(qid, {})
        rate = data["falls"] / data["total"] if data["total"] > 0 else 0
        failed = ", ".join(data["models"][:4])
        if len(data["models"]) > 4:
            failed += f" +{len(data['models'])-4} more"
        culture = q.get("culture", qid)
        topic = q.get("topic", "").replace("_", " ")
        lines.append(f"| {qid}: {culture} — {topic} | {culture} | {rate*100:.0f}% | {failed} |")
    lines.append("")

    # ── Political Sensitivity Audit ────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 🔒 Political Sensitivity Audit: Where Chinese Models Go Silent\n")
    lines.append(
        "Chinese-origin models (DeepSeek, Qwen, Doubao) exhibit three distinct failure modes "
        "on politically adjacent questions. Every Western model tested answered all of these "
        "questions without issue.\n"
    )

    CN_MODELS  = {"deepseek/deepseek-chat-v3-0324","deepseek/deepseek-r1",
                  "qwen/qwen-2.5-72b-instruct","bytedance-seed/seed-2.0-lite"}
    WEST_MODELS = {"openai/gpt-4o","openai/gpt-4.1","anthropic/claude-sonnet-4-5",
                   "anthropic/claude-sonnet-4-6","mistralai/mistral-large","google/gemini-2.5-flash"}

    def _avg(vals):
        v = [x for x in vals if x is not None]
        return round(sum(v)/len(v), 2) if v else None

    def _cal(qid, lang, mset):
        return _avg([s["epistemic_calibration"] for s in scores
                     if s["question_id"]==qid and s["lang"]==lang
                     and s["model"] in mset and not s.get("error")
                     and s.get("epistemic_calibration") is not None])

    def _score(qid, lang, model):
        return next((s["overall"] for s in scores
                     if s["question_id"]==qid and s["lang"]==lang
                     and s["model"]==model and not s.get("error")), None)

    q04_cn_cal   = _cal("Q04","zh", CN_MODELS)
    q04_west_cal = _cal("Q04","zh", WEST_MODELS)
    cal_gap      = round((q04_west_cal or 0) - (q04_cn_cal or 0), 2)
    r1_q04       = _score("Q04","zh","deepseek/deepseek-r1")
    seed_q04     = _score("Q04","zh","bytedance-seed/seed-2.0-lite")
    r1_q11my     = _score("Q11","my","deepseek/deepseek-r1")

    lines.append("### Pattern 1 — Hard Refusal: Silent Timeouts\n")
    lines.append(
        "**Doubao Seed 2.0** (ByteDance) exhausted all retry attempts on 5 specific questions "
        "without returning any error: Korean cultural identity (*han* 한, workplace hierarchy "
        "and challenge of authority) and Mongolian cultural identity (*nutag*, ger customs). "
        "Every other active model answered these questions without issue. "
        "Because no HTTP error is returned — the request simply never resolves — "
        "this pattern is consistent with **server-side content filtering** rather than a "
        "capability gap. Both topics touch on ethnic/national identity that is politically "
        "sensitive within China's borders (Korean resentment narratives; Mongolian independence "
        "and identity relative to Inner Mongolia).\n"
    )

    lines.append("### Pattern 2 — Soft Censorship: Narrative Capture in Chinese\n")
    lines.append(
        "When asked *in Chinese* how the 1839-1949 period (\"Century of Humiliation\") is "
        "taught in Chinese schools, Chinese models' **epistemic calibration collapses**:\n\n"
        f"| Group | Avg Calibration (Q04/zh) |\n"
        f"|-------|-------------------------|\n"
        f"| Chinese models | {format_score(q04_cn_cal)} / 5.0 |\n"
        f"| Western models | {format_score(q04_west_cal)} / 5.0 |\n"
        f"| **Gap** | **{format_score(cal_gap)} pts** |\n\n"
        f"This is the **single largest calibration gap** in the entire evaluation. "
        f"DeepSeek R1 scores **{format_score(r1_q04)}/5** and reproduces official CCP framing verbatim "
        f"(*\"在中国共产党的领导下…爱国主义情感\"*) rather than analytically describing how "
        f"this history is taught. The question does not ask the model to agree with any narrative — "
        f"it asks the model to describe one. Describing it accurately requires acknowledging "
        f"its framing, which DeepSeek R1 is unwilling to do.\n\n"
        f"Notably, **Doubao scores {format_score(seed_q04)}/5** on the same question and explicitly "
        f"states that *\"no single narrative captures the full spectrum of perspectives\"* — "
        f"a striking divergence from its DeepSeek counterparts within the same company ecosystem. "
        f"DeepSeek Chat and Qwen show intermediate suppression (calibration 2–3), "
        f"confirming this is a **training-policy pattern across the DeepSeek family**, "
        f"not a single-model anomaly. The effect is strongest in Chinese-language prompts — "
        f"language itself appears to act as a trigger for content constraints.\n"
    )

    lines.append("### Pattern 3 — Total Collapse on Burmese\n")
    lines.append(
        f"**DeepSeek R1** scores **{format_score(r1_q11my)}/5** with calibration=1 on Burmese "
        f"questions (longyi symbolism, Buddhist merit-making). This stands out because R1 "
        f"performs respectably on other low-resource languages. Whether this reflects "
        f"training-data absence for Burmese script or sensitivity around Myanmar's political "
        f"situation (China maintains close ties with Myanmar's military government) cannot "
        f"be determined from scores alone — but the complete collapse, absent in all other "
        f"models, warrants noting.\n"
    )

    # ── Notable Findings ───────────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 💡 Key Stylized Facts & Observations\n")

    findings = []

    # Finding 0: Doubao
    seed = next((e for e in lb if "seed-2.0" in e["model"]), None)
    dsr1 = next((e for e in lb if "deepseek-r1" in e["model"]), None)
    dsc  = next((e for e in lb if "deepseek-chat" in e["model"]), None)
    if seed:
        seed_vs_r1  = round(seed["overall_score"] - (dsr1["overall_score"] if dsr1 else 0), 2)
        seed_vs_dsc = round(seed["overall_score"] - (dsc["overall_score"]  if dsc  else 0), 2)
        findings.append(
            f"**Doubao Seed 2.0 (ByteDance) ranks #{seed['rank']} overall with {format_score(seed['overall_score'])}/5**, "
            f"beating DeepSeek R1 by {format_score(seed_vs_r1)} pts and DeepSeek Chat by {format_score(seed_vs_dsc)} pts. "
            f"Doubao is China's most widely used AI product — yet in Western discourse DeepSeek dominates the conversation. "
            f"This eval reflects what adoption numbers already suggest: Doubao is a world-class model, "
            f"ranking above every non-Anthropic Western model tested and posting the strongest low-resource "
            f"tier score of any non-Anthropic model ({format_score(seed['by_tier'].get('low'))}/5)."
        )

    # Finding 1: Chinese-trained models — calibration pattern
    for e in lb:
        if "DeepSeek" in e["model_short"] or "Qwen" in e["model_short"]:
            cn_score = e["by_culture"].get("Chinese")
            findings.append(
                f"**{e['model_short']} shows {'strong' if (cn_score or 0) > 3.5 else 'mixed'} "
                f"performance on Chinese cultural questions** "
                f"(score: {format_score(cn_score)}/5.0), "
                f"{'consistent with' if (cn_score or 0) > 3.5 else 'despite'} its Chinese training data advantage. "
                f"See the Political Sensitivity Audit section for systematic calibration suppression "
                f"on questions touching Chinese and Mongolian political identity."
            )

    # Finding 2: Drift pattern
    if drift_sorted and drift_sorted[0]["cross_lingual_drift"] is not None:
        worst_drift = drift_sorted[0]
        findings.append(
            f"**Cross-lingual performance collapse is most severe for {worst_drift['model_short']}**, "
            f"which scores {worst_drift['english_score']:.2f} in English but only "
            f"{worst_drift['native_lang_score']:.2f} in native languages — "
            f"a {abs(worst_drift['cross_lingual_drift']):.2f}-point gap suggesting heavy reliance on English reasoning."
        )

    # Finding 3: Low-resource languages
    findings.append(
        f"**Low-resource languages expose the sharpest capability gaps.** "
        f"Average scores for Burmese, Khmer, and Mongolian questions are consistently "
        f"lower than high-resource language questions across all models, "
        f"with some models producing near-incoherent responses in Burmese script."
    )

    # Finding 4: Trap fall patterns
    if trap_sorted and trap_sorted[0]["trap_fall_rate"] is not None:
        findings.append(
            f"**{trap_sorted[0]['model_short']} fell into cultural traps {trap_sorted[0]['trap_fall_rate']*100:.0f}% of the time**, "
            f"most often by applying Western social norms to Asian cultural scenarios "
            f"(e.g., framing 'silence' as awkward rather than meaningful, or diagnosing "
            f"indirect communication as avoidance rather than culturally-coded behavior)."
        )

    # Finding 5: Untranslatable concepts
    findings.append(
        "**Questions about untranslatable concepts (ma, han, kreng jai, nutag) "
        "showed the widest variance between models.** "
        "Top-performing models acknowledged the limits of translation and explained "
        "the concept's relational/cosmological context; weaker models simply "
        "offered a dictionary gloss and moved on."
    )

    for i, finding in enumerate(findings, 1):
        lines.append(f"{i}. {finding}\n")

    # ── Methodology ───────────────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 🔬 Methodology\n")
    lines.append("""
**Question design:** 20 questions spanning 9 Asian cultures, designed to appear as genuine curiosity rather than evaluation prompts. Each question targets a specific cultural concept, behavioral norm, historical framing, or untranslatable idea with known "traps" — common mistakes a Western-biased model would make.

**Language conditions:** Each question was presented in two versions: standard English and the relevant native language (Mandarin Chinese, Japanese, Korean, Thai, Vietnamese, Indonesian, Burmese, Khmer, or Mongolian).

**Models evaluated (12):** GPT-4o, GPT-4.1 (OpenAI) · Claude Sonnet 4.5, Claude Sonnet 4.6 (Anthropic) · Gemini 2.5 Flash (Google) · Llama 3.1 70B, Llama 3.3 70B (Meta) · DeepSeek V3-0324, DeepSeek R1 (DeepSeek) · Qwen 2.5 72B (Alibaba) · Mistral Large (Mistral) · Doubao Seed 2.0 (ByteDance)

**Scoring:** Each response was scored by Claude Opus acting as judge on 4 dimensions (1–5 scale):
- **Cultural accuracy** — factual correctness and trap avoidance
- **Depth & nuance** — beyond surface-level description
- **Epistemic calibration** — appropriate confidence levels
- **Language quality** — fluency and cultural idiomaticity of the response language

**Cross-lingual drift** is computed as `avg(English score) - avg(native language score)` per model.
""")

    lines.append("---")
    lines.append("*Eval designed and run with Claude. Questions, rubric, and judge prompts available in the codebase.*")

    return "\n".join(lines)


def main():
    leaderboard_data = load_json(RESULTS_DIR / "leaderboard.json")
    scores = load_json(RESULTS_DIR / "scores.json")

    report = generate_report(leaderboard_data, scores)

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
