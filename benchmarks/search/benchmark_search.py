"""Compare chess search algorithms across multiple positions."""

from statistics import median
from time import perf_counter

from benchmarks.search.benchmark_positions import get_benchmark_positions
from chess_engine.core.constants import square_name
from chess_engine.notation.fen import generate_fen
from chess_engine.engine.minimax import minimax
from chess_engine.engine.negamax import negamax
from chess_engine.engine.alphabeta import alphabeta


ALGORITHMS = {
    "Minimax": minimax,
    "Negamax": negamax,
    "Alpha-Beta": alphabeta,
}

DEFAULT_DEPTHS = [1, 2]
STARTING_POSITION_DEPTHS = [1, 2, 3]
REPEATS = 3


def format_move(move):
    """Convert a Move object into UCI notation."""

    if move is None:
        return "None"

    result = (
        square_name(move.from_square)
        + square_name(move.to_square)
    )

    if move.promotion is not None:
        promotion_symbols = {
            2: "n",
            3: "b",
            4: "r",
            5: "q",
        }

        result += promotion_symbols[int(move.promotion)]

    return result


def benchmark_algorithm(position, algorithm, depth):
    """Run an algorithm repeatedly and return its measurements."""

    times = []
    results = []

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    for _ in range(REPEATS):

        start_time = perf_counter()

        result = algorithm(position, depth)

        elapsed = perf_counter() - start_time

        times.append(elapsed)
        results.append(result)

        # Verify that searching did not modify the position.
        if generate_fen(position) != original_fen:
            raise RuntimeError(
                f"{algorithm.__name__} modified the board during search."
            )

        if position.zobrist_hash != original_hash:
            raise RuntimeError(
                f"{algorithm.__name__} failed to restore the Zobrist hash."
            )

    # Verify deterministic search results.
    reference = results[0]

    for result in results[1:]:
        if (
            result.score != reference.score
            or result.best_move != reference.best_move
            or result.nodes != reference.nodes
        ):
            raise RuntimeError(
                f"{algorithm.__name__} returned inconsistent results "
                f"at depth {depth}."
            )

    median_time = median(times)
    nodes = reference.nodes

    nps = nodes / median_time if median_time > 0 else 0

    return {
        "score": reference.score,
        "best_move": format_move(reference.best_move),
        "nodes": nodes,
        "time": median_time,
        "nps": nps,
    }


def benchmark_search():
    """Benchmark all search algorithms across multiple positions."""

    positions = get_benchmark_positions()

    print("\nKNIGHTFALL — SEARCH BENCHMARK V2")
    print("=" * 95)
    print(f"Algorithms: {', '.join(ALGORITHMS)}")
    print(f"Starting position depths: {STARTING_POSITION_DEPTHS}")
    print(f"Other position depths: {DEFAULT_DEPTHS}")
    print(f"Repeated runs: {REPEATS}")

    for position_name, position in positions.items():

        depths = (
            STARTING_POSITION_DEPTHS
            if position_name == "Starting Position"
            else DEFAULT_DEPTHS
        )

        print("\n" + "=" * 95)
        print(f"POSITION: {position_name}")
        print("=" * 95)

        for depth in depths:

            print(f"\nDepth: {depth}")
            print("-" * 95)

            scores = {}

            for name, algorithm in ALGORITHMS.items():

                result = benchmark_algorithm(
                    position,
                    algorithm,
                    depth,
                )

                scores[name] = result["score"]

                print(
                    f"{name:12} | "
                    f"Score: {result['score']:7} | "
                    f"Best: {result['best_move']:6} | "
                    f"Nodes: {result['nodes']:9} | "
                    f"Time: {result['time']:9.4f}s | "
                    f"NPS: {result['nps']:12.0f}"
                )

            if len(set(scores.values())) == 1:
                print("\nScore agreement: PASS")
            else:
                print("\nWARNING: Search algorithms disagree!")
                print(scores)


if __name__ == "__main__":
    benchmark_search()