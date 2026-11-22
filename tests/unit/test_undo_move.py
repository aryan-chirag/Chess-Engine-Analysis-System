
import pytest

from chess_engine.core.board import Board
from chess_engine.core.constants import CastlingRights, parse_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.pieces import (
    Color,
    PieceType,
    make_piece,
)
from chess_engine.core.position import Position


def create_position(pieces, **kwargs):
    board = Board()

    for square, color, piece_type in pieces:
        board.set_piece(
            parse_square(square),
            make_piece(color, piece_type),
        )

    return Position(board=board, **kwargs)


def snapshot(position):
    """Captures every relevant position field for comparison."""

    return (
        tuple(
            position.board.get_piece(square)
            for square in position.board.iter_squares()
        ),
        position.side_to_move,
        position.castling_rights,
        position.en_passant_square,
        position.halfmove_clock,
        position.fullmove_number,
    )


def test_undo_normal_move():
    position = Position.starting_position()
    original = snapshot(position)

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_capture():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("e4", Color.WHITE, PieceType.ROOK),
        ("e5", Color.BLACK, PieceType.BISHOP),
    ])

    original = snapshot(position)

    move = Move(
        parse_square("e4"),
        parse_square("e5"),
        flags=MoveFlag.CAPTURE,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_promotion():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("a7", Color.WHITE, PieceType.PAWN),
    ])

    original = snapshot(position)

    move = Move(
        parse_square("a7"),
        parse_square("a8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_en_passant():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("e5", Color.WHITE, PieceType.PAWN),
        ("d5", Color.BLACK, PieceType.PAWN),
    ], en_passant_square=parse_square("d6"))

    original = snapshot(position)

    move = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_white_kingside_castling():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("h1", Color.WHITE, PieceType.ROOK),
        ("e8", Color.BLACK, PieceType.KING),
    ], castling_rights=CastlingRights.WHITE_KINGSIDE)

    original = snapshot(position)

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_black_queenside_castling():
    position = create_position([
        ("e1", Color.WHITE, PieceType.KING),
        ("e8", Color.BLACK, PieceType.KING),
        ("a8", Color.BLACK, PieceType.ROOK),
    ], side_to_move=Color.BLACK,
    castling_rights=CastlingRights.BLACK_QUEENSIDE)

    original = snapshot(position)

    move = Move(
        parse_square("e8"),
        parse_square("c8"),
        flags=MoveFlag.CASTLING,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_restores_castling_rights_after_king_move():
    position = Position.starting_position()
    original = snapshot(position)

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert position.castling_rights == CastlingRights.ALL
    assert snapshot(position) == original


def test_undo_restores_clocks_and_en_passant_square():
    position = Position.starting_position()

    position.halfmove_clock = 12
    position.fullmove_number = 8
    position.en_passant_square = None

    original = snapshot(position)

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    state = position.make_move(move)
    position.undo_move(move, state)

    assert snapshot(position) == original


def test_undo_rejects_invalid_move_state():
    position = Position.starting_position()

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    state = position.make_move(move)

    with pytest.raises(TypeError):
        position.undo_move(move, None)

    # The valid state must still work.
    position.undo_move(move, state)
