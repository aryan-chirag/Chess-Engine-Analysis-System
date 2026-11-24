
"""Move ordering heuristics for chess search."""

from chess_engine.core.move import Move
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    piece_type,
)
from chess_engine.engine.evaluation_terms import MATERIAL_VALUES


# Move ordering priority bonuses.
TT_MOVE_BONUS = 100_000
PROMOTION_BONUS = 20_000
CAPTURE_BONUS = 10_000


def _get_captured_piece(position, move):
    """Return the piece captured by a move, if any."""

    if move.is_en_passant:
        if position.side_to_move == Color.WHITE:
            captured_square = move.to_square - 16
        else:
            captured_square = move.to_square + 16

        return position.board.get_piece(captured_square)

    return position.board.get_piece(move.to_square)


def score_move(position, move, tt_move=None):
    """Assign a heuristic score to a move."""

    # A transposition-table move receives the highest priority.
    if tt_move is not None and move == tt_move:
        return TT_MOVE_BONUS

    moving_piece = position.board.get_piece(move.from_square)
    attacker_type = piece_type(moving_piece)

    score = 0

    # Promotions receive a large bonus.
    if move.is_promotion:
        score += PROMOTION_BONUS
        score += MATERIAL_VALUES[move.promotion]

    # Captures use Most Valuable Victim - Least Valuable Attacker.
    if move.is_capture:
        captured_piece = _get_captured_piece(position, move)

        if captured_piece == EMPTY:
            raise ValueError("Capture move has no captured piece.")

        victim_type = piece_type(captured_piece)

        score += CAPTURE_BONUS
        score += (
            MATERIAL_VALUES[victim_type] * 10
            - MATERIAL_VALUES[attacker_type]
        )

    return score


def order_moves(position, moves, tt_move=None):
    """Return moves sorted from highest to lowest heuristic score."""

    return sorted(
        moves,
        key=lambda move: score_move(position, move, tt_move),
        reverse=True,
    )
