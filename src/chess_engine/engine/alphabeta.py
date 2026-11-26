"""Alpha-Beta Pruning chess search implementation."""

from chess_engine.core.attacks import is_in_check
from chess_engine.engine.evaluation import evaluate
from chess_engine.engine.minimax import MATE_SCORE
from chess_engine.engine.move_ordering import order_moves
from chess_engine.engine.quiescence import _quiescence
from chess_engine.engine.search_result import SearchResult
from chess_engine.engine.transposition import (
    Bound,
    TranspositionTable,
)
from chess_engine.movegen.legality import generate_legal_moves


def _alphabeta(
    position,
    depth,
    alpha,
    beta,
    nodes,
    transposition_table=None,
    preferred_move=None,
    use_quiescence=True,
    max_quiescence_ply=16,
):
    """Search a position and return its principal variation."""

    nodes[0] += 1

    original_alpha = alpha
    original_beta = beta

    legal_moves = generate_legal_moves(position)

    # Handle checkmate and stalemate.
    if not legal_moves:
        if is_in_check(position):
            return -MATE_SCORE, None, ()

        return 0, None, ()

    # Extend the search using Quiescence Search at the horizon.
    if depth == 0:
        if use_quiescence:
            score, q_nodes = _quiescence(
                position,
                alpha,
                beta,
                ply=0,
                max_ply=max_quiescence_ply,
                count_node=False,
            )

            nodes[0] += q_nodes

            return score, None, ()

        return evaluate(position), None, ()

    search_config = (
        (True, max_quiescence_ply)
        if use_quiescence
        else (False, 0)
    )

    tt_move = preferred_move

    if transposition_table is not None:
        entry = transposition_table.probe(
            position.zobrist_hash,
            search_config=search_config,
        )

        if entry is not None:

            if entry.depth >= depth:
                transposition_table.depth_hits += 1
            else:
                transposition_table.shallow_hits += 1

            cached_move_is_legal = entry.best_move in legal_moves

            if cached_move_is_legal:
                tt_move = entry.best_move
                transposition_table.move_ordering_hits += 1

            if entry.depth >= depth:

                if (
                    entry.bound == Bound.EXACT
                    and cached_move_is_legal
                ):
                    transposition_table.exact_hits += 1

                    # This is a cached move, not a reconstructed full PV.
                    return (
                        entry.score,
                        entry.best_move,
                        (entry.best_move,),
                    )

                if entry.bound == Bound.LOWERBOUND:
                    alpha = max(alpha, entry.score)
                    transposition_table.bound_hits += 1

                elif entry.bound == Bound.UPPERBOUND:
                    beta = min(beta, entry.score)
                    transposition_table.bound_hits += 1

                if alpha >= beta:
                    transposition_table.record_cutoff()

                    cached_pv = (
                        (entry.best_move,)
                        if cached_move_is_legal
                        else ()
                    )

                    return (
                        entry.score,
                        entry.best_move if cached_move_is_legal else None,
                        cached_pv,
                    )

    legal_moves = order_moves(
        position,
        legal_moves,
        tt_move=tt_move,
    )

    best_score = float("-inf")
    best_move = None
    best_pv = ()

    for move in legal_moves:

        state = position.make_move(move)

        try:
            child_score, _, child_pv = _alphabeta(
                position,
                depth - 1,
                -beta,
                -alpha,
                nodes,
                transposition_table=transposition_table,
                use_quiescence=use_quiescence,
                max_quiescence_ply=max_quiescence_ply,
            )

        finally:
            position.undo_move(move, state)

        score = -child_score

        if score > best_score:
            best_score = score
            best_move = move
            best_pv = (move,) + child_pv

        alpha = max(alpha, score)

        if alpha >= beta:
            break

    if transposition_table is not None:

        if best_score <= original_alpha:
            bound = Bound.UPPERBOUND
        elif best_score >= original_beta:
            bound = Bound.LOWERBOUND
        else:
            bound = Bound.EXACT

        transposition_table.store(
            position.zobrist_hash,
            depth,
            int(best_score),
            bound,
            best_move,
            search_config=search_config,
        )

    return best_score, best_move, best_pv


def alphabeta(
    position,
    depth: int,
    preferred_move=None,
    transposition_table=None,
    use_quiescence=True,
    max_quiescence_ply=16,
) -> SearchResult:
    """Search a position using Alpha-Beta pruning."""

    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("Search depth must be a non-negative integer.")

    if (
        transposition_table is not None
        and not isinstance(transposition_table, TranspositionTable)
    ):
        raise ValueError("Invalid transposition table.")

    if not isinstance(use_quiescence, bool):
        raise ValueError("Quiescence setting must be a boolean.")

    if (
        isinstance(max_quiescence_ply, bool)
        or not isinstance(max_quiescence_ply, int)
        or max_quiescence_ply < 1
    ):
        raise ValueError(
            "Maximum quiescence ply must be a positive integer."
        )

    nodes = [0]

    score, best_move, principal_variation = _alphabeta(
        position,
        depth,
        float("-inf"),
        float("inf"),
        nodes,
        transposition_table=transposition_table,
        preferred_move=preferred_move,
        use_quiescence=use_quiescence,
        max_quiescence_ply=max_quiescence_ply,
    )

    return SearchResult(
        best_move=best_move,
        score=int(score),
        depth=depth,
        nodes=nodes[0],
        principal_variation=principal_variation,
    )