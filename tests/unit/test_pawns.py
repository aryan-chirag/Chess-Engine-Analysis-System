import pytest

from chess_engine.core.constants import parse_square

from chess_engine.core.move import MoveFlag

from chess_engine.core.pieces import (
    Color,
    PieceType,
    make_piece,
)

from chess_engine.core.position import Position

from chess_engine.movegen.pawns import generate_pawn_moves


def move_set(moves):
    return {move.to_uci() for move in moves}


def test_white_starting_pawn_moves():

    position = Position.starting_position()

    moves = generate_pawn_moves(position)

    assert len(moves) == 16

    assert "e2e3" in move_set(moves)
    assert "e2e4" in move_set(moves)


def test_black_starting_pawn_moves():

    position = Position.starting_position()

    position.side_to_move = Color.BLACK

    moves = generate_pawn_moves(position)

    assert len(moves) == 16

    assert "e7e6" in move_set(moves)
    assert "e7e5" in move_set(moves)


def test_blocked_pawn_cannot_move():

    position = Position.starting_position()

    position.board.set_piece(
        parse_square("e3"),
        make_piece(Color.WHITE, PieceType.KNIGHT),
    )

    moves = generate_pawn_moves(position)

    assert "e2e3" not in move_set(moves)
    assert "e2e4" not in move_set(moves)


def test_double_push_blocked_by_second_square():

    position = Position.starting_position()

    position.board.set_piece(
        parse_square("e4"),
        make_piece(Color.BLACK, PieceType.KNIGHT),
    )

    moves = generate_pawn_moves(position)

    assert "e2e3" in move_set(moves)
    assert "e2e4" not in move_set(moves)


def test_pawn_cannot_move_diagonally_without_capture():

    position = Position.starting_position()

    moves = generate_pawn_moves(position)

    assert "e2d3" not in move_set(moves)
    assert "e2f3" not in move_set(moves)


def test_pawn_capture():

    position = Position.starting_position()

    position.board.set_piece(
        parse_square("d3"),
        make_piece(Color.BLACK, PieceType.KNIGHT),
    )

    moves = generate_pawn_moves(position)

    pawn_capture = next(
        move for move in moves
        if move.to_uci() == "e2d3"
    )

    assert pawn_capture.is_capture


def test_pawn_cannot_capture_own_piece():

    position = Position.starting_position()

    position.board.set_piece(
        parse_square("d3"),
        make_piece(Color.WHITE, PieceType.KNIGHT),
    )

    moves = generate_pawn_moves(position)

    assert "e2d3" not in move_set(moves)


def test_white_pawn_promotion():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("a7"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_pawn_moves(position)

    promotions = {
        move.to_uci()
        for move in moves
        if move.from_square == parse_square("a7")
    }

    assert promotions == {
        "a7a8q",
        "a7a8r",
        "a7a8b",
        "a7a8n",
    }


def test_promotion_capture():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("a7"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    position.board.set_piece(
        parse_square("b8"),
        make_piece(Color.BLACK, PieceType.ROOK),
    )

    moves = generate_pawn_moves(position)

    capture_promotions = {
        move.to_uci()
        for move in moves
        if move.from_square == parse_square("a7")
        and move.is_capture
    }

    assert capture_promotions == {
        "a7b8q",
        "a7b8r",
        "a7b8b",
        "a7b8n",
    }


def test_black_pawn_promotion():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("a2"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    position.side_to_move = Color.BLACK

    moves = generate_pawn_moves(position)

    promotions = {
        move.to_uci()
        for move in moves
        if move.from_square == parse_square("a2")
    }

    assert promotions == {
        "a2a1q",
        "a2a1r",
        "a2a1b",
        "a2a1n",
    }


def test_en_passant():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e5"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    position.board.set_piece(
        parse_square("d5"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    position.en_passant_square = parse_square("d6")

    moves = generate_pawn_moves(position)

    ep_move = next(
        move for move in moves
        if move.to_uci() == "e5d6"
    )

    assert ep_move.is_capture
    assert ep_move.is_en_passant


def test_en_passant_requires_enemy_pawn():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e5"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    position.en_passant_square = parse_square("d6")

    moves = generate_pawn_moves(position)

    assert "e5d6" not in move_set(moves)


def test_en_passant_requires_empty_target():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e5"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    position.board.set_piece(
        parse_square("d5"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    position.board.set_piece(
        parse_square("d6"),
        make_piece(Color.BLACK, PieceType.KNIGHT),
    )

    position.en_passant_square = parse_square("d6")

    moves = generate_pawn_moves(position)

    # e5d6 is still a valid normal capture of the knight.
    # However, it must NOT be generated as an en passant capture.

    target_move = next(
        (
            move
            for move in moves
            if move.to_uci() == "e5d6"
        ),
        None,
    )

    assert target_move is not None
    assert target_move.is_capture
    assert not target_move.is_en_passant