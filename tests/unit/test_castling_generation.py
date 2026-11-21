from chess_engine.core.board import Board
from chess_engine.core.constants import CastlingRights, parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.position import Position
from chess_engine.movegen.castling import generate_castling_moves
from chess_engine.movegen.legality import generate_legal_moves


def castle_position():
    board = Board()
    for sq, color, kind in (
        ("e1", Color.WHITE, PieceType.KING),
        ("a1", Color.WHITE, PieceType.ROOK),
        ("h1", Color.WHITE, PieceType.ROOK),
        ("e8", Color.BLACK, PieceType.KING),
    ):
        board.set_piece(parse_square(sq), make_piece(color, kind))
    return Position(board=board, castling_rights=CastlingRights.WHITE_KINGSIDE | CastlingRights.WHITE_QUEENSIDE)


def test_both_white_castles_available_when_clear():
    moves = generate_castling_moves(castle_position())
    assert {m.to_square for m in moves} == {parse_square("c1"), parse_square("g1")}


def test_castling_not_available_when_king_in_check():
    p = castle_position()
    p.board.set_piece(parse_square("e8"), 0)
    p.board.set_piece(parse_square("e7"), make_piece(Color.BLACK, PieceType.ROOK))
    assert generate_castling_moves(p) == []


def test_castling_not_available_through_attacked_square():
    p = castle_position()
    p.board.set_piece(parse_square("f8"), make_piece(Color.BLACK, PieceType.ROOK))
    assert parse_square("g1") not in {m.to_square for m in generate_castling_moves(p)}


def test_castling_not_available_when_path_occupied():
    p = castle_position()
    p.board.set_piece(parse_square("f1"), make_piece(Color.WHITE, PieceType.KNIGHT))
    assert parse_square("g1") not in {m.to_square for m in generate_castling_moves(p)}
