"""Alpha-Beta Pruning chess search implementation."""

from chess_engine.core.attacks import is_in_check
from chess_engine.engine.evaluation import evaluate
from chess_engine.engine.minimax import MATE_SCORE
from chess_engine.engine.move_ordering import order_moves
from chess_engine.engine.search_result import SearchResult
from chess_engine.engine.transposition import Bound, TranspositionTable
from chess_engine.movegen.legality import generate_legal_moves


def _alphabeta(
    position,
    depth,
    alpha,
    beta,
    nodes,
    transposition_table=None,
    preferred_move=None,
):
    """Recursively search a position using Alpha-Beta pruning."""

    nodes[0] += 1

    legal_moves = generate_legal_moves(position)

    # Handle checkmate and stalemate.
    if not legal_moves:
        if is_in_check(position):
            return -MATE_SCORE, None

        return 0, None

    # Evaluate the position when the search depth is reached.
    if depth == 0:
        return evaluate(position), None

    tt_move = preferred_move

    if transposition_table is not None:

        entry = transposition_table.probe(position.zobrist_hash)

        if entry is not None:

            cached_move_is_legal = entry.best_move in legal_moves

            if cached_move_is_legal:
                tt_move = entry.best_move

            if entry.depth >= depth:

                if (
                    entry.bound == Bound.EXACT
                    and cached_move_is_legal
                ):
                    return entry.score, entry.best_move

                if entry.bound == Bound.LOWERBOUND:
                    alpha = max(alpha, entry.score)

                elif entry.bound == Bound.UPPERBOUND:
                    beta = min(beta, entry.score)

                if alpha >= beta:
                    transposition_table.record_cutoff()

                    return (
                        entry.score,
                        entry.best_move if cached_move_is_legal else None,
                    )

    # Record the effective search window after TT adjustments.
    search_alpha = alpha
    search_beta = beta

    # Search promising moves first.
    legal_moves = order_moves(
        position,
        legal_moves,
        tt_move=tt_move,
    )

    best_score = float("-inf")
    best_move = None

    for move in legal_moves:

        state = position.make_move(move)

        try:
            child_score, _ = _alphabeta(
                position,
                depth - 1,
                -beta,
                -alpha,
                nodes,
                transposition_table=transposition_table,
            )

        finally:
            position.undo_move(move, state)

        score = -child_score

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)

        if alpha >= beta:
            break

    # Classify and store the search result.
    if transposition_table is not None:

        if best_score <= search_alpha:
            bound = Bound.UPPERBOUND

        elif best_score >= search_beta:
            bound = Bound.LOWERBOUND

        else:
            bound = Bound.EXACT

        transposition_table.store(
            position.zobrist_hash,
            depth,
            int(best_score),
            bound,
            best_move,
        )

    return best_score, best_move


def alphabeta(
    position,
    depth: int,
    preferred_move=None,
    transposition_table=None,
) -> SearchResult:
    """Search a position using Alpha-Beta pruning."""

    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("Search depth must be a non-negative integer.")

    if (
        transposition_table is not None
        and not isinstance(transposition_table, TranspositionTable)
    ):
        raise ValueError("Invalid transposition table.")

    nodes = [0]

    score, best_move = _alphabeta(
        position,
        depth,
        float("-inf"),
        float("inf"),
        nodes,
        transposition_table=transposition_table,
        preferred_move=preferred_move,
    )

    return SearchResult(
        best_move=best_move,
        score=int(score),
        depth=depth,
        nodes=nodes[0],
    )