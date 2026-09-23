"""Quick test for difficulty rating."""

from sudoku_solver.samples import generate_puzzle_with_unique_solution
from sudoku_solver.difficulty import rate_difficulty


def main():
    print("Testing difficulty rating...\n")

    header = f"{'Holes':<8} {'Givens':<8} {'BT nodes':<10} {'Depth':<8} {'DLX':<8} {'Score':<8} Label"
    print(header)
    print("-" * len(header))

    for target in [30, 35, 40, 45, 50, 55]:
        p = generate_puzzle_with_unique_solution(target, seed=42)
        d = rate_difficulty(p)
        print(
            f"{target:<8} {d.givens_count:<8} "
            f"{d.backtracking_nodes:<10} {d.backtracking_depth:<8} "
            f"{d.dlx_nodes:<8} {d.score:<8} {d.emoji} {d.label}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()