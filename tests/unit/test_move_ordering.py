
"""Tests for chess move ordering."""

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
from chess_engine.engine.move_ordering import (
    CAPTURE_BONUS,
    PROMOTION_BONUS,
    TT_MOVE_BONUS,
    order_moves,
    score_move,
)


def create_position(pieces, side=Color.WHITE):
    """Create a position containing the specified pieces."""

    board = Board()

    for square, color, piece_type in pieces:
        board.set_piece(
            parse_square(square),
            make_piece(color, piece_type),
        )

    return Position(
        board=board,
        side_to_move=side,
        castling_rights=CastlingRights.NONE,
    )


def test_tt_move_receives_highest_priority():
    position = Position.starting_position()

    moves = [
        Move(parse_square("e2"), parse_square("e4")),
        Move(parse_square("d2"), parse_square("d4")),
        Move(parse_square("g1"), parse_square("f3")),
    ]

    tt_move = moves[1]

    ordered = order_moves(position, moves, tt_move)

    assert ordered[0] == tt_move
    assert score_move(position, tt_move, tt_move) == TT_MOVE_BONUS


def test_promotion_receives_bonus():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("e7", Color.WHITE, PieceType.PAWN),
    ])

    promotion = Move(
        parse_square("e7"),
        parse_square("e8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION,
    )

    # Use an unoccupied promotion square in a separate position.
    position.board.set_piece(parse_square("e8"), 0)

    score = score_move(position, promotion)

    assert score == PROMOTION_BONUS + 900


def test_capture_score_uses_victim_and_attacker_values():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("e4", Color.WHITE, PieceType.PAWN),
        ("d5", Color.BLACK, PieceType.QUEEN),
    ])

    capture = Move(
        parse_square("e4"),
        parse_square("d5"),
        flags=MoveFlag.CAPTURE,
    )

    assert score_move(position, capture) == (
        CAPTURE_BONUS + 9000 - 100
    )


def test_en_passant_uses_captured_pawn():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("e5", Color.WHITE, PieceType.PAWN),
        ("d5", Color.BLACK, PieceType.PAWN),
    ])

    capture = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    assert score_move(position, capture) == (
        CAPTURE_BONUS + 1000 - 100
    )


def test_quiet_move_has_zero_score():
    position = Position.starting_position()

    quiet_move = Move(
        parse_square("e2"),
        parse_square("e4"),
    )

    assert score_move(position, quiet_move) == 0


def test_moves_are_sorted_by_descending_score():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("e4", Color.WHITE, PieceType.PAWN),
        ("d5", Color.BLACK, PieceType.QUEEN),
    ])

    quiet_move = Move(
        parse_square("e4"),
        parse_square("e5"),
    )

    capture_move = Move(
        parse_square("e4"),
        parse_square("d5"),
        flags=MoveFlag.CAPTURE,
    )

    moves = [quiet_move, capture_move]

    ordered = order_moves(position, moves)

    assert ordered[0] == capture_move
    assert ordered[1] == quiet_move


def test_ordering_does_not_modify_original_move_list():
    position = Position.starting_position()

    moves = [
        Move(parse_square("e2"), parse_square("e4")),
        Move(parse_square("d2"), parse_square("d4")),
    ]

    original_moves = moves.copy()

    order_moves(position, moves)

    assert moves == original_moves


def test_missing_captured_piece_raises_error():
    position = Position.starting_position()

    invalid_capture = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.CAPTURE,
    )

    try:
        score_move(position, invalid_capture)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for missing capture target.")
