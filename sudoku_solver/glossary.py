"""Centralized glossary for tooltips."""

GLOSSARY = {
    "confidence_threshold": {
        "short": "Minimum model certainty",
        "long": "Digits with confidence below this value are ignored. "
                "Higher = stricter (may miss digits). Lower = looser "
                "(may accept noise).",
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
        "long": "Knuth's algorithm for Exact Cover. Uses a 2D circular "
                "linked list where cover/uncover is O(1).",
    },
}