
"""Iterative Deepening chess search implementation."""

from chess_engine.engine.alphabeta import alphabeta
from chess_engine.engine.search_result import SearchResult


def iterative_deepening(position, max_depth: int) -> SearchResult:
    """Search progressively deeper using Alpha-Beta pruning."""

    if (
        isinstance(max_depth, bool)
        or not isinstance(max_depth, int)
        or max_depth < 0
    ):
        raise ValueError("Maximum search depth must be a non-negative integer.")

    total_nodes = 0
    last_result = None

    # Depth zero is handled as a single fixed-depth search.
    if max_depth == 0:
        return alphabeta(position, 0)

    for depth in range(1, max_depth + 1):

        result = alphabeta(position, depth)

        total_nodes += result.nodes
        last_result = result

        # No legal move means the root position is terminal.
        if result.best_move is None:
            break

    return SearchResult(
        best_move=last_result.best_move,
        score=last_result.score,
        depth=last_result.depth,
        nodes=total_nodes,
        principal_variation=last_result.principal_variation,
    )
