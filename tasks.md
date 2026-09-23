# 🎯 Sudoku ML — Tasks & Roadmap

> **Philosophy:** Ship small, ship often. One active sprint at a time.
> Every task has a checkbox, and enough detail to pick up months later.

**Last updated:** 2026-09-23
**Current Sprint:** 🎯 Sprint 1 — Quick Wins

---

## 📊 Legend

| Symbol | Meaning |
|--------|---------|
| 🎯 | Active sprint |
| ✅ | Done |
| ⏳ | In progress |
| 🧊 | Icebox (not planned) |
| ⭐ | High impact |
| ⚠️ | Blocked / needs decision |
| 🔗 | Depends on another task |

---

# 🎯 Sprint 1 — Quick Wins

**Duration:** 1 day
**Goal:** Polish UX with zero architectural risk.

---

## ✅ #4 Copy Board as Text

**Why:** Users often want to paste the puzzle into a solver, spreadsheet, or notes app.

**Files to touch:**
- `sudoku_solver/pipeline.py` — add `board_to_text()` helper
- `app.py` — add "Copy as text" button near solution tab

**Implementation details:**
- [ ] Create `board_to_text(board, style="dots")` in `sudoku_solver/pipeline.py`
  - Styles to support:
    - `"dots"` → `5 3 . . 7 . . . .`
    - `"zeros"` → `5 3 0 0 7 0 0 0 0`
    - `"grid"` → box-drawn ASCII (already have `_print_board` logic)
- [ ] Add `board_to_text(board, style="compact")` — single-line format like `530070000600195000...`
- [ ] In `app.py`, add a "Copy as text" section under the **Solution** tab
  - [ ] Three `st.code()` blocks with different formats
  - [ ] Each has its own copy button (Streamlit's `st.code` has built-in copy)
- [ ] Add a small helper note: "Click the copy icon in the top-right corner"

**Acceptance criteria:**
- Clicking any copy button copies the correct format
- All 3 formats handle empty cells consistently
- Works on mobile (Streamlit's native copy works on mobile Safari/Chrome)

---

## ✅ #5 Keyboard Shortcut Ctrl+Enter for Solve

**Why:** Saves a click when iterating on different images.

**Files to touch:**
- `app.py` — inject small JS via `st.markdown`

**Implementation details:**
- [ ] Add JS snippet that listens for `Ctrl+Enter` and clicks the primary button
- [ ] Guard: only trigger when a "Solve" button exists on the page
- [ ] Add tooltip on the button: "Ctrl+Enter to solve"
- [ ] Test on:
  - [ ] Chrome desktop
  - [ ] Firefox desktop
  - [ ] Safari desktop
  - [ ] Mobile (no keyboard, so no-op)

**Reference snippet:**
```js
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    const btn = [...document.querySelectorAll('button')]
      .find(b => b.innerText.includes('Solve puzzle'));
    btn?.click();
  }
});
```

**Acceptance criteria:**
- Ctrl+Enter (Windows/Linux) and Cmd+Enter (Mac) both work
- No false triggers when typing in a text field
- Button still works normally with mouse click

---

## ✅ #6 Explanation Tooltips

**Why:** Turn cryptic metrics into a learning opportunity.

**Files to touch:**
- `sudoku_solver/styles.py` — tooltip CSS
- `app.py` — wrap labels with tooltip HTML
- `sudoku_solver/glossary.py` *(new)* — centralized definitions

**Implementation details:**
- [ ] Create `sudoku_solver/glossary.py` with a dict:
  ```python
  GLOSSARY = {
      "confidence_threshold": {
          "short": "Minimum model certainty",
          "long": "Digits with confidence below this value are ignored. "
                  "Higher = stricter (may miss digits). Lower = looser "
                  "(may accept noise).",
          "range": "0.00 – 0.99",
          "default": 0.70,
      },
      "nodes_explored": {
          "short": "Recursive calls made",
          "long": "Every time the solver explores a new decision point, "
                  "this counter increments. Fewer nodes = more efficient.",
      },
      "backtracks": {
          "short": "Dead-ends rolled back",
          "long": "When the solver hits a dead-end and must undo a choice, "
                  "this counter increments. High backtracking = poor heuristics.",
      },
      "mrv": {
          "short": "Minimum Remaining Values",
          "long": "A heuristic: always try the most-constrained variable "
                  "first. In DLX, this means picking the column with the "
                  "fewest candidates.",
      },
      "dlx": {
          "short": "Dancing Links / Algorithm X",
          "long": "Knuth's algorithm for the Exact Cover problem. Uses a "
                  "2D circular linked list where cover/uncover is O(1).",
      },
      "exact_cover": {
          "short": "Every constraint exactly once",
          "long": "Given a binary matrix, choose rows so that every column "
                  "is covered by exactly one chosen row.",
      },
      # ... continue for all metrics
  }
  ```
- [ ] Add CSS for `.tooltip` and `.tooltip:hover .tooltip-text`
- [ ] Add helper function `tip(key)` in `sudoku_solver/styles.py` that returns HTML
- [ ] Wrap these labels with `tip(...)`:
  - [ ] Confidence threshold (sidebar)
  - [ ] Nodes explored (stats table)
  - [ ] Backtracks (stats table)
  - [ ] MRV heuristic (comparison section)
  - [ ] Solver algorithm (radio)
  - [ ] Difficulty badge
- [ ] Add a "📖 Glossary" expander at the bottom of the page listing all terms

**Acceptance criteria:**
- Hovering over any tooltip shows the explanation
- Works on both light and dark themes
- Mobile: tap-and-hold shows tooltip

---

## ✅ #3 History / Session Log

**Why:** Users often solve multiple puzzles; a log lets them compare and revisit.

**Files to touch:**
- `app.py` — sidebar section + state management
- `sudoku_solver/history.py` *(new)* — history data model

**Implementation details:**
- [ ] Create `sudoku_solver/history.py`:
  ```python
  from dataclasses import dataclass, field
  from datetime import datetime
  from typing import Optional
  import numpy as np

  @dataclass
  class SolveRecord:
      id: str                       # short uuid
      timestamp: datetime
      board: np.ndarray             # 9×9, 0 = empty
      solution: np.ndarray
      solved: bool
      difficulty: dict              # {"label", "emoji", "color"}
      solver_used: str              # "dlx" | "backtracking"
      solver_time_ms: float
      image_thumb: Optional[bytes] = None   # small PNG thumbnail
      source: str = "upload"        # "upload" | "sample" | "generated" | "camera"

  class HistoryStore:
      def __init__(self, max_items: int = 20): ...
      def add(self, record: SolveRecord) -> None: ...
      def all(self) -> list[SolveRecord]: ...
      def get(self, id: str) -> Optional[SolveRecord]: ...
      def remove(self, id: str) -> None: ...
      def clear(self) -> None: ...
      def to_dict(self) -> dict: ...        # for session_state
      @classmethod
      def from_dict(cls, d: dict) -> "HistoryStore": ...
  ```
- [ ] Store history in `st.session_state["history"]`
  - ⚠️ **Important:** streamlit session_state doesn't persist across restarts.
  - For persistence, see **Sprint 2 #3+ (optional persistence)** below.
- [ ] Add a **"History"** expander in the sidebar showing:
  - [ ] Count of solves
  - [ ] List of last N solves with:
    - [ ] Thumbnail (small, 40×40)
    - [ ] Difficulty badge
    - [ ] Solver used
    - [ ] Time
    - [ ] Relative time ("2 min ago")
  - [ ] "Clear history" button
  - [ ] Click on an entry → load that board into the current view
- [ ] After each solve, call `history.add(SolveRecord(...))`
- [ ] Cap at 20 items (FIFO eviction)

**Memory concerns:**
- Each thumbnail ≤ 5 KB
- 20 items × (9×9 int + 9×9 int + 5 KB) ≈ 200 KB total
- ✅ No infrastructure pressure

**Acceptance criteria:**
- History survives within a session
- Clicking an item re-renders that puzzle
- Clearing history works
- No memory leaks over many solves

---

# 🏃 Sprint 2 — Camera & PDF

**Duration:** 2-3 days
**Goal:** New input source (camera) and new output format (PDF).
**Depends on:** Sprint 1 (#3 History)

---

## ⭐ #1 Live Camera Input

**Why:** Mobile users can't easily pick files; camera solves it directly.

**Files to touch:**
- `app.py` — add tab UI
- `sudoku_solver/styles.py` — camera tab styling

**Implementation details:**
- [ ] Add a tabbed interface at upload section:
  ```python
  tab_upload, tab_camera = st.tabs(["📤 Upload", "📸 Camera"])
  ```
- [ ] In `tab_camera`, use `st.camera_input("Take a photo of the puzzle")`
- [ ] Convert returned `UploadedFile` to same format as uploader:
  - [ ] Reuse `np.frombuffer` + `cv2.imdecode` logic
  - [ ] Skip client-side optimization (camera output is already JPEG)
- [ ] Track source in `session_state` for history (`"source": "camera"`)
- [ ] Add a hint: "Hold the phone parallel to the grid for best results"
- [ ] Test on:
  - [ ] Mobile Chrome (Android)
  - [ ] Mobile Safari (iOS)
  - [ ] Desktop Chrome

**Known issues:**
- iOS Safari sometimes rotates the image → detect EXIF and rotate if needed

**Acceptance criteria:**
- User can take a photo and immediately solve
- Works on mobile and desktop
- Image is not upside-down or sideways
- No WebSocket disconnects (camera input is stable)

---

## ⭐ #2 PDF Download (enriched)

**Why:** PNG is nice, but PDF can include more context (board, solution, stats, history).

**Files to touch:**
- `sudoku_solver/pdf_export.py` *(new)*
- `app.py` — download button
- `pyproject.toml` / `requirements.txt` — add `reportlab`

**Implementation details:**
- [ ] Add `reportlab` dependency
- [ ] Create `sudoku_solver/pdf_export.py` with `build_solution_pdf(record) -> bytes`
- [ ] PDF structure:
  ```
  ┌─────────────────────────────────────┐
  │   🧩 Sudoku Solution                │
  │   ─────────────────────────         │
  │   Date: 2026-09-23 14:32            │
  │   Difficulty: 🟠 Hard               │
  │   Solver: DLX (5.87 ms)             │
  │                                     │
  │   ┌───────────┐  ┌───────────┐     │
  │   │  Original │  │  Solved   │     │
  │   │  grid     │  │  grid     │     │
  │   └───────────┘  └───────────┘     │
  │                                     │
  │   Stats:                            │
  │   • Digits detected: 30/81          │
  │   • Cells solved: 51                │
  │   • Avg confidence: 98.7%           │
  │   • Time: 5.87 ms                   │
  │                                     │
  │   [Original photo thumbnail]        │
  │                                     │
  │   Generated by Sudoku ML            │
  │   github.com/satanic-kangaroo/...   │
  └─────────────────────────────────────┘
  ```
- [ ] Support **multi-page export** (if history has multiple records):
  - [ ] Page 1 = cover / summary
  - [ ] Pages 2..N = one puzzle per page
  - [ ] Add a checkbox in the UI: "Include history (N puzzles)"
- [ ] Board rendering in PDF: use ReportLab `Table` with proper borders
- [ ] Include the original photo (if available) as a small thumbnail

**Acceptance criteria:**
- PDF downloads successfully
- Layout looks clean in both single and multi-page mode
- Cyrillic/Arabic text (if added later) renders correctly
- File size < 500 KB for 5 puzzles

---

## 🧊 #3+ Optional Persistence (Icebox for later)

**Not in this sprint** — just noting here:
- Session history is lost when app restarts
- If we later want persistence:
  - Option A: SQLite in `~/.sudoku_ml/history.db`
  - Option B: User account + cloud storage
  - Option C: Export/import JSON file
- ⏳ Revisit after Sprint 3

---

# 🏃 Sprint 3 — Generator & Learning

**Duration:** 1 week
**Goal:** Turn the app from a *tool* into a *learning platform*.
**Depends on:** Sprint 1 (History)

---

## ⭐ #9 Puzzle Generator with Difficulty Rating

**Why:** Users can generate infinite puzzles; also useful for training/testing the solver.

**Files to touch:**
- `sudoku_solver/samples.py` — extend existing generator
- `sudoku_solver/difficulty.py` *(new)* — scientific difficulty rating
- `app.py` — expand "Generate" section

**Implementation details:**

### Part A: Core generation (already partially exists)
- [ ] Verify `generate_random_puzzle_image()` produces **unique-solution** puzzles
  - [ ] Add `has_unique_solution(board)` — runs DLX twice with different random seeds, checks if two solutions exist
  - [ ] If not unique, re-punch the last cell
- [ ] Refactor: separate `generate_solved_board()` from `punch_holes(board, n)`

### Part B: Difficulty rating
- [ ] Create `sudoku_solver/difficulty.py`:
  ```python
  def rate_difficulty(board) -> DifficultyScore:
      """
      Rate based on multiple factors:
      - Number of givens
      - Backtracking solver: nodes + max depth
      - DLX solver: nodes
      - Human techniques needed (if human_solver is available)
      """
  ```
- [ ] Factors:
  - [ ] `givens_count` (higher = easier)
  - [ ] `backtracking_nodes` (higher = harder)
  - [ ] `max_recursion_depth`
  - [ ] `branching_factor_at_root`
  - [ ] (Sprint 3 part 2) `human_techniques_required`
- [ ] Combine into a single score 1-10
- [ ] Map score to label:
  - [ ] 1–3 = 🟢 Easy
  - [ ] 4–5 = 🟡 Medium
  - [ ] 6–7 = 🟠 Hard
  - [ ] 8–9 = 🔴 Expert
  - [ ] 10 = ⚫ Evil

### Part C: UI
- [ ] Replace current hole slider with a "Difficulty target" selector:
  ```
  🟢 Easy  🟡 Medium  🟠 Hard  🔴 Expert  🎲 Random
  ```
- [ ] Behind the scenes, keep generating until the target difficulty is hit (max 10 attempts)
- [ ] Show:
  - [ ] Actual difficulty score
  - [ ] Givens count
  - [ ] Generation time
- [ ] Add "Show puzzle" preview before solving

**Acceptance criteria:**
- Generated puzzles always have exactly one solution
- Difficulty labels correlate with human perception (validate on 20 manual tests)
- Generation takes < 3 seconds even for hardest levels

---

## ⭐ #10 Human Solver / Step-by-Step Explanation

**Why:** The most requested feature. Turns the app into a teaching tool.
**Depends on:** #9 (difficulty rating shares the technique framework)

**Files to touch:**
- `sudoku_solver/human_solver.py` *(new)* — the big one
- `sudoku_solver/techniques.py` *(new)* — individual technique implementations
- `app.py` — new "Learn" tab

**Concept:** Solve like a human would, step by step, using logical techniques before falling back to guessing.

### Part A: Techniques library

Implement these in order of complexity:

**Tier 1 — Basic (always needed):**
- [ ] **Naked Single** — a cell has only one candidate left
- [ ] **Hidden Single** — a digit fits in only one cell of a row/col/box

**Tier 2 — Intermediate:**
- [ ] **Naked Pair** — two cells in a unit share exactly two candidates
- [ ] **Hidden Pair** — two digits only appear in the same two cells
- [ ] **Naked Triple** / **Hidden Triple**
- [ ] **Pointing Pair/Triple** — a digit in a box restricted to one row/col
- [ ] **Box-Line Reduction** — same idea inverted

**Tier 3 — Advanced:**
- [ ] **X-Wing** — 2×2 pattern on 4 cells
- [ ] **Swordfish** — 3×3 extension
- [ ] **XY-Wing** — pivot + 2 pincers
- [ ] **XYZ-Wing**

**Tier 4 — Expert:**
- [ ] **Unique Rectangle** types 1-4
- [ ] **Coloring / Simple Colors**
- [ ] **XY-Chain**

**Fallback:**
- [ ] If no technique applies → backtracking guess
- [ ] Mark this step visually as "guessing"

### Part B: Engine

- [ ] `human_solver.py`:
  ```python
  @dataclass
  class SolveStep:
      index: int
      technique: str           # "naked_single", "x_wing", ...
      cells_involved: list[tuple[int, int]]
      digits_eliminated: list[int]
      placement: Optional[tuple[int, int, int]]  # (r, c, digit)
      explanation: str         # human-readable text
      board_before: np.ndarray
      board_after: np.ndarray
      candidates_before: dict  # {(r, c): set[int]}

  def solve_humanly(board) -> tuple[np.ndarray, list[SolveStep]]:
      """Solve step by step, recording every deduction."""
  ```
- [ ] Track candidate sets throughout
- [ ] Priority order: cheapest technique first → escalate if stuck

### Part C: Explanations

For each technique, write a **human-friendly explanation** in the user's language:

Example outputs:
```
Step 1 — Naked Single
  Cell R4C5 has only one possible value: 8.
  All other digits (1-7, 9) appear in its row, column, or box.

Step 2 — Hidden Single
  In row 3, digit 4 can only fit in cell R3C7.
  Every other cell in the row already excludes 4.

Step 3 — X-Wing on digit 6
  Digit 6 is restricted to R2C4, R2C8, R7C4, R7C8.
  These four cells form an X pattern → 6 can't appear elsewhere in
  columns 4 and 8.
```

### Part D: UI

- [ ] Add a new tab **"📚 Learn"**
- [ ] Show the board with:
  - [ ] Highlighted cells (colored by technique type)
  - [ ] Candidates overlay (small digits in corners)
- [ ] Timeline slider:
  - [ ] Step 0 = original puzzle
  - [ ] Step N = final solution
- [ ] Play/Pause/Step forward/Step back buttons
- [ ] Auto-play mode with adjustable speed
- [ ] Sidebar shows:
  - [ ] Current technique name
  - [ ] Human-readable explanation
  - [ ] List of previously used techniques with counts
- [ ] Statistics: "Solved with 12 steps using 5 techniques"

**Acceptance criteria:**
- [ ] The engine solves >90% of published Sudoku puzzles using only logic
- [ ] Every step is verifiable by hand
- [ ] The explanation text is clear to a beginner
- [ ] Animation runs smoothly on mobile

---

# 🏃 Sprint 4 — Wow Factor

**Duration:** 2 weeks
**Goal:** Make the project viral.
**Depends on:** Sprint 2 (#1 Camera)

---

## ⭐ #8 DLX Visualizer

**Why:** DLX is the most "magical" algorithm here; visualizing it is mesmerizing and educational.

**Files to touch:**
- `components/dlx_visualizer/index.html` *(new)* — D3.js visualizer
- `components/dlx_visualizer/dlx_viz.js` *(new)*
- `sudoku_solver/dlx_solver.py` — add event emission
- `app.py` — new "Visualize" tab

**Implementation details:**

### Part A: Instrument DLX
- [ ] Add optional `event_log` parameter to `_search()`
- [ ] Emit events:
  - [ ] `choose_column(col_id, size)`
  - [ ] `try_row(row_id)`
  - [ ] `cover_column(col_id)`
  - [ ] `uncover_column(col_id)`
  - [ ] `dead_end()`
  - [ ] `solution_found()`
- [ ] Events are lightweight dicts — no heavy serialization

### Part B: D3 Visualizer
- [ ] Use **D3.js** with force-directed layout or grid layout
- [ ] Render nodes as circles, connections as lines
- [ ] Columns highlighted in blue, rows in orange
- [ ] Animate cover/uncover:
  - [ ] Nodes fade out and fly to the side
  - [ ] Lines retract smoothly
- [ ] Timeline scrubber at bottom
- [ ] Speed control (0.25× — 4×)

### Part C: Sync with Python
- [ ] Stream events via `st.components.v1.html`
- [ ] Use `st.session_state` to hold the event log
- [ ] The component reads from a static JSON blob (no real-time push needed)

### Part D: Wrap
- [ ] Add "🎬 Visualize DLX" button next to the comparison
- [ ] Opens a modal / new tab with the visualizer
- [ ] Include a short intro paragraph explaining what's happening

**Acceptance criteria:**
- Runs smoothly at 60 FPS for ~500 events
- Works on mobile (may need reduced detail)
- User can understand what's happening without reading code

---

## ⭐ #7 AR Overlay

**Why:** The single most impressive feature. Almost no Sudoku app does this live.
**Depends on:** #1 Live Camera

**Files to touch:**
- `sudoku_solver/ar_overlay.py` *(new)*
- `app.py` — new "AR" mode

**Implementation details:**

### Part A: Frame processing
- [ ] Capture frame from `streamlit-webrtc` (or `st.camera_input` in loop)
- [ ] Downscale to 640×480 for speed
- [ ] Run detection pipeline:
  - [ ] Grid detection
  - [ ] Warp
  - [ ] Digit recognition (batched)
  - [ ] Solve
- [ ] Overlay solution back onto **original frame** (not warped)

### Part B: Stability
- [ ] Track grid corners across frames (optical flow or Kalman filter)
- [ ] Only re-solve when digit set changes
- [ ] Smooth overlay positions between frames

### Part C: Performance
- [ ] Convert model to TFLite for faster inference (~5× faster)
- [ ] Batch all 81 cells in one model call
- [ ] Cache last solved board and reuse if board unchanged

### Part D: UI
- [ ] New tab **"📸 Live"**
- [ ] Show video feed with overlay
- [ ] FPS counter
- [ ] "Snapshot and solve" button (freezes frame)

**Acceptance criteria:**
- ≥ 10 FPS on a mid-range phone
- Overlay stays locked to the grid
- Works with moderate hand shake

**Known risks:**
- streamlit-webrtc has a learning curve
- Mobile browser WebRTC permissions may vary

---

# 🏃 Sprint 5 — Product

**Duration:** 2 weeks
**Goal:** Turn into a real shippable product.
**Depends on:** All previous sprints (architecture must be stable)

---

## ⭐ #11 TFLite + PWA

**Why:** Offline-capable, privacy-first, installable on phones.

**Files to touch:**
- `scripts/export_tflite.py` *(new)*
- `pwa/` *(new)* — Progressive Web App
- `pwa/service-worker.js`
- `pwa/manifest.json`

**Implementation details:**

### Part A: TFLite export
- [ ] Script: `scripts/export_tflite.py`
  ```python
  import tensorflow as tf

  model = tf.keras.models.load_model("digit_model.keras")
  converter = tf.lite.TFLiteConverter.from_keras_model(model)
  converter.optimizations = [tf.lite.Optimize.DEFAULT]
  # Optional: int8 quantization (smaller, faster, slightly less accurate)
  # converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

  tflite = converter.convert()
  open("models/digit_model.tflite", "wb").write(tflite)
  ```
- [ ] Verify accuracy on test set (target: ≥ 99%)
- [ ] Compare size: `.keras` vs `.tflite`

### Part B: PWA
- [ ] Port inference to **TensorFlow.js**:
  - [ ] Convert TFLite → TFJS via `tensorflowjs_converter`
  - [ ] Load in browser, run inference
- [ ] Port pipeline to JS:
  - [ ] Grid detection: **OpenCV.js**
  - [ ] Warp: `cv2.getPerspectiveTransform` equivalent
  - [ ] Solver: port DLX to JS (or use Backtracking for simplicity)
- [ ] Service worker for offline caching
- [ ] `manifest.json` for install prompt

### Part C: Deployment
- [ ] Host on GitHub Pages or Vercel
- [ ] Landing page with "Install app" button
- [ ] Test install flow on:
  - [ ] Android Chrome
  - [ ] iOS Safari (uses "Add to Home Screen")
  - [ ] Desktop Chrome

**Acceptance criteria:**
- App works completely offline
- Install prompt appears
- Inference runs in < 500 ms on mid-range phone
- Model size < 500 KB

---

# 🧊 Icebox — Open Source Community

**Not in sprint planning** — long-term vision.

## Distribution
- [ ] PyPI package (`pip install sudoku-ml`)
- [ ] Docker image (`docker run satanickangaroo/sudoku-ml`)
- [ ] Conda-forge recipe
- [ ] Homebrew tap (macOS)

## Documentation
- [ ] MkDocs Material site
- [ ] API reference (auto-generated from docstrings)
- [ ] Tutorial series ("Build it yourself in 30 min")
- [ ] Algorithm deep-dive blog posts
- [ ] Video walkthroughs

## CI/CD
- [ ] GitHub Actions:
  - [ ] Lint (`ruff`, `black`)
  - [ ] Test (`pytest` + coverage)
  - [ ] Type check (`mypy`)
  - [ ] Auto-deploy to Streamlit Cloud on merge
  - [ ] Auto-release to PyPI on tag
- [ ] Pre-commit hooks
- [ ] Dependabot

## Community
- [ ] `CONTRIBUTING.md`
- [ ] `CODE_OF_CONDUCT.md`
- [ ] `SECURITY.md`
- [ ] Issue templates (bug, feature, question)
- [ ] PR template
- [ ] Discussions enabled
- [ ] "Good first issue" labels
- [ ] Contributor recognition (all-contributors bot)

---

# 🧊 Icebox — Out-of-the-Box Ideas

**Saved for later. Revisit when core is rock-solid.**

## 🤖 Sudoku Coach
Instead of solving, guide the user with hints:
- "Look at R4C5. Can you spot a hidden single?"
- Progressive hints (nudge → technique name → exact move)
- Track user's progress and mistakes

## 🎮 Sudoku Battle
- Multiplayer: race against another user
- WebSocket-based real-time
- Elo rating system
- Leaderboards

## 🧩 Sudoku Variants
- **Diagonal Sudoku** — both main diagonals must contain 1-9
- **Irregular Sudoku** — 9 non-rectangular regions
- **Killer Sudoku** — regions have sum constraints
- **Samurai Sudoku** — 5 overlapping grids
- **Thermo Sudoku** — thermometers
- **Arrow Sudoku** — arrows with sums
- **Multi-Sudoku** — 3-9 grids side by side

**Note:** DLX architecture already supports variants; only constraint columns need to change.

## 📊 Sudoku Research Lab
- Batch benchmark on 1000+ puzzles
- Statistical analysis of solver performance
- Puzzle difficulty classification ML model
- Generate a "state of Sudoku solvers" report
- Support importing from known datasets (Norvig's, Kaggle)

## 🎨 Sudoku Art
- Take an image (photo, logo)
- Generate a Sudoku puzzle whose solution forms that image
- Very Instagram-friendly

## 🌍 Localization
- [ ] Persian (fa)
- [ ] Arabic (ar)
- [ ] French (fr)
- [ ] Spanish (es)
- [ ] German (de)
- [ ] Chinese (zh)
- [ ] Japanese (ja)
- RTL support for Arabic/Persian

## 🔌 REST API
- FastAPI backend
- Endpoints:
  - `POST /solve` — image → solution
  - `POST /generate` — difficulty → puzzle
  - `POST /explain` — puzzle → steps
  - `GET /benchmark` — run benchmark
- Swagger UI
- Rate limiting
- API keys

## 📚 Batch PDF Workbook
- Upload a PDF of 50 puzzles
- Solve all
- Output a new PDF with solutions overlaid
- Useful for teachers, publishers

## 📱 Native Mobile Apps
- React Native or Flutter wrapper
- Uses the same TFLite model
- Native camera integration
- Push notifications (daily puzzle)

---

# 📝 Decision Log

Record major decisions here so future-you understands the "why".

| Date | Decision | Reason |
|------|----------|--------|
| 2026-09-22 | Use custom Streamlit component for uploader | Fix mobile WebSocket disconnect + reduce payload 95% |
| 2026-09-22 | Use DLX as default solver, Backtracking as fallback | DLX is 100-200× faster on hard puzzles |
| 2026-09-22 | Synthetic dataset over MNIST | Sudoku digits are printed, not handwritten |
| 2026-09-23 | Skip PyPI for now | Focus on user features; packaging later |
| 2026-09-23 | Session-only history (no persistence) | Infrastructure simplicity; revisit in Sprint 3 |

---

# 🎯 Current Focus

**Sprint:** 1 — Quick Wins
**Next task:** #4 Copy Board as Text
**Est. time:** 30 min

**Blocked items:** None

**Notes:**
- Remember to update this file after each sprint
- Archive completed sprints into `CHANGELOG.md`
- Keep `README.md` in sync with new features

---

*Last updated: 2026-09-23*