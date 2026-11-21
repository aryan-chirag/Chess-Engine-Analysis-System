"""Knight pseudo-legal move generation."""

from chess_engine.core.constants import is_valid_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    piece_color,
    piece_type,
)


KNIGHT_OFFSETS = (
    33, 31,
    18, 14,
    -14, -18,
    -31, -33,
)


def generate_knight_moves(position) -> list[Move]:
    """
    Generate pseudo-legal knight moves for the side to move.

    Knights can jump over other pieces.

    This function does not check whether moving a knight
    leaves its own king in check.
    """

    moves = []

    side = position.side_to_move
    enemy = Color.BLACK if side == Color.WHITE else Color.WHITE

    for from_square in position.board.iter_squares():

        piece = position.board.get_piece(from_square)

        if piece == EMPTY:
            continue

        if piece_color(piece) != side:
            continue

        if piece_type(piece) != PieceType.KNIGHT:
            continue

        for offset in KNIGHT_OFFSETS:

            target = from_square + offset

            # Reject squares outside the board.
            if not is_valid_square(target):
                continue

            target_piece = position.board.get_piece(target)

            # A knight cannot land on its own piece.
            if target_piece != EMPTY:

                if piece_color(target_piece) != enemy:
                    continue

                # Kings cannot be captured as ordinary moves.
                if piece_type(target_piece) == PieceType.KING:
                    continue

                moves.append(
                    Move(
                        from_square=from_square,
                        to_square=target,
                        flags=MoveFlag.CAPTURE,
                    )
                )

            else:

                moves.append(
                    Move(
                        from_square=from_square,
                        to_square=target,
                    )
                )

    return moves