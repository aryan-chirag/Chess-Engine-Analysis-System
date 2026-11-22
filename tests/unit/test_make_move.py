import pytest

from chess_engine.core.position import Position
from chess_engine.core.constants import parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.move import Move



from chess_engine.core.position import Position
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    make_piece,
)




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


def test_capture_removes_opponent_piece():
    position = Position.starting_position()

    # Prepare a simple capture position.
    position.board.set_piece(20, EMPTY)
    position.board.set_piece(36, make_piece(Color.WHITE, PieceType.PAWN))
    position.board.set_piece(52, make_piece(Color.BLACK, PieceType.PAWN))

    move = Move(
        from_square=36,
        to_square=52,
        flags=MoveFlag.CAPTURE,
    )

    state = position.make_move(move)

    assert position.board.get_piece(36) == EMPTY
    assert position.board.get_piece(52) == make_piece(
        Color.WHITE, PieceType.PAWN
    )

    assert state.captured_piece == make_piece(
        Color.BLACK, PieceType.PAWN
    )
    assert state.captured_square == 52


def test_capture_resets_halfmove_clock():
    position = Position.starting_position()
    position.halfmove_clock = 12

    position.board.set_piece(20, EMPTY)
    position.board.set_piece(36, make_piece(Color.WHITE, PieceType.KNIGHT))
    position.board.set_piece(52, make_piece(Color.BLACK, PieceType.PAWN))

    move = Move(36, 52, flags=MoveFlag.CAPTURE)

    position.make_move(move)

    assert position.halfmove_clock == 0


def test_pawn_promotes_to_queen():
    position = Position.starting_position()

    position.board.set_piece(100, EMPTY)
    position.board.set_piece(96, EMPTY)
    position.board.set_piece(112, EMPTY)

    position.board.set_piece(
        96,
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    move = Move(
        96,
        112,
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION,
    )

    position.make_move(move)

    assert position.board.get_piece(112) == make_piece(
        Color.WHITE, PieceType.QUEEN
    )


def test_pawn_can_promote_to_knight():
    position = Position.starting_position()

    position.board.set_piece(100, EMPTY)
    position.board.set_piece(96, EMPTY)
    position.board.set_piece(112, EMPTY)

    position.board.set_piece(
        96,
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    move = Move(
        96,
        112,
        promotion=PieceType.KNIGHT,
        flags=MoveFlag.PROMOTION,
    )

    position.make_move(move)

    assert position.board.get_piece(112) == make_piece(
        Color.WHITE, PieceType.KNIGHT
    )


def test_promotion_capture():
    position = Position.starting_position()

    # Remove the original black pawn from a7.
    position.board.set_piece(96, EMPTY)

    # Place a white pawn on a7.
    position.board.set_piece(
        96,
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    # Place a black rook on b8.
    position.board.set_piece(
        113,
        make_piece(Color.BLACK, PieceType.ROOK),
    )

    move = Move(
        96,
        113,
        promotion=PieceType.QUEEN,
        flags=MoveFlag.CAPTURE | MoveFlag.PROMOTION,
    )

    state = position.make_move(move)

    assert position.board.get_piece(113) == make_piece(
        Color.WHITE, PieceType.QUEEN
    )

    assert state.captured_piece == make_piece(
        Color.BLACK, PieceType.ROOK
    )

    assert state.captured_square == 113






def test_capture_cannot_target_friendly_piece():
    position = Position.starting_position()

    move = Move(0, 16, flags=MoveFlag.CAPTURE)

    with pytest.raises(ValueError):
        position.make_move(move)


def test_capture_cannot_target_empty_square():
    position = Position.starting_position()

    move = Move(1, 34, flags=MoveFlag.CAPTURE)

    with pytest.raises(ValueError):
        position.make_move(move)


def test_promotion_requires_promotion_flag():
    position = Position.starting_position()

    position.board.set_piece(100, EMPTY)
    position.board.set_piece(96, EMPTY)

    position.board.set_piece(
        96,
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    move = Move(96, 112)

    with pytest.raises(ValueError):
        position.make_move(move)