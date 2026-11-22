import pytest

from chess_engine.core.constants import CastlingRights, parse_square
from chess_engine.core.pieces import Color, PieceType, make_piece
from chess_engine.core.state import MoveState


def test_move_state_stores_basic_information():
    state = MoveState(
        moved_piece=make_piece(Color.WHITE, PieceType.PAWN),
        previous_side_to_move=Color.WHITE,
    )

    assert state.moved_piece == make_piece(Color.WHITE, PieceType.PAWN)
    assert state.captured_piece == 0
    assert state.previous_side_to_move == Color.WHITE


def test_move_state_stores_capture_information():
    state = MoveState(
        moved_piece=make_piece(Color.WHITE, PieceType.ROOK),
        captured_piece=make_piece(Color.BLACK, PieceType.QUEEN),
        captured_square=parse_square("a8"),
    )

    assert state.captured_piece == make_piece(Color.BLACK, PieceType.QUEEN)
    assert state.captured_square == parse_square("a8")


def test_move_state_stores_previous_position_metadata():
    state = MoveState(
        moved_piece=make_piece(Color.WHITE, PieceType.KING),
        previous_side_to_move=Color.WHITE,
        previous_castling_rights=CastlingRights.ALL,
        previous_en_passant_square=parse_square("e6"),
        previous_halfmove_clock=12,
        previous_fullmove_number=8,
        previous_zobrist_hash=123456,
    )

    assert state.previous_castling_rights == CastlingRights.ALL
    assert state.previous_en_passant_square == parse_square("e6")
    assert state.previous_halfmove_clock == 12
    assert state.previous_fullmove_number == 8
    assert state.previous_zobrist_hash == 123456


def test_move_state_rejects_invalid_moved_piece():
    with pytest.raises(ValueError):
        MoveState(moved_piece=0)


def test_move_state_rejects_invalid_captured_square():
    with pytest.raises(ValueError):
        MoveState(
            moved_piece=make_piece(Color.WHITE, PieceType.PAWN),
            captured_piece=make_piece(Color.BLACK, PieceType.PAWN),
            captured_square=128,
        )


def test_move_state_requires_captured_square_for_capture():
    with pytest.raises(ValueError):
        MoveState(
            moved_piece=make_piece(Color.WHITE, PieceType.PAWN),
            captured_piece=make_piece(Color.BLACK, PieceType.PAWN),
        )


def test_move_state_rejects_negative_halfmove_clock():
    with pytest.raises(ValueError):
        MoveState(
            moved_piece=make_piece(Color.WHITE, PieceType.PAWN),
            previous_halfmove_clock=-1,
        )


def test_move_state_rejects_invalid_fullmove_number():
    with pytest.raises(ValueError):
        MoveState(
            moved_piece=make_piece(Color.WHITE, PieceType.PAWN),
            previous_fullmove_number=0,
        )


def test_move_state_is_immutable():
    state = MoveState(
        moved_piece=make_piece(Color.WHITE, PieceType.PAWN)
    )

    with pytest.raises(AttributeError):
        state.moved_piece = make_piece(Color.WHITE, PieceType.QUEEN)