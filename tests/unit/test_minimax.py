import pytest

from chess_engine.core.constants import parse_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.position import Position
from chess_engine.engine.minimax import minimax


def position_snapshot(position):
    return (
        position.board.squares.copy(),
        position.side_to_move,
        position.castling_rights,
        position.en_passant_square,
        position.halfmove_clock,
        position.fullmove_number,
        position.zobrist_hash,
    )


def test_minimax_returns_a_legal_move():
    position = Position.starting_position()

    result = minimax(position, 1)

    assert result.best_move is not None
    assert result.best_move in __import__(
        "chess_engine.movegen.legality",
        fromlist=["generate_legal_moves"],
    ).generate_legal_moves(position)


def test_minimax_returns_search_information():
    position = Position.starting_position()

    result = minimax(position, 2)

    assert result.depth == 2
    assert result.nodes > 1
    assert result.best_move is not None


def test_minimax_preserves_position():
    position = Position.starting_position()
    original = position_snapshot(position)

    minimax(position, 2)

    assert position_snapshot(position) == original


def test_minimax_finds_immediate_material_gain():
    from chess_engine.core.board import Board
    from chess_engine.core.pieces import Color, PieceType, make_piece

    board = Board()

    board.set_piece(
        parse_square("a1"),
        make_piece(Color.WHITE, PieceType.KING),
    )
    board.set_piece(
        parse_square("h8"),
        make_piece(Color.BLACK, PieceType.KING),
    )
    board.set_piece(
        parse_square("e4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )
    board.set_piece(
        parse_square("e5"),
        make_piece(Color.BLACK, PieceType.BISHOP),
    )

    position = Position(board=board)

    result = minimax(position, 1)

    assert result.score == 500
    assert result.best_move == Move(
        parse_square("e4"),
        parse_square("e5"),
        flags=MoveFlag.CAPTURE,
    )



@pytest.mark.parametrize("depth", [-1, 1.5, True])
def test_minimax_rejects_invalid_depth(depth):
    position = Position.starting_position()

    with pytest.raises(ValueError):
        minimax(position, depth)


def test_minimax_handles_stalemate():
    from chess_engine.core.board import Board
    from chess_engine.core.pieces import Color, PieceType, make_piece

    board = Board()

    board.set_piece(
        parse_square("a8"),
        make_piece(Color.BLACK, PieceType.KING),
    )
    board.set_piece(
        parse_square("c6"),
        make_piece(Color.WHITE, PieceType.KING),
    )
    board.set_piece(
        parse_square("b6"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    position = Position(
        board=board,
        side_to_move=Color.BLACK,
    )

    result = minimax(position, 2)

    assert result.best_move is None
    assert result.score == 0