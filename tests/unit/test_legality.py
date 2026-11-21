from chess_engine.core.board import Board
from chess_engine.core.constants import parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.position import Position
from chess_engine.movegen.legality import generate_legal_moves


def build_position(pieces):
    board = Board()
    for square, color, kind in pieces:
        board.set_piece(parse_square(square), make_piece(color, kind))
    return Position(board=board)


def test_king_cannot_move_into_rook_attack():
    position = build_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("a8", Color.BLACK, PieceType.KING),
        ("e8", Color.BLACK, PieceType.ROOK),
    ])
    legal = generate_legal_moves(position)
    assert parse_square("e2") not in {
        move.to_square for move in legal if move.from_square == parse_square("e1")
    }


def test_pinned_rook_cannot_expose_its_king():
    position = build_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e2", Color.WHITE, PieceType.ROOK),
        ("e8", Color.BLACK, PieceType.ROOK),
        ("a8", Color.BLACK, PieceType.KING),
    ])
    legal = generate_legal_moves(position)
    rook_moves = [move for move in legal if move.from_square == parse_square("e2")]
    assert rook_moves
    assert all((move.to_square & 7) == 4 for move in rook_moves)
