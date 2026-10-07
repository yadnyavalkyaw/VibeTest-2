"""Self-contained HTML report (Paperly 2026 Academic SaaS Aesthetic).
Offline, single-file leave-behind artifact with print-ready A4 CSS and dark obsidian styling.
"""
from __future__ import annotations

from jinja2 import BaseLoader, Environment, select_autoescape

from ..schemas.scan import ScanResult

_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VibeTest report — {{ result.target_url }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400..800;1,400..800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --bg: #070b13;
    --card: #0f1523;
    --ink: #f1f5f9;
    --muted: #828f9f;
    --line: #1c2638;
    --line-light: #25334a;
    --accent: #14b8a6;
    --critical: #f43f5e;
    --high: #fb923c;
    --medium: #facc15;
    --low: #38bdf8;
    --info: #94a3b8;
  }
  @media print {
    body { background: #fff !important; color: #0f172a !important; font-size: 12px !important; }
    .meta, .card, .finding { background: #fff !important; border-color: #cbd5e1 !important; color: #0f172a !important; box-shadow: none !important; }
    pre, .evidence, .explanation { background: #f8fafc !important; color: #0f172a !important; border-color: #e2e8f0 !important; }
    h1, .finding-title { color: #0f172a !important; }
  }
  body {
    background: radial-gradient(1000px 500px at 50% -100px, rgba(20, 184, 166, 0.08), transparent 70%), var(--bg);
    color: var(--ink);
    font-family: var(--font-sans);
    font-size: 14.5px;
    max-width: 980px; margin: 2.5rem auto 3.5rem; padding: 0 1.4rem; line-height: 1.6;
    letter-spacing: -0.012em;
    -webkit-font-smoothing: antialiased;
  }
  h1 { font-size: 1.75rem; font-weight: 800; color: #fff; margin-bottom: .4rem; letter-spacing: -0.03em; }
  .meta {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 12px; padding: 1.25rem 1.45rem; margin-bottom: 1.6rem;
    font-size: .88rem; color: var(--muted);
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
  }
  .meta strong { color: #fff; }
  .meta .badge-row { display: flex; gap: .45rem; margin-top: .7rem; flex-wrap: wrap; }
  .tech-pill {
    background: #151e2e; color: #93c5fd; border: 1px solid #233149;
    padding: .24rem .72rem; border-radius: 999px; font-size: .75rem; font-weight: 650;
    letter-spacing: .01em;
  }
  .finding {
    background: var(--card); border: 1px solid var(--line);
    border-left: 5px solid var(--line); border-radius: 12px;
    padding: 1.25rem 1.45rem; margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
  }
  .sev-critical { border-left-color: var(--critical); }
  .sev-high { border-left-color: var(--high); }
  .sev-medium { border-left-color: var(--medium); }
  .sev-low { border-left-color: var(--low); }
  .sev-info { border-left-color: var(--info); }
  .badge {
    display: inline-block; padding: .24rem .65rem; border-radius: 999px;
    font-size: .7rem; font-weight: 750; text-transform: uppercase; letter-spacing: .06em;
  }
  .badge.critical { background: rgba(244,63,94,.12); color: #fda4af; border: 1px solid rgba(244,63,94,.32); }
  .badge.high { background: rgba(251,146,60,.12); color: #fdba74; border: 1px solid rgba(251,146,60,.32); }
  .badge.medium { background: rgba(250,204,21,.12); color: #fef08a; border: 1px solid rgba(250,204,21,.32); }
  .badge.low { background: rgba(56,189,248,.12); color: #7dd3fc; border: 1px solid rgba(56,189,248,.32); }
  .badge.info { background: rgba(148,163,184,.12); color: #cbd5e1; border: 1px solid rgba(148,163,184,.32); }
  .title-row { display: flex; align-items: center; gap: .65rem; margin-bottom: .35rem; flex-wrap: wrap; }
  .finding-title { font-size: 1.1rem; font-weight: 750; color: #fff; letter-spacing: -0.02em; }
  .category-mono { font-family: var(--font-mono); font-size: .8rem; color: var(--muted); margin-bottom: .65rem; letter-spacing: -0.01em; }
  .explanation {
    background: #090e18; border: 1px solid var(--line); border-radius: 8px;
    padding: .85rem 1.05rem; font-size: .88rem; color: #cbd5e1; margin: .65rem 0; line-height: 1.6;
  }
  details { margin: .6rem 0; border: 1px solid var(--line); border-radius: 8px; padding: .6rem .95rem; background: #080d16; }
  details summary { cursor: pointer; color: var(--muted); font-size: .84rem; font-weight: 650; }
  .evidence {
    background: #05080f; border: 1px solid var(--line); border-radius: 6px;
    padding: .75rem .95rem; font-family: var(--font-mono); font-size: .81rem;
    color: #e2e8f0; margin-top: .45rem; line-height: 1.5;
  }
  .fix-box {
    background: rgba(16,48,47,.35); border: 1px solid rgba(20,184,166,.4);
    border-radius: 8px; padding: .85rem 1.05rem; margin-top: .85rem; font-size: .88rem; color: #ccfbf1;
  }
  .fix-box strong { color: #5eead4; text-transform: uppercase; font-size: .78rem; letter-spacing: .08em; }
  hr { border: 0; border-top: 1px solid var(--line); margin: 2.2rem 0; }
  .foot { color: var(--muted); font-size: .8rem; text-align: center; }
</style>
</head>
<body>
<h1>VibeTest security report</h1>
<div class="meta">
  <div>Target: <strong>{{ result.target_url }}</strong></div>
  <div>Scanned: {{ result.started_at }} &middot; Total findings: <strong>{{ result.findings | length }}</strong></div>
  {% set tech = result.artifact.tech %}
  {% set known = ([tech.framework, tech.hosting] + tech.backend_services) | select | list %}
  {% if known %}
  <div style="margin-top: .4rem;">Detected technology: {{ known | join(' · ') }}</div>
  <div class="badge-row">
    {% for t in known %}<span class="tech-pill">{{ t }}</span>{% endfor %}
  </div>
  {% endif %}
</div>
{% for f in result.findings %}
<div class="finding sev-{{ f.severity.value }}">
  <div class="title-row">
    <span class="badge {{ f.severity.value }}">{{ f.severity.value }}</span>
    <span class="finding-title">{{ f.title }}</span>
  </div>
  <div class="category-mono">{{ f.category }}{% if f.cwe_id %} &middot; {{ f.cwe_id }}{% endif %}{% if f.owasp_2025 %} &middot; {{ f.owasp_2025 }}{% endif %}</div>
  {% if f.explanation %}<div class="explanation">{{ f.explanation }}</div>{% endif %}
  {% if f.evidence %}
  <details>
    <summary>Evidence ({{ f.evidence | length }})</summary>
    {% for ev in f.evidence %}
    <div class="evidence">
      <strong>Target:</strong> {{ ev.url }}{% if ev.detail %} &mdash; {{ ev.detail }}{% endif %}
      {% if ev.snippet %}<br><strong>Snippet:</strong> {{ ev.snippet }}{% endif %}
    </div>
    {% endfor %}
  </details>
  {% endif %}
  {% if f.remediation_hint %}
  <div class="fix-box">
    <strong>What to do:</strong> {{ f.remediation_hint }}
  </div>
  {% endif %}
</div>
{% else %}
<div class="finding">No findings recorded. Note: this does <em>not</em> prove the target is entirely secure.</div>
{% endfor %}
<hr>
<p class="foot">Generated by VibeTest DeepScan &mdash; authorized targets only. This report is not a guarantee of absolute security.</p>
</body>
</html>
"""

_env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html", "xml"]))


def render_report(result: ScanResult) -> str:
    return _env.from_string(_TEMPLATE).render(result=result)
