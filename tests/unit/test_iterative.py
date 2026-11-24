
"""Tests for Iterative Deepening search."""

import pytest

from chess_engine.core.position import Position
from chess_engine.engine.alphabeta import alphabeta
from chess_engine.engine.iterative import iterative_deepening
from chess_engine.notation.fen import generate_fen


def test_iterative_deepening_returns_legal_move():
    position = Position.starting_position()

    result = iterative_deepening(position, 2)

    assert result.best_move is not None


def test_iterative_deepening_matches_alphabeta_score():
    position = Position.starting_position()

    iterative_result = iterative_deepening(position, 2)
    alphabeta_result = alphabeta(position, 2)

    assert iterative_result.score == alphabeta_result.score


def test_iterative_deepening_matches_alphabeta_best_move():
    position = Position.starting_position()

    iterative_result = iterative_deepening(position, 2)
    alphabeta_result = alphabeta(position, 2)

    assert iterative_result.best_move == alphabeta_result.best_move


def test_iterative_deepening_reports_maximum_depth():
    position = Position.starting_position()

    result = iterative_deepening(position, 3)

    assert result.depth == 3


def test_iterative_deepening_counts_nodes_from_all_iterations():
    position = Position.starting_position()

    expected_nodes = sum(
        alphabeta(position, depth).nodes
        for depth in range(1, 4)
    )

    result = iterative_deepening(position, 3)

    assert result.nodes == expected_nodes


def test_iterative_deepening_preserves_position():
    position = Position.starting_position()

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    iterative_deepening(position, 2)

    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_iterative_deepening_supports_depth_zero():
    position = Position.starting_position()

    result = iterative_deepening(position, 0)
    expected = alphabeta(position, 0)

    assert result.score == expected.score
    assert result.best_move == expected.best_move
    assert result.depth == 0


@pytest.mark.parametrize("depth", [-1, 1.5, True, "3", None])
def test_iterative_deepening_rejects_invalid_depth(depth):
    position = Position.starting_position()

    with pytest.raises(ValueError):
        iterative_deepening(position, depth)
