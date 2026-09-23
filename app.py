"""
Sudoku Solver — Streamlit Web App
Run: uv run streamlit run app.py
"""

import numpy as np
import cv2
import streamlit as st
import tensorflow as tf

from sudoku_solver.uploader import optimized_image_uploader
from sudoku_solver import solve_sudoku_from_image, board_to_text
from sudoku_solver.styles import CUSTOM_CSS, render_board_html, tip
import streamlit.components.v1 as components
from sudoku_solver.history import (
    SolveRecord,
    HistoryStore,
    make_thumbnail,
    relative_time,
)
from datetime import datetime

# ============================================================
# Helper: render a stats table row
# ============================================================

def _stat_row(label, v_bt, v_dlx, unit="", emphasize=False,
              no_ratio=False, integer=False):
    """Render a single comparison row in HTML."""
    def fmt(v):
        if integer:
            return f"{int(v):,}"
        return f"{v:.2f} {unit}".strip()

    if no_ratio or v_dlx == 0:
        ratio = "—"
    else:
        r = v_bt / v_dlx
        if r < 1:
            ratio = f"{1/r:.1f}× (DLX)"
        elif r > 1:
            ratio = f"{r:.1f}× (BT)"
        else:
            ratio = "tie"

    bt_class  = "win" if v_bt < v_dlx else ""
    dlx_class = "win" if v_dlx < v_bt else ""
    label_style = "font-weight:700;" if emphasize else ""

    return f"""
        <tr>
            <td style="{label_style}">{label}</td>
            <td class="mono {bt_class}">{fmt(v_bt)}</td>
            <td class="mono {dlx_class}">{fmt(v_dlx)}</td>
            <td class="mono">{ratio}</td>
        </tr>
    """


# ============================================================
# Keyboard shortcut helper
# ============================================================

def inject_keyboard_shortcut():
    """
    Install a global Ctrl+Enter / Cmd+Enter listener via an iframe
    component, which Streamlit doesn't sanitize.
    """
    components.html(
        """
        <script>
        (function() {
            var KEY = '__sudoku_kb_installed_v2';
            var doc = window.parent.document;

            if (doc[KEY]) return;
            doc[KEY] = true;

            console.log('[Sudoku ML] Keyboard shortcut installed');

            doc.addEventListener('keydown', function(e) {
                // Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
                if (!(e.ctrlKey || e.metaKey)) return;
                if (e.key !== 'Enter' && e.code !== 'Enter') return;

                var buttons = doc.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var b = buttons[i];
                    var txt = (b.innerText || b.textContent || '').trim();
                    if (txt.indexOf('Solve puzzle') !== -1) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('[Sudoku ML] Triggering solve');
                        b.click();
                        return;
                    }
                }
            }, true);  // capture phase
        })();
        </script>
        """,
        height=0,
        width=0,
    )
# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="Sudoku Solver",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Initialize history store
if "history" not in st.session_state:
    st.session_state.history = HistoryStore(max_items=20)

history: HistoryStore = st.session_state.history
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Install keyboard shortcut (once per session)
inject_keyboard_shortcut()

# ============================================================
# Model Loading
# ============================================================
@st.cache_resource(show_spinner=False)
def load_model():
    return tf.keras.models.load_model("digit_model.keras")


# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown("## Settings")

    confidence_threshold = st.slider(
        "Confidence threshold",
        min_value=0.0, max_value=0.99, value=0.70, step=0.05,
        help="Digits below this confidence will be ignored. "
             "Higher = stricter, but may drop valid digits.",
    )

    st.markdown("## Solver")
    solver_choice = st.radio(
        "Algorithm",
        options=[
            "DLX (Dancing Links)",
            "Backtracking (simple)",
            "Compare both",
        ],
        index=0,
        help="DLX is much faster on hard puzzles. "
             "Compare runs both and shows the timing.",
    )

    if solver_choice == "DLX (Dancing Links)":
        st.caption(
            "🔷 Knuth's Algorithm X on an Exact Cover matrix. "
            "Uses MRV heuristic — typically 100× faster on hard puzzles."
        )
    elif solver_choice == "Backtracking (simple)":
        st.caption(
            "🔶 Classic row-by-row DFS. "
            "Simple and educational, but slower on hard puzzles."
        )
    else:
        st.caption(
            "⚖️ Runs both solvers and compares their timings."
        )

    if solver_choice == "Compare both":
        benchmark_runs = st.slider(
            "Benchmark runs",
            min_value=3, max_value=20, value=5, step=1,
            help="Each solver will be timed this many times. "
                 "More runs = more accurate but slower.",
        )
    else:
        benchmark_runs = 5

    st.markdown("## About")
    st.markdown(
        """
        <div class="text-muted" style="font-size:0.875rem; line-height:1.7;">
        A deep-learning pipeline that reads Sudoku puzzles from photos
        and solves them instantly.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## History")

    if len(history) == 0:
        st.caption("No solves yet. Solve a puzzle to see it here.")
    else:
        st.caption(f"{len(history)} recent solve(s)")

        for record in reversed(history.all()):
            with st.container():
                cols = st.columns([1, 3])

                with cols[0]:
                    if record.thumbnail_png:
                        st.image(record.thumbnail_png, width=50)
                    else:
                        st.markdown("🧩")

                with cols[1]:
                    emoji = record.difficulty.get("emoji", "🟢")
                    label = record.difficulty.get("label", "—")
                    algo_short = "DLX" if record.solver_used == "dlx" else "BT"
                    time_str = relative_time(record.timestamp)

                    st.markdown(
                        f"<div style='font-size:0.78rem; line-height:1.3;'>"
                        f"<b>{emoji} {label}</b><br>"
                        f"<span style='color:var(--text-muted);'>"
                        f"{algo_short} · {record.solver_time_ms:.1f}ms · {time_str}"
                        f"</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Load",
                        key=f"load_{record.id}",
                        use_container_width=True,
                    ):
                        st.session_state["solve_result"] = {
                            "board":          record.board,
                            "solution":       record.solution,
                            "warped":         None,
                            "warped_solved":  None,
                            "confidences":    np.ones((9, 9)) * 0.99,
                            "solved":         record.solved,
                            "solver_algorithm": record.solver_used,
                            "solver_time_ms": record.solver_time_ms,
                            "solver_stats":   {},
                            "difficulty":     record.difficulty,
                        }
                        st.session_state["_last_image_id"] = None
                        st.rerun()

        st.markdown("---")
        if st.button("🗑️ Clear history", use_container_width=True):
            history.clear()
            st.rerun()

    st.markdown("## Resources")
    st.markdown(
        """
        <div style="font-size:0.875rem; line-height:2;">
            <a href="https://github.com/satanic-kangaroo/sudoku-ml">📁 GitHub Repository</a><br>
            <a href="https://github.com/satanic-kangaroo/sudoku-ml/issues">🐛 Report an issue</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Header
# ============================================================
st.markdown(
    """
    <div class="app-header">
        <div class="logo">🧩</div>
        <div class="title-block">
            <h1>Sudoku Solver</h1>
            <p>Solve any Sudoku puzzle from a photo</p>
        </div>
        <div class="version">v1.0</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Upload
# ============================================================
st.markdown("### Upload image")

with st.expander("⚙️ Upload options", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        max_dim = st.slider(
            "Max dimension (px)",
            min_value=400, max_value=2000, value=1000, step=100,
            help="Larger = better detail, but bigger upload.",
        )
    with col_b:
        quality = st.slider(
            "JPEG quality",
            min_value=0.5, max_value=0.95, value=0.85, step=0.05,
            help="Lower = smaller file, faster upload.",
        )

uploaded = optimized_image_uploader(
    max_dimension=max_dim,
    quality=quality,
    key="sudoku_uploader",
)


# ============================================================
# Empty state
# ============================================================
if uploaded is None:
    st.markdown(
        """
        <div class="empty-state" style="margin-top:1.5rem;">
            <span class="icon">📷</span>
            <h3>No image yet</h3>
            <p>Drop or choose a Sudoku photo to get started</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### How it works")
    st.markdown(
        """
        <div class="card">
            <ol>
                <li>Detects the Sudoku grid using OpenCV</li>
                <li>Recognizes digits with a CNN model</li>
                <li>Solves the puzzle with DLX or Backtracking</li>
                <li>Displays the solution on the original image</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# Decode
# ============================================================
img_bytes = uploaded["bytes"]
img_array = np.frombuffer(img_bytes, dtype=np.uint8)
img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

if img_bgr is None:
    st.error("❌ Could not decode image.")
    st.stop()

# If the image has changed, clear the previous result
_current_image_id = None
if uploaded is not None:
    _current_image_id = f"upload_{uploaded.get('name', '')}_{len(uploaded.get('bytes', b''))}"
elif st.session_state.get("sample_image_bgr") is not None:
    _current_image_id = f"sample_{id(st.session_state['sample_image_bgr'])}"

if st.session_state.get("_last_image_id") != _current_image_id:
    st.session_state["_last_image_id"] = _current_image_id
    st.session_state["solve_result"] = None
    st.session_state["solve_signature"] = None


# ============================================================
# Upload stats
# ============================================================
orig_kb = uploaded["original_size"] / 1024
new_kb  = uploaded["optimized_size"] / 1024
saving  = (1 - uploaded["optimized_size"] / max(uploaded["original_size"], 1)) * 100

m1, m2, m3 = st.columns(3)
m1.metric("Original",   f"{orig_kb:.1f} KB")
m2.metric("Optimized",  f"{new_kb:.1f} KB", delta=f"−{saving:.0f}%")
m3.metric("Dimensions", f"{uploaded['width']}×{uploaded['height']}")


# ============================================================
# Preview + Solve
# ============================================================
st.markdown("---")
col_preview, col_action = st.columns([3, 2], gap="large")

with col_preview:
    st.markdown("### Preview")
    st.image(
        cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
        use_container_width=True,
    )

with col_action:
    st.markdown("### Ready to solve?")
    st.markdown(
        """
        <div class="text-muted" style="font-size:0.9rem; line-height:1.7;
                                       margin-bottom:1rem;">
        The model will detect the grid, recognize all digits,
        and solve the puzzle.
        </div>
        """,
        unsafe_allow_html=True,
    )

    solve_clicked = st.button(
        "🚀  Solve puzzle",
        type="primary",
        use_container_width=True,
        help="Tip: Ctrl+Enter (Cmd+Enter on Mac) to solve",
    )

# ============================================================
# Resolve solver settings (always available, outside conditionals)
# ============================================================
compare_mode = solver_choice == "Compare both"
algorithm = (
    "dlx" if solver_choice == "DLX (Dancing Links)"
    else "backtracking"
)


# ============================================================
# Solve (only when button clicked)
# ============================================================
if solve_clicked:
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(msg, pct):
        status_text.markdown(
            f'<div class="text-muted" style="font-size:0.9rem;">{msg}</div>',
            unsafe_allow_html=True,
        )
        progress_bar.progress(pct)

    with st.spinner("Loading model…"):
        model = load_model()

    result = solve_sudoku_from_image(
        img_bgr,
        model,
        confidence_threshold=confidence_threshold,
        algorithm=algorithm,
        compare_mode=compare_mode,
        benchmark_runs=benchmark_runs,
        progress_callback=update_progress,
    )

    progress_bar.empty()
    status_text.empty()

    # Save result to session_state
    st.session_state["solve_result"] = result
    st.session_state["solve_signature"] = (
        solver_choice,
        confidence_threshold,
        compare_mode,
        benchmark_runs,
    )

    # Add to history (only if solved successfully)
    if result.get("solved"):
        history.add(SolveRecord(
            board=result["board"].copy(),
            solution=result["solution"].copy(),
            solved=True,
            difficulty=result.get("difficulty", {}),
            solver_used=result["solver_algorithm"],
            solver_time_ms=result["solver_time_ms"],
            source="upload",
            thumbnail_png=make_thumbnail(img_bgr),
        ))


# ============================================================
# Render results (persists across reruns)
# ============================================================
if st.session_state.get("solve_result") is not None:
    result = st.session_state["solve_result"]

    # Warn if settings changed since last solve
    current_sig = (solver_choice, confidence_threshold, compare_mode, benchmark_runs)
    prev_sig = st.session_state.get("solve_signature")
    if prev_sig is not None and current_sig != prev_sig:
        st.info(
            "⚙️ Settings changed since the last solve. "
            "Click **Solve puzzle** to re-run with the new settings."
        )

    if "error" in result:
        st.error(f"❌ {result['error']}")
        st.info("Try a clearer image where the grid is fully visible.")
        st.stop()

    board           = result["board"]
    solution        = result["solution"]
    warped          = result["warped"]
    warped_solved   = result["warped_solved"]
    confidences     = result["confidences"]
    solved          = result["solved"]
    used_algo       = result["solver_algorithm"]
    solver_ms       = result["solver_time_ms"]
    diff            = result.get("difficulty", {})

    st.markdown("---")
    st.markdown("## Results")

    if not solved:
        st.error("❌ Could not solve the puzzle. "
                 "The detected board may contain an error.")
        st.markdown("#### Detected board")
        st.markdown(render_board_html(board), unsafe_allow_html=True)
        st.stop()

    st.success("✅ Puzzle solved successfully")

    # Solver info row
    algo_label = {
        "dlx": "DLX (Dancing Links)",
        "backtracking": "Backtracking",
    }.get(used_algo, used_algo)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        if diff:
            st.markdown(
                f'<span class="diff-badge" style="color:{diff["color"]};'
                f'border-color:{diff["color"]};">'
                f'{diff["emoji"]} <b>{diff["label"]}</b></span>',
                unsafe_allow_html=True,
            )
    with c2:
        st.markdown(f"**Solver:** {algo_label}")
    with c3:
        st.markdown(f"**Time:** `{solver_ms:.2f} ms`")

    # ===== COMPARISON MODE =====
    if "comparison" in result:
        cmp = result["comparison"]

        st.markdown("---")
        st.markdown("## ⚖️ Solver comparison")

        if cmp["winner"] == "tie":
            st.info("🤝 Both solvers finished in almost identical time.")
        else:
            winner_label = {
                "dlx": "DLX (Dancing Links)",
                "backtracking": "Backtracking",
            }[cmp["winner"]]
            st.markdown(
                f"""
                <div class="winner-card">
                    <div class="trophy">🏆</div>
                    <div class="winner-info">
                        <div class="winner-name">Winner: {winner_label}</div>
                        <div class="winner-sub">
                            {cmp['speedup']:.1f}× faster on this puzzle
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        t_bt  = cmp["backtracking"]["time_ms"]["median"]
        t_dlx = cmp["dlx"]["time_ms"]["median"]
        t_max = max(t_bt, t_dlx, 0.01)
        pct_bt  = (t_bt  / t_max) * 100
        pct_dlx = (t_dlx / t_max) * 100

        st.markdown(
            f"""
            <div class="race-container">
                <div class="race-row">
                    <div class="race-label">🔶 Backtracking</div>
                    <div class="race-track">
                        <div class="race-bar bar-bt" style="width:{pct_bt:.1f}%;"></div>
                    </div>
                    <div class="race-time">{t_bt:.2f} ms</div>
                </div>
                <div class="race-row">
                    <div class="race-label">🔷 DLX</div>
                    <div class="race-track">
                        <div class="race-bar bar-dlx" style="width:{pct_dlx:.1f}%;"></div>
                    </div>
                    <div class="race-time">{t_dlx:.2f} ms</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📊 Detailed statistics", expanded=True):
            st.markdown(
                f"""
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Backtracking</th>
                            <th>DLX</th>
                            <th>Ratio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_stat_row("Time — min",
                                   cmp["backtracking"]["time_ms"]["min"],
                                   cmp["dlx"]["time_ms"]["min"], "ms")}
                        {_stat_row("Time — median",
                                   cmp["backtracking"]["time_ms"]["median"],
                                   cmp["dlx"]["time_ms"]["median"], "ms",
                                   emphasize=True)}
                        {_stat_row("Time — mean",
                                   cmp["backtracking"]["time_ms"]["mean"],
                                   cmp["dlx"]["time_ms"]["mean"], "ms")}
                        {_stat_row("Time — max",
                                   cmp["backtracking"]["time_ms"]["max"],
                                   cmp["dlx"]["time_ms"]["max"], "ms")}
                        {_stat_row("Time — std dev",
                                   cmp["backtracking"]["time_ms"]["std"],
                                   cmp["dlx"]["time_ms"]["std"], "ms",
                                   no_ratio=True)}
                        {_stat_row(f"Nodes explored {tip('nodes_explored')}",
                                   cmp["backtracking"]["nodes"]["median"],
                                   cmp["dlx"]["nodes"]["median"], "",
                                   integer=True)}
                        {_stat_row(f"Backtracks / dead-ends {tip('backtracks')}",
                                   cmp["backtracking"]["backtracks"]["median"],
                                   cmp["dlx"]["backtracks"]["median"], "",
                                   integer=True)}
                        {_stat_row("Max recursion depth",
                                   cmp["backtracking"]["max_depth"]["median"],
                                   cmp["dlx"]["max_depth"]["median"], "",
                                   integer=True)}
                    </tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                f"Each solver ran **{benchmark_runs} times** on the same board. "
                "Values are median unless otherwise noted. "
                "A warm-up run was discarded before measuring."
            )

        if cmp["winner"] == "dlx":
            with st.expander("🎓 Why DLX is faster"):
                nodes_ratio = (
                    cmp["backtracking"]["nodes"]["median"] /
                    max(cmp["dlx"]["nodes"]["median"], 1)
                )
                st.markdown(
                    f"""
                    **Two reasons:**

                    1. **MRV heuristic (Minimum Remaining Values)** —
                       DLX always picks the constraint column with the
                       *fewest candidates*, which prunes most branches
                       before they explode. Backtracking picks the first
                       empty cell — often a poor choice.

                    2. **O(1) cover/uncover** — Dancing Links let each
                       constraint removal be a constant-time pointer
                       update. Backtracking re-scans rows/columns/boxes
                       for every `is_valid()` call.

                    **On this puzzle:**
                    - Backtracking visited **~{int(cmp['backtracking']['nodes']['median']):,}** nodes
                    - DLX visited only **~{int(cmp['dlx']['nodes']['median']):,}** nodes
                    - That's **{nodes_ratio:.1f}× fewer** nodes explored
                    """
                )

    # ===== TABS =====
    tab1, tab2, tab3 = st.tabs(["Solution", "Detection", "Images"])

    with tab1:
        given_mask  = board > 0
        solved_mask = (board == 0) & (solution > 0)

        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown('<div class="board-label">Input puzzle</div>',
                        unsafe_allow_html=True)
            st.markdown(
                render_board_html(board, given_mask=given_mask,
                                  solved_mask=solved_mask),
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown('<div class="board-label">Solved</div>',
                        unsafe_allow_html=True)
            st.markdown(render_board_html(solution, given_mask=given_mask),
                        unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="board-label">Detected by the CNN</div>',
                    unsafe_allow_html=True)
        st.markdown(render_board_html(board), unsafe_allow_html=True)

        with st.expander("Confidence matrix"):
            rows = []
            for r in range(9):
                row = []
                for c in range(9):
                    row.append("  ·  " if board[r, c] == 0
                               else f"{confidences[r, c]:.2f} ")
                rows.append(" ".join(row))
            st.code("\n".join(rows), language=None)

    with tab3:
        if warped is None or warped_solved is None:
            st.info("📷 Image preview is not available for history-loaded puzzles.")
        else:
            col_x, col_y = st.columns(2, gap="large")
            with col_x:
                st.markdown('<div class="board-label">Warped grid</div>',
                            unsafe_allow_html=True)
                st.image(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB),
                         use_container_width=True)
            with col_y:
                st.markdown('<div class="board-label">With solution (red)</div>',
                            unsafe_allow_html=True)
                st.image(cv2.cvtColor(warped_solved, cv2.COLOR_BGR2RGB),
                         use_container_width=True)

            _, buffer = cv2.imencode(".png", warped_solved)
            st.download_button(
                "💾  Download solved image",
                data=buffer.tobytes(),
                file_name="sudoku_solved.png",
                mime="image/png",
                use_container_width=True,
            )

    # ===== Export section =====
    st.markdown("### 📋 Export")
    st.caption(
        "Copy the puzzle in a format that fits your workflow. "
        "Click the copy icon in the top-right corner of any block."
    )

    export_choice = st.radio(
        "Format",
        options=[
            "🔤 Compact  ·  single line",
            "🔡 Dots     ·  human-readable",
            "🔢 Zeros    ·  code-friendly",
            "📦 Grid     ·  ASCII art",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="export_format_choice",
    )

    style_map = {
        "🔤 Compact  ·  single line": "compact",
        "🔡 Dots     ·  human-readable": "dots",
        "🔢 Zeros    ·  code-friendly": "zeros",
        "📦 Grid     ·  ASCII art": "grid",
    }
    chosen_style = style_map[export_choice]

    text = board_to_text(board, style=chosen_style)
    st.code(text, language=None)

    hints = {
        "compact": "Paste into solvers, scripts, or URL parameters.",
        "dots":    "Human-readable, great for sharing on forums.",
        "zeros":   "Directly importable in most Sudoku libraries.",
        "grid":    "Visual preview — good for screenshots.",
    }
    st.caption(hints[chosen_style])

    # ===== Stats =====
    st.markdown("### Stats")
    num_detected = int(np.sum(board > 0))
    num_solved   = int(np.sum(solution > 0)) - num_detected
    low_conf     = int(np.sum((board == 0) & (confidences > 0.1)))
    avg_conf     = float(confidences[board > 0].mean()) if num_detected else 0.0

    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("Digits detected",  f"{num_detected}/81")
    m2.metric("Cells solved",     f"{num_solved}")
    m3.metric("Avg. confidence",  f"{avg_conf * 100:.1f}%")
    m4.metric("Low-confidence",   f"{low_conf}")