"""Adaptive (light + dark) CSS for the Sudoku Solver app."""

import numpy as np


CUSTOM_CSS = """
<style>
/* ============================================================
   DESIGN TOKENS — LIGHT (default)
   ============================================================ */
:root {
    /* Brand */
    --primary:         #4f46e5;
    --primary-hover:   #4338ca;
    --primary-soft:    #eef2ff;
    --primary-on:      #ffffff;

    /* Semantic */
    --success:         #059669;
    --success-soft:    #ecfdf5;
    --danger:          #dc2626;
    --danger-soft:     #fef2f2;
    --warning:         #d97706;
    --warning-soft:    #fffbeb;

    /* Surfaces */
    --bg:              #f6f7fb;
    --surface:         #ffffff;
    --surface-hover:   #f8fafc;
    --surface-active:  #f1f5f9;

    /* Borders */
    --border:          #e5e7eb;
    --border-strong:   #cbd5e1;

    /* Text */
    --text:            #0f172a;
    --text-muted:      #64748b;
    --text-subtle:     #94a3b8;

    /* Shadows */
    --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.06);
    --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.08);

    /* Sudoku board */
    --board-border:       #1e293b;
    --board-grid:         #e5e7eb;
    --board-grid-strong:  #334155;
    --board-bg:           #ffffff;
    --board-given-bg:     #f8fafc;
    --board-given-text:   #0f172a;
    --board-solved-bg:    #fef2f2;
    --board-solved-text:  #dc2626;
    --board-empty-text:   #cbd5e1;

    /* Fonts */
    --font:      -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo,
                 Consolas, monospace;
}

/* ============================================================
   DESIGN TOKENS — DARK
   ============================================================ */
@media (prefers-color-scheme: dark) {
    :root {
        --primary:         #818cf8;
        --primary-hover:   #a5b4fc;
        --primary-soft:    #1e1b4b;
        --primary-on:      #0b1220;

        --success:         #34d399;
        --success-soft:    #064e3b;
        --danger:          #f87171;
        --danger-soft:     #450a0a;
        --warning:         #fbbf24;
        --warning-soft:    #451a03;

        --bg:              #0b1220;
        --surface:         #111a2e;
        --surface-hover:   #16223c;
        --surface-active:  #1c2b4a;

        --border:          #1f2c48;
        --border-strong:   #334155;

        --text:            #e2e8f0;
        --text-muted:      #94a3b8;
        --text-subtle:     #64748b;

        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.30);
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.35), 0 1px 2px rgba(0, 0, 0, 0.25);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.40);
        --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.50);

        --board-border:       #475569;
        --board-grid:         #1f2c48;
        --board-grid-strong:  #64748b;
        --board-bg:           #0f172a;
        --board-given-bg:     #1a2540;
        --board-given-text:   #e2e8f0;
        --board-solved-bg:    #2a1215;
        --board-solved-text:  #fca5a5;
        --board-empty-text:   #475569;
    }
}

/* ============================================================
   BASE / RESET
   ============================================================ */
html, body, [class*="css"], .stApp {
    font-family: var(--font);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp,
[data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ============================================================
   SIDEBAR TOGGLE BUTTON (Open / Close)
   ============================================================ */

/* حذف نکن کل toolbar — فقط آیتم‌های اضافی */
[data-testid="stToolbarActions"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* دکمهٔ باز کردن سایدبار — هر دو نسخه (قدیم و جدید) */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    position: fixed !important;
    top: 0.85rem !important;
    left: 0.85rem !important;
    z-index: 1000000 !important;

    width: 42px !important;
    height: 42px !important;
    padding: 0 !important;

    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: var(--shadow-sm) !important;
    color: var(--text) !important;

    cursor: pointer !important;
    transition: background 0.18s ease, border-color 0.18s ease,
                color 0.18s ease, transform 0.18s ease,
                box-shadow 0.18s ease !important;
}

/* آیکون داخل دکمه */
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg {
    width: 20px !important;
    height: 20px !important;
    fill: currentColor !important;
    transition: transform 0.18s ease !important;
}

/* حالت هاور */
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover {
    background: var(--primary-soft) !important;
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) scale(1.04) !important;
}

/* حرکت جزئی آیکون در هاور */
[data-testid="stSidebarCollapsedControl"]:hover svg,
[data-testid="collapsedControl"]:hover svg {
    transform: translateX(2px) !important;
}

/* حالت کلیک */
[data-testid="stSidebarCollapsedControl"]:active,
[data-testid="collapsedControl"]:active {
    transform: translateY(0) scale(0.97) !important;
    box-shadow: var(--shadow-xs) !important;
}

/* حالت فوکوس برای دسترس‌پذیری (کیبورد) */
[data-testid="stSidebarCollapsedControl"]:focus-visible,
[data-testid="collapsedControl"]:focus-visible {
    outline: 2px solid var(--primary) !important;
    outline-offset: 2px !important;
}

/* ============================================================
   دکمهٔ بستن سایدبار (وقتی سایدبار باز است)
   ============================================================ */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    padding: 0.35rem !important;
    transition: background 0.15s ease, color 0.15s ease !important;
}

[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapseButton"]:hover {
    background: var(--surface-hover) !important;
    color: var(--primary) !important;
}

[data-testid="stSidebarCollapseButton"] svg {
    fill: currentColor !important;
}
/* Layout */
.main .block-container {
    max-width: 1180px;
    padding: 1.5rem 2rem 4rem 2rem;
}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */
h1, h2, h3, h4, h5, h6 {
    color: var(--text);
    font-weight: 700;
    letter-spacing: -0.01em;
}

h2 { font-size: 1.5rem;  margin-top: 2rem; }
h3 { font-size: 1.15rem; margin-top: 1.5rem; }
h4 { font-size: 1rem;    margin-top: 1rem; }

p, .stMarkdown p {
    color: var(--text-muted);
    line-height: 1.65;
}

a, a:visited {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
}

a:hover { text-decoration: underline; }

code, pre {
    font-family: var(--font-mono);
    color: var(--text);
}

/* ============================================================
   APP HEADER
   ============================================================ */
.app-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.75rem;
}

.app-header .logo {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    background: var(--primary-soft);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    flex-shrink: 0;
    border: 1px solid var(--border);
}

.app-header .title-block h1 {
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0;
    color: var(--text);
    line-height: 1.2;
}

.app-header .title-block p {
    margin: 0.2rem 0 0 0;
    font-size: 0.9rem;
    color: var(--text-muted);
}

.app-header .version {
    margin-left: auto;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--primary);
    background: var(--primary-soft);
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    border: 1px solid var(--border);
    letter-spacing: 0.03em;
}

/* ============================================================
   BUTTONS
   ============================================================ */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    padding: 0.65rem 1.4rem !important;
    transition: background 0.15s ease, box-shadow 0.15s ease,
                transform 0.15s ease, border-color 0.15s ease;
    min-height: 44px;
    font-family: var(--font) !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--primary) !important;
    color: var(--primary-on) !important;
    border: 1px solid var(--primary) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: var(--primary-hover) !important;
    border-color: var(--primary-hover) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px);
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    background: var(--surface-hover) !important;
    border-color: var(--border-strong) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
}

/* ============================================================
   FILE UPLOADER
   ============================================================ */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border-strong) !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
    transition: border-color 0.2s ease, background 0.2s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    background: var(--surface-hover) !important;
}

[data-testid="stFileUploader"] section {
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] div {
    color: var(--text-muted) !important;
}

[data-testid="stFileUploader"] button {
    background: var(--primary) !important;
    color: var(--primary-on) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ============================================================
   SIDEBAR
   ============================================================ */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.25rem;
}

[data-testid="stSidebar"] h2 {
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-subtle) !important;
    font-weight: 700 !important;
    margin: 1.5rem 0 0.75rem 0 !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] h2:first-child {
    margin-top: 0 !important;
}

/* ============================================================
   SLIDER
   ============================================================ */
[data-testid="stSlider"] [role="slider"] {
    background-color: var(--primary) !important;
    border-color: var(--primary) !important;
}

[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    box-shadow: 0 0 0 2px var(--primary) !important;
}

/* Track fill */
[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background: var(--primary) !important;
}

/* ============================================================
   METRICS
   ============================================================ */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.9rem 1rem !important;
    box-shadow: var(--shadow-xs) !important;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}

[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-sm) !important;
    border-color: var(--border-strong) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: var(--text) !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    font-variant-numeric: tabular-nums;
}

/* ============================================================
   TABS
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0 !important;
    margin-bottom: 1.25rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: color 0.15s ease, border-color 0.15s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ============================================================
   PROGRESS BAR
   ============================================================ */
.stProgress > div > div {
    background: var(--border) !important;
    border-radius: 999px !important;
}

.stProgress > div > div > div > div {
    background: var(--primary) !important;
    transition: width 0.3s ease;
}

/* ============================================================
   ALERTS
   ============================================================ */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
}

[data-testid="stAlert"] svg { color: currentColor !important; }

/* ============================================================
   EXPANDER
   ============================================================ */
details {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.25rem 0.5rem !important;
}

details summary {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.5rem !important;
    cursor: pointer;
}

details summary:hover { color: var(--primary) !important; }

/* ============================================================
   CARDS
   ============================================================ */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-xs);
    margin-bottom: 1rem;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.75rem;
}

.card ol, .card ul {
    margin: 0;
    padding-left: 1.25rem;
    color: var(--text-muted);
    line-height: 1.9;
    font-size: 0.9rem;
}

.card ol li::marker {
    color: var(--primary);
    font-weight: 700;
}

/* ============================================================
   EMPTY STATE
   ============================================================ */
.empty-state {
    text-align: center;
    padding: 3.5rem 2rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: var(--shadow-xs);
}

.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 0.75rem;
    display: block;
    opacity: 0.85;
}

.empty-state h3 {
    margin: 0 0 0.4rem 0;
    font-size: 1.15rem;
    color: var(--text);
}

.empty-state p {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.92rem;
}

/* ============================================================
   SUDOKU BOARD
   ============================================================ */
.board-wrapper {
    text-align: center;
    padding: 0.75rem 0;
}

.board-label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-subtle);
    margin-bottom: 0.7rem;
}

.sudoku-board {
    display: inline-grid;
    grid-template-columns: repeat(9, 42px);
    grid-template-rows: repeat(9, 42px);
    border: 2.5px solid var(--board-border);
    border-radius: 10px;
    overflow: hidden;
    background: var(--board-bg);
    box-shadow: var(--shadow-md);
    direction: ltr;
}

.sudoku-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    border-right: 1px solid var(--board-grid);
    border-bottom: 1px solid var(--board-grid);
    transition: background 0.15s ease, color 0.15s ease;
}

.sudoku-cell.box-right  { border-right: 2px solid var(--board-grid-strong); }
.sudoku-cell.box-bottom { border-bottom: 2px solid var(--board-grid-strong); }

.sudoku-cell.last-col { border-right: none; }
.sudoku-cell.last-row { border-bottom: none; }

.sudoku-cell.given {
    color: var(--board-given-text);
    background: var(--board-given-bg);
}

.sudoku-cell.solved {
    color: var(--board-solved-text);
    background: var(--board-solved-bg);
    font-weight: 700;
}

.sudoku-cell.empty {
    color: var(--board-empty-text);
    background: var(--board-bg);
}

/* ============================================================
   UTILITIES
   ============================================================ */
.text-muted    { color: var(--text-muted); }
.text-subtle   { color: var(--text-subtle); }
.text-primary  { color: var(--primary); }
.text-center   { text-align: center; }

/* Force color inheritance in markdown blocks */
.stMarkdown, .stMarkdown * {
    color: inherit;
}

/* Ensure metric container labels don't fight */
.stMarkdown h3, .stMarkdown h4 { color: var(--text); }

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 768px) {
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        top: 0.5rem !important;
        left: 0.5rem !important;
        width: 44px !important;
        height: 44px !important;
    }
    .app-header {
        padding-left: 3rem;
    }
    .sudoku-board {
        grid-template-columns: repeat(9, 34px);
        grid-template-rows: repeat(9, 34px);
    }
    .sudoku-cell { font-size: 1rem; }
    .app-header .title-block h1 { font-size: 1.3rem; }
    .main .block-container { padding: 1rem 1rem 3rem 1rem; }
}
/* ============================================================
   SOLVER COMPARISON
   ============================================================ */
.race-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin: 1rem 0;
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
}

.race-row {
    display: grid;
    grid-template-columns: 130px 1fr 100px;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.9rem;
}

.race-label {
    font-weight: 700;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 0.35rem;
}

.race-track {
    position: relative;
    height: 26px;
    background: var(--surface-hover);
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--border);
}

.race-bar {
    height: 100%;
    border-radius: 5px;
    transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
    display: flex;
    align-items: center;
    padding-left: 0.5rem;
    color: white;
    font-weight: 700;
    font-size: 0.75rem;
}

.race-bar.bar-bt {
    background: linear-gradient(90deg, #f59e0b, #ea580c);
}

.race-bar.bar-dlx {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

.race-time {
    font-family: var(--font-mono);
    font-weight: 700;
    color: var(--text);
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-size: 0.85rem;
}

.winner-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border: 1px solid #fbbf24;
    border-radius: 12px;
    margin: 0.75rem 0;
    box-shadow: 0 2px 12px rgba(251, 191, 36, 0.25);
}

@media (prefers-color-scheme: dark) {
    .winner-card {
        background: linear-gradient(135deg, #422006, #713f12);
        border-color: #a16207;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
    }
}

.winner-card .trophy {
    font-size: 1.75rem;
}

.winner-card .winner-info {
    flex: 1;
}

.winner-card .winner-name {
    font-weight: 800;
    font-size: 1rem;
    color: var(--text);
}

.winner-card .winner-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.15rem;
}

.stats-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    margin: 0.5rem 0;
}

.stats-table th {
    text-align: left;
    padding: 0.6rem 0.8rem;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.72rem;
    border-bottom: 1px solid var(--border);
}

.stats-table td {
    padding: 0.55rem 0.8rem;
    border-bottom: 1px solid var(--border);
    font-variant-numeric: tabular-nums;
    color: var(--text);
}

.stats-table td.mono {
    font-family: var(--font-mono);
}

.stats-table tr:last-child td {
    border-bottom: none;
}

.stats-table td.win {
    color: var(--success);
    font-weight: 700;
}

.diff-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    background: var(--surface-hover);
    border: 1px solid var(--border);
}
</style>
"""


def render_board_html(board, given_mask=None, solved_mask=None):
    """Render a 9x9 board as HTML (theme-adaptive via CSS variables)."""
    if given_mask is None:
        given_mask = board > 0
    if solved_mask is None:
        solved_mask = np.zeros_like(board, dtype=bool)

    cells = []
    for r in range(9):
        for c in range(9):
            classes = ["sudoku-cell"]

            if c == 8:
                classes.append("last-col")
            elif c in (2, 5):
                classes.append("box-right")

            if r == 8:
                classes.append("last-row")
            elif r in (2, 5):
                classes.append("box-bottom")

            if board[r, c] == 0:
                classes.append("empty")
                text = "·"
            elif given_mask[r, c]:
                classes.append("given")
                text = str(int(board[r, c]))
            else:
                classes.append("solved")
                text = str(int(board[r, c]))

            cells.append(f'<div class="{" ".join(classes)}">{text}</div>')

    return (
        '<div class="board-wrapper">'
        '<div class="sudoku-board">' + "".join(cells) + "</div>"
        "</div>"
    )