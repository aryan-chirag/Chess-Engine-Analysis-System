"""Pseudo-legal king move generation."""

from chess_engine.core.constants import is_valid_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import EMPTY, PieceType, piece_color, piece_type

KING_OFFSETS = (1, -1, 16, -16, 15, 17, -15, -17)


def generate_king_moves(position) -> list[Move]:
    """Generate adjacent king moves; king safety is checked elsewhere."""
    moves = []
    side = position.side_to_move
    enemy = side.opposite
    king_piece = next(
        (sq for sq in position.board.iter_squares()
         if position.board.get_piece(sq) != EMPTY
         and piece_color(position.board.get_piece(sq)) == side
         and piece_type(position.board.get_piece(sq)) == PieceType.KING),
        None,
    )
    if king_piece is None:
        return moves

    for offset in KING_OFFSETS:
        target = king_piece + offset
        if not is_valid_square(target):
            continue
        occupant = position.board.get_piece(target)
        if occupant == EMPTY:
            moves.append(Move(king_piece, target))
        elif piece_color(occupant) == enemy and piece_type(occupant) != PieceType.KING:
            moves.append(Move(king_piece, target, flags=MoveFlag.CAPTURE))
    return moves
