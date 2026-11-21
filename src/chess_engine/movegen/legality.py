"""Legal move filtering by applying candidates to temporary positions."""

from chess_engine.core.attacks import is_in_check
from chess_engine.core.constants import CastlingRights
from chess_engine.core.move import MoveFlag
from chess_engine.core.pieces import Color, EMPTY, PieceType, make_piece, piece_type
from chess_engine.movegen.generator import generate_pseudo_legal_moves


def _updated_castling_rights(position, move, moving_piece, captured_piece):
    rights = position.castling_rights
    start = move.from_square
    end = move.to_square
    if moving_piece == make_piece(Color.WHITE, PieceType.KING):
        rights &= ~(CastlingRights.WHITE_KINGSIDE | CastlingRights.WHITE_QUEENSIDE)
    elif moving_piece == make_piece(Color.BLACK, PieceType.KING):
        rights &= ~(CastlingRights.BLACK_KINGSIDE | CastlingRights.BLACK_QUEENSIDE)

    rook_rights = {
        0: CastlingRights.WHITE_QUEENSIDE,
        7: CastlingRights.WHITE_KINGSIDE,
        112: CastlingRights.BLACK_QUEENSIDE,
        119: CastlingRights.BLACK_KINGSIDE,
    }
    if piece_type(moving_piece) == PieceType.ROOK:
        rights &= ~rook_rights.get(start, CastlingRights.NONE)
    if captured_piece != EMPTY and piece_type(captured_piece) == PieceType.ROOK:
        rights &= ~rook_rights.get(end, CastlingRights.NONE)
    return rights


def _position_after_move(position, move):
    """Build a lightweight independent position after applying move."""
    from chess_engine.core.position import Position
    from chess_engine.core.board import Board

    board = Board()
    board.squares = position.board.squares.copy()
    moving = board.get_piece(move.from_square)
    captured = board.get_piece(move.to_square)
    side = position.side_to_move

    board.set_piece(move.from_square, EMPTY)
    if move.is_en_passant:
        captured_square = move.to_square - (16 if side == Color.WHITE else -16)
        board.set_piece(captured_square, EMPTY)
    if move.is_castling:
        if move.to_square > move.from_square:
            rook_from, rook_to = move.from_square + 3, move.from_square + 1
        else:
            rook_from, rook_to = move.from_square - 4, move.from_square - 1
        rook = board.get_piece(rook_from)
        board.set_piece(rook_from, EMPTY)
        board.set_piece(rook_to, rook)

    placed = make_piece(side, move.promotion) if move.promotion else moving
    board.set_piece(move.to_square, placed)

    ep_square = None
    if move.flags & MoveFlag.DOUBLE_PAWN_PUSH:
        ep_square = (move.from_square + move.to_square) // 2

    halfmove = 0 if piece_type(moving) == PieceType.PAWN or captured != EMPTY or move.is_en_passant else position.halfmove_clock + 1
    fullmove = position.fullmove_number + (1 if side == Color.BLACK else 0)
    return Position(
        board=board,
        side_to_move=side.opposite,
        castling_rights=_updated_castling_rights(position, move, moving, captured),
        en_passant_square=ep_square,
        halfmove_clock=halfmove,
        fullmove_number=fullmove,
    )


def generate_legal_moves(position):
    """Return pseudo-legal moves that do not leave the moving king in check."""
    legal = []
    moving_side = position.side_to_move
    for move in generate_pseudo_legal_moves(position):
        child = _position_after_move(position, move)
        if not is_in_check(child, moving_side):
            legal.append(move)
    return legal


def is_legal_move(position, move) -> bool:
    """Return whether a Move object appears in the legal move list."""
    return move in generate_legal_moves(position)
