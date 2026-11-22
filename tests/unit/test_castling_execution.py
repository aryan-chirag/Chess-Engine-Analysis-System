import pytest

from chess_engine.core.board import Board
from chess_engine.core.constants import (
    CastlingRights,
    parse_square,
)
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import (
    Color,
    PieceType,
    make_piece,
)
from chess_engine.core.position import Position


def create_castling_position():

    board = Board()

    for square, color, piece_type in (
        ("e1", Color.WHITE, PieceType.KING),
        ("a1", Color.WHITE, PieceType.ROOK),
        ("h1", Color.WHITE, PieceType.ROOK),
        ("e8", Color.BLACK, PieceType.KING),
        ("a8", Color.BLACK, PieceType.ROOK),
        ("h8", Color.BLACK, PieceType.ROOK),
    ):

        board.set_piece(
            parse_square(square),
            make_piece(color, piece_type),
        )

    return Position(
        board=board,
        castling_rights=CastlingRights.ALL,
    )



def test_white_kingside_castling():

    position = create_castling_position()

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING,
    )

    position.make_move(move)

    assert position.board.get_piece(parse_square("g1")) == make_piece(
        Color.WHITE, PieceType.KING
    )

    assert position.board.get_piece(parse_square("f1")) == make_piece(
        Color.WHITE, PieceType.ROOK
    )

    assert position.board.get_piece(parse_square("e1")) == 0
    assert position.board.get_piece(parse_square("h1")) == 0

    assert not (
        position.castling_rights
        & (
            CastlingRights.WHITE_KINGSIDE
            | CastlingRights.WHITE_QUEENSIDE
        )
    )


def test_white_queenside_castling():

    position = create_castling_position()

    move = Move(
        parse_square("e1"),
        parse_square("c1"),
        flags=MoveFlag.CASTLING,
    )

    position.make_move(move)

    assert position.board.get_piece(parse_square("c1")) == make_piece(
        Color.WHITE, PieceType.KING
    )

    assert position.board.get_piece(parse_square("d1")) == make_piece(
        Color.WHITE, PieceType.ROOK
    )

    assert position.board.get_piece(parse_square("a1")) == 0


def test_black_kingside_castling():

    position = create_castling_position()
    position.side_to_move = Color.BLACK

    move = Move(
        parse_square("e8"),
        parse_square("g8"),
        flags=MoveFlag.CASTLING,
    )

    position.make_move(move)

    assert position.board.get_piece(parse_square("g8")) == make_piece(
        Color.BLACK, PieceType.KING
    )

    assert position.board.get_piece(parse_square("f8")) == make_piece(
        Color.BLACK, PieceType.ROOK
    )


def test_black_queenside_castling():

    position = create_castling_position()
    position.side_to_move = Color.BLACK

    move = Move(
        parse_square("e8"),
        parse_square("c8"),
        flags=MoveFlag.CASTLING,
    )

    position.make_move(move)

    assert position.board.get_piece(parse_square("c8")) == make_piece(
        Color.BLACK, PieceType.KING
    )

    assert position.board.get_piece(parse_square("d8")) == make_piece(
        Color.BLACK, PieceType.ROOK
    )




def test_castling_without_rights():

    position = create_castling_position()
    position.castling_rights = CastlingRights.NONE

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING,
    )

    with pytest.raises(ValueError):
        position.make_move(move)


def test_castling_without_rook():

    position = create_castling_position()

    position.board.set_piece(parse_square("h1"), 0)

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING,
    )

    with pytest.raises(ValueError):
        position.make_move(move)


def test_castling_with_blocked_path():

    position = create_castling_position()

    position.board.set_piece(
        parse_square("f1"),
        make_piece(Color.WHITE, PieceType.KNIGHT),
    )

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING,
    )

    with pytest.raises(ValueError):
        position.make_move(move)



def test_rook_move_removes_castling_right():

    position = create_castling_position()

    move = Move(
        parse_square("h1"),
        parse_square("h2"),
    )

    position.make_move(move)

    assert not (
        position.castling_rights
        & CastlingRights.WHITE_KINGSIDE
    )

    assert (
        position.castling_rights
        & CastlingRights.WHITE_QUEENSIDE
    )

def test_rook_capture_removes_castling_right():

    position = create_castling_position()

    position.board.set_piece(
        parse_square("h2"),
        make_piece(Color.BLACK, PieceType.BISHOP),
    )

    position.side_to_move = Color.BLACK

    move = Move(
        parse_square("h2"),
        parse_square("h1"),
        flags=MoveFlag.CAPTURE,
    )

    position.make_move(move)

    assert not (
        position.castling_rights
        & CastlingRights.WHITE_KINGSIDE
    )




