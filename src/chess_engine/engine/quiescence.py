"""Quiescence Search implementation."""

from chess_engine.core.attacks import is_in_check
from chess_engine.engine.evaluation import evaluate
from chess_engine.engine.minimax import MATE_SCORE
from chess_engine.engine.move_ordering import order_moves
from chess_engine.movegen.legality import generate_legal_moves


def _quiescence(
    position,
    alpha,
    beta,
    ply,
    max_ply,
    count_node=True,
):
    """Search tactical continuations until the position is quiet."""

    nodes = 1 if count_node else 0

    in_check = is_in_check(position)
    legal_moves = generate_legal_moves(position)

    # Detect checkmate and stalemate.
    if not legal_moves:
        if in_check:
            return -MATE_SCORE, nodes

        return 0, nodes

    # Safety limit prevents excessively long tactical sequences.
    if ply >= max_ply:
        return evaluate(position), nodes

    if not in_check:
        stand_pat = evaluate(position)

        if stand_pat >= beta:
            return stand_pat, nodes

        alpha = max(alpha, stand_pat)

        tactical_moves = [
            move
            for move in legal_moves
            if move.is_capture or move.is_promotion
        ]

        if not tactical_moves:
            return stand_pat, nodes

        moves = order_moves(position, tactical_moves)

        best_score = stand_pat

    else:
        # No stand-pat evaluation is allowed while in check.
        moves = order_moves(position, legal_moves)

        best_score = float("-inf")

    for move in moves:
        state = position.make_move(move)

        try:
            child_score, child_nodes = _quiescence(
                position,
                -beta,
                -alpha,
                ply + 1,
                max_ply,
            )
        finally:
            position.undo_move(move, state)

        nodes += child_nodes

        score = -child_score

        if score > best_score:
            best_score = score

        alpha = max(alpha, score)

        if alpha >= beta:
            break

    return int(best_score), nodes


def quiescence(
    position,
    alpha=float("-inf"),
    beta=float("inf"),
    max_ply=16,
) -> tuple[int, int]:
    """Run Quiescence Search and return its score and node count."""

    if alpha >= beta:
        raise ValueError("Alpha must be less than beta.")

    if (
        isinstance(max_ply, bool)
        or not isinstance(max_ply, int)
        or max_ply < 1
    ):
        raise ValueError("Maximum quiescence ply must be a positive integer.")

    return _quiescence(
        position,
        alpha,
        beta,
        ply=0,
        max_ply=max_ply,
    )