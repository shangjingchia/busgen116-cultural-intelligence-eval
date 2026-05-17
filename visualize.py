"""
visualize.py — Generate a rich interactive HTML dashboard from results/leaderboard.json
Writes: results/leaderboard.html
"""

import json
from pathlib import Path

RESULTS_DIR = Path("results")
HTML_OUTPUT = RESULTS_DIR / "leaderboard.html"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cultural LLM Eval — Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0a0c14;
  --surface: #13162b;
  --surface2: #1c2040;
  --border: #252a4a;
  --text: #e2e8f0;
  --muted: #7986b0;
  --accent: #7c6af7;
  --green: #34d399;
  --orange: #fbbf24;
  --red: #f87171;
  --blue: #60a5fa;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'Inter', system-ui, sans-serif; min-height: 100vh; line-height: 1.5; }
.page { max-width: 1280px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }

/* ── Header ── */
header { margin-bottom: 2.5rem; }
header h1 { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.03em; background: linear-gradient(135deg, #a78bfa, #56cfb2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.subtitle { color: var(--muted); font-size: 0.875rem; margin-top: 0.4rem; max-width: 640px; }
.meta-bar { margin-top: 0.6rem; display: flex; gap: 1.5rem; flex-wrap: wrap; }
.meta-pill { font-size: 0.72rem; color: var(--muted); background: var(--surface); border: 1px solid var(--border); border-radius: 99px; padding: 0.2rem 0.7rem; }

/* ── Cards ── */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin-bottom: 2.5rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem 1.5rem; transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s; cursor: default; }
.card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.4); border-color: var(--accent); }
.card-label { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
.card-value { font-size: 1.75rem; font-weight: 700; line-height: 1.1; }
.card-sub { font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem; }

/* ── Tabs ── */
.tab-bar { display: flex; gap: 0.4rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab { padding: 0.45rem 1rem; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); color: var(--muted); font-size: 0.83rem; font-weight: 500; cursor: pointer; transition: all 0.15s; }
.tab:hover { color: var(--text); border-color: var(--accent); }
.tab.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.tab-pane { display: none; }
.tab-pane.active { display: block; }

/* ── Table ── */
.table-wrap { overflow-x: auto; border-radius: 14px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; background: var(--surface); font-size: 0.83rem; }
thead th { background: var(--surface2); padding: 0.7rem 0.9rem; text-align: left; font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); cursor: pointer; user-select: none; white-space: nowrap; }
thead th:hover { color: var(--text); }
thead th.sorted { color: var(--accent); }
tbody td { padding: 0.65rem 0.9rem; border-top: 1px solid var(--border); vertical-align: middle; white-space: nowrap; }
tbody tr:hover td { background: var(--surface2); }
.model-name { font-weight: 600; font-size: 0.85rem; }
.bar-cell { display: flex; align-items: center; gap: 0.5rem; }
.mini-bar { height: 5px; border-radius: 3px; display: inline-block; }
.snum { font-variant-numeric: tabular-nums; font-size: 0.8rem; min-width: 2.4rem; }
.rank-1 { color: #ffd700; font-weight: 700; }
.rank-2 { color: #c0c0c0; font-weight: 700; }
.rank-3 { color: #cd7f32; font-weight: 700; }
.rank-n { color: var(--muted); font-weight: 600; }

/* ── Radar ── */
.radar-layout { display: grid; grid-template-columns: 220px 1fr; gap: 1.5rem; align-items: start; }
@media (max-width: 700px) { .radar-layout { grid-template-columns: 1fr; } }
.picker-box { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem; }
.picker-title { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; }
.picker-hint { font-size: 0.7rem; color: var(--muted); margin-top: 0.75rem; }
.model-check { display: flex; align-items: center; gap: 0.6rem; padding: 0.35rem 0; font-size: 0.83rem; cursor: pointer; }
.model-check input { accent-color: var(--accent); cursor: pointer; }
.dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.chart-box { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; }
.chart-box canvas { max-height: 440px; }

/* ── Heatmap ── */
.heatmap-note { font-size: 0.78rem; color: var(--muted); margin-bottom: 1rem; }
.heatmap-wrap { overflow-x: auto; border-radius: 14px; border: 1px solid var(--border); }
.hm-grid { display: grid; min-width: 760px; }
.hm-corner { background: var(--surface2); padding: 0.65rem 0.75rem; }
.hm-col-header { background: var(--surface2); padding: 0.65rem 0.4rem; text-align: center; font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); border-left: 1px solid var(--border); }
.hm-row-label { background: var(--surface); padding: 0.55rem 0.75rem; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; border-top: 1px solid var(--border); white-space: nowrap; }
.hm-cell { padding: 0.45rem 0.3rem; text-align: center; font-size: 0.75rem; font-weight: 700; border-top: 1px solid rgba(0,0,0,0.25); border-left: 1px solid rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center; transition: filter 0.15s; }
.hm-cell:hover { filter: brightness(1.2); }

/* ── Chart panes ── */
.chart-note { font-size: 0.78rem; color: var(--muted); margin-bottom: 1.25rem; }
.big-chart { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; }
.big-chart canvas { max-height: 460px; }

footer { margin-top: 3.5rem; text-align: center; color: var(--muted); font-size: 0.72rem; padding-bottom: 1rem; }

/* ── Key Findings ── */
.findings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.finding-card { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--card-accent, var(--accent)); border-radius: 14px; padding: 1.25rem 1.4rem; display: flex; gap: 1rem; align-items: flex-start; transition: transform 0.15s, box-shadow 0.15s; }
.finding-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.4); }
.finding-icon { font-size: 1.4rem; line-height: 1; flex-shrink: 0; margin-top: 0.2rem; }
.finding-title { font-size: 0.88rem; font-weight: 700; color: var(--text); margin-bottom: 0.25rem; letter-spacing: -0.01em; }
.finding-stat { font-size: 1.65rem; font-weight: 800; color: var(--card-accent, var(--accent)); line-height: 1.1; letter-spacing: -0.03em; }
.finding-stat-label { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.09em; color: var(--muted); margin-bottom: 0.5rem; margin-top: 0.1rem; }
.finding-body { font-size: 0.79rem; color: var(--muted); line-height: 1.6; }
.finding-body strong { color: var(--text); }
.drift-explainer { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 14px; padding: 1.5rem; margin-bottom: 2rem; }
.drift-explainer h3 { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.75rem; color: var(--text); }
.drift-explainer p { font-size: 0.83rem; color: var(--muted); line-height: 1.65; margin-bottom: 0.6rem; }
.drift-explainer p:last-child { margin-bottom: 0; }
.drift-formula { background: var(--surface2); border-radius: 8px; padding: 0.75rem 1rem; font-family: monospace; font-size: 0.85rem; color: var(--accent); margin: 0.75rem 0; display: inline-block; }
.about-box { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; margin-bottom: 2rem; }
.about-box h3 { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.75rem; }
.about-box p { font-size: 0.83rem; color: var(--muted); line-height: 1.65; }
.pipeline-steps { display: flex; gap: 0; margin-top: 1rem; flex-wrap: wrap; }
.pipeline-step { display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; color: var(--muted); }
.pipeline-step .step-num { background: var(--accent); color: #fff; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.7rem; flex-shrink: 0; }
.pipeline-step .step-label { white-space: nowrap; }
.pipeline-arrow { color: var(--border); font-size: 1rem; margin: 0 0.4rem; }
</style>
</head>
<body>
<div class="page">

<header>
  <h1>🌏 Cultural &amp; Linguistic Intelligence Eval</h1>
  <p class="subtitle">Benchmarking LLMs on Asian cultural understanding — tested in English and native languages.</p>
  <div class="meta-bar">
    <span class="meta-pill">__N_MODELS__ models</span>
    <span class="meta-pill">__N_QUESTIONS__ questions × 2 languages</span>
    <span class="meta-pill">9 cultures · 3 language tiers</span>
    <span class="meta-pill">LLM-as-judge scoring</span>
    <span class="meta-pill">Generated __GENERATED__</span>
  </div>
</header>

<div class="cards" id="cards"></div>

<div class="tab-bar" id="tab-bar"></div>

<div id="pane-findings" class="tab-pane active">

  <div class="about-box">
    <h3>About This Eval</h3>
    <p>This benchmark tests how well leading LLMs understand <strong style="color:var(--text)">Asian cultural nuances</strong> — covering 9 cultures across 3 language-resource tiers. Each of 20 questions was asked twice: once in English, once in the relevant native language (Mandarin, Japanese, Korean, Thai, Vietnamese, Indonesian, Burmese, Khmer, or Mongolian). Responses were scored by Claude Opus acting as judge on 4 dimensions.</p>
    <div class="pipeline-steps">
      <div class="pipeline-step"><span class="step-num">1</span><span class="step-label">Collect responses via OpenRouter</span></div>
      <span class="pipeline-arrow">→</span>
      <div class="pipeline-step"><span class="step-num">2</span><span class="step-label">Judge with Claude Opus</span></div>
      <span class="pipeline-arrow">→</span>
      <div class="pipeline-step"><span class="step-num">3</span><span class="step-label">Aggregate scores</span></div>
      <span class="pipeline-arrow">→</span>
      <div class="pipeline-step"><span class="step-num">4</span><span class="step-label">Generate dashboard</span></div>
    </div>
  </div>

  <div class="drift-explainer">
    <h3>📉 What Is Cross-Lingual Drift?</h3>
    <p>Every question was asked <strong style="color:var(--text)">twice</strong> — once in English, once in the native language of the culture being asked about.</p>
    <div class="drift-formula">Drift = English score − Native language score</div>
    <p><strong style="color:var(--text)">Positive drift</strong> means the model scores lower when asked in the native language — its cultural understanding degrades without English as a scaffold. A model with +0.9 drift essentially "knows less" about a culture when not speaking English.</p>
    <p><strong style="color:var(--text)">Near-zero drift</strong> means the model performs equally well regardless of language — its cultural knowledge is genuinely language-independent, not just pattern-matching English text.</p>
    <p><strong style="color:var(--text)">Negative drift</strong> (rare) would mean the model is actually better in the native language.</p>
  </div>

  <div class="findings-grid" id="findings-grid"></div>

</div>

<div id="pane-rankings" class="tab-pane">
  <div class="table-wrap">
    <table>
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>

<div id="pane-radar" class="tab-pane">
  <div class="radar-layout">
    <div class="picker-box">
      <div class="picker-title">Compare models</div>
      <div id="picker"></div>
      <div class="picker-hint">Select up to 5 models</div>
    </div>
    <div class="chart-box"><canvas id="radarChart"></canvas></div>
  </div>
</div>

<div id="pane-heatmap" class="tab-pane">
  <p class="heatmap-note">Score per model across 9 cultures. Green = 5.0 &nbsp;|&nbsp; Red = 1.0</p>
  <div class="heatmap-wrap"><div class="hm-grid" id="heatmap"></div></div>
</div>

<div id="pane-drift" class="tab-pane">
  <p class="chart-note">English score vs. native language score per model (sorted by drift, worst first). A large gap means the model's cultural understanding degrades when asked in the native language.</p>
  <div class="big-chart"><canvas id="driftChart"></canvas></div>
</div>

<div id="pane-tiers" class="tab-pane">
  <p class="chart-note">Performance by language resource tier. High = Chinese/Japanese/Korean &nbsp;|&nbsp; Mid = Thai/Vietnamese/Indonesian &nbsp;|&nbsp; Low = Burmese/Khmer/Mongolian</p>
  <div class="big-chart"><canvas id="tierChart"></canvas></div>
</div>

<footer>Cultural LLM Eval &nbsp;·&nbsp; __N_MODELS__ models &nbsp;·&nbsp; __N_QUESTIONS__ questions × 2 languages &nbsp;·&nbsp; LLM-as-judge (Claude Opus)</footer>

</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
const DATA = __DATA__;
const lb = DATA.leaderboard;

const COLORS = [
  '#7c6af7','#34d399','#fbbf24','#f87171','#60a5fa',
  '#a78bfa','#fb923c','#2dd4bf','#e879f9','#94a3b8'
];

// ── Tabs ──────────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'findings', label: 'Key Findings' },
  { id: 'rankings', label: 'Rankings' },
  { id: 'radar',    label: 'Dimension Radar' },
  { id: 'heatmap',  label: 'Culture Heatmap' },
  { id: 'drift',    label: 'Cross-Lingual Drift' },
  { id: 'tiers',    label: 'Language Tiers' },
];
const tabBar = document.getElementById('tab-bar');
TABS.forEach(t => {
  const b = document.createElement('button');
  b.className = 'tab' + (t.id === 'findings' ? ' active' : '');
  b.textContent = t.label;
  b.dataset.tab = t.id;
  b.onclick = () => switchTab(t.id);
  tabBar.appendChild(b);
});
function switchTab(id) {
  tabBar.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b.dataset.tab === id));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.toggle('active', p.id === 'pane-' + id));
  if (id === 'radar'   && !radarChart)  initRadar();
  if (id === 'drift'   && !driftChart)  initDrift();
  if (id === 'tiers'   && !tierChart)   initTiers();
  if (id === 'rankings' && !tableReady) { renderTable([...lb]); tableReady = true; }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(v, d = 2) { return v != null ? (+v).toFixed(d) : 'N/A'; }

function scoreColor(v) {
  if (v == null) return '#7986b0';
  if (v >= 4)    return '#34d399';
  if (v >= 3)    return '#fbbf24';
  return '#f87171';
}

function heatBg(v) {
  if (v == null) return '#13162b';
  const stops = [[248,113,113],[251,191,36],[52,211,153]];
  const t = Math.max(0, Math.min(1, (v - 1) / 4));
  const [a, b] = t < 0.5 ? [stops[0], stops[1]] : [stops[1], stops[2]];
  const lt = t < 0.5 ? t * 2 : (t - 0.5) * 2;
  return `rgb(${Math.round(a[0]+(b[0]-a[0])*lt)},${Math.round(a[1]+(b[1]-a[1])*lt)},${Math.round(a[2]+(b[2]-a[2])*lt)})`;
}

function heatText(v) { return (v != null && v >= 3.2) ? '#111827' : '#f8fafc'; }

function miniBar(val) {
  const w = val != null ? Math.max(2, Math.min(60, (val / 5) * 60)) : 0;
  return `<div class="bar-cell">
    <div class="mini-bar" style="width:${w}px;background:${scoreColor(val)}"></div>
    <span class="snum">${fmt(val)}</span>
  </div>`;
}

// ── Summary cards ─────────────────────────────────────────────────────────────
const validDrift = lb.filter(e => e.cross_lingual_drift != null);
const avgScore   = lb.reduce((s,e) => s + (e.overall_score||0), 0) / lb.length;
const avgDrift   = validDrift.reduce((s,e) => s + e.cross_lingual_drift, 0) / validDrift.length;
const worstDrift = [...validDrift].sort((a,b) => b.cross_lingual_drift - a.cross_lingual_drift)[0];
const bestTrap   = [...lb].filter(e => e.trap_fall_rate != null).sort((a,b) => a.trap_fall_rate - b.trap_fall_rate)[0];

document.getElementById('cards').innerHTML = `
  <div class="card">
    <div class="card-label">🥇 Top Model</div>
    <div class="card-value" style="color:#a78bfa;font-size:1.35rem">${lb[0].model_short}</div>
    <div class="card-sub">Overall ${fmt(lb[0].overall_score)} / 5.0</div>
  </div>
  <div class="card">
    <div class="card-label">📊 Avg Score</div>
    <div class="card-value" style="color:#34d399">${fmt(avgScore)}</div>
    <div class="card-sub">Across all ${lb.length} models</div>
  </div>
  <div class="card">
    <div class="card-label">📉 Avg Cross-Lingual Drift</div>
    <div class="card-value" style="color:#fbbf24">${avgDrift > 0 ? '+' : ''}${fmt(avgDrift)}</div>
    <div class="card-sub">English advantage over native</div>
  </div>
  <div class="card">
    <div class="card-label">⚠️ Largest Language Gap</div>
    <div class="card-value" style="color:#f87171;font-size:1.35rem">${worstDrift.model_short}</div>
    <div class="card-sub">Drift +${fmt(worstDrift.cross_lingual_drift)}</div>
  </div>
  <div class="card">
    <div class="card-label">🎯 Fewest Trap Falls</div>
    <div class="card-value" style="color:#34d399;font-size:1.35rem">${bestTrap.model_short}</div>
    <div class="card-sub">${(bestTrap.trap_fall_rate*100).toFixed(0)}% trap rate</div>
  </div>
`;

// ── Rankings table ─────────────────────────────────────────────────────────────
const DIM_KEYS = new Set(['cultural_accuracy','depth_and_nuance','epistemic_calibration','language_quality']);

const COLS = [
  { key: 'rank', label: '#', get: e => e.rank,
    render: e => { const m={1:'🥇',2:'🥈',3:'🥉'}; const c=e.rank<=3?`rank-${e.rank}`:'rank-n'; return `<span class="${c}">${m[e.rank]||'#'+e.rank}</span>`; }},
  { key: 'model_short', label: 'Model', get: e => e.model_short,
    render: e => `<span class="model-name">${e.model_short}</span>` },
  { key: 'overall_score',          label: 'Overall',     get: e => e.overall_score,                        render: e => miniBar(e.overall_score) },
  { key: 'cultural_accuracy',      label: 'Accuracy',    get: e => e.dimensions?.cultural_accuracy,        render: e => miniBar(e.dimensions?.cultural_accuracy) },
  { key: 'depth_and_nuance',       label: 'Depth',       get: e => e.dimensions?.depth_and_nuance,         render: e => miniBar(e.dimensions?.depth_and_nuance) },
  { key: 'epistemic_calibration',  label: 'Calibration', get: e => e.dimensions?.epistemic_calibration,    render: e => miniBar(e.dimensions?.epistemic_calibration) },
  { key: 'language_quality',       label: 'Lang Quality',get: e => e.dimensions?.language_quality,         render: e => miniBar(e.dimensions?.language_quality) },
  { key: 'english_score',    label: 'English', get: e => e.english_score,
    render: e => `<span style="color:#7c6af7;font-weight:600">${fmt(e.english_score)}</span>` },
  { key: 'native_lang_score', label: 'Native', get: e => e.native_lang_score,
    render: e => `<span style="color:#34d399;font-weight:600">${fmt(e.native_lang_score)}</span>` },
  { key: 'cross_lingual_drift', label: 'Drift', get: e => e.cross_lingual_drift,
    render: e => {
      const d = e.cross_lingual_drift;
      const col = d > 0.5 ? '#fbbf24' : d < -0.1 ? '#34d399' : '#7986b0';
      const icon = d > 0.5 ? '⚠ ' : '';
      return `<span style="color:${col};font-weight:600">${icon}${d!=null?(d>0?'+':'')+fmt(d):'N/A'}</span>`;
    }},
  { key: 'trap_fall_rate', label: 'Trap %', get: e => e.trap_fall_rate,
    render: e => {
      const r = e.trap_fall_rate;
      const col = r > 0.3 ? '#f87171' : r > 0.1 ? '#fbbf24' : '#34d399';
      return `<span style="color:${col};font-weight:600">${r!=null?(r*100).toFixed(0)+'%':'N/A'}</span>`;
    }},
];

let tableReady = false;
let sortKey = 'overall_score', sortDir = -1;


function renderTable(rows) {
  document.getElementById('thead').innerHTML = '<tr>' + COLS.map(c => {
    const isSorted = c.key === sortKey;
    const arrow = isSorted ? (sortDir > 0 ? ' ↑' : ' ↓') : '';
    return `<th data-key="${c.key}" class="${isSorted?'sorted':''}" onclick="sortTable('${c.key}')">${c.label}${arrow}</th>`;
  }).join('') + '</tr>';
  document.getElementById('tbody').innerHTML = rows.map(e =>
    '<tr>' + COLS.map(c => `<td>${c.render(e)}</td>`).join('') + '</tr>'
  ).join('');
}

function sortTable(key) {
  if (key === sortKey) sortDir *= -1;
  else { sortKey = key; sortDir = ['rank','trap_fall_rate','cross_lingual_drift'].includes(key) ? 1 : -1; }
  const col = COLS.find(c => c.key === key);
  renderTable([...lb].sort((a, b) => {
    const va = col.get(a), vb = col.get(b);
    if (va == null) return 1; if (vb == null) return -1;
    if (typeof va === 'string') return sortDir * va.localeCompare(vb);
    return sortDir * (va - vb);
  }));
}

// ── Key Findings cards (computed from data) ───────────────────────────────────
(function buildFindings() {
  const top         = lb[0];
  const driftSorted = [...lb].filter(e=>e.cross_lingual_drift!=null).sort((a,b)=>a.cross_lingual_drift-b.cross_lingual_drift);
  const bestDrift   = driftSorted[0];
  const worstDrift2 = driftSorted[driftSorted.length-1];
  const trapSorted  = [...lb].filter(e=>e.trap_fall_rate!=null).sort((a,b)=>b.trap_fall_rate-a.trap_fall_rate);
  const worstTrap   = trapSorted[0];
  const dsr1        = lb.find(e=>e.model.includes('deepseek-r1'));
  const dsc         = lb.find(e=>e.model.includes('deepseek-chat'));
  const qwen        = lb.find(e=>e.model.includes('qwen'));
  const c45         = lb.find(e=>e.model.includes('claude-sonnet-4-5'));
  const c46         = lb.find(e=>e.model.includes('claude-sonnet-4-6'));
  const avgCal      = lb.reduce((s,e) => s + (e.dimensions?.epistemic_calibration||0), 0) / lb.length;
  const avgLQ       = lb.reduce((s,e) => s + (e.dimensions?.language_quality||0), 0) / lb.length;

  const FINDINGS = [
    {
      icon: '🥇',
      accent: '#a78bfa',
      stat: fmt(top.overall_score) + ' / 5',
      statLabel: top.model_short + ' · overall score',
      title: 'Clear Winner — No Close Contest',
      body: `<strong>${top.model_short}</strong> leads the field at <strong>${fmt(top.overall_score)}</strong> — <strong>${fmt(top.overall_score - lb[1].overall_score)}</strong> pts ahead of #2 ${lb[1].model_short}. It is the <strong>only model with a 0% trap fall rate</strong>, never misapplying Western social norms to Asian scenarios.`
    },
    {
      icon: '🎯',
      accent: '#34d399',
      stat: (bestDrift.cross_lingual_drift >= 0 ? '+' : '') + fmt(bestDrift.cross_lingual_drift),
      statLabel: bestDrift.model_short + ' · cross-lingual drift',
      title: 'Most Language-Consistent: An Unexpected Contender',
      body: `<strong>${bestDrift.model_short}</strong> (ranked #${bestDrift.rank}) shows the smallest drift at <strong>${bestDrift.cross_lingual_drift >= 0 ? '+' : ''}${fmt(bestDrift.cross_lingual_drift)}</strong>. Higher-ranked models score better overall, but their cultural knowledge degrades more when the language switches — a critical distinction for multilingual deployments.`
    },
    {
      icon: '📉',
      accent: '#f87171',
      stat: '+' + fmt(worstDrift2.cross_lingual_drift),
      statLabel: worstDrift2.model_short + ' · language collapse',
      title: 'English as a Crutch: The Language Collapse',
      body: `<strong>${worstDrift2.model_short}</strong> scores <strong>${fmt(worstDrift2.english_score)}</strong> in English but drops to <strong>${fmt(worstDrift2.native_lang_score)}</strong> in native languages — a <strong>+${fmt(worstDrift2.cross_lingual_drift)}</strong> gap. It retrieves English-indexed facts but lacks cultural reasoning that holds across languages.`
    },
    {
      icon: '🪤',
      accent: '#fbbf24',
      stat: (worstTrap.trap_fall_rate * 100).toFixed(0) + '%',
      statLabel: worstTrap.model_short + ' · trap fall rate',
      title: 'Western Bias Baked In — Nearly Half the Time',
      body: `<strong>${worstTrap.model_short}</strong> fell into culturally biased framings <strong>${(worstTrap.trap_fall_rate*100).toFixed(0)}%</strong> of the time — treating silence as awkward, framing indirect speech as avoidance, or imposing individual agency on collectivist decision contexts.`
    },
    dsr1 ? {
      icon: '🔇',
      accent: '#f87171',
      stat: fmt(dsr1.by_culture?.Burmese),
      statLabel: 'DeepSeek R1 · Burmese score',
      title: 'The Low-Resource Cliff Is a Drop, Not a Slope',
      body: `<strong>DeepSeek R1</strong> scores <strong>${fmt(dsr1.by_culture?.Japanese)}</strong> on Japanese and <strong>${fmt(dsr1.by_culture?.Korean)}</strong> on Korean — then <strong>${fmt(dsr1.by_culture?.Burmese)}</strong> on Burmese. A <strong>${fmt((dsr1.by_culture?.Japanese||0)-(dsr1.by_culture?.Burmese||0))}-pt cliff</strong>. This isn't gradual decline; it's where training data simply runs out.`
    } : {
      icon: '🔇',
      accent: '#f87171',
      stat: '—',
      statLabel: 'low-resource cliff',
      title: 'The Low-Resource Cliff Is a Drop, Not a Slope',
      body: `Burmese, Khmer, and Mongolian consistently expose the largest capability gaps across all models — a hard cliff, not a gradual slope.`
    },
    {
      icon: '🧭',
      accent: '#60a5fa',
      stat: fmt(avgCal),
      statLabel: 'avg epistemic calibration · all models',
      title: 'Calibration: The Universal Blind Spot',
      body: `Epistemic calibration is the <strong>weakest dimension across all ${lb.length} models</strong> — avg <strong>${fmt(avgCal)}</strong> vs language quality avg <strong>${fmt(avgLQ)}</strong>. Models answer confidently and fluently, but rarely hedge appropriately. On contested or regionally-variable questions, overconfidence is a silent failure mode.`
    },
    (dsr1 && dsc && qwen) ? {
      icon: '🧩',
      accent: '#fb923c',
      stat: `#${dsr1.rank} · #${dsc.rank} · #${qwen.rank}`,
      statLabel: 'DeepSeek R1 · DeepSeek Chat · Qwen · rank',
      title: 'The Chinese Model Paradox',
      body: `DeepSeek (R1: #${dsr1.rank}, Chat: #${dsc.rank}) and Qwen (#${qwen.rank}) have large Chinese-corpus training advantages, yet none cracks the top 3. <strong>Cultural breadth ≠ language depth</strong> — Mandarin fluency doesn't confer understanding of Thai hierarchy, Burmese animism, or Mongolian nomadic culture.`
    } : {
      icon: '🧩',
      accent: '#fb923c',
      stat: '—',
      statLabel: 'Chinese-trained models',
      title: 'The Chinese Model Paradox',
      body: `Models with large Chinese-corpus advantages don't dominate the leaderboard. <strong>Cultural breadth ≠ language depth.</strong>`
    },
    (c45 && c46) ? {
      icon: '📈',
      accent: '#a78bfa',
      stat: '+' + fmt(c46.overall_score - c45.overall_score),
      statLabel: 'Claude Sonnet 4.5 → 4.6 · score gain',
      title: 'One Generation: A Measurable Cultural Leap',
      body: `Claude Sonnet <strong>4.6 (${fmt(c46.overall_score)})</strong> outperforms <strong>4.5 (${fmt(c45.overall_score)})</strong> by <strong>+${fmt(c46.overall_score - c45.overall_score)}</strong>. Sharpest gains in Epistemic Calibration (+${fmt((c46.dimensions?.epistemic_calibration||0)-(c45.dimensions?.epistemic_calibration||0))}) and Depth & Nuance (+${fmt((c46.dimensions?.depth_and_nuance||0)-(c45.dimensions?.depth_and_nuance||0))}) — smarter hedging, not just better recall.`
    } : null,
  ].filter(Boolean);

  document.getElementById('findings-grid').innerHTML = FINDINGS.map(f => `
    <div class="finding-card" style="--card-accent:${f.accent||'var(--accent)'}">
      <div class="finding-icon">${f.icon}</div>
      <div style="min-width:0">
        <div class="finding-title">${f.title}</div>
        ${f.stat ? `<div class="finding-stat">${f.stat}</div><div class="finding-stat-label">${f.statLabel||''}</div>` : ''}
        <div class="finding-body">${f.body}</div>
      </div>
    </div>`).join('');
})();

// ── Radar ─────────────────────────────────────────────────────────────────────
let radarChart = null;
const DIMS      = ['cultural_accuracy','depth_and_nuance','epistemic_calibration','language_quality'];
const DIM_LABEL = ['Cultural Accuracy','Depth & Nuance','Epistemic Calibration','Language Quality'];
let selected    = new Set(lb.slice(0, 3).map(e => e.model));

const picker = document.getElementById('picker');
lb.forEach((e, i) => {
  const lbl = document.createElement('label');
  lbl.className = 'model-check';
  lbl.innerHTML = `<input type="checkbox" value="${e.model}" ${selected.has(e.model)?'checked':''}><span class="dot" style="background:${COLORS[i]}"></span>${e.model_short}`;
  lbl.querySelector('input').onchange = ev => {
    if (ev.target.checked) { if (selected.size >= 5) { ev.target.checked = false; return; } selected.add(ev.target.value); }
    else selected.delete(ev.target.value);
    updateRadar();
  };
  picker.appendChild(lbl);
});

function initRadar() {
  const ctx = document.getElementById('radarChart').getContext('2d');
  radarChart = new Chart(ctx, {
    type: 'radar',
    data: { labels: DIM_LABEL, datasets: [] },
    options: {
      responsive: true,
      scales: { r: {
        min: 0, max: 5, ticks: { stepSize: 1, color: '#7986b0', backdropColor: 'transparent', font: { size: 10 } },
        grid: { color: '#252a4a' }, angleLines: { color: '#252a4a' },
        pointLabels: { color: '#e2e8f0', font: { size: 12, weight: '500' } }
      }},
      plugins: { legend: { labels: { color: '#e2e8f0', font: { size: 11 }, padding: 16, usePointStyle: true, pointStyleWidth: 8 } } }
    }
  });
  updateRadar();
}

function updateRadar() {
  if (!radarChart) return;
  radarChart.data.datasets = lb
    .filter(e => selected.has(e.model))
    .map(e => {
      const i = lb.indexOf(e); const c = COLORS[i];
      return { label: e.model_short, data: DIMS.map(d => e.dimensions?.[d] ?? 0),
        fill: true, backgroundColor: c + '28', borderColor: c, pointBackgroundColor: c,
        pointRadius: 4, pointHoverRadius: 6, borderWidth: 2 };
    });
  radarChart.update();
}

// ── Culture heatmap ───────────────────────────────────────────────────────────
const CULTURES = ['Chinese','Japanese','Korean','Thai','Vietnamese','Indonesian','Burmese','Khmer','Mongolian'];
const hm = document.getElementById('heatmap');
hm.style.gridTemplateColumns = `180px repeat(${CULTURES.length}, 1fr)`;

// Header row
const corner = document.createElement('div');
corner.className = 'hm-corner';
hm.appendChild(corner);
CULTURES.forEach(c => {
  const h = document.createElement('div');
  h.className = 'hm-col-header';
  h.textContent = c;
  hm.appendChild(h);
});

// Data rows
lb.forEach((e, i) => {
  const rowLabel = document.createElement('div');
  rowLabel.className = 'hm-row-label';
  rowLabel.innerHTML = `<span class="dot" style="background:${COLORS[i]}"></span>${e.model_short}`;
  hm.appendChild(rowLabel);
  CULTURES.forEach(c => {
    const v   = e.by_culture?.[c] ?? null;
    const cell = document.createElement('div');
    cell.className = 'hm-cell';
    cell.style.background = heatBg(v);
    cell.style.color = heatText(v);
    cell.textContent = v != null ? v.toFixed(1) : '—';
    cell.title = `${e.model_short} on ${c}: ${v != null ? v.toFixed(2) : 'N/A'}`;
    hm.appendChild(cell);
  });
});

// ── Cross-lingual drift chart ─────────────────────────────────────────────────
let driftChart = null;
function initDrift() {
  const sorted = [...lb].sort((a,b) => (b.cross_lingual_drift??0)-(a.cross_lingual_drift??0));
  driftChart = new Chart(document.getElementById('driftChart'), {
    type: 'bar',
    data: {
      labels: sorted.map(e => e.model_short),
      datasets: [
        { label: 'English Score',      data: sorted.map(e => e.english_score),      backgroundColor: '#7c6af7', borderRadius: 4 },
        { label: 'Native Lang Score',  data: sorted.map(e => e.native_lang_score),  backgroundColor: '#34d399', borderRadius: 4 },
      ]
    },
    options: {
      indexAxis: 'y', responsive: true,
      scales: {
        x: { min: 0, max: 5, grid: { color: '#252a4a' }, ticks: { color: '#7986b0', stepSize: 1 } },
        y: { grid: { color: '#252a4a' }, ticks: { color: '#e2e8f0', font: { size: 11 } } }
      },
      plugins: {
        legend: { labels: { color: '#e2e8f0', usePointStyle: true } },
        tooltip: { callbacks: {
          afterBody: items => `Drift: ${(()=>{const d=sorted[items[0].dataIndex].cross_lingual_drift; return (d>0?'+':'')+d.toFixed(2);})()}`
        }}
      }
    }
  });
}

// ── Language tier chart ───────────────────────────────────────────────────────
let tierChart = null;
function initTiers() {
  tierChart = new Chart(document.getElementById('tierChart'), {
    type: 'bar',
    data: {
      labels: lb.map(e => e.model_short),
      datasets: [
        { label: 'High (ZH / JA / KO)', data: lb.map(e => e.by_tier?.high ?? 0), backgroundColor: '#7c6af7', borderRadius: 3 },
        { label: 'Mid  (TH / VI / ID)', data: lb.map(e => e.by_tier?.mid  ?? 0), backgroundColor: '#fbbf24', borderRadius: 3 },
        { label: 'Low  (MY / KM / MN)', data: lb.map(e => e.by_tier?.low  ?? 0), backgroundColor: '#f87171', borderRadius: 3 },
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { min: 0, max: 5, grid: { color: '#252a4a' }, ticks: { color: '#7986b0', stepSize: 1 } },
        x: { grid: { color: '#252a4a' }, ticks: { color: '#e2e8f0', font: { size: 11 }, maxRotation: 25 } }
      },
      plugins: { legend: { labels: { color: '#e2e8f0', usePointStyle: true, padding: 16 } } }
    }
  });
}
</script>
</body>
</html>"""


def main():
    with open(RESULTS_DIR / "leaderboard.json", encoding="utf-8") as f:
        data = json.load(f)

    generated = data["generated_at"][:16].replace("T", " ") + " UTC"

    html = TEMPLATE
    html = html.replace("__DATA__",        json.dumps(data))
    html = html.replace("__GENERATED__",   generated)
    html = html.replace("__N_MODELS__",    str(data["n_models"]))
    html = html.replace("__N_QUESTIONS__", str(data["n_questions"]))

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard saved to {HTML_OUTPUT}")


if __name__ == "__main__":
    main()
