import pytest

from chess_engine.core.position import Position
from chess_engine.core.constants import parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.move import Move


def create_position():
    return Position.starting_position()


def test_make_move_moves_piece():
    position = create_position()

    move = Move(
        from_square=parse_square("e2"),
        to_square=parse_square("e4"),
    )

    position.make_move(move)

    assert position.board.get_piece(parse_square("e2")) == 0
    assert position.board.get_piece(parse_square("e4")) == make_piece(
        Color.WHITE, PieceType.PAWN
    )


def test_make_move_changes_side_to_move():
    position = create_position()

    move = Move(
        from_square=parse_square("e2"),
        to_square=parse_square("e3"),
    )

    position.make_move(move)

    assert position.side_to_move == Color.BLACK


def test_black_move_increments_fullmove_number():
    position = create_position()
    position.side_to_move = Color.BLACK

    position.board.set_piece(parse_square("e7"), 0)
    position.board.set_piece(
        parse_square("e6"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    move = Move(
        from_square=parse_square("e6"),
        to_square=parse_square("e5"),
    )

    position.make_move(move)

    assert position.fullmove_number == 2


def test_pawn_move_resets_halfmove_clock():
    position = create_position()
    position.halfmove_clock = 10

    move = Move(
        from_square=parse_square("e2"),
        to_square=parse_square("e3"),
    )

    position.make_move(move)

    assert position.halfmove_clock == 0


def test_piece_move_increments_halfmove_clock():
    position = create_position()

    position.board.set_piece(parse_square("e2"), 0)
    position.board.set_piece(
        parse_square("e3"),
        make_piece(Color.WHITE, PieceType.KNIGHT),
    )

    position.halfmove_clock = 5

    move = Move(
        from_square=parse_square("e3"),
        to_square=parse_square("f5"),
    )

    position.make_move(move)

    assert position.halfmove_clock == 6


def test_cannot_move_from_empty_square():
    position = create_position()

    move = Move(
        from_square=parse_square("e4"),
        to_square=parse_square("e5"),
    )

    with pytest.raises(ValueError):
        position.make_move(move)


def test_cannot_move_opponents_piece():
    position = create_position()

    move = Move(
        from_square=parse_square("e7"),
        to_square=parse_square("e6"),
    )

    with pytest.raises(ValueError):
        position.make_move(move)