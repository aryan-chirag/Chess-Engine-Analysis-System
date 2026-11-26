"""Iterative Deepening chess search implementation."""

from chess_engine.engine.alphabeta import alphabeta
from chess_engine.engine.search_result import SearchResult
from chess_engine.engine.transposition import TranspositionTable


def iterative_deepening(
    position,
    max_depth: int,
    transposition_table=None,
) -> SearchResult:
    """Search progressively deeper using Alpha-Beta and a shared TT."""

    if (
        isinstance(max_depth, bool)
        or not isinstance(max_depth, int)
        or max_depth < 0
    ):
        raise ValueError("Maximum search depth must be a non-negative integer.")

    if (
        transposition_table is not None
        and not isinstance(transposition_table, TranspositionTable)
    ):
        raise ValueError("Invalid transposition table.")

    if max_depth == 0:
        return alphabeta(
            position,
            0,
            transposition_table=transposition_table,
        )

    if transposition_table is None:
        transposition_table = TranspositionTable()

    # Mark the beginning of a new search without clearing useful entries.
    transposition_table.new_search()

    total_nodes = 0
    last_result = None
    preferred_move = None

    for depth in range(1, max_depth + 1):

        result = alphabeta(
            position,
            depth,
            preferred_move=preferred_move,
            transposition_table=transposition_table,
        )

        total_nodes += result.nodes
        last_result = result
        preferred_move = result.best_move

        if result.best_move is None:
            break

    return SearchResult(
        best_move=last_result.best_move,
        score=last_result.score,
        depth=last_result.depth,
        nodes=total_nodes,
        principal_variation=last_result.principal_variation,
    )
