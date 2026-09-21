"""
Sudoku Solver — Streamlit Web App
Run: uv run streamlit run app.py
"""

import io
import os
import numpy as np
import cv2
import streamlit as st
import tensorflow as tf

from sudoku_solver import solve_sudoku_from_image
from sudoku_solver.styles import CUSTOM_CSS, render_board_html


# ============================================================
# Page Config
# ============================================================

st.set_page_config(
    page_title="Sudoku Solver",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# Model Loading (cached)
# ============================================================

@st.cache_resource(show_spinner=False)
def load_model():
    return tf.keras.models.load_model("digit_model.keras")


# ============================================================
# Sidebar
# ============================================================

# ────────────────────────────────────────────────────────────
# Sidebar — "About" section
# ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Settings")

    confidence_threshold = st.slider(
        "Confidence threshold",
        min_value=0.0,
        max_value=0.99,
        value=0.70,
        step=0.05,
        help="Digits below this confidence will be ignored. "
             "Higher = stricter, but may drop valid digits.",
    )

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

    st.markdown("## Resources")
    st.markdown(
        """
        <div style="font-size:0.875rem; line-height:2;">
            <a href="https://github.com/yourusername/sudoku-ml">📁 GitHub Repository</a><br>
            <a href="https://github.com/yourusername/sudoku-ml/issues">🐛 Report an issue</a>
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
# Upload Section
# ============================================================

col_upload, col_info = st.columns([5, 4], gap="large")

with col_upload:
    st.markdown("### Upload image")

    uploaded_file = st.file_uploader(
        "Upload a Sudoku image",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        label_visibility="collapsed",
    )

# ────────────────────────────────────────────────────────────
# "How it works" card
# ────────────────────────────────────────────────────────────
with col_info:
    st.markdown("### How it works")
    st.markdown(
        """
        <div class="card">
            <ol>
                <li>Detects the Sudoku grid using OpenCV</li>
                <li>Recognizes digits with a CNN model</li>
                <li>Solves the puzzle with backtracking</li>
                <li>Displays the solution on the original image</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# If no file uploaded — empty state
# ============================================================

if uploaded_file is None:
    st.markdown(
        """
        <div class="empty-state" style="margin-top:1.5rem;">
            <span class="icon">📷</span>
            <h3>No image yet</h3>
            <p>Upload a Sudoku photo above to get started</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# Process the uploaded file
# ============================================================

file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

if img_bgr is None:
    st.error("❌ Invalid file. Please upload a valid image.")
    st.stop()


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

# ────────────────────────────────────────────────────────────
# "Ready to solve?" panel — no more inline colors
# ────────────────────────────────────────────────────────────
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
    )

    st.markdown(
        """
        <div style="margin-top:0.75rem;">
            <div style="font-size:0.8rem; font-weight:600;
                        color:#64748b; margin-bottom:0.4rem;">
                Confidence threshold
            </div>
            <div style="font-size:0.95rem; font-weight:700;
                        color:#4f46e5;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"**{confidence_threshold:.2f}**")
    st.markdown("</div></div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Progress callback — theme-aware
# ────────────────────────────────────────────────────────────
if solve_clicked:
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(msg, pct):
        status_text.markdown(
            f'<div class="text-muted" style="font-size:0.9rem;">{msg}</div>',
            unsafe_allow_html=True,
        )
        progress_bar.progress(pct)

    with st.spinner("Loading model..."):
        model = load_model()

    result = solve_sudoku_from_image(
        img_bgr,
        model,
        confidence_threshold=confidence_threshold,
        progress_callback=update_progress,
    )

    progress_bar.empty()
    status_text.empty()

    if "error" in result:
        st.error(f"❌ {result['error']}")
        st.info("Try a clearer image where the grid is fully visible.")
        st.stop()

    board = result["board"]
    solution = result["solution"]
    warped = result["warped"]
    warped_solved = result["warped_solved"]
    confidences = result["confidences"]
    solved = result["solved"]

    st.markdown("---")
    st.markdown("## Results")

    if not solved:
        st.error(
            "❌ Could not solve the puzzle. "
            "The detected board may contain an error."
        )
        st.markdown("#### Detected board")
        st.markdown(
            render_board_html(board),
            unsafe_allow_html=True,
        )
        st.stop()

    st.success("✅ Puzzle solved successfully")

    # ===== Tabs =====
    tab1, tab2, tab3 = st.tabs(["Solution", "Detection", "Images"])

    with tab1:
        given_mask = board > 0
        solved_mask = (board == 0) & (solution > 0)

        col_a, col_b = st.columns(2, gap="large")

        with col_a:
            st.markdown('<div class="board-label">Input puzzle</div>',
                        unsafe_allow_html=True)
            st.markdown(
                render_board_html(board,
                                  given_mask=given_mask,
                                  solved_mask=solved_mask),
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown('<div class="board-label">Solved</div>',
                        unsafe_allow_html=True)
            st.markdown(
                render_board_html(solution, given_mask=given_mask),
                unsafe_allow_html=True,
            )

    with tab2:
        st.markdown('<div class="board-label">Detected by the CNN</div>',
                    unsafe_allow_html=True)
        st.markdown(
            render_board_html(board),
            unsafe_allow_html=True,
        )

        with st.expander("Confidence matrix"):
            st.markdown(
                '<div style="font-size:0.85rem; color:#64748b; '
                'margin-bottom:0.5rem;">Values are model confidence '
                '(0.00 – 1.00) for each detected cell.</div>',
                unsafe_allow_html=True,
            )
            rows = []
            for r in range(9):
                row = []
                for c in range(9):
                    if board[r, c] == 0:
                        row.append("  ·  ")
                    else:
                        row.append(f"{confidences[r, c]:.2f} ")
                rows.append(" ".join(row))
            st.code("\n".join(rows), language=None)

    with tab3:
        col_x, col_y = st.columns(2, gap="large")

        with col_x:
            st.markdown('<div class="board-label">Warped grid</div>',
                        unsafe_allow_html=True)
            st.image(
                cv2.cvtColor(warped, cv2.COLOR_BGR2RGB),
                use_container_width=True,
            )

        with col_y:
            st.markdown('<div class="board-label">With solution (red)</div>',
                        unsafe_allow_html=True)
            st.image(
                cv2.cvtColor(warped_solved, cv2.COLOR_BGR2RGB),
                use_container_width=True,
            )

        _, buffer = cv2.imencode(".png", warped_solved)
        st.download_button(
            "💾  Download solved image",
            data=buffer.tobytes(),
            file_name="sudoku_solved.png",
            mime="image/png",
            use_container_width=True,
        )

    # ===== Stats =====
    st.markdown("### Stats")

    num_detected = int(np.sum(board > 0))
    num_solved = int(np.sum(solution > 0)) - num_detected
    low_conf = int(np.sum((board == 0) & (confidences > 0.1)))
    avg_conf = float(confidences[board > 0].mean()) if num_detected else 0.0

    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("Digits detected", f"{num_detected}/81")
    m2.metric("Cells solved", f"{num_solved}")
    m3.metric("Avg. confidence", f"{avg_conf * 100:.1f}%")
    m4.metric("Low-confidence", f"{low_conf}")