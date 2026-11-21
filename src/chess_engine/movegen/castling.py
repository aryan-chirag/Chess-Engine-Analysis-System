"""Castling move generation and validation."""

from chess_engine.core.attacks import is_square_attacked
from chess_engine.core.constants import CastlingRights
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import Color, EMPTY, PieceType, make_piece


def generate_castling_moves(position):
    """Generate castling moves when rights, path and king safety permit."""
    side = position.side_to_move
    board = position.board
    enemy = side.opposite
    moves = []

    if side == Color.WHITE:
        king_from = 4
        options = (
            (CastlingRights.WHITE_KINGSIDE, 7, (5, 6), 6, (5, 6)),
            (CastlingRights.WHITE_QUEENSIDE, 0, (1, 2, 3), 2, (3, 2)),
        )
    else:
        king_from = 116
        options = (
            (CastlingRights.BLACK_KINGSIDE, 119, (117, 118), 118, (117, 118)),
            (CastlingRights.BLACK_QUEENSIDE, 112, (113, 114, 115), 114, (115, 114)),
        )

    if board.get_piece(king_from) != make_piece(side, PieceType.KING):
        return moves
    if is_square_attacked(position, king_from, enemy):
        return moves

    for right, rook_from, empty_squares, king_to, safe_squares in options:
        if not (position.castling_rights & right):
            continue
        if board.get_piece(rook_from) != make_piece(side, PieceType.ROOK):
            continue
        if any(board.get_piece(sq) != EMPTY for sq in empty_squares):
            continue
        if any(is_square_attacked(position, sq, enemy) for sq in safe_squares):
            continue
        moves.append(Move(king_from, king_to, flags=MoveFlag.CASTLING))
    return moves
