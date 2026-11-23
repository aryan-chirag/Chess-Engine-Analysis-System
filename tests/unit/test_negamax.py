"""Tests for the Negamax search algorithm."""

import pytest

from chess_engine.core.position import Position
from chess_engine.engine.minimax import minimax
from chess_engine.engine.negamax import negamax
from chess_engine.movegen.legality import generate_legal_moves


def test_negamax_returns_a_legal_move():
    position = Position.starting_position()

    result = negamax(position, 2)

    assert result.best_move in generate_legal_moves(position)


def test_negamax_returns_search_information():
    position = Position.starting_position()

    result = negamax(position, 2)

    assert result.depth == 2
    assert result.nodes > 0
    assert isinstance(result.score, int)


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_negamax_matches_minimax_score(depth):
    position = Position.starting_position()

    minimax_result = minimax(position, depth)
    negamax_result = negamax(position, depth)

    assert negamax_result.score == minimax_result.score


def test_negamax_preserves_position():
    position = Position.starting_position()

    original_board = position.board.squares.copy()
    original_side = position.side_to_move
    original_castling = position.castling_rights
    original_ep = position.en_passant_square
    original_halfmove = position.halfmove_clock
    original_fullmove = position.fullmove_number
    original_hash = position.zobrist_hash

    negamax(position, 3)

    assert position.board.squares == original_board
    assert position.side_to_move == original_side
    assert position.castling_rights == original_castling
    assert position.en_passant_square == original_ep
    assert position.halfmove_clock == original_halfmove
    assert position.fullmove_number == original_fullmove
    assert position.zobrist_hash == original_hash


@pytest.mark.parametrize("depth", [-1, 1.5, True])
def test_negamax_rejects_invalid_depth(depth):
    position = Position.starting_position()

    with pytest.raises(ValueError):
        negamax(position, depth)