import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Cultural LLM Eval",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Palette — Rice Paper & Lacquer ────────────────────────────────────────────
BG      = "#faf5ee"   # rice paper
CARD    = "#f0e8d8"   # warm parchment card
BORDER  = "#d4bea0"   # tan border
GRID    = "#e8ddc8"   # light grid lines
TEXT    = "#1a1208"   # ink black
TEXT2   = "#6a5840"   # aged ink
CINNA   = "#c8280e"   # cinnabar red  朱砂红
GOLD    = "#c89010"   # imperial gold 金色
JADE    = "#1a9850"   # deep jade     翠玉绿

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=0)
def load():
    with open(Path(__file__).parent / "results" / "leaderboard.json", encoding="utf-8") as f:
        return json.load(f)

DATA = load()
lb   = DATA["leaderboard"]

# Radar fallback colors (index-based, for models picked interactively)
COLORS = [
    "#c8280e","#1a9850","#c89010","#c83050","#1878c8",
    "#8030c8","#d07018","#0a9890","#a87010","#6030b8",
    "#c85010",
]

COMPANY_MAP = {
    "Claude Sonnet 4.6":  ("Anthropic", 0),
    "Claude Sonnet 4.5":  ("Anthropic", 0),
    "GPT-4.1":            ("OpenAI",    1),
    "GPT-4o":             ("OpenAI",    1),
    "Gemini 2.5 Flash":   ("Google",    2),
    "DeepSeek V3-0324":   ("DeepSeek",  3),
    "DeepSeek R1":        ("DeepSeek",  3),
    "Doubao Seed 2.0":    ("ByteDance", 4),
    "Mistral Large":      ("Mistral",   5),
    "Llama 3.3 70B":      ("Meta",      6),
    "Llama 3.1 70B":      ("Meta",      6),
    "Qwen 2.5 72B":       ("Alibaba",   7),
}

COMPANY_COLORS = {
    "Anthropic": CINNA,     # cinnabar red   朱砂红
    "OpenAI":    JADE,      # deep jade      翠玉绿
    "Google":    "#1878c8", # deep sky blue  天蓝
    "DeepSeek":  GOLD,      # imperial gold  金色
    "ByteDance": "#c83050", # plum red       桃红
    "Mistral":   "#d07018", # saffron        藤黄
    "Meta":      "#0a9890", # teal jade      松石绿
    "Alibaba":   "#8030c8", # lotus purple   莲紫
}

def company_sort_key(e):
    _, order = COMPANY_MAP.get(e["model_short"], ("Unknown", 99))
    return (order, e["model_short"])

def model_color(model_short):
    company, _ = COMPANY_MAP.get(model_short, ("Unknown", 0))
    return COMPANY_COLORS.get(company, TEXT2)

def fmt(v, d=2):
    return f"{v:.{d}f}" if v is not None else "N/A"

def hex_rgba(hex_color, alpha=0.18):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.fc {{
    background:{CARD}; border:1px solid {BORDER};
    border-radius:10px; padding:1.1rem 1.3rem 1rem; margin-bottom:0.75rem;
}}
.ft {{ font-size:0.92rem; font-weight:700; margin-bottom:0.2rem; color:{TEXT}; line-height:1.3; }}
.fs {{ font-size:1.55rem; font-weight:800; letter-spacing:-0.03em; line-height:1.15; margin-top:0.1rem; }}
.fl {{
    font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em;
    color:{TEXT2}; margin-bottom:0.5rem; margin-top:0.15rem;
}}
.fb {{ font-size:0.85rem; color:{TEXT}; line-height:1.7; opacity:0.82; }}
.fb b {{ color:{TEXT}; opacity:1; font-weight:600; }}
div[data-testid="metric-container"] {{
    background:{CARD}; border:1px solid {BORDER};
    border-radius:10px; padding:0.9rem 1.1rem;
}}
div[data-testid="stMetricValue"] > div {{
    font-size:1.05rem !important; font-weight:700 !important;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
div[data-testid="stMetricLabel"] > div {{
    font-size:0.72rem !important; white-space:nowrap;
}}
</style>
""", unsafe_allow_html=True)

# Shared Plotly layout kwargs
def plot_layout(**extra):
    base = dict(
        paper_bgcolor=BG,
        plot_bgcolor=CARD,
        font=dict(color=TEXT),
        legend=dict(bgcolor=CARD, bordercolor=BORDER, borderwidth=1),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    base.update(extra)
    return base

def axis_style(**kw):
    return dict(tickcolor=TEXT2, gridcolor=GRID, **kw)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 🌏 Cultural & Linguistic Intelligence Eval")
st.caption("Benchmarking LLMs on Asian cultural understanding — tested in English and native languages.")
st.markdown(
    f'<div style="font-size:0.78rem;color:{TEXT2};margin-top:-0.3rem;margin-bottom:0.2rem;">'
    f'Shang Jing Chia &nbsp;·&nbsp; BUSGEN 116 &nbsp;·&nbsp; Stanford University'
    f' &nbsp;·&nbsp; <a href="https://github.com/shangjingchia/busgen116-cultural-intelligence-eval"'
    f' target="_blank" style="color:{TEXT2};text-decoration:underline;">GitHub</a>'
    f'</div>',
    unsafe_allow_html=True,
)
pills = [f"{len(lb)} models", "20 questions × 2 languages", "9 cultures · 3 language tiers", "LLM-as-judge scoring"]
pill_html = " ".join(
    f'<span style="background:{CARD};border:1px solid {BORDER};border-radius:99px;'
    f'padding:2px 10px;font-size:0.72rem;color:{TEXT2}">{p}</span>'
    for p in pills
)
st.markdown(pill_html, unsafe_allow_html=True)
st.divider()

# ── Summary cards ──────────────────────────────────────────────────────────────
top       = lb[0]
avg_score = sum(e["overall_score"] for e in lb) / len(lb)
dv        = [e for e in lb if e.get("cross_lingual_drift") is not None]
avg_drift = sum(e["cross_lingual_drift"] for e in dv) / len(dv)
wdrift    = max(dv, key=lambda e: e["cross_lingual_drift"])
btrap     = min((e for e in lb if e.get("trap_fall_rate") is not None), key=lambda e: e["trap_fall_rate"])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🥇 Top Model",    top["model_short"],        f"{top['overall_score']:.2f} / 5.0")
c2.metric("📊 Avg Score",    f"{avg_score:.2f} / 5.0",  f"across {len(lb)} models")
c3.metric("📉 Avg Drift",    f"+{avg_drift:.2f}",       "English advantage over native")
c4.metric("⚠️ Largest Gap", wdrift["model_short"],     f"drift +{wdrift['cross_lingual_drift']:.2f}")
c5.metric("🎯 Fewest Traps", btrap["model_short"],      f"{btrap['trap_fall_rate']*100:.0f}% trap rate")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
t_find, t_rank, t_radar, t_heat, t_drift, t_tier, t_method = st.tabs([
    "🔍 Key Findings", "🏆 Rankings", "🕸 Dimension Radar",
    "🌡 Culture Heatmap", "📉 Cross-Lingual Drift", "📊 Language Tiers",
    "🔬 Methodology",
])

# ─── Key Findings ──────────────────────────────────────────────────────────────
with t_find:
    drs = sorted([e for e in lb if e.get("cross_lingual_drift") is not None],
                 key=lambda e: e["cross_lingual_drift"])
    best_drft   = drs[0]
    worst_drft2 = drs[-1]
    ts          = sorted([e for e in lb if e.get("trap_fall_rate") is not None],
                         key=lambda e: -e["trap_fall_rate"])
    worst_trap  = ts[0]
    dsr1  = next((e for e in lb if "deepseek-r1"       in e["model"]), None)
    dsc   = next((e for e in lb if "deepseek-chat"      in e["model"]), None)
    qwen  = next((e for e in lb if "qwen"               in e["model"]), None)
    c45   = next((e for e in lb if "claude-sonnet-4-5"  in e["model"]), None)
    c46   = next((e for e in lb if "claude-sonnet-4-6"  in e["model"]), None)
    seed  = next((e for e in lb if "seed-2.0"           in e["model"]), None)
    avg_cal = sum(e["dimensions"].get("epistemic_calibration", 0) for e in lb) / len(lb)
    avg_lq  = sum(e["dimensions"].get("language_quality", 0) for e in lb) / len(lb)

    def card(icon, title, stat, stat_label, body, accent):
        return (
            f'<div class="fc" style="border-left:3px solid {accent}">'
            f'<div class="ft">{icon}&nbsp; {title}</div>'
            f'<div class="fs" style="color:{accent}">{stat}</div>'
            f'<div class="fl">{stat_label}</div>'
            f'<div class="fb">{body}</div>'
            f'</div>'
        )

    findings = [
        ("🥇", "Clear Winner — No Close Contest",
         f"{fmt(top['overall_score'])} / 5",
         f"{top['model_short']} · overall score",
         f"<b>{top['model_short']}</b> leads at <b>{fmt(top['overall_score'])}</b> — <b>{fmt(top['overall_score']-lb[1]['overall_score'])}</b> pts ahead of #2 {lb[1]['model_short']}. "
         f"The <b>only model with a 0% trap fall rate</b>, never misapplying Western social norms to Asian scenarios.",
         CINNA),

        *([("🐋", "The Overlooked Giant: Doubao Beats DeepSeek — and Most of the West Doesn't Know It",
         f"#{seed['rank']} · {fmt(seed['overall_score'])} / 5",
         f"Doubao Seed 2.0 (ByteDance) · overall score",
         f"<b>Doubao</b> is China's most widely used AI product — ByteDance reported hundreds of millions of users "
         f"on the Doubao app, dwarfing DeepSeek's user base. Yet in Western discourse, DeepSeek dominates the conversation. "
         f"The numbers here reflect what adoption already signals: Doubao scores <b>{fmt(seed['overall_score'])}</b>, "
         + (f"beating <b>DeepSeek R1 ({fmt(dsr1['overall_score'])})</b> by <b>{fmt(seed['overall_score']-dsr1['overall_score'])} pts</b> " if dsr1 else "")
         + (f"and <b>DeepSeek Chat ({fmt(dsc['overall_score'])})</b> by <b>{fmt(seed['overall_score']-dsc['overall_score'])} pts</b>. " if dsc else "")
         + f"It ranks <b>#{seed['rank']}</b> overall — above every non-Anthropic Western model tested — "
         f"and posts the <b>strongest low-resource tier score</b> of any non-Anthropic model ({fmt(seed['by_tier'].get('low'))}).",
         "#c83050")] if seed else []),

        ("🎯", "Most Language-Consistent: An Unexpected Contender",
         ('+' if best_drft['cross_lingual_drift'] >= 0 else '') + fmt(best_drft['cross_lingual_drift']),
         f"{best_drft['model_short']} · cross-lingual drift",
         f"<b>{best_drft['model_short']}</b> (ranked #{best_drft['rank']}) shows the smallest drift. "
         f"Higher-ranked models score better overall but degrade more when the language switches — "
         f"a critical distinction for multilingual deployments.",
         JADE),

        ("📉", "English as a Crutch: The Language Collapse",
         f"+{fmt(worst_drft2['cross_lingual_drift'])}",
         f"{worst_drft2['model_short']} · language collapse",
         f"<b>{worst_drft2['model_short']}</b> scores <b>{fmt(worst_drft2['english_score'])}</b> in English "
         f"but drops to <b>{fmt(worst_drft2['native_lang_score'])}</b> in native languages. "
         f"It retrieves English-indexed facts but lacks cultural reasoning that holds across languages.",
         "#e05a6a"),

        ("🪤", "Western Bias Baked In — Nearly Half the Time",
         f"{worst_trap['trap_fall_rate']*100:.0f}%",
         f"{worst_trap['model_short']} · trap fall rate",
         f"<b>{worst_trap['model_short']}</b> fell into culturally biased framings "
         f"<b>{worst_trap['trap_fall_rate']*100:.0f}%</b> of the time — "
         f"treating silence as awkward, framing indirect speech as avoidance, "
         f"or imposing individual agency on collectivist decision contexts.",
         GOLD),
    ]

    if dsr1:
        findings.append((
            "🔇", "The Low-Resource Cliff Is a Drop, Not a Slope",
            fmt(dsr1['by_culture'].get('Burmese')),
            "DeepSeek R1 · Burmese score",
            f"<b>DeepSeek R1</b> scores <b>{fmt(dsr1['by_culture'].get('Japanese'))}</b> on Japanese "
            f"and <b>{fmt(dsr1['by_culture'].get('Korean'))}</b> on Korean — "
            f"then <b>{fmt(dsr1['by_culture'].get('Burmese'))}</b> on Burmese. "
            f"A <b>{fmt(dsr1['by_culture'].get('Japanese',0)-dsr1['by_culture'].get('Burmese',0))}-pt cliff</b>. "
            f"This isn't gradual decline; it's where training data simply runs out.",
            "#e05a6a",
        ))

    findings.append((
        "🧭", "Calibration: The Universal Blind Spot",
        fmt(avg_cal),
        "avg epistemic calibration · all models",
        f"The <b>weakest dimension across all {len(lb)} models</b> — "
        f"avg <b>{fmt(avg_cal)}</b> vs language quality avg <b>{fmt(avg_lq)}</b>. "
        f"Models answer confidently and fluently but rarely hedge appropriately. "
        f"Overconfidence on contested cultural questions is a silent failure mode.",
        "#4d9fd6",
    ))

    if dsr1 and dsc and qwen:
        findings.append((
            "🧩", "The Chinese Model Paradox",
            f"#{dsr1['rank']} · #{dsc['rank']} · #{qwen['rank']}",
            "DeepSeek R1 · DeepSeek Chat · Qwen · rank",
            f"Despite large Chinese-corpus training advantages, none crack the top 3. "
            f"<b>Cultural breadth ≠ language depth</b> — Mandarin fluency doesn't confer "
            f"understanding of Thai hierarchy, Burmese animism, or Mongolian nomadic culture.",
            "#e8894c",
        ))

    if c45 and c46:
        cal_gain   = c46['dimensions']['epistemic_calibration'] - c45['dimensions']['epistemic_calibration']
        depth_gain = c46['dimensions']['depth_and_nuance'] - c45['dimensions']['depth_and_nuance']
        findings.append((
            "📈", "One Generation: A Measurable Cultural Leap",
            f"+{fmt(c46['overall_score']-c45['overall_score'])}",
            "Claude Sonnet 4.5 → 4.6 · score gain",
            f"Claude Sonnet <b>4.6 ({fmt(c46['overall_score'])})</b> outperforms "
            f"<b>4.5 ({fmt(c45['overall_score'])})</b>. "
            f"Sharpest gains: Epistemic Calibration (+{fmt(cal_gain)}) "
            f"and Depth & Nuance (+{fmt(depth_gain)}) — smarter hedging, not just better recall.",
            CINNA,
        ))

    half = (len(findings) + 1) // 2
    col1, col2 = st.columns(2)
    with col1:
        for f in findings[:half]:
            st.markdown(card(*f), unsafe_allow_html=True)
    with col2:
        for f in findings[half:]:
            st.markdown(card(*f), unsafe_allow_html=True)

    # ── Political Sensitivity Callout ──────────────────────────────────────────
    st.divider()

    # Gather data points for the callout
    cn_models = ["deepseek/deepseek-chat-v3-0324","deepseek/deepseek-r1","qwen/qwen-2.5-72b-instruct","bytedance-seed/seed-2.0-lite"]
    west_models = ["openai/gpt-4o","openai/gpt-4.1","anthropic/claude-sonnet-4-5","anthropic/claude-sonnet-4-6","mistralai/mistral-large","google/gemini-2.5-flash"]

    import json as _json
    from pathlib import Path as _Path
    from collections import defaultdict as _dd

    @st.cache_data(ttl=0)
    def load_scores():
        with open(_Path(__file__).parent / "results" / "scores.json", encoding="utf-8") as f:
            return _json.load(f)

    _scores = load_scores()

    def _cal_avg(qid, lang, model_list):
        vals = [s["epistemic_calibration"] for s in _scores
                if s["question_id"]==qid and s["lang"]==lang
                and s["model"] in model_list and not s.get("error")
                and s.get("epistemic_calibration") is not None]
        return round(sum(vals)/len(vals),2) if vals else None

    def _overall_avg(qid, lang, model_list):
        vals = [s["overall"] for s in _scores
                if s["question_id"]==qid and s["lang"]==lang
                and s["model"] in model_list and not s.get("error")
                and s.get("overall") is not None]
        return round(sum(vals)/len(vals),2) if vals else None

    q04_cn_cal   = _cal_avg("Q04","zh", cn_models)
    q04_west_cal = _cal_avg("Q04","zh", west_models)
    q04_r1_score = next((s["overall"] for s in _scores if s["question_id"]=="Q04" and s["lang"]=="zh" and s["model"]=="deepseek/deepseek-r1" and not s.get("error")), None)
    q04_seed_score = next((s["overall"] for s in _scores if s["question_id"]=="Q04" and s["lang"]=="zh" and s["model"]=="bytedance-seed/seed-2.0-lite" and not s.get("error")), None)

    cal_gap = round((q04_west_cal or 0) - (q04_cn_cal or 0), 2)
    _r1_my = [s["overall"] for s in _scores if s["lang"] == "my"
              and s["model"] == "deepseek/deepseek-r1"
              and not s.get("error") and s.get("overall") is not None]
    r1_burmese_native = round(sum(_r1_my) / len(_r1_my), 2) if _r1_my else None

    st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-left:4px solid {CINNA};
     border-radius:10px;padding:1.1rem 1.4rem 0.9rem;margin-top:0.6rem;">
  <div style="font-size:0.95rem;font-weight:800;color:{TEXT};margin-bottom:0.2rem;">
    🔒 Where Chinese Models Go Silent — A Political Sensitivity Audit
  </div>
  <div style="font-size:0.85rem;color:{TEXT2};line-height:1.6;">
    Chinese-origin models (DeepSeek, Qwen, Doubao) show three distinct failure modes on politically
    adjacent questions — none present in Western models tested on the same prompts.
  </div>
</div>
""", unsafe_allow_html=True)

    _c1, _c2, _c3 = st.columns(3)
    with _c1:
        st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-top:3px solid {CINNA};border-radius:8px;padding:0.9rem 1rem;height:100%;">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:{CINNA};margin-bottom:0.35rem;">① Hard Refusal</div>
  <div style="font-size:0.86rem;color:{TEXT};font-weight:600;margin-bottom:0.35rem;">Silent timeouts</div>
  <div style="font-size:0.83rem;color:{TEXT2};line-height:1.65;">
    Doubao exhausts all retries on 5 questions about <b style="color:{TEXT};">Korean cultural identity</b>
    (<i>han</i>, workplace hierarchy) and <b style="color:{TEXT};">Mongolian identity</b>
    (<i>nutag</i>, ger customs) — returning no error. Every other active model answers freely.
    Consistent with server-side content filtering, not a capability gap.
  </div>
</div>
""", unsafe_allow_html=True)
    with _c2:
        st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-top:3px solid {GOLD};border-radius:8px;padding:0.9rem 1rem;height:100%;">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:{GOLD};margin-bottom:0.35rem;">② Soft Censorship</div>
  <div style="font-size:0.86rem;color:{TEXT};font-weight:600;margin-bottom:0.35rem;">Narrative capture in Chinese</div>
  <div style="font-size:0.83rem;color:{TEXT2};line-height:1.65;">
    Asked <i>in Chinese</i> how 1839–1949 is taught in schools, calibration collapses:
    <b style="color:{TEXT};">Chinese avg {fmt(q04_cn_cal)} vs {fmt(q04_west_cal)} for Western</b>
    ({fmt(cal_gap)}-pt gap — the largest in the eval).
    DeepSeek R1 ({fmt(q04_r1_score)}/5) reproduces official CCP framing verbatim.
    Doubao ({fmt(q04_seed_score)}/5) explicitly notes no single narrative is complete.
  </div>
</div>
""", unsafe_allow_html=True)
    with _c3:
        st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-top:3px solid {TEXT2};border-radius:8px;padding:0.9rem 1rem;height:100%;">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:{TEXT2};margin-bottom:0.35rem;">③ Total Collapse</div>
  <div style="font-size:0.86rem;color:{TEXT};font-weight:600;margin-bottom:0.35rem;">DeepSeek R1 on Burmese</div>
  <div style="font-size:0.83rem;color:{TEXT2};line-height:1.65;">
    DeepSeek R1 averages <b style="color:{TEXT};">{fmt(r1_burmese_native)} / 5</b> in native Burmese
    — vs {fmt(dsr1['by_culture'].get('Japanese') if dsr1 else None)} on Japanese and
    {fmt(dsr1['by_culture'].get('Korean') if dsr1 else None)} on Korean. A near-total collapse
    despite performing well on other low-resource languages. Whether this reflects
    training-data absence or sensitivity around Myanmar's political situation
    cannot be separated from scores alone.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="font-size:0.8rem;color:{TEXT2};line-height:1.6;border-top:1px solid {BORDER};padding-top:0.65rem;margin-top:0.1rem;">
  DeepSeek Chat and Qwen answered all questions without hard errors but show the same calibration
  suppression on Q04/zh — confirming a training-policy effect, not a single-model anomaly.
  The pattern is most severe in Chinese-language prompts: <b style="color:{TEXT};">language itself appears to act as a trigger</b> for content constraints.
</div>
""", unsafe_allow_html=True)

# ─── Rankings ──────────────────────────────────────────────────────────────────
with t_rank:
    medals = {1: "🥇 ", 2: "🥈 ", 3: "🥉 "}
    rows = [{
        "Rank":         e["rank"],
        "Model":        medals.get(e["rank"], "") + e["model_short"],
        "Overall":      e["overall_score"],
        "Accuracy":     e["dimensions"]["cultural_accuracy"],
        "Depth":        e["dimensions"]["depth_and_nuance"],
        "Calibration":  e["dimensions"]["epistemic_calibration"],
        "Lang Quality": e["dimensions"]["language_quality"],
        "English":      e["english_score"],
        "Native":       e["native_lang_score"],
        "Drift":        e["cross_lingual_drift"],
        "Trap %":       round(e["trap_fall_rate"] * 100, 0),
    } for e in lb]

    st.caption("Hover any column header for a definition of what it measures.")
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Overall":      st.column_config.ProgressColumn("Overall",      min_value=0, max_value=5, format="%.2f",
                help="Unweighted mean of all 4 dimensions across all questions and both languages. Scale: 1–5."),
            "Accuracy":     st.column_config.ProgressColumn("Accuracy",     min_value=0, max_value=5, format="%.2f",
                help="Cultural Accuracy — factual and cultural correctness; whether the model avoided the known trap embedded in each question. Scale: 1–5."),
            "Depth":        st.column_config.ProgressColumn("Depth",        min_value=0, max_value=5, format="%.2f",
                help="Depth & Nuance — goes beyond surface-level or stereotyped descriptions; demonstrates genuine cultural understanding. Scale: 1–5."),
            "Calibration":  st.column_config.ProgressColumn("Calibration",  min_value=0, max_value=5, format="%.2f",
                help="Epistemic Calibration — appropriate confidence: neither overconfident on contested topics nor so hedged it says nothing. Scale: 1–5."),
            "Lang Quality": st.column_config.ProgressColumn("Lang Quality", min_value=0, max_value=5, format="%.2f",
                help="Language Quality — fluency and cultural idiomaticity of the response. For native-language responses, penalises translated-feeling output. Scale: 1–5."),
            "English":      st.column_config.NumberColumn("English",
                help="Average score across all questions when the prompt was asked in English."),
            "Native":       st.column_config.NumberColumn("Native",
                help="Average score across all questions when the prompt was asked in the culture's native language (Mandarin, Japanese, Korean, Thai, Vietnamese, Indonesian, Burmese, Khmer, or Mongolian)."),
            "Drift":        st.column_config.NumberColumn("Drift",
                help="Cross-lingual drift = English score − Native score, averaged per question. Positive = model performs better in English. The larger the gap, the more the model relies on English as a scaffold for cultural knowledge."),
            "Rank":         st.column_config.NumberColumn("Rank", format="%d"),
            "Trap %":       st.column_config.NumberColumn("Trap %", format="%.0f%%",
                help="Percentage of questions where the model fell into the known cultural trap — e.g. applying Western norms to Asian scenarios, giving a dictionary gloss instead of explaining cultural weight, or reproducing an official narrative uncritically."),
        },
    )

# ─── Dimension Radar ───────────────────────────────────────────────────────────
with t_radar:
    selected = st.multiselect(
        "Select models to compare (up to 5)",
        options=[e["model_short"] for e in lb],
        default=[lb[i]["model_short"] for i in range(min(3, len(lb)))],
        max_selections=5,
    )
    DIMS      = ["cultural_accuracy","depth_and_nuance","epistemic_calibration","language_quality"]
    DIM_LABEL = ["Cultural Accuracy","Depth & Nuance","Epistemic Calibration","Language Quality"]

    fig = go.Figure()
    for e in lb:
        if e["model_short"] not in selected:
            continue
        idx  = next(j for j, x in enumerate(lb) if x["model"] == e["model"])
        vals = [e["dimensions"].get(d, 0) for d in DIMS] + [e["dimensions"].get(DIMS[0], 0)]
        lbls = DIM_LABEL + [DIM_LABEL[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=lbls, fill="toself", name=e["model_short"],
            line=dict(color=COLORS[idx % len(COLORS)], width=2),
            fillcolor=hex_rgba(COLORS[idx % len(COLORS)]),
        ))
    fig.update_layout(
        **plot_layout(height=500, margin=dict(t=30, b=20)),
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(visible=True, range=[0, 5], tickcolor=TEXT2,
                            gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT2)),
            angularaxis=dict(gridcolor=BORDER, linecolor=BORDER),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── Culture Heatmap ───────────────────────────────────────────────────────────
with t_heat:
    CULTURES = ["Chinese","Japanese","Korean","Thai","Vietnamese","Indonesian","Burmese","Khmer","Mongolian"]

    # ── Notable findings ──
    cult_avgs = {
        c: round(sum(e["by_culture"][c] for e in lb if e["by_culture"].get(c)) /
                 sum(1 for e in lb if e["by_culture"].get(c)), 2)
        for c in CULTURES
    }
    weakest_c  = min(cult_avgs, key=cult_avgs.get)
    strongest_c = max(cult_avgs, key=cult_avgs.get)
    ranges = {
        e["model_short"]: max(v for v in e["by_culture"].values() if v) -
                           min(v for v in e["by_culture"].values() if v)
        for e in lb if any(e["by_culture"].values())
    }
    most_consistent = min(ranges, key=ranges.get)
    most_volatile   = max(ranges, key=ranges.get)

    st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-left:3px solid {CINNA};
     border-radius:8px;padding:0.85rem 1.1rem;margin-bottom:0.9rem;font-size:0.82rem;line-height:1.8;">
<b style="color:{TEXT};font-size:0.88rem;">Notable Findings</b><br>
<span style="color:{TEXT2};">
&bull; <b style="color:{TEXT};">Burmese & Khmer are the hardest cultures</b> — avg {cult_avgs['Burmese']} and {cult_avgs['Khmer']} vs {cult_avgs['Vietnamese']} for Vietnamese (the top culture). Low-resource languages expose gaps training data simply doesn't cover.<br>
&bull; <b style="color:{TEXT};">{most_volatile}</b> shows the widest spread across cultures ({ranges[most_volatile]:.2f} pts) — strong on high-resource languages, sharp cliff on Burmese and Khmer.<br>
&bull; <b style="color:{TEXT};">{most_consistent}</b> is the most geographically consistent model (range {ranges[most_consistent]:.2f} pts), suggesting more even cultural coverage in its training.<br>
&bull; <b style="color:{TEXT};">Vietnamese outperforms Chinese</b> ({cult_avgs['Vietnamese']} vs {cult_avgs['Chinese']}) despite being a mid-resource language — possibly due to richer online discourse relative to its speaker base.
</span>
</div>
""", unsafe_allow_html=True)

    clb = sorted(lb, key=company_sort_key)
    row_labels = [f"{COMPANY_MAP.get(e['model_short'],('?',0))[0]} · {e['model_short']}" for e in clb]
    hm_z = [[e["by_culture"].get(c) for c in CULTURES] for e in clb]

    fig = go.Figure(go.Heatmap(
        z=hm_z, x=CULTURES, y=row_labels,
        colorscale=[[0, "#fce8d0"], [0.5, "#6898d8"], [1, "#1838a8"]],
        zmin=1, zmax=5,
        text=[[f"{v:.1f}" if v is not None else "—" for v in row] for row in hm_z],
        texttemplate="%{text}", textfont=dict(size=11),
        hovertemplate="%{y} on %{x}: %{z:.2f}<extra></extra>",
        colorbar=dict(
            title=dict(text="Score", font=dict(color=TEXT)),
            tickfont=dict(color=TEXT),
            outlinecolor=BORDER,
        ),
    ))
    fig.update_layout(
        **plot_layout(height=max(380, len(clb) * 38)),
        xaxis=axis_style(),
        yaxis=axis_style(autorange="reversed"),
    )
    st.caption("Grouped by company · 青花 gradient: pale = low score · deep cobalt = high score")
    st.plotly_chart(fig, use_container_width=True)

# ─── Cross-Lingual Drift ───────────────────────────────────────────────────────
with t_drift:
    all_drifts = [e["cross_lingual_drift"] for e in lb if e.get("cross_lingual_drift") is not None]
    n_positive = sum(1 for d in all_drifts if d > 0)
    avg_d      = round(sum(all_drifts) / len(all_drifts), 2) if all_drifts else 0
    st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-left:3px solid {CINNA};
     border-radius:8px;padding:0.85rem 1.1rem;margin-bottom:0.9rem;font-size:0.82rem;line-height:1.8;">
<b style="color:{TEXT};">Every model scores higher in English than in the native language</b>
<span style="color:{TEXT2};"> — {n_positive}/{len(all_drifts)} models, avg gap
<b style="color:{TEXT};">+{avg_d:.2f} pts</b>.
Current LLMs reason and retrieve cultural knowledge more reliably in English
regardless of the query language.</span>
</div>
""", unsafe_allow_html=True)
    st.caption("Bar color = company. Solid = English score | Outlined = Native language score.")
    clb    = sorted(lb, key=company_sort_key)
    names  = [e["model_short"] for e in clb]
    colors = [model_color(e["model_short"]) for e in clb]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names, x=[e["english_score"] for e in clb],
        name="English", orientation="h",
        marker=dict(color=colors),
    ))
    fig.add_trace(go.Bar(
        y=names, x=[e["native_lang_score"] for e in clb],
        name="Native Language", orientation="h",
        marker=dict(
            color=[hex_rgba(c, 0.2) for c in colors],
            line=dict(color=colors, width=2),
        ),
    ))
    fig.update_layout(
        **plot_layout(barmode="group", height=max(400, len(clb) * 38)),
        xaxis=axis_style(range=[0, 5], dtick=1),
        yaxis=axis_style(),
    )
    fig.update_layout(legend_traceorder="reversed")
    st.plotly_chart(fig, use_container_width=True)

# ─── Language Tiers ────────────────────────────────────────────────────────────
with t_tier:
    st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;
     padding:0.75rem 1.1rem;margin-bottom:0.9rem;font-size:0.82rem;line-height:2.0;">
<b style="color:{TEXT};">Language Resource Tiers</b> — grouped by amount of training data typically available<br>
<span style="color:{JADE};">&#9646;</span> <b style="color:{TEXT};">High-resource</b>
  <span style="color:{TEXT2};">Chinese (ZH) · Japanese (JA) · Korean (KO) — large web corpora, rich literary & cultural text</span><br>
<span style="color:{GOLD};">&#9646;</span> <b style="color:{TEXT};">Mid-resource</b>
  <span style="color:{TEXT2};">Thai (TH) · Vietnamese (VI) · Indonesian (ID) — growing digital presence, moderate training coverage</span><br>
<span style="color:{CINNA};">&#9646;</span> <b style="color:{TEXT};">Low-resource</b>
  <span style="color:{TEXT2};">Burmese (MY) · Khmer (KM) · Mongolian (MN) — limited online data, underrepresented in most pretraining corpora</span>
</div>
""", unsafe_allow_html=True)
    clb   = sorted(lb, key=company_sort_key)
    names = [e["model_short"] for e in clb]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names, y=[e["by_tier"]["high"] for e in clb],
        name="High-resource — Chinese · Japanese · Korean", marker=dict(color=JADE),
    ))
    fig.add_trace(go.Bar(
        x=names, y=[e["by_tier"]["mid"] for e in clb],
        name="Mid-resource — Thai · Vietnamese · Indonesian", marker=dict(color=GOLD),
    ))
    fig.add_trace(go.Bar(
        x=names, y=[e["by_tier"]["low"] for e in clb],
        name="Low-resource — Burmese · Khmer · Mongolian", marker=dict(color=CINNA),
    ))
    fig.update_layout(
        **plot_layout(barmode="group", height=460),
        yaxis=axis_style(
            range=[0, 5], dtick=1,
            title=dict(text="Avg Overall Score (1–5)", font=dict(size=12, color=TEXT2)),
        ),
        xaxis=axis_style(tickangle=-25),
    )
    st.caption("Each bar is the average Overall score (1–5) for that model across the questions in that language tier. Higher = better cultural understanding in those languages.")
    st.plotly_chart(fig, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
# ─── Methodology ───────────────────────────────────────────────────────────────
with t_method:
    from collections import Counter as _Counter
    import json as _json
    from pathlib import Path as _Path

    @st.cache_data(ttl=0)
    def load_questions():
        with open(_Path(__file__).parent / "questions.json", encoding="utf-8") as f:
            return _json.load(f)

    _qs = load_questions()
    _culture_counts  = _Counter(q["culture"]  for q in _qs)
    _tier_counts     = _Counter(q["tier"]      for q in _qs)
    _topic_counts    = _Counter(q["topic"]     for q in _qs)
    _n_scores        = len(load_scores())

    st.markdown("## 🔬 Methodology")
    st.caption("A detailed account of how this evaluation was designed, executed, and scored — for readers who want to assess its validity or reproduce it.")
    st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;
     padding:0.75rem 1.1rem;margin-bottom:0.5rem;font-size:0.82rem;line-height:1.8;">
<b style="color:{TEXT};">About this project</b>
<span style="color:{TEXT2};"> — Built by <b style="color:{TEXT};">Shang Jing Chia</b>
for <b style="color:{TEXT};">BUSGEN 116</b> at <b style="color:{TEXT};">Stanford University</b>.
This evaluation was designed, executed, and analyzed end-to-end: question authorship,
async model elicitation across 12 LLMs via OpenRouter, LLM-as-judge scoring with Claude Opus,
aggregation pipeline, and this interactive dashboard. &nbsp;
<a href="https://github.com/shangjingchia/busgen116-cultural-intelligence-eval"
   target="_blank" style="color:{TEXT2};text-decoration:underline;">View source on GitHub →</a></span>
</div>
""", unsafe_allow_html=True)
    st.divider()

    # ── 1. Motivation ───────────────────────────────────────────────────────────
    st.markdown("### 1. Motivation and Scope")
    st.markdown(f"""
Most LLM benchmarks test knowledge retrieval or reasoning in English. This evaluation targets a different
failure mode: **culturally-indexed knowledge that degrades when the query language changes**, and
**Western-centric framing that surfaces as confident but wrong answers** on Asian cultural questions.

The eval is deliberately narrow — {DATA['n_questions']} questions, 9 cultures, {len(lb)} models — because breadth
without depth produces noise. Each question was designed to have a *known correct answer profile* (expected
themes) and a *known common failure mode* (the trap), making scoring defensible rather than impressionistic.

**What this eval does not claim to measure:**
General cultural knowledge breadth · translation quality · factual encyclopedic recall ·
performance on non-Asian cultures · safety or alignment properties.
""")

    # ── 2. Question Design ──────────────────────────────────────────────────────
    st.markdown("### 2. Question Design")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**By culture**")
        for culture, n in sorted(_culture_counts.items(), key=lambda x: -x[1]):
            st.markdown(f"- {culture}: {n}")
    with col2:
        st.markdown("**By language tier**")
        tier_labels = {"high": "High-resource (ZH/JA/KO)", "mid": "Mid-resource (TH/VI/ID)", "low": "Low-resource (MY/KM/MN)"}
        for tier in ["high","mid","low"]:
            st.markdown(f"- {tier_labels[tier]}: {_tier_counts[tier]}")
    with col3:
        st.markdown("**By topic type**")
        topic_labels = {"social_norms":"Social norms","untranslatable_concept":"Untranslatable concepts",
                        "behavioral_norm":"Behavioral norms","historical_framing":"Historical framing","social_hierarchy":"Social hierarchy"}
        for t, n in sorted(_topic_counts.items(), key=lambda x: -x[1]):
            st.markdown(f"- {topic_labels.get(t,t)}: {n}")

    st.markdown(f"""
Each question has three design components baked in:

**Expected themes** — a list of concepts a strong answer *must* address. For example, a question about
Korean workplace hierarchy expects coverage of *nunchi*, *kibun*, the *hoobae/sunbae* dynamic, and
indirect face-saving strategies. Answers that miss these score lower on `depth_and_nuance`.

**Trap** — the specific error a Western-biased or underinformed model is likely to make. For the same
Korean question, the trap is *"giving generic 'speak up diplomatically' Western corporate advice."*
The judge is explicitly told the trap and asked whether the model fell into it. This produces
the `fell_into_trap` boolean used in trap fall rate calculations.

**Language condition** — every question was asked twice: once in English, once in the native language
of the culture being asked about ({', '.join(set(q['native_language_name'] for q in _qs))}). This generates
the paired scores used to compute cross-lingual drift.

Questions were written to *appear as genuine curiosity* rather than evaluation prompts — no leading
framing, no hints about expected content — so that models respond naturally rather than pattern-matching
to an evaluation context.
""")

    # ── 3. Model Elicitation ────────────────────────────────────────────────────
    st.markdown("### 3. Model Elicitation")
    st.markdown("""
All models were queried via **OpenRouter** using a uniform configuration:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Temperature | 0.3 | Low enough for deterministic-ish answers; avoids pure greedy decoding |
| Max tokens | 800 | Sufficient for a thorough cultural explanation without truncating |
| Concurrency | 5 parallel requests | Respects rate limits while keeping runtime tractable |
| Retries | 3 attempts per call | Handles transient timeouts; persistent failures recorded as errors |
| Timeout | 90 seconds per call | Catches silent hangs (relevant for the Doubao content-filter pattern) |

**System prompt** (identical for all models):
> *"You are a knowledgeable assistant with deep expertise in world cultures, languages, and social norms.
> Answer the following question thoughtfully and in detail. Do not hedge excessively — share your genuine
> understanding even for nuanced cultural topics."*

The system prompt was held constant across all models and both languages. No few-shot examples were
provided. The instruction to *"not hedge excessively"* was included to prevent models from defaulting
to generic disclaimers on sensitive cultural topics, which would inflate calibration scores artificially.
""")

    # ── 4. LLM-as-Judge ─────────────────────────────────────────────────────────
    st.markdown("### 4. LLM-as-Judge Design")
    st.markdown(f"""
**Judge model:** `anthropic/claude-opus-4-5` via OpenRouter
**Total judge calls:** ~{_n_scores} (one per model × question × language combination)

Each response was scored independently. The judge was given:
1. The original question (in the elicitation language)
2. The culture being asked about
3. The list of **expected themes** a good answer should cover
4. The **known trap** / common mistake
5. The model response

The judge returned a structured JSON object — never free-form text — enforced via the system prompt
(`"Always return valid JSON only. No preamble, no markdown fences"`). Malformed responses triggered
a retry; persistent failures were excluded from the leaderboard.

**Judge system persona:**
> *"You are an expert cultural anthropologist and linguist... especially attuned to: subtle stereotyping
> or overgeneralization, Western-centric framing disguised as neutral analysis, missing key
> culturally-specific concepts, confident wrongness vs appropriate epistemic humility, quality
> degradation when a model answers in a non-English language."*

This persona was chosen to make the judge *actively look* for the failure modes the eval is designed
to detect, rather than defaulting to surface fluency as a proxy for quality.
""")

    # ── 5. Scoring Rubric ───────────────────────────────────────────────────────
    st.markdown("### 5. Scoring Rubric")
    st.markdown("""
All dimensions use a **1–5 integer scale**. The overall score is the unweighted mean of the four dimensions, rounded to one decimal place.

| Dimension | What it measures | Score 1 | Score 3 | Score 5 |
|-----------|-----------------|---------|---------|---------|
| **Cultural Accuracy** | Factual/cultural correctness; trap avoidance | Factually wrong or falls directly into trap | Partially correct, misses key nuances | Accurate, avoids trap, covers expected themes |
| **Depth & Nuance** | Goes beyond surface or stereotyped description | Generic, stereotyped, or superficial | Some depth but misses important layers | Rich, specific, demonstrates genuine cultural understanding |
| **Epistemic Calibration** | Appropriate confidence — neither overconfident nor over-hedged | Confidently wrong *or* so hedged it says nothing | Mostly calibrated but some overconfidence or excessive hedging | Confident where warranted, humble where appropriate |
| **Language Quality** | Fluency and cultural idiomaticity of the response language | Broken, unnatural, or machine-translated feel | Functional but stilted or generic | Fluent, natural, culturally idiomatic |

For **Language Quality**, the rubric distinguishes between English responses (clarity and precision) and
native-language responses (natural fluency vs. translated feel, and whether responding in the native
language changes the model's depth or framing). This asymmetry is intentional — it captures a real
quality difference that English-only evals systematically miss.

The judge also returns:
- `key_observation` — 1–2 sentence summary of the most notable strength or weakness
- `missed_themes` — list of expected themes not addressed
- `fell_into_trap` — boolean; used in trap fall rate calculations
""")

    # ── 6. Aggregation ──────────────────────────────────────────────────────────
    st.markdown("### 6. Score Aggregation")
    st.markdown("""
**Overall score** per model: unweighted mean of all valid `overall` scores across all questions and both languages.

**Cross-lingual drift** per model:
```
drift = mean( english_score(q) − native_score(q) ) for all questions q where both scores exist
```
Computed per question first, then averaged — this prevents questions with only one language from
inflating or deflating the drift estimate. A positive drift means the model performs better in English;
negative (rare) means it performs better in the native language.

**By-culture and by-tier scores**: simple averages of `overall` within each group. No weighting by
question difficulty or culture population size.

**Trap fall rate** per model: `trap_falls / trap_total` across all questions where `fell_into_trap`
is not null. Questions where the judge could not determine trap status are excluded from the denominator.

**Leaderboard ranking**: sorted descending by overall score. Ties broken by `cultural_accuracy`.
""")

    # ── 7. Limitations ──────────────────────────────────────────────────────────
    st.markdown("### 7. Limitations and Threats to Validity")
    st.markdown(f"""
**Single judge, no inter-rater reliability.** All {_n_scores} scores come from one judge model
(Claude Opus 4.5). No human raters, no secondary LLM judge, no inter-rater kappa. The judge's
cultural priors — shaped by its own training data — almost certainly introduce systematic bias.
In particular, the judge may be more confident evaluating high-resource language responses and
may underweight subtleties in low-resource languages.

**Small N per culture.** With {DATA['n_questions']} questions distributed across 9 cultures, some cultures
have as few as 1–2 questions (Khmer: 1). Scores for these cultures carry high variance and should
be interpreted cautiously.

**No temperature sweep or sampling.** Each model was queried once per question/language pair at
temperature=0.3. Score variance from stochastic decoding is not characterized. A model that happens
to produce an unusually good or bad response on a given run could shift its leaderboard position.

**Questions are in English and one native language only.** A question about Korean culture asked
in Thai, for instance, is not tested. The "cross-lingual drift" metric specifically captures
English vs. *the relevant* native language — it does not generalize to arbitrary language pairs.

**The judge knows the expected answer.** Providing `expected_themes` and `trap` to the judge
anchors scores to a pre-defined answer profile. This improves consistency but may penalize
genuinely insightful answers that take a different, equally valid approach. It also means the
rubric encodes the question author's cultural assumptions.

**Selection effects in question design.** Questions were chosen to have clear cultural answers.
Questions where cultural norms are genuinely contested, regionally variable, or evolving over
time are harder to include because they resist a well-defined expected-themes list. This biases
the question set toward *canonical* cultural knowledge and away from contested or emergent norms.

**Content filtering is confounded with capability.** For models that timeout on specific questions
(see Political Sensitivity Audit), it is impossible to distinguish a capability gap from a
content policy. Timeouts are treated as missing data and excluded from score aggregation.
""")

    # ── 8. Reproducibility ──────────────────────────────────────────────────────
    st.markdown("### 8. Reproducibility")
    st.markdown("""
The full pipeline is open and resumable:

```
run_eval.py     → results/raw_responses.json   (model responses, one per model×question×lang)
judge.py        → results/scores.json          (scored responses, one per raw response)
leaderboard.py  → results/leaderboard.json     (aggregated leaderboard)
app.py          → this dashboard
```

Each step checks for already-completed work and skips it — re-running any script after a partial
failure picks up where it left off. All intermediate artifacts are stored as JSON and can be
inspected directly.

**To reproduce from scratch**, you need an OpenRouter API key with access to all 12 models.
Approximate cost: **~$18–36** (run_eval: ~$8–18, judge: ~$10–18 at Claude Opus rates).

**To add a new model**, add its OpenRouter model ID to the `MODELS` list in `run_eval.py` and
its display name to `MODELS_SHORT` in `leaderboard.py`, then re-run the pipeline from step 1.
The resumable design means only the new model's calls will be made.
""")

    # ── Question Bank ───────────────────────────────────────────────────────────
    st.markdown("### 9. Question Bank")
    st.markdown("All 20 questions used in this evaluation. Each was asked in English and the relevant native language. **Trap** shows the specific failure mode the question was designed to surface.")

    TIER_BADGE = {
        "high": (f"background:#1a9850;color:#fff", "High-resource"),
        "mid":  (f"background:#c89010;color:#fff", "Mid-resource"),
        "low":  (f"background:#c8280e;color:#fff", "Low-resource"),
    }
    TOPIC_LABEL = {
        "social_norms":           "Social norms",
        "untranslatable_concept": "Untranslatable concept",
        "behavioral_norm":        "Behavioral norm",
        "historical_framing":     "Historical framing",
        "social_hierarchy":       "Social hierarchy",
    }

    for culture in ["Chinese","Japanese","Korean","Thai","Vietnamese","Indonesian","Burmese","Khmer","Mongolian"]:
        culture_qs = [q for q in _qs if q["culture"] == culture]
        if not culture_qs:
            continue
        st.markdown(f"<div style='font-size:0.88rem;font-weight:700;color:{TEXT};margin:1rem 0 0.4rem;'>{culture}</div>", unsafe_allow_html=True)
        for q in culture_qs:
            tier_style, tier_label = TIER_BADGE.get(q["tier"], ("", q["tier"]))
            topic = TOPIC_LABEL.get(q.get("topic",""), q.get("topic",""))
            st.markdown(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;padding:0.85rem 1rem;margin-bottom:0.5rem;">
  <div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.45rem;flex-wrap:wrap;">
    <span style="font-size:0.72rem;font-weight:700;color:{TEXT2};">{q['id']}</span>
    <span style="font-size:0.7rem;padding:0.15rem 0.55rem;border-radius:99px;font-weight:600;{tier_style}">{tier_label}</span>
    <span style="font-size:0.7rem;padding:0.15rem 0.55rem;border-radius:99px;background:{BORDER};color:{TEXT2};font-weight:600;">{topic}</span>
    <span style="font-size:0.7rem;color:{TEXT2};">· {q.get('native_language_name','')}</span>
  </div>
  <div style="font-size:0.85rem;color:{TEXT};line-height:1.6;margin-bottom:0.5rem;">{q['english']}</div>
  <div style="font-size:0.78rem;color:{TEXT2};line-height:1.5;border-top:1px solid {BORDER};padding-top:0.4rem;">
    <b style="color:{CINNA};">Trap:</b> {q['trap']}
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption(
    f"Cultural LLM Eval · {len(lb)} models · {DATA['n_questions']} questions × 2 languages "
    f"· LLM-as-judge (Claude Opus) · Generated {DATA['generated_at'][:10]} "
    f"· Shang Jing Chia · BUSGEN 116 · Stanford University "
    f"· github.com/shangjingchia/busgen116-cultural-intelligence-eval"
)
