import pytest

from chess_engine.core.position import Position
from chess_engine.core.constants import parse_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    make_piece,
)


def test_white_double_pawn_push_sets_en_passant_square():

    position = Position.starting_position()

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    position.make_move(move)

    assert position.en_passant_square == parse_square("e3")
    assert position.side_to_move == Color.BLACK


def test_black_double_pawn_push_sets_en_passant_square():

    position = Position.starting_position()

    white_move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    position.make_move(white_move)

    black_move = Move(
        parse_square("d7"),
        parse_square("d5"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    position.make_move(black_move)

    assert position.en_passant_square == parse_square("d6")
    assert position.side_to_move == Color.WHITE


def test_white_en_passant_capture():

    position = Position.starting_position()

    position.board.set_piece(parse_square("e2"), EMPTY)
    position.board.set_piece(parse_square("e4"), EMPTY)
    position.board.set_piece(parse_square("e5"), make_piece(Color.WHITE, PieceType.PAWN))
    position.board.set_piece(parse_square("d7"), EMPTY)
    position.board.set_piece(parse_square("d5"), make_piece(Color.BLACK, PieceType.PAWN))

    position.en_passant_square = parse_square("d6")

    move = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    state = position.make_move(move)

    assert position.board.get_piece(parse_square("d6")) == make_piece(Color.WHITE, PieceType.PAWN)
    assert position.board.get_piece(parse_square("d5")) == EMPTY

    assert state.captured_piece == make_piece(Color.BLACK, PieceType.PAWN)
    assert state.captured_square == parse_square("d5")

    assert position.en_passant_square is None
    assert position.side_to_move == Color.BLACK
    assert position.halfmove_clock == 0


def test_black_en_passant_capture():

    position = Position.starting_position()

    position.board.set_piece(parse_square("e2"), EMPTY)
    position.board.set_piece(parse_square("e4"), EMPTY)
    position.board.set_piece(parse_square("e4"), make_piece(Color.WHITE, PieceType.PAWN))

    position.board.set_piece(parse_square("d7"), EMPTY)
    position.board.set_piece(parse_square("d5"), EMPTY)
    position.board.set_piece(parse_square("d4"), make_piece(Color.BLACK, PieceType.PAWN))

    position.en_passant_square = parse_square("e3")
    position.side_to_move = Color.BLACK

    move = Move(
        parse_square("d4"),
        parse_square("e3"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    state = position.make_move(move)

    assert position.board.get_piece(parse_square("e3")) == make_piece(Color.BLACK, PieceType.PAWN)
    assert position.board.get_piece(parse_square("e4")) == EMPTY

    assert state.captured_piece == make_piece(Color.WHITE, PieceType.PAWN)
    assert state.captured_square == parse_square("e4")

    assert position.en_passant_square is None
    assert position.side_to_move == Color.WHITE


def test_en_passant_target_cleared_after_normal_move():

    position = Position.starting_position()

    position.en_passant_square = parse_square("e3")

    move = Move(
        parse_square("g1"),
        parse_square("f3"),
    )

    position.make_move(move)

    assert position.en_passant_square is None


def test_invalid_en_passant_target():

    position = Position.starting_position()

    move = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    with pytest.raises(ValueError):
        position.make_move(move)


def test_en_passant_requires_pawn():

    position = Position.starting_position()

    position.board.set_piece(
        parse_square("e5"),
        make_piece(Color.WHITE, PieceType.KNIGHT),
    )

    position.en_passant_square = parse_square("d6")

    move = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    with pytest.raises(ValueError):
        position.make_move(move)


def test_double_pawn_push_requires_starting_rank():

    position = Position.starting_position()

    position.board.set_piece(parse_square("e2"), EMPTY)
    position.board.set_piece(
        parse_square("e3"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    move = Move(
        parse_square("e3"),
        parse_square("e5"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    with pytest.raises(ValueError):
        position.make_move(move)


def test_double_pawn_push_cannot_jump_over_piece():

    position = Position.starting_position()

    # Place a piece on the intermediate square.
    position.board.set_piece(
        parse_square("e3"),
        make_piece(Color.WHITE, PieceType.KNIGHT),
    )

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    with pytest.raises(ValueError):
        position.make_move(move)