"""Tests for Alpha-Beta chess search."""

import pytest

from chess_engine.core.position import Position
from chess_engine.engine.alphabeta import alphabeta
from chess_engine.engine.minimax import minimax
from chess_engine.engine.negamax import negamax
from chess_engine.movegen.legality import generate_legal_moves


def test_alphabeta_returns_a_legal_move():
    position = Position.starting_position()

    result = alphabeta(position, 2)

    assert result.best_move in generate_legal_moves(position)


def test_alphabeta_returns_search_information():
    position = Position.starting_position()

    result = alphabeta(position, 2)

    assert result.depth == 2
    assert result.nodes > 0
    assert isinstance(result.score, int)


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_alphabeta_matches_negamax_score(depth):
    position = Position.starting_position()

    negamax_result = negamax(position, depth)
    alphabeta_result = alphabeta(position, depth)

    assert alphabeta_result.score == negamax_result.score


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_alphabeta_matches_minimax_score(depth):
    position = Position.starting_position()

    minimax_result = minimax(position, depth)
    alphabeta_result = alphabeta(position, depth)

    assert alphabeta_result.score == minimax_result.score


def test_alphabeta_searches_no_more_nodes_than_negamax():
    position = Position.starting_position()

    negamax_result = negamax(position, 3)
    alphabeta_result = alphabeta(position, 3)

    assert alphabeta_result.nodes <= negamax_result.nodes


def test_alphabeta_preserves_position():
    position = Position.starting_position()

    original_board = position.board.squares.copy()
    original_side = position.side_to_move
    original_castling = position.castling_rights
    original_ep = position.en_passant_square
    original_halfmove = position.halfmove_clock
    original_fullmove = position.fullmove_number
    original_hash = position.zobrist_hash

    alphabeta(position, 3)

    assert position.board.squares == original_board
    assert position.side_to_move == original_side
    assert position.castling_rights == original_castling
    assert position.en_passant_square == original_ep
    assert position.halfmove_clock == original_halfmove
    assert position.fullmove_number == original_fullmove
    assert position.zobrist_hash == original_hash


@pytest.mark.parametrize("depth", [-1, 1.5, True])
def test_alphabeta_rejects_invalid_depth(depth):
    position = Position.starting_position()

    with pytest.raises(ValueError):
        alphabeta(position, depth)