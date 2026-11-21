"""Attack detection and check queries for 0x88 positions."""

from chess_engine.core.constants import is_valid_square
from chess_engine.core.pieces import Color, EMPTY, PieceType, piece_color, piece_type

KING_OFFSETS = (1, -1, 16, -16, 15, 17, -15, -17)
KNIGHT_OFFSETS = (33, 31, 18, 14, -14, -18, -31, -33)
BISHOP_DIRECTIONS = (15, 17, -15, -17)
ROOK_DIRECTIONS = (1, -1, 16, -16)


def is_square_attacked(position, square: int, by_color: Color) -> bool:
    """Return whether *square* is attacked by at least one piece of by_color.

    This deliberately tests attacks, not legal moves. Pinned pieces still
    attack squares, and pawn diagonals count even when their target is empty.
    """
    if not is_valid_square(square):
        raise ValueError(f"Invalid square: {square}")

    board = position.board
    by_color = Color(by_color)

    # A white pawn attacks one rank up; a black pawn attacks one rank down.
    pawn = int(PieceType.PAWN) + (8 if by_color == Color.BLACK else 0)
    pawn_sources = (square - 15, square - 17) if by_color == Color.WHITE else (square + 15, square + 17)
    for source in pawn_sources:
        if is_valid_square(source) and board.get_piece(source) == pawn:
            return True

    knight = int(PieceType.KNIGHT) + (8 if by_color == Color.BLACK else 0)
    for offset in KNIGHT_OFFSETS:
        source = square + offset
        if is_valid_square(source) and board.get_piece(source) == knight:
            return True

    king = int(PieceType.KING) + (8 if by_color == Color.BLACK else 0)
    for offset in KING_OFFSETS:
        source = square + offset
        if is_valid_square(source) and board.get_piece(source) == king:
            return True

    bishop = int(PieceType.BISHOP) + (8 if by_color == Color.BLACK else 0)
    rook = int(PieceType.ROOK) + (8 if by_color == Color.BLACK else 0)
    queen = int(PieceType.QUEEN) + (8 if by_color == Color.BLACK else 0)

    for directions, attackers in (
        (BISHOP_DIRECTIONS, (bishop, queen)),
        (ROOK_DIRECTIONS, (rook, queen)),
    ):
        for direction in directions:
            target = square + direction
            while is_valid_square(target):
                piece = board.get_piece(target)
                if piece != EMPTY:
                    if piece in attackers:
                        return True
                    break
                target += direction

    return False


def is_in_check(position, color: Color | None = None) -> bool:
    """Return whether color's king is currently attacked."""
    color = position.side_to_move if color is None else Color(color)
    king_square = position.king_square(color)
    if king_square is None:
        raise ValueError(f"Position has no {color.name.lower()} king")
    return is_square_attacked(position, king_square, color.opposite)
