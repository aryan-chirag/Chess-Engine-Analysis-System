import pytest

from chess_engine.core.constants import parse_square

from chess_engine.core.move import (
    Move,
    MoveFlag,
)

from chess_engine.core.pieces import PieceType


def test_normal_move():

    move = Move(
        parse_square("e2"),
        parse_square("e4")
    )

    assert move.to_uci() == "e2e4"

    assert not move.is_capture
    assert not move.is_promotion
    assert not move.is_castling


def test_capture_move():

    move = Move(
        parse_square("e4"),
        parse_square("d5"),
        flags=MoveFlag.CAPTURE
    )

    assert move.is_capture


def test_double_pawn_push():

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH
    )

    assert move.is_double_pawn_push


def test_castling_move():

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING
    )

    assert move.is_castling


def test_en_passant_move():

    move = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT
    )

    assert move.is_capture
    assert move.is_en_passant


def test_queen_promotion():

    move = Move(
        parse_square("e7"),
        parse_square("e8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION
    )

    assert move.is_promotion
    assert move.to_uci() == "e7e8q"


def test_underpromotion():

    move = Move(
        parse_square("e7"),
        parse_square("e8"),
        promotion=PieceType.KNIGHT,
        flags=MoveFlag.PROMOTION
    )

    assert move.to_uci() == "e7e8n"


def test_capture_promotion():

    move = Move(
        parse_square("e7"),
        parse_square("d8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.CAPTURE | MoveFlag.PROMOTION
    )

    assert move.is_capture
    assert move.is_promotion

    assert move.to_uci() == "e7d8q"


def test_invalid_square():

    with pytest.raises(ValueError):

        Move(8, 20)


def test_same_start_and_destination():

    with pytest.raises(ValueError):

        Move(
            parse_square("e4"),
            parse_square("e4")
        )


def test_invalid_promotion():

    with pytest.raises(ValueError):

        Move(
            parse_square("e7"),
            parse_square("e8"),
            promotion=PieceType.KING,
            flags=MoveFlag.PROMOTION
        )


def test_missing_promotion_flag():

    with pytest.raises(ValueError):

        Move(
            parse_square("e7"),
            parse_square("e8"),
            promotion=PieceType.QUEEN
        )


def test_missing_promotion_piece():

    with pytest.raises(ValueError):

        Move(
            parse_square("e7"),
            parse_square("e8"),
            flags=MoveFlag.PROMOTION
        )


def test_move_is_immutable():

    move = Move(
        parse_square("e2"),
        parse_square("e4")
    )

    with pytest.raises(AttributeError):

        move.to_square = parse_square("e5")