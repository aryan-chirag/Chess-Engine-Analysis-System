"""Sliding-piece move generation."""

from chess_engine.core.constants import is_valid_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    piece_color,
    piece_type,
)


BISHOP_DIRECTIONS = (15, 17, -15, -17)

ROOK_DIRECTIONS = (1, -1, 16, -16)

QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS


def generate_sliding_moves(position, piece_type_to_generate, directions):
    """
    Generate pseudo-legal moves for a sliding piece.

    Sliding pieces continue in each permitted direction until:
    - The board edge is reached.
    - A friendly piece blocks the path.
    - An enemy piece is captured.

    This function does not check king safety.
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

        if piece_type(piece) != piece_type_to_generate:
            continue

        for direction in directions:

            target = from_square + direction

            while is_valid_square(target):

                target_piece = position.board.get_piece(target)

                if target_piece == EMPTY:

                    moves.append(
                        Move(
                            from_square=from_square,
                            to_square=target,
                        )
                    )

                else:

                    if piece_color(target_piece) == enemy:

                        if piece_type(target_piece) != PieceType.KING:
                            moves.append(
                                Move(
                                    from_square=from_square,
                                    to_square=target,
                                    flags=MoveFlag.CAPTURE,
                                )
                            )

                    # Stop at any occupied square.
                    break

                target += direction

    return moves


def generate_bishop_moves(position):
    """Generate pseudo-legal bishop moves."""

    return generate_sliding_moves(
        position,
        PieceType.BISHOP,
        BISHOP_DIRECTIONS,
    )


def generate_rook_moves(position):
    """Generate pseudo-legal rook moves."""

    return generate_sliding_moves(
        position,
        PieceType.ROOK,
        ROOK_DIRECTIONS,
    )



def generate_queen_moves(position):
    """Generate pseudo-legal queen moves."""

    return generate_sliding_moves(
        position,
        PieceType.QUEEN,
        QUEEN_DIRECTIONS,
    )


