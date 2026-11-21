from chess_engine.core.board import Board
from chess_engine.core.constants import parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.position import Position
from chess_engine.movegen.kings import generate_king_moves


def position_with_king(square, color=Color.WHITE):
    board = Board()
    board.set_piece(parse_square(square), make_piece(color, PieceType.KING))
    return Position(board=board, side_to_move=color)


def test_king_has_eight_moves_from_center():
    moves = generate_king_moves(position_with_king("e4"))
    assert {move.to_square for move in moves} == {
        parse_square(s) for s in ("d3", "e3", "f3", "d4", "f4", "d5", "e5", "f5")
    }


def test_king_has_three_moves_from_corner():
    moves = generate_king_moves(position_with_king("a1"))
    assert {move.to_square for move in moves} == {
        parse_square("a2"), parse_square("b1"), parse_square("b2")
    }


def test_king_cannot_move_onto_own_piece():
    position = position_with_king("e4")
    position.board.set_piece(parse_square("e5"), make_piece(Color.WHITE, PieceType.PAWN))
    assert parse_square("e5") not in {m.to_square for m in generate_king_moves(position)}


def test_king_can_capture_enemy_non_king_piece():
    position = position_with_king("e4")
    position.board.set_piece(parse_square("e5"), make_piece(Color.BLACK, PieceType.PAWN))
    move = next(m for m in generate_king_moves(position) if m.to_square == parse_square("e5"))
    assert move.is_capture


def test_king_cannot_capture_enemy_king():
    position = position_with_king("e4")
    position.board.set_piece(parse_square("e5"), make_piece(Color.BLACK, PieceType.KING))
    assert parse_square("e5") not in {m.to_square for m in generate_king_moves(position)}


def test_black_king_has_eight_moves_from_center():
    assert len(generate_king_moves(position_with_king("e5", Color.BLACK))) == 8
