"""Tests for Alpha-Beta integration with Quiescence Search."""

from chess_engine.core.position import Position
from chess_engine.engine.alphabeta import alphabeta
from chess_engine.notation.fen import generate_fen, parse_fen


TACTICAL_POSITION = "4k3/8/8/4q3/4R3/8/8/4K3 w - - 0 1"


def test_quiescence_is_enabled_by_default():
    position = Position.starting_position()

    result = alphabeta(position, 2)

    assert result.depth == 2
    assert result.nodes > 0


def test_quiescence_changes_tactical_leaf_evaluation():
    position = parse_fen(TACTICAL_POSITION)

    without_quiescence = alphabeta(
        position,
        0,
        use_quiescence=False,
    )

    with_quiescence = alphabeta(
        position,
        0,
        use_quiescence=True,
    )

    assert without_quiescence.score == -400
    assert with_quiescence.score > without_quiescence.score
    assert with_quiescence.nodes > without_quiescence.nodes


def test_quiescence_search_preserves_position():
    position = parse_fen(TACTICAL_POSITION)

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    alphabeta(position, 2)

    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_quiescence_does_not_change_reference_search():
    position = Position.starting_position()

    result_without_quiescence = alphabeta(
        position,
        2,
        use_quiescence=False,
    )

    result_with_quiescence = alphabeta(
        position,
        2,
        use_quiescence=True,
    )

    # The opening position has no immediate tactical captures.
    assert result_with_quiescence.score == result_without_quiescence.score


def test_quiescence_node_count_includes_tactical_continuations():
    position = parse_fen(TACTICAL_POSITION)

    result = alphabeta(
        position,
        0,
        use_quiescence=True,
    )

    assert result.nodes > 1


def test_quiescence_respects_maximum_ply():
    position = Position.starting_position()

    result = alphabeta(
        position,
        2,
        max_quiescence_ply=2,
    )

    assert result.nodes > 0