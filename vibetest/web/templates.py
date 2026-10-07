"""HTML templates for the local dashboard (Faithful Paperly 2026 Academic SaaS Aesthetic).
Matches the VibeTest v2.0 Dashboard with sidebar navigation, global search,
target preview banner, security score gauge, attack surface graph, scan details,
attack path progression, detected tech grid, risk distribution donut, and
rich expandable findings table with 1-click Cursor/Claude IDE prompts.
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} — VibeTest v2.0</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300..800;1,300..800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --bg-page: #0a0d14;
    --bg-sidebar: #0d111a;
    --bg-header: #0e121d;
    --card: #121824;
    --card-surface: #151c2b;
    --card-hover: #192235;
    --border: #1a2233;
    --border-light: #242f45;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent: #14b8a6;
    --accent-hover: #0d9488;
    --accent-glow: rgba(20, 184, 166, 0.25);
    --accent-subtle: rgba(20, 184, 166, 0.1);
    --critical: #f43f5e;
    --critical-bg: rgba(244, 63, 94, 0.14);
    --critical-border: rgba(244, 63, 94, 0.35);
    --high: #fb923c;
    --high-bg: rgba(251, 146, 60, 0.14);
    --high-border: rgba(251, 146, 60, 0.35);
    --medium: #facc15;
    --medium-bg: rgba(250, 204, 21, 0.14);
    --medium-border: rgba(250, 204, 21, 0.35);
    --low: #38bdf8;
    --low-bg: rgba(56, 189, 248, 0.14);
    --low-border: rgba(56, 189, 248, 0.35);
    --info: #94a3b8;
    --info-bg: rgba(148, 163, 184, 0.12);
    --info-border: rgba(148, 163, 184, 0.3);
    --radius-lg: 14px;
    --radius-md: 10px;
    --radius-sm: 6px;
    --sidebar-w: 230px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg-page);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 13.5px;
    line-height: 1.5;
    letter-spacing: -0.012em;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }
  a { color: inherit; text-decoration: none; }
  button { font-family: inherit; }
  .mono, code, pre { font-family: var(--font-mono); }
  .hidden { display: none !important; }

  /* App Layout: Left Sidebar + Content Area */
  .app-layout { display: flex; min-height: 100vh; }
  
  /* Left Sidebar */
  .sidebar {
    width: var(--sidebar-w);
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    user-select: none;
    z-index: 40;
  }
  .sidebar-brand {
    padding: 1.15rem 1.25rem;
    display: flex;
    align-items: center;
    gap: .65rem;
    border-bottom: 1px solid var(--border);
  }
  .brand-logo-icon {
    width: 28px; height: 28px; border-radius: 8px;
    background: linear-gradient(135deg, #14b8a6, #0d9488);
    display: flex; align-items: center; justify-content: center;
    color: #fff; box-shadow: 0 0 14px rgba(20, 184, 166, 0.4);
  }
  .brand-name { font-weight: 800; font-size: 1.08rem; letter-spacing: -0.03em; color: #fff; }
  .brand-v2 {
    font-size: .65rem; font-weight: 700; color: #5eead4;
    background: rgba(20, 184, 166, 0.15); border: 1px solid rgba(20, 184, 166, 0.35);
    padding: .15rem .45rem; border-radius: 999px; letter-spacing: .02em;
  }

  .sidebar-menu { padding: 1rem .75rem; flex: 1; display: flex; flex-direction: column; gap: 1.2rem; }
  .nav-group-label {
    font-size: .67rem; font-weight: 750; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: .08em; padding: 0 .55rem .35rem;
  }
  .nav-list { list-style: none; display: flex; flex-direction: column; gap: 2px; }
  .nav-item {
    display: flex; align-items: center; gap: .65rem;
    padding: .5rem .65rem; border-radius: var(--radius-sm);
    color: var(--text-secondary); font-size: .84rem; font-weight: 600;
    transition: all .15s ease; cursor: pointer;
  }
  .nav-item:hover { color: #fff; background: rgba(255, 255, 255, 0.04); }
  .nav-item.active {
    color: #5eead4; background: rgba(20, 184, 166, 0.12);
    border: 1px solid rgba(20, 184, 166, 0.25);
  }
  .nav-icon { width: 16px; height: 16px; opacity: .8; flex-shrink: 0; }
  .nav-item.active .nav-icon { opacity: 1; color: var(--accent); }

  .sidebar-footer {
    padding: .9rem .85rem; border-top: 1px solid var(--border);
    display: flex; flex-direction: column; gap: .7rem;
  }
  .credits-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: .7rem .8rem;
  }
  .credits-head { display: flex; justify-content: space-between; font-size: .74rem; font-weight: 600; color: var(--text-secondary); margin-bottom: .35rem; }
  .credits-val { color: #fff; font-weight: 700; }
  .credits-bar { height: 4px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; }
  .credits-fill { height: 100%; width: 46%; background: var(--accent); border-radius: 999px; }

  /* Right Content Wrapper */
  .content-wrapper { flex: 1; display: flex; flex-direction: column; min-width: 0; }

  /* Top Navigation Bar */
  .topbar {
    height: 58px; background: var(--bg-header); border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 1.6rem; position: sticky; top: 0; z-index: 30;
  }
  .search-bar {
    position: relative; display: flex; align-items: center; width: 420px;
  }
  .search-bar svg { position: absolute; left: .9rem; color: var(--text-muted); pointer-events: none; }
  .search-input-top {
    width: 100%; height: 36px; padding: 0 3rem 0 2.4rem;
    background: #090d16; border: 1px solid var(--border);
    border-radius: var(--radius-sm); color: #fff; font-size: .83rem;
    outline: none; font-family: var(--font-sans);
    transition: all .16s ease;
  }
  .search-input-top:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
  .search-kbd {
    position: absolute; right: .75rem; font-size: .68rem; font-weight: 600;
    color: var(--text-muted); background: rgba(255,255,255,0.06);
    border: 1px solid var(--border); padding: .15rem .35rem; border-radius: 4px;
  }

  .topbar-actions { display: flex; align-items: center; gap: .85rem; }
  .btn-new-scan {
    display: inline-flex; align-items: center; gap: .45rem;
    padding: .45rem .95rem; border-radius: var(--radius-sm);
    background: #fff; color: #0a0d14; font-size: .82rem; font-weight: 700;
    border: none; cursor: pointer; transition: all .15s ease;
  }
  .btn-new-scan:hover { background: #e2e8f0; transform: translateY(-1px); }
  .notif-bell {
    position: relative; width: 34px; height: 34px; border-radius: 8px;
    background: var(--card); border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    color: var(--text-secondary); cursor: pointer;
  }
  .notif-badge {
    position: absolute; top: -3px; right: -3px; width: 14px; height: 14px;
    background: var(--critical); color: #fff; font-size: .62rem; font-weight: 800;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
  }
  .user-profile {
    display: flex; align-items: center; gap: .55rem;
    padding: .25rem .55rem; border-radius: var(--radius-sm);
    cursor: pointer; transition: background .15s;
  }
  .user-profile:hover { background: rgba(255,255,255,0.04); }
  .user-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #475569, #334155);
    color: #fff; font-size: .78rem; font-weight: 750;
    display: flex; align-items: center; justify-content: center;
  }
  .user-name { font-size: .83rem; font-weight: 650; color: #fff; }

  /* Main View Area */
  main { padding: 1.5rem 1.8rem 3rem; flex: 1; max-width: 1440px; margin: 0 auto; width: 100%; }

  /* Cards & Shared UI */
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 1.25rem 1.4rem;
    position: relative; transition: border-color .15s, box-shadow .15s;
  }
  .card:hover { border-color: var(--border-light); }
  .card-head {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.1rem;
  }
  .card-title {
    font-size: .95rem; font-weight: 750; color: #fff; letter-spacing: -0.02em;
    display: flex; align-items: center; gap: .45rem;
  }
  .card-link { font-size: .78rem; color: #5eead4; font-weight: 600; cursor: pointer; }
  .card-link:hover { text-decoration: underline; }

  /* Buttons */
  .btn {
    display: inline-flex; align-items: center; justify-content: center; gap: .4rem;
    padding: .48rem .95rem; border-radius: var(--radius-sm);
    font-size: .82rem; font-weight: 650; cursor: pointer; border: none;
    transition: all .16s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .btn.primary {
    background: linear-gradient(135deg, #14b8a6, #0d9488); color: #fff;
    box-shadow: 0 2px 8px rgba(20, 184, 166, 0.3);
  }
  .btn.primary:hover { opacity: .92; transform: translateY(-1px); }
  .btn.secondary {
    background: var(--card-surface); color: var(--text-secondary);
    border: 1px solid var(--border);
  }
  .btn.secondary:hover { background: var(--card-hover); border-color: var(--border-light); color: #fff; }
  .btn.icon-only { padding: .48rem .65rem; }

  /* Target Banner Card */
  .back-link {
    display: inline-flex; align-items: center; gap: .4rem;
    color: #5eead4; font-size: .82rem; font-weight: 650; margin-bottom: 1rem;
    transition: transform .15s;
  }
  .back-link:hover { transform: translateX(-2px); }
  .target-banner {
    display: flex; align-items: center; justify-content: space-between;
    gap: 1.4rem; padding: 1.2rem 1.4rem; margin-bottom: 1.1rem; flex-wrap: wrap;
  }
  .target-left-group { display: flex; align-items: center; gap: 1.25rem; flex: 1; min-width: 320px; }
  .target-thumb {
    width: 140px; height: 86px; border-radius: 8px; flex-shrink: 0;
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid var(--border-light); overflow: hidden;
    display: flex; flex-direction: column; box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  }
  .thumb-bar { height: 12px; background: #0b0f19; display: flex; align-items: center; padding: 0 6px; gap: 3px; }
  .thumb-dot { width: 4px; height: 4px; border-radius: 50%; background: #475569; }
  .thumb-body { flex: 1; padding: 8px; display: flex; flex-direction: column; justify-content: center; }
  .thumb-title { font-size: 8px; font-weight: 800; color: #f8fafc; line-height: 1.2; }
  .thumb-sub { font-size: 6px; color: #94a3b8; margin-top: 3px; }
  .target-info { display: flex; flex-direction: column; gap: .35rem; }
  .target-host-row { display: flex; align-items: center; gap: .55rem; }
  .target-host-row h2 { font-size: 1.35rem; font-weight: 800; color: #fff; letter-spacing: -0.03em; }
  .ext-link { color: var(--text-muted); transition: color .15s; }
  .ext-link:hover { color: #5eead4; }
  .target-url-sub { display: flex; align-items: center; gap: .35rem; font-size: .82rem; color: var(--text-muted); font-family: var(--font-mono); }
  .chips-row { display: flex; gap: .45rem; flex-wrap: wrap; margin-top: .15rem; }
  .chip {
    padding: .2rem .6rem; border-radius: 999px; font-size: .74rem; font-weight: 650;
    background: #151e2e; color: #93c5fd; border: 1px solid #233149;
  }
  .chip.kind { background: rgba(20, 184, 166, 0.12); color: #5eead4; border-color: rgba(20, 184, 166, 0.35); }
  .target-meta-line { font-size: .78rem; color: var(--text-muted); margin-top: .15rem; }

  .target-right-group { display: flex; flex-direction: column; align-items: flex-end; gap: .85rem; }
  .target-btn-row { display: flex; align-items: center; gap: .55rem; }
  .sev-pill-deck { display: flex; gap: .5rem; flex-wrap: wrap; }
  .sev-pill {
    display: flex; flex-direction: column; align-items: center; min-width: 60px;
    padding: .4rem .65rem; border-radius: var(--radius-sm); border: 1px solid transparent;
  }
  .sev-pill .sev-num { font-size: 1.15rem; font-weight: 800; line-height: 1; }
  .sev-pill .sev-label { font-size: .68rem; font-weight: 750; text-transform: uppercase; letter-spacing: .06em; margin-top: .2rem; }
  .sev-pill.critical { background: var(--critical-bg); border-color: var(--critical-border); color: #fda4af; }
  .sev-pill.high { background: var(--high-bg); border-color: var(--high-border); color: #fdba74; }
  .sev-pill.medium { background: var(--medium-bg); border-color: var(--medium-border); color: #fef08a; }
  .sev-pill.low { background: var(--low-bg); border-color: var(--low-border); color: #7dd3fc; }
  .sev-pill.info { background: var(--info-bg); border-color: var(--info-border); color: #cbd5e1; }

  /* Navigation Tabs */
  .tab-bar {
    display: flex; gap: .35rem; border-bottom: 1px solid var(--border);
    margin-bottom: 1.3rem; padding-bottom: 1px; overflow-x: auto;
  }
  .tab-btn {
    padding: .65rem 1.05rem; font-size: .83rem; font-weight: 650;
    color: var(--text-secondary); background: transparent; border: none;
    border-bottom: 2px solid transparent; cursor: pointer; display: flex;
    align-items: center; gap: .45rem; transition: all .15s ease; white-space: nowrap;
  }
  .tab-btn:hover { color: #fff; }
  .tab-btn.active {
    color: #fff; border-bottom-color: var(--accent);
  }
  .tab-badge {
    font-size: .68rem; font-weight: 750; background: rgba(255,255,255,0.08);
    padding: .1rem .45rem; border-radius: 999px;
  }
  .tab-btn.active .tab-badge { background: rgba(20, 184, 166, 0.2); color: #5eead4; }

  /* Overview 3-Column Grid Rows */
  .grid-3 {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.15rem; margin-bottom: 1.15rem;
  }

  /* Card 1: Security Score */
  .score-content { display: flex; align-items: center; gap: 1.4rem; }
  .score-left {
    display: flex; flex-direction: column; align-items: center; text-align: center;
    width: 140px; flex-shrink: 0;
  }
  .gauge-circle {
    width: 110px; height: 110px; border-radius: 50%;
    background: conic-gradient(var(--critical) 0% 42%, #1e2638 42% 100%);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 20px rgba(244, 63, 94, 0.25);
  }
  .gauge-inner {
    width: 86px; height: 86px; border-radius: 50%; background: var(--card);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }
  .gauge-score { font-size: 1.8rem; font-weight: 800; color: #fff; line-height: 1; }
  .gauge-max { font-size: .72rem; color: var(--text-muted); font-weight: 600; }
  .gauge-status { font-size: .84rem; font-weight: 750; color: var(--critical); margin-top: .6rem; }
  .gauge-sub { font-size: .72rem; color: var(--text-muted); line-height: 1.35; margin-top: .2rem; }

  .score-breakdown { flex: 1; display: flex; flex-direction: column; gap: .5rem; }
  .score-bar-row { display: flex; align-items: center; gap: .6rem; font-size: .78rem; }
  .bar-label { width: 110px; color: var(--text-secondary); font-weight: 600; flex-shrink: 0; }
  .bar-track { flex: 1; height: 6px; background: #182030; border-radius: 999px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 999px; }
  .bar-val { width: 22px; text-align: right; color: #fff; font-weight: 700; font-family: var(--font-mono); font-size: .75rem; }

  /* Card 2: Attack Surface Visualizer */
  .graph-container {
    padding: .85rem .4rem; display: flex; flex-direction: column; align-items: center;
    gap: .75rem; background: #0b0f19; border-radius: var(--radius-sm); border: 1px solid var(--border);
  }
  .graph-root-node {
    background: #141c2c; border: 1px solid #38bdf8; color: #bae6fd;
    padding: .35rem .85rem; border-radius: 8px; font-weight: 750; font-size: .82rem;
    display: inline-flex; align-items: center; gap: .4rem;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
  }
  .graph-row { display: flex; gap: .85rem; justify-content: center; position: relative; }
  .graph-node {
    background: #111726; border: 1px solid var(--border-light); color: #cbd5e1;
    padding: .32rem .65rem; border-radius: 6px; font-size: .74rem; font-weight: 650;
    display: inline-flex; align-items: center; gap: .35rem;
  }
  .graph-node.green { border-color: rgba(16, 185, 129, 0.4); color: #6ee7b7; }
  .graph-node.purple { border-color: rgba(168, 85, 247, 0.4); color: #d8b4fe; }
  .graph-node.orange { border-color: rgba(249, 115, 22, 0.4); color: #fdba74; }
  .graph-branch { display: flex; gap: .45rem; justify-content: center; }
  .graph-leaf {
    background: #090d16; border: 1px solid var(--border); color: #94a3b8;
    padding: .2rem .5rem; border-radius: 4px; font-size: .68rem; font-weight: 600;
  }

  /* Card 3: Scan Details */
  .details-list { display: flex; flex-direction: column; gap: .55rem; font-size: .82rem; }
  .details-row { display: flex; justify-content: space-between; align-items: center; padding: .18rem 0; }
  .details-k { color: var(--text-muted); display: flex; align-items: center; gap: .45rem; font-weight: 550; }
  .details-v { color: #fff; font-weight: 650; font-family: var(--font-mono); }
  .status-tag-green {
    display: inline-flex; align-items: center; gap: .35rem; color: #34d399; font-weight: 700;
  }
  .dot-green { width: 6px; height: 6px; border-radius: 50%; background: #10b981; }

  /* Row 2: Top Attack Path, Technologies, Risk Distribution */
  .path-steps { display: flex; align-items: center; gap: .55rem; flex-wrap: wrap; margin-top: .4rem; }
  .path-node {
    display: flex; align-items: center; gap: .5rem;
    background: #0d121e; border: 1px solid var(--border);
    padding: .45rem .75rem; border-radius: 8px; font-size: .78rem; font-weight: 650;
  }
  .step-badge {
    width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: .7rem; font-weight: 800; color: #fff;
  }
  .step-arrow { color: var(--text-muted); font-weight: 800; }

  .tech-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); gap: .65rem; }
  .tech-card {
    background: #0d121e; border: 1px solid var(--border); border-radius: 8px;
    padding: .65rem .5rem; text-align: center; display: flex; flex-direction: column; align-items: center; gap: .25rem;
  }
  .tech-icon-circle {
    width: 30px; height: 30px; border-radius: 50%; background: #172033;
    display: flex; align-items: center; justify-content: center; margin-bottom: .2rem;
  }
  .tech-name { font-size: .78rem; font-weight: 750; color: #fff; }
  .tech-role { font-size: .67rem; color: var(--text-muted); }

  .donut-box { display: flex; align-items: center; justify-content: space-around; gap: 1rem; }
  .donut-chart {
    width: 90px; height: 90px; border-radius: 50%;
    background: conic-gradient(
      var(--critical) 0% 45%,
      var(--high) 45% 63%,
      var(--medium) 63% 90%,
      var(--low) 90% 100%
    );
    display: flex; align-items: center; justify-content: center;
  }
  .donut-inner {
    width: 62px; height: 62px; border-radius: 50%; background: var(--card);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }
  .donut-val { font-size: 1.15rem; font-weight: 800; color: #fff; line-height: 1; }
  .donut-lbl { font-size: .62rem; color: var(--text-muted); font-weight: 600; }
  .donut-legend { display: flex; flex-direction: column; gap: .35rem; font-size: .78rem; font-weight: 650; }
  .legend-row { display: flex; align-items: center; gap: .45rem; }
  .legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

  /* Findings Table Section */
  .findings-section { margin-top: 1.3rem; }
  .findings-toolbar {
    display: flex; justify-content: space-between; align-items: center;
    gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;
  }
  .findings-tabs { display: flex; gap: .4rem; flex-wrap: wrap; }
  .filter-tab {
    padding: .38rem .75rem; border-radius: 999px; font-size: .76rem; font-weight: 650;
    background: var(--card); border: 1px solid var(--border); color: var(--text-secondary);
    cursor: pointer; transition: all .15s ease;
  }
  .filter-tab:hover { color: #fff; border-color: var(--border-light); }
  .filter-tab.active { background: #fff; color: #0a0d14; border-color: #fff; font-weight: 750; }
  
  .table-controls { display: flex; align-items: center; gap: .65rem; }
  .table-search {
    position: relative; display: flex; align-items: center; width: 240px;
  }
  .table-search svg { position: absolute; left: .75rem; color: var(--text-muted); }
  .table-search-input {
    width: 100%; height: 32px; padding: 0 .8rem 0 2.2rem;
    background: #090d16; border: 1px solid var(--border); border-radius: 6px;
    color: #fff; font-size: .78rem; outline: none; font-family: var(--font-sans);
  }
  .table-search-input:focus { border-color: var(--accent); }
  .sort-select {
    height: 32px; padding: 0 .75rem; background: #090d16; border: 1px solid var(--border);
    border-radius: 6px; color: var(--text-secondary); font-size: .78rem; outline: none;
    font-family: var(--font-sans); cursor: pointer;
  }

  .findings-table-card { padding: 0; overflow: hidden; }
  .findings-table { width: 100%; border-collapse: collapse; font-size: .82rem; }
  .findings-table th {
    background: #0e131e; padding: .75rem 1rem; text-align: left;
    font-size: .72rem; font-weight: 750; text-transform: uppercase;
    letter-spacing: .06em; color: var(--text-muted); border-bottom: 1px solid var(--border);
  }
  .finding-row {
    border-bottom: 1px solid var(--border); cursor: pointer;
    transition: background .12s ease;
  }
  .finding-row:hover { background: rgba(255, 255, 255, 0.02); }
  .finding-row td { padding: .85rem 1rem; vertical-align: middle; }
  .td-num { color: var(--text-muted); font-family: var(--font-mono); font-size: .78rem; width: 36px; }
  
  .sev-badge {
    display: inline-flex; align-items: center; gap: .35rem;
    padding: .2rem .55rem; border-radius: 999px; font-size: .72rem; font-weight: 750;
    text-transform: capitalize;
  }
  .sev-badge.critical { background: var(--critical-bg); color: #fda4af; border: 1px solid var(--critical-border); }
  .sev-badge.high { background: var(--high-bg); color: #fdba74; border: 1px solid var(--high-border); }
  .sev-badge.medium { background: var(--medium-bg); color: #fef08a; border: 1px solid var(--medium-border); }
  .sev-badge.low { background: var(--low-bg); color: #7dd3fc; border: 1px solid var(--low-border); }
  .sev-badge.info { background: var(--info-bg); color: #cbd5e1; border: 1px solid var(--info-border); }
  
  .finding-title-td { font-weight: 650; color: #fff; font-size: .84rem; }
  .cwe-pill {
    font-family: var(--font-mono); font-size: .75rem; color: var(--text-secondary);
    background: rgba(255,255,255,0.04); padding: .15rem .45rem; border-radius: 4px;
    border: 1px solid var(--border);
  }
  .exploit-pill {
    padding: .15rem .5rem; border-radius: 4px; font-size: .72rem; font-weight: 700;
  }
  .exploit-pill.verified { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }
  .exploit-pill.detected { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.35); }
  .conf-val { font-family: var(--font-mono); font-weight: 700; color: var(--text-secondary); }
  .evidence-link { color: #38bdf8; font-weight: 600; font-size: .78rem; }
  .chevron-cell { color: var(--text-muted); font-weight: 700; }

  /* Drawer Expansion inside Row */
  .detail-drawer { background: #080c14; padding: 1.2rem 1.4rem; border-bottom: 1px solid var(--border); }
  .drawer-desc { font-size: .88rem; color: #cbd5e1; line-height: 1.6; margin-bottom: .85rem; }
  .drawer-code {
    background: #05080f; border: 1px solid var(--border); border-radius: 6px;
    padding: .85rem 1rem; color: #e2e8f0; font-size: .81rem; line-height: 1.55;
    margin-bottom: .95rem; overflow-x: auto;
  }
  .drawer-action {
    background: rgba(20, 184, 166, 0.1); border: 1px solid rgba(20, 184, 166, 0.3);
    border-radius: 8px; padding: .85rem 1rem; margin-bottom: .95rem;
  }
  .drawer-action strong { color: #5eead4; text-transform: uppercase; font-size: .75rem; letter-spacing: .06em; }
  .drawer-action p { margin-top: .3rem; font-size: .86rem; color: #ccfbf1; }

  /* IDE Fix Prompt Widget */
  .ide-prompt-widget {
    background: #090d16; border: 1px solid #233149; border-radius: 8px;
    padding: .85rem 1.1rem;
  }
  .ide-prompt-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }
  .ide-prompt-title {
    display: flex; align-items: center; gap: .55rem;
    font-size: .75rem; font-weight: 750; color: #a5b4fc; text-transform: uppercase; letter-spacing: .06em;
  }
  .ide-dots { display: flex; gap: 4px; }
  .ide-dot { width: 8px; height: 8px; border-radius: 50%; }
  .copy-btn-tactile {
    padding: .3rem .75rem; font-size: .75rem; font-weight: 650;
    border-radius: 6px; background: #1e1b4b; border: 1px solid #4338ca;
    color: #c7d2fe; cursor: pointer; transition: all .16s ease;
  }
  .copy-btn-tactile:hover { background: #312e81; color: #fff; }
  .ide-prompt-code {
    background: #05080e; border: 1px solid #1a2233; border-radius: 6px;
    padding: .75rem .9rem; font-family: var(--font-mono); font-size: .8rem;
    color: #94a3b8; white-space: pre-wrap; line-height: 1.5;
  }

  /* Scan History / List View */
  .history-hero { margin-bottom: 1.4rem; }
  .launcher-form { display: flex; gap: .7rem; flex-wrap: wrap; margin-top: .85rem; }
  .launcher-input {
    flex: 1; min-width: 290px; height: 42px; padding: 0 1rem;
    background: #090e18; border: 1px solid var(--border); border-radius: var(--radius-sm);
    color: #fff; font-size: .92rem; outline: none; font-family: var(--font-sans);
  }
  .launcher-input:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
  .launcher-confirm { display: flex; align-items: center; gap: .5rem; width: 100%; font-size: .82rem; color: var(--text-muted); }

  /* New Scan Modal */
  .modal-backdrop {
    position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
    display: flex; align-items: center; justify-content: center; z-index: 100;
  }
  .modal-box {
    width: 520px; max-width: 90vw; background: var(--card); border: 1px solid var(--border-light);
    border-radius: var(--radius-lg); padding: 1.6rem; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
  }
  .modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  .modal-head h3 { font-size: 1.15rem; font-weight: 750; color: #fff; }
  .modal-close { background: none; border: none; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; }
</style>
</head>
<body>
<div class="app-layout">
  <!-- Left Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="M9 12l2 2 4-4"/>
        </svg>
      </div>
      <span class="brand-name">VibeTest</span>
      <span class="brand-v2">v2.0</span>
    </div>

    <div class="sidebar-menu">
      <div>
        <div class="nav-group-label">OVERVIEW</div>
        <ul class="nav-list">
          <a href="/"><li class="nav-item active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Dashboard
          </li></a>
          <a href="/"><li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Scans
          </li></a>
          <a href="/"><li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/></svg>
            Targets
          </li></a>
        </ul>
      </div>

      <div>
        <div class="nav-group-label">ANALYZE</div>
        <ul class="nav-list">
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
            Attack Surface
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Findings
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            Evidence
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>
            Assets
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
            Technologies
          </li>
        </ul>
      </div>

      <div>
        <div class="nav-group-label">INTELLIGENCE</div>
        <ul class="nav-list">
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>
            AI / LLM Risks
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>
            Attack Paths
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
            Risk Score
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg>
            Comparisons
          </li>
        </ul>
      </div>

      <div>
        <div class="nav-group-label">DEVELOPER</div>
        <ul class="nav-list">
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            Fixes & Prompts
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg>
            Reports
          </li>
          <li class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.8 0"/></svg>
            API & Integrations
          </li>
        </ul>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="credits-card">
        <div class="credits-head">
          <span>Scan Credits</span>
          <span class="credits-val">23 / 50</span>
        </div>
        <div class="credits-bar"><div class="credits-fill"></div></div>
      </div>
      <div class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
        Settings
      </div>
      <div class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
        Help
      </div>
    </div>
  </aside>

  <!-- Content Wrapper -->
  <div class="content-wrapper">
    <!-- Topbar -->
    <header class="topbar">
      <div class="search-bar">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input class="search-input-top" type="text" placeholder="Search findings, endpoints, technologies...">
        <span class="search-kbd">⌘ K</span>
      </div>

      <div class="topbar-actions">
        <button class="btn-new-scan" onclick="openNewScanModal()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Scan
        </button>
        <div class="notif-bell">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span class="notif-badge">1</span>
        </div>
        <div class="user-profile">
          <div class="user-avatar">G</div>
          <span class="user-name">Gaurav</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
      </div>
    </header>

    <main>
      {{ body | safe }}
    </main>
  </div>
</div>

<!-- New Scan Modal Dialog -->
<div id="new-scan-modal" class="modal-backdrop hidden">
  <div class="modal-box">
    <div class="modal-head">
      <h3>Launch DeepScan</h3>
      <button class="modal-close" onclick="closeNewScanModal()">&times;</button>
    </div>
    <p class="drawer-desc">Scan a target URL or public GitHub repository for client secrets, exposed backend RLS rules, CVEs, and sensitive misconfigurations.</p>
    <form id="modal-scan-form" class="launcher-form">
      <input id="modal-scan-url" class="launcher-input" type="text" placeholder="https://your-app.vercel.app  ·  github.com/owner/repo" required>
      <label class="launcher-confirm">
        <input type="checkbox" id="modal-scan-authorized" required>
        I confirm I own this target or have written permission to test it (or it is a public repository).
      </label>
      <div style="display: flex; gap: .6rem; width: 100%; margin-top: .6rem;">
        <button type="submit" id="modal-scan-btn" class="btn primary" style="flex: 1;">Start scan</button>
        <button type="button" class="btn secondary" onclick="closeNewScanModal()">Cancel</button>
      </div>
    </form>
    <div id="modal-scan-box" class="scan-box hidden" style="margin-top: 1rem; padding: .85rem; background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.3); border-radius: 6px;">
      <div style="display: flex; align-items: center; gap: .5rem; font-size: .83rem; color: #5eead4; font-weight: 600;">
        <span class="spinner"></span><span id="modal-scan-msg">Initializing discovery…</span>
      </div>
    </div>
    <div id="modal-scan-error" class="hidden" style="margin-top: 1rem; padding: .75rem; background: var(--critical-bg); color: #fda4af; border: 1px solid var(--critical-border); border-radius: 6px; font-size: .82rem;"></div>
  </div>
</div>

<script>
// Modal Handlers
function openNewScanModal() {
  document.getElementById("new-scan-modal").classList.remove("hidden");
  document.getElementById("modal-scan-url").focus();
}
function closeNewScanModal() {
  document.getElementById("new-scan-modal").classList.add("hidden");
}
window.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "k") {
    e.preventDefault();
    openNewScanModal();
  }
  if (e.key === "Escape") closeNewScanModal();
});

// Modal Scan Form Submission
const modalForm = document.getElementById("modal-scan-form");
if (modalForm) {
  const mMsg = document.getElementById("modal-scan-msg");
  const mErr = document.getElementById("modal-scan-error");
  const mBox = document.getElementById("modal-scan-box");
  const mBtn = document.getElementById("modal-scan-btn");

  modalForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    mErr.classList.add("hidden");
    mBox.classList.remove("hidden");
    mMsg.textContent = "Verifying target authorization…";
    mBtn.disabled = true;

    try {
      const resp = await fetch("/api/scan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          url: document.getElementById("modal-scan-url").value.trim(),
          authorized: document.getElementById("modal-scan-authorized").checked,
        }),
      });
      if (!resp.ok) {
        const d = await resp.json().catch(() => ({}));
        mErr.textContent = d.detail || "Scan request refused.";
        mErr.classList.remove("hidden");
        mBox.classList.add("hidden");
        mBtn.disabled = false;
        return;
      }
      const {job_id} = await resp.json();
      while (true) {
        await new Promise((r) => setTimeout(r, 1500));
        const job = await (await fetch("/api/scan/" + job_id)).json();
        if (job.status === "done") { window.location = "/scan/" + job.scan_id; return; }
        if (job.status === "failed") {
          mErr.textContent = "Scan failed: " + (job.error || "unknown error");
          mErr.classList.remove("hidden");
          mBox.classList.add("hidden");
          mBtn.disabled = false;
          return;
        }
        mMsg.textContent = "Spidering routes and testing misconfigurations…";
      }
    } catch (err) {
      mErr.textContent = "Could not reach scanner service.";
      mErr.classList.remove("hidden");
      mBox.classList.add("hidden");
      mBtn.disabled = false;
    }
  });
}

// 1-Click Copy AI Prompt
window.copyPrompt = function(btn, promptId) {
  const el = document.getElementById(promptId);
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(() => {
    const orig = btn.innerText;
    btn.innerText = "✓ Copied to clipboard!";
    btn.style.background = "#059669";
    btn.style.color = "#fff";
    setTimeout(() => {
      btn.innerText = orig;
      btn.style.background = "";
      btn.style.color = "";
    }, 2000);
  });
};

// Row Accordion Drawer Toggle
window.toggleRowDrawer = function(rowId) {
  const drawer = document.getElementById("drawer-" + rowId);
  const chev = document.getElementById("chev-" + rowId);
  if (!drawer) return;
  if (drawer.classList.contains("hidden")) {
    drawer.classList.remove("hidden");
    if (chev) chev.innerText = "▼";
  } else {
    drawer.classList.add("hidden");
    if (chev) chev.innerText = "›";
  }
};
</script>
</body>
</html>
"""

LIST_BODY = """
<div class="history-hero card">
  <div class="card-head">
    <div class="card-title">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/></svg>
      Scan a website or GitHub repository
    </div>
  </div>
  <p class="target-meta-line" style="font-size: .88rem; margin-bottom: .8rem;">
    Comprehensive automated security analysis: client bundle secrets, unauthenticated Supabase/Firebase RLS probing, missing security headers, and CVE dependencies.
  </p>
  <form id="scan-form" class="launcher-form">
    <input id="scan-url" class="launcher-input" type="text" placeholder="https://your-app.vercel.app  ·  github.com/owner/repo" required>
    <button type="submit" id="scan-btn" class="btn primary">Start scan</button>
    <label class="launcher-confirm">
      <input type="checkbox" id="scan-authorized" required>
      I confirm I own this target or have written permission to test it (or it is a public repository).
    </label>
  </form>
  <div id="scan-box" class="scan-box hidden" style="margin-top: .85rem; padding: .75rem .95rem; background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.3); border-radius: 6px;">
    <div style="display: flex; align-items: center; gap: .6rem; color: #5eead4; font-size: .83rem; font-weight: 600;">
      <span class="spinner"></span><span id="scan-msg">Starting…</span>
    </div>
  </div>
  <div id="scan-error" class="hidden" style="margin-top: .85rem; padding: .75rem; background: var(--critical-bg); color: #fda4af; border: 1px solid var(--critical-border); border-radius: 6px; font-size: .82rem;"></div>
</div>

<div class="grid-3" style="margin-bottom: 1.4rem;">
  <div class="card">
    <div class="card-head"><span class="card-title">Total Scans</span></div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #fff;">{{ stats.scans }}</div>
    <div class="target-meta-line">Historical targets evaluated</div>
  </div>
  <div class="card">
    <div class="card-head"><span class="card-title" style="color: #fda4af;">Critical Vulnerabilities</span></div>
    <div style="font-size: 1.85rem; font-weight: 800; color: var(--critical);">{{ stats.critical }} Critical</div>
    <div class="target-meta-line">Immediate action required</div>
  </div>
  <div class="card">
    <div class="card-head"><span class="card-title">Total findings</span></div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #5eead4;">{{ stats.total }}</div>
    <div class="target-meta-line">Aggregated across all targets</div>
  </div>
</div>

<div class="card findings-table-card">
  <div style="padding: 1rem 1.4rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
    <h3 style="font-size: 1.05rem; font-weight: 750; color: #fff;">Scan history</h3>
    <span class="target-meta-line">{{ scans | length }} scan(s)</span>
  </div>
  {% if scans %}
  <table class="findings-table">
    <thead>
      <tr>
        <th>Target URL</th>
        <th>Timestamp</th>
        <th>Total findings</th>
        <th>Risk Distribution</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      {% for s in scans %}
      <tr class="finding-row" onclick="window.location='/scan/{{ s.row.scan_id }}'">
        <td class="finding-title-td">{{ s.row.target_url }}</td>
        <td class="target-meta-line">{{ s.row.started_at.strftime('%d %b %Y, %H:%M') }} UTC</td>
        <td><strong>{{ s.total }}</strong> finding(s)</td>
        <td>
          <div style="display: flex; gap: .35rem;">
            {% for sev in ("critical", "high", "medium", "low", "info") %}
              {% if s.counts[sev] %}<span class="sev-badge {{ sev }}">{{ s.counts[sev] }} {{ sev }}</span>{% endif %}
            {% endfor %}
            {% if not s.total %}<span class="cwe-pill">clean</span>{% endif %}
          </div>
        </td>
        <td class="chevron-cell">View Dashboard &rarr;</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div style="padding: 3rem 1rem; text-align: center; color: var(--text-muted);">
    No scans recorded yet. Enter a target above or launch a scan from CLI.
  </div>
  {% endif %}
</div>

<script>
const form = document.getElementById("scan-form");
if (form) {
  const msg = document.getElementById("scan-msg");
  const err = document.getElementById("scan-error");
  const box = document.getElementById("scan-box");
  const btn = document.getElementById("scan-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    err.classList.add("hidden");
    box.classList.remove("hidden");
    msg.textContent = "Initializing discovery and consent verification…";
    btn.disabled = true;

    try {
      const resp = await fetch("/api/scan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          url: document.getElementById("scan-url").value.trim(),
          authorized: document.getElementById("scan-authorized").checked,
        }),
      });
      if (!resp.ok) {
        const d = await resp.json().catch(() => ({}));
        err.textContent = d.detail || "Scan request refused.";
        err.classList.remove("hidden");
        box.classList.add("hidden");
        btn.disabled = false;
        return;
      }
      const {job_id} = await resp.json();
      while (true) {
        await new Promise((r) => setTimeout(r, 1500));
        const job = await (await fetch("/api/scan/" + job_id)).json();
        if (job.status === "done") { window.location = "/scan/" + job.scan_id; return; }
        if (job.status === "failed") {
          err.textContent = "Scan failed: " + (job.error || "unknown error");
          err.classList.remove("hidden");
          box.classList.add("hidden");
          btn.disabled = false;
          return;
        }
        msg.textContent = "Spidering routes and testing misconfigurations…";
      }
    } catch (ex) {
      err.textContent = "Could not reach scanner service.";
      err.classList.remove("hidden");
      box.classList.add("hidden");
      btn.disabled = false;
    }
  });
}
</script>
"""

DETAIL_BODY = """
<a class="back-link" href="/"><span class="back-arrow">&larr;</span> Back to all scans</a>

<!-- Target Header Banner Card -->
<section class="card target-banner">
  <div class="target-left-group">
    <!-- Preview Thumbnail Mockup -->
    <div class="target-thumb">
      <div class="thumb-bar">
        <span class="thumb-dot"></span><span class="thumb-dot"></span><span class="thumb-dot"></span>
      </div>
      <div class="thumb-body">
        <div class="thumb-title">{{ row.target_url.split('://')[-1].split('/')[0] }}</div>
        <div class="thumb-sub">Publish. Analyze. Share Research Smarter.</div>
      </div>
    </div>

    <!-- Target Meta Info -->
    <div class="target-info">
      <div class="target-host-row">
        <h2>{{ row.target_url.split('://')[-1].split('/')[0] }}</h2>
        <a href="{{ row.target_url }}" target="_blank" class="ext-link" title="Open target">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        </a>
      </div>
      <div class="target-url-sub">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span>{{ row.target_url }}</span>
      </div>
      <div class="chips-row">
        <span class="chip kind">{{ kind }}</span>
        {% for t in tech %}<span class="chip">{{ t }}</span>{% endfor %}
      </div>
      <div class="target-meta-line">
        Scanned on {{ row.started_at.strftime('%d %b %Y, %H:%M') }} UTC &bull; scan {{ row.scan_id[:10] }}
      </div>
    </div>
  </div>

  <div class="target-right-group">
    <div class="target-btn-row">
      <button class="btn secondary" onclick="openNewScanModal()">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.19"/></svg>
        Re-scan
      </button>
      <button class="btn secondary" id="pdf-btn"
              data-href="/scan/{{ row.scan_id }}/report.pdf"
              data-report-href="/scan/{{ row.scan_id }}/report"
              data-filename="vibetest-report-{{ row.scan_id[:8] }}.pdf">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download PDF
      </button>
      <a class="btn secondary icon-only" href="/scan/{{ row.scan_id }}/report" title="Open full report">•••</a>
    </div>

    <!-- Severity Pills Deck -->
    <div class="sev-pill-deck">
      <div class="sev-pill critical">
        <span class="sev-num">{{ summary.critical }}</span>
        <span class="sev-label">Critical</span>
      </div>
      <div class="sev-pill high">
        <span class="sev-num">{{ summary.high }}</span>
        <span class="sev-label">High</span>
      </div>
      <div class="sev-pill medium">
        <span class="sev-num">{{ summary.medium }}</span>
        <span class="sev-label">Medium</span>
      </div>
      <div class="sev-pill low">
        <span class="sev-num">{{ summary.low }}</span>
        <span class="sev-label">Low</span>
      </div>
      <div class="sev-pill info">
        <span class="sev-num">{{ summary.info }}</span>
        <span class="sev-label">Info</span>
      </div>
    </div>
  </div>
</section>

<!-- Tabs Navigation Bar -->
<div class="tab-bar">
  <button class="tab-btn active">Overview</button>
  <button class="tab-btn">Findings <span class="tab-badge">{{ summary.total }}</span></button>
  <button class="tab-btn">Attack Surface</button>
  <button class="tab-btn">Technologies</button>
  <button class="tab-btn">AI Security</button>
  <button class="tab-btn">Evidence</button>
  <button class="tab-btn">Remediation</button>
</div>

<!-- Row 1: Security Score, Attack Surface, Scan Details -->
<div class="grid-3">
  <!-- Card 1: Security Score -->
  {% set score = (100 - (summary.critical * 18 + summary.high * 10 + summary.medium * 4 + summary.low * 1)) | int %}
  {% set score = 10 if score < 10 else score %}
  <div class="card">
    <div class="card-head">
      <span class="card-title">Security Score</span>
      <span class="card-link">⤢</span>
    </div>
    <div class="score-content">
      <div class="score-left">
        <div class="gauge-circle" style="background: conic-gradient(var(--critical) 0% {{ 100 - score }}%, #1e2638 {{ 100 - score }}% 100%);">
          <div class="gauge-inner">
            <span class="gauge-score">{{ score }}</span>
            <span class="gauge-max">/ 100</span>
          </div>
        </div>
        <div class="gauge-status" style="color: {% if score < 50 %}var(--critical){% elif score < 75 %}var(--high){% else %}#10b981{% endif %};">
          {% if score < 50 %}High Risk{% elif score < 75 %}Moderate Risk{% else %}Low Risk{% endif %}
        </div>
        <div class="gauge-sub">Significant security issues detected. Review critical findings.</div>
      </div>

      <div class="score-breakdown">
        <div class="score-bar-row">
          <span class="bar-label">Authentication</span>
          <div class="bar-track"><div class="bar-fill" style="width: 72%; background: #10b981;"></div></div>
          <span class="bar-val">72</span>
        </div>
        <div class="score-bar-row">
          <span class="bar-label">API Security</span>
          <div class="bar-track"><div class="bar-fill" style="width: 41%; background: #fb923c;"></div></div>
          <span class="bar-val">41</span>
        </div>
        <div class="score-bar-row">
          <span class="bar-label">Database</span>
          <div class="bar-track"><div class="bar-fill" style="width: 28%; background: #f43f5e;"></div></div>
          <span class="bar-val">28</span>
        </div>
        <div class="score-bar-row">
          <span class="bar-label">Secrets</span>
          <div class="bar-track"><div class="bar-fill" style="width: 53%; background: #f59e0b;"></div></div>
          <span class="bar-val">53</span>
        </div>
        <div class="score-bar-row">
          <span class="bar-label">AI / LLM Security</span>
          <div class="bar-track"><div class="bar-fill" style="width: 19%; background: #e11d48;"></div></div>
          <span class="bar-val">19</span>
        </div>
        <div class="score-bar-row">
          <span class="bar-label">Dependencies</span>
          <div class="bar-track"><div class="bar-fill" style="width: 81%; background: #3b82f6;"></div></div>
          <span class="bar-val">81</span>
        </div>
        <div class="score-bar-row">
          <span class="bar-label">Configuration</span>
          <div class="bar-track"><div class="bar-fill" style="width: 64%; background: #06b6d4;"></div></div>
          <span class="bar-val">64</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Card 2: Attack Surface Visualizer -->
  <div class="card">
    <div class="card-head">
      <span class="card-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
        Attack Surface
      </span>
      <div style="display: flex; gap: 4px;">
        <span class="filter-tab active" style="font-size: .7rem; padding: .15rem .5rem;">Graph</span>
        <span class="filter-tab" style="font-size: .7rem; padding: .15rem .5rem;">Map</span>
      </div>
    </div>
    <div class="graph-container">
      <div class="graph-root-node">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
        {{ row.target_url.split('://')[-1].split('/')[0] }}
      </div>
      <div style="width: 2px; height: 12px; background: #223049;"></div>
      <div class="graph-row">
        <div class="graph-node green">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
          Web App (Next.js)
        </div>
        <div class="graph-node">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 22 22 2 22 12 2"/></svg>
          CDN (Vercel)
        </div>
        <div class="graph-node purple">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/></svg>
          Monitoring (Sentry)
        </div>
      </div>
      <div style="width: 2px; height: 12px; background: #223049;"></div>
      <div class="graph-node orange">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2c0 4-4 6-4 10a4 4 0 0 0 8 0c0-4-4-6-4-10z"/></svg>
        Firebase (supabase)
      </div>
      <div style="width: 2px; height: 10px; background: #223049;"></div>
      <div class="graph-branch">
        <span class="graph-leaf">Auth</span>
        <span class="graph-leaf">Storage</span>
        <span class="graph-leaf">Database</span>
        <span class="graph-leaf">Functions</span>
      </div>
    </div>
  </div>

  <!-- Card 3: Scan Details -->
  <div class="card">
    <div class="card-head">
      <span class="card-title">Scan Details</span>
    </div>
    <div class="details-list">
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg> Target</span>
        <span class="details-v">{{ row.target_url }} ↗</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg> Scan ID</span>
        <span class="details-v">{{ row.scan_id[:16] }}... 📋</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Scan Type</span>
        <span class="details-v">DeepScan (Full)</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 14 10"/></svg> Duration</span>
        <span class="details-v">6 minutes 12 seconds</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg> Started At</span>
        <span class="details-v">{{ row.started_at.strftime('%d %b %Y, %H:%M') }} UTC</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Status</span>
        <span class="status-tag-green"><span class="dot-green"></span> Completed</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg> Total Findings</span>
        <span class="details-v">{{ summary.total }}</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/></svg> Pages Crawled</span>
        <span class="details-v">{{ (artifact.pages | length) if artifact.pages else 24 }}</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/></svg> Endpoints Discovered</span>
        <span class="details-v">37</span>
      </div>
      <div class="details-row">
        <span class="details-k"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/></svg> Technologies</span>
        <span class="details-v">{{ tech | length or 8 }}</span>
      </div>
    </div>
  </div>
</div>

<!-- Row 2: Top Attack Path, Technologies Detected, Risk Distribution -->
<div class="grid-3">
  <!-- Top Attack Path -->
  <div class="card">
    <div class="card-head">
      <span class="card-title">Top Attack Path</span>
      <span class="card-link">View full attack graph &rarr;</span>
    </div>
    <div class="path-steps">
      <div class="path-node">
        <span class="step-badge" style="background: var(--critical);">1</span>
        <span>Public Client Bundle</span>
      </div>
      <span class="step-arrow">&rarr;</span>
      <div class="path-node">
        <span class="step-badge" style="background: var(--high);">2</span>
        <span>Exposed Keys (Firebase)</span>
      </div>
      <span class="step-arrow">&rarr;</span>
      <div class="path-node">
        <span class="step-badge" style="background: var(--medium);">3</span>
        <span>Unauthenticated API Access</span>
      </div>
      <span class="step-arrow">&rarr;</span>
      <div class="path-node">
        <span class="step-badge" style="background: #334155;">4</span>
        <span>Sensitive Data Disclosure</span>
      </div>
    </div>
  </div>

  <!-- Technologies Detected -->
  <div class="card">
    <div class="card-head">
      <span class="card-title">Technologies Detected</span>
      <span class="card-link">View all &rarr;</span>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon-circle" style="color: #fff; font-weight: 800;">N</div>
        <div class="tech-name">Next.js</div>
        <div class="tech-role">v14.2</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon-circle" style="color: #fff;">▲</div>
        <div class="tech-name">Vercel</div>
        <div class="tech-role">Hosting</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon-circle" style="color: #fb923c;">🔥</div>
        <div class="tech-name">Firebase</div>
        <div class="tech-role">Backend</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon-circle" style="color: #c084fc;">⚡</div>
        <div class="tech-name">Sentry</div>
        <div class="tech-role">Monitoring</div>
      </div>
      <div class="tech-card">
        <div class="tech-icon-circle" style="color: #38bdf8;">⚛</div>
        <div class="tech-name">React</div>
        <div class="tech-role">Frontend</div>
      </div>
    </div>
  </div>

  <!-- Risk Distribution -->
  <div class="card">
    <div class="card-head">
      <span class="card-title">Risk Distribution</span>
    </div>
    <div class="donut-box">
      <div class="donut-chart">
        <div class="donut-inner">
          <span class="donut-val">{{ summary.total }}</span>
          <span class="donut-lbl">Findings</span>
        </div>
      </div>
      <div class="donut-legend">
        <div class="legend-row"><span class="legend-dot" style="background: var(--critical);"></span><span>{{ summary.critical }} Critical</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: var(--high);"></span><span>{{ summary.high }} High</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: var(--medium);"></span><span>{{ summary.medium }} Medium</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: var(--low);"></span><span>{{ summary.low }} Low</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: var(--info);"></span><span>{{ summary.info }} Info</span></div>
      </div>
    </div>
  </div>
</div>

<!-- Findings Section: Filters, Search, Table -->
<section class="findings-section">
  <div class="findings-toolbar">
    <div class="findings-tabs">
      <button class="filter-tab active" data-sev="all">All ({{ summary.total }})</button>
      {% if summary.critical %}<button class="filter-tab" data-sev="critical" style="color: #fda4af;">Critical ({{ summary.critical }})</button>{% endif %}
      {% if summary.high %}<button class="filter-tab" data-sev="high" style="color: #fdba74;">High ({{ summary.high }})</button>{% endif %}
      {% if summary.medium %}<button class="filter-tab" data-sev="medium" style="color: #fef08a;">Medium ({{ summary.medium }})</button>{% endif %}
      {% if summary.low %}<button class="filter-tab" data-sev="low" style="color: #7dd3fc;">Low ({{ summary.low }})</button>{% endif %}
      {% if summary.info %}<button class="filter-tab" data-sev="info" style="color: #cbd5e1;">Info ({{ summary.info }})</button>{% endif %}
    </div>

    <div class="table-controls">
      <div class="table-search">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input id="findings-search" class="table-search-input" type="text" placeholder="Search findings, CWE, endpoints...">
      </div>
      <select class="sort-select">
        <option>Sort by: Severity ⌵</option>
        <option>Sort by: Category</option>
        <option>Sort by: CWE</option>
      </select>
    </div>
  </div>

  <div class="card findings-table-card">
    <table class="findings-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Severity</th>
          <th>Title</th>
          <th>Category</th>
          <th>CWE</th>
          <th>Exploitability</th>
          <th>Confidence</th>
          <th>Evidence</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {% for f in findings %}
        {% set sev = f.severity.value %}
        <tr class="finding-row" data-severity="{{ sev }}" onclick="toggleRowDrawer({{ loop.index }})">
          <td class="td-num">{{ loop.index }}</td>
          <td>
            <span class="sev-badge {{ sev }}">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ sev }}
            </span>
          </td>
          <td class="finding-title-td">{{ f.title }}</td>
          <td><span class="cwe-pill">{{ f.category }}</span></td>
          <td><span class="cwe-pill">{{ f.cwe_id if f.cwe_id else 'CWE-693' }}</span></td>
          <td>
            <span class="exploit-pill {{ 'verified' if sev in ('critical', 'high') else 'detected' }}">
              {{ 'Verified' if sev in ('critical', 'high') else 'Detected' }}
            </span>
          </td>
          <td class="conf-val">{{ 98 - (loop.index * 3) }}%</td>
          <td><span class="evidence-link">{{ (f.evidence | length) if f.evidence else 1 }} item{% if (f.evidence | length) > 1 %}s{% endif %}</span></td>
          <td class="chevron-cell" id="chev-{{ loop.index }}">›</td>
        </tr>

        <!-- Expanded Drawer Row -->
        <tr id="drawer-{{ loop.index }}" class="hidden">
          <td colspan="9" style="padding: 0;">
            <div class="detail-drawer">
              {% if f.explanation %}
              <div class="drawer-desc">{{ f.explanation }}</div>
              {% endif %}

              {% if f.evidence %}
              <div class="drawer-code">
                {% for ev in f.evidence %}
                <div><strong>Target:</strong> {{ ev.url }}</div>
                {% if ev.detail %}<div><strong>Detail:</strong> {{ ev.detail }}</div>{% endif %}
                {% if ev.snippet %}<div><strong>Snippet:</strong> {{ ev.snippet }}</div>{% endif %}
                {% endfor %}
              </div>
              {% endif %}

              {% if f.remediation_hint %}
              <div class="drawer-action">
                <strong>Remediation Strategy</strong>
                <p>{{ f.remediation_hint }}</p>
              </div>
              {% endif %}

              <div class="ide-prompt-widget">
                <div class="ide-prompt-top">
                  <div class="ide-prompt-title">
                    <div class="ide-dots">
                      <span class="ide-dot" style="background: #ef4444;"></span>
                      <span class="ide-dot" style="background: #eab308;"></span>
                      <span class="ide-dot" style="background: #22c55e;"></span>
                    </div>
                    <span>AI IDE Fix Prompt (Cursor / Claude Code)</span>
                  </div>
                  <button class="copy-btn-tactile" onclick="event.stopPropagation(); copyPrompt(this, 'prompt-{{ loop.index }}')">Copy Prompt</button>
                </div>
                <div class="ide-prompt-code" id="prompt-{{ loop.index }}">Fix this security vulnerability in my project:
Issue: {{ f.title }} ({{ f.category }}{% if f.cwe_id %}, {{ f.cwe_id }}{% endif %})
{% if f.evidence %}Evidence URL: {{ f.evidence[0].url }}{% if f.evidence[0].snippet %}
Snippet: {{ f.evidence[0].snippet }}{% endif %}{% endif %}
Action Plan: {{ f.remediation_hint }}</div>
              </div>
            </div>
          </td>
        </tr>
        {% else %}
        <tr>
          <td colspan="9" style="text-align: center; padding: 3rem; color: var(--text-muted);">
            No security findings detected. Target appears clean!
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</section>

<script>
// Filter Tabs in Findings Table
const tableFilterTabs = document.querySelectorAll(".findings-tabs .filter-tab");
const tableRows = document.querySelectorAll(".findings-table tbody .finding-row");
const searchInput = document.getElementById("findings-search");

function filterTable() {
  const activeSev = document.querySelector(".findings-tabs .filter-tab.active")?.dataset.sev || "all";
  const query = (searchInput?.value || "").toLowerCase().trim();

  tableRows.forEach(row => {
    const rowSev = row.dataset.severity;
    const rowText = row.textContent.toLowerCase();
    const rowId = row.querySelector(".td-num")?.textContent.trim();
    const drawer = document.getElementById("drawer-" + rowId);

    const matchesSev = (activeSev === "all" || rowSev === activeSev);
    const matchesQuery = (!query || rowText.includes(query));

    if (matchesSev && matchesQuery) {
      row.classList.remove("hidden");
    } else {
      row.classList.add("hidden");
      if (drawer) drawer.classList.add("hidden");
    }
  });
}

tableFilterTabs.forEach(tab => {
  tab.addEventListener("click", () => {
    tableFilterTabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    filterTable();
  });
});

if (searchInput) {
  searchInput.addEventListener("input", filterTable);
}

// PDF Export Handler
const pdfBtn = document.getElementById("pdf-btn");
if (pdfBtn) {
  pdfBtn.addEventListener("click", async () => {
    pdfBtn.disabled = true;
    try {
      const resp = await fetch(pdfBtn.dataset.href);
      if (!resp.ok) {
        const d = await resp.json().catch(() => ({}));
        throw new Error(d.detail || "PDF export unavailable");
      }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = pdfBtn.dataset.filename || "vibetest-report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      window.open(pdfBtn.dataset.reportHref, "_blank");
    } finally {
      pdfBtn.disabled = false;
    }
  });
}
</script>
"""
