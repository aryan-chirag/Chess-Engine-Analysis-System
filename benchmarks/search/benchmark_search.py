"""Compare chess search algorithms."""

from time import perf_counter

from chess_engine.core.position import Position
from chess_engine.engine.minimax import minimax
from chess_engine.engine.negamax import negamax
from chess_engine.engine.alphabeta import alphabeta


def benchmark_search():
    position = Position.starting_position()

    algorithms = {
        "Minimax": minimax,
        "Negamax": negamax,
        "Alpha-Beta": alphabeta,
    }

    depths = [1, 2, 3]

    print("\nChess Search Benchmark")
    print("=" * 65)

    for depth in depths:
        print(f"\nDepth: {depth}")
        print("-" * 65)

        for name, algorithm in algorithms.items():
            start_time = perf_counter()

            result = algorithm(position, depth)

            elapsed = perf_counter() - start_time

            print(f"{name:12} | "
                  f"Score: {result.score:7} | "
                  f"Nodes: {result.nodes:8} | "
                  f"Time: {elapsed:8.4f}s")


if __name__ == "__main__":
    benchmark_search()