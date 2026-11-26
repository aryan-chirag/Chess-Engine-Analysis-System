
"""Tests for Iterative Deepening search."""

import pytest
from chess_engine.engine.transposition import TranspositionTable
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


def test_iterative_deepening_uses_previous_best_move(monkeypatch):
    position = Position.starting_position()
    searched_moves = []

    original_alphabeta = alphabeta

    def tracking_alphabeta(
        position,
        depth,
        preferred_move=None,
        transposition_table=None,
    ):
        searched_moves.append(preferred_move)

        return original_alphabeta(
            position,
            depth,
            preferred_move=preferred_move,
            transposition_table=transposition_table,
        )

    monkeypatch.setattr(
        "chess_engine.engine.iterative.alphabeta",
        tracking_alphabeta,
    )

    iterative_deepening(position, 3)

    assert searched_moves[0] is None
    assert searched_moves[1] is not None
    assert searched_moves[2] is not None



def test_alphabeta_accepts_preferred_move():
    position = Position.starting_position()

    initial_result = alphabeta(position, 1)

    result = alphabeta(
        position,
        2,
        preferred_move=initial_result.best_move,
    )

    assert result.best_move is not None

def test_iterative_deepening_reuses_same_transposition_table(monkeypatch):
    position = Position.starting_position()
    table = TranspositionTable()
    used_tables = []

    original_alphabeta = alphabeta

    def tracking_alphabeta(
        position,
        depth,
        preferred_move=None,
        transposition_table=None,
    ):
        used_tables.append(transposition_table)

        return original_alphabeta(
            position,
            depth,
            preferred_move=preferred_move,
            transposition_table=transposition_table,
        )

    monkeypatch.setattr(
        "chess_engine.engine.iterative.alphabeta",
        tracking_alphabeta,
    )

    iterative_deepening(
        position,
        3,
        transposition_table=table,
    )

    assert len(used_tables) == 3
    assert all(used_table is table for used_table in used_tables)


def test_iterative_deepening_creates_transposition_table():
    position = Position.starting_position()

    result = iterative_deepening(position, 2)

    assert result.best_move is not None
    assert result.depth == 2


def test_iterative_deepening_rejects_invalid_transposition_table():
    position = Position.starting_position()

    with pytest.raises(ValueError):
        iterative_deepening(
            position,
            2,
            transposition_table="not a table",
        )


