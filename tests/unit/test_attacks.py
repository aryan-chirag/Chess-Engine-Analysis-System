from chess_engine.core.board import Board
from chess_engine.core.constants import parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.position import Position
from chess_engine.core.attacks import is_in_check, is_square_attacked


def make_position(*pieces, side=Color.WHITE):
    board = Board()
    for square, color, kind in pieces:
        board.set_piece(parse_square(square), make_piece(color, kind))
    return Position(board=board, side_to_move=side)


def test_rook_attacks_along_open_file():
    p = make_position(("a1", Color.WHITE, PieceType.KING), ("h8", Color.BLACK, PieceType.KING), ("a8", Color.BLACK, PieceType.ROOK))
    assert is_square_attacked(p, parse_square("a4"), Color.BLACK)


def test_blocker_stops_rook_attack():
    p = make_position(("a1", Color.WHITE, PieceType.KING), ("h8", Color.BLACK, PieceType.KING), ("a8", Color.BLACK, PieceType.ROOK), ("a5", Color.WHITE, PieceType.PAWN))
    assert not is_square_attacked(p, parse_square("a4"), Color.BLACK)


def test_pawn_attacks_empty_diagonal_square():
    p = make_position(("a1", Color.WHITE, PieceType.KING), ("h8", Color.BLACK, PieceType.KING), ("d4", Color.BLACK, PieceType.PAWN))
    assert is_square_attacked(p, parse_square("c3"), Color.BLACK)


def test_knight_attack():
    p = make_position(("a1", Color.WHITE, PieceType.KING), ("h8", Color.BLACK, PieceType.KING), ("f5", Color.BLACK, PieceType.KNIGHT))
    assert is_square_attacked(p, parse_square("e3"), Color.BLACK)


def test_check_detected_from_rook():
    p = make_position(("e1", Color.WHITE, PieceType.KING), ("a8", Color.BLACK, PieceType.KING), ("e8", Color.BLACK, PieceType.ROOK))
    assert is_in_check(p, Color.WHITE)


def test_pinned_piece_still_attacks_square():
    p = make_position(("e1", Color.WHITE, PieceType.KING), ("e2", Color.WHITE, PieceType.ROOK), ("e8", Color.BLACK, PieceType.ROOK), ("a8", Color.BLACK, PieceType.KING))
    assert is_square_attacked(p, parse_square("e3"), Color.WHITE)
