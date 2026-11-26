import pytest

from chess_engine.core.position import Position
from chess_engine.engine.minimax import MATE_SCORE
from chess_engine.engine.quiescence import quiescence
from chess_engine.notation.fen import generate_fen, parse_fen


def test_quiescence_returns_score_and_node_count():
    position = Position.starting_position()

    score, nodes = quiescence(position)

    assert isinstance(score, int)
    assert isinstance(nodes, int)
    assert nodes >= 1


def test_quiescence_preserves_starting_position():
    position = Position.starting_position()

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    quiescence(position)

    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_quiescence_searches_captures():
    position = parse_fen(
        "4k3/8/8/4q3/4R3/8/8/4K3 w - - 0 1"
    )

    score, nodes = quiescence(position)

    assert score > 0
    assert nodes > 1


def test_quiescence_searches_promotions():
    position = parse_fen(
        "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"
    )

    score, nodes = quiescence(position)

    assert isinstance(score, int)
    assert nodes > 1


def test_quiescence_handles_checkmate():
    position = parse_fen(
        "7k/6Q1/5K2/8/8/8/8/8 b - - 0 1"
    )

    score, nodes = quiescence(position)

    assert score == -MATE_SCORE
    assert nodes == 1


def test_quiescence_searches_all_check_evasions():
    position = parse_fen(
        "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1"
    )

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    score, nodes = quiescence(position)

    assert isinstance(score, int)
    assert nodes > 1
    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_quiescence_rejects_invalid_window():
    position = Position.starting_position()

    with pytest.raises(ValueError):
        quiescence(position, alpha=10, beta=10)

    with pytest.raises(ValueError):
        quiescence(position, alpha=20, beta=10)


def test_quiescence_handles_beta_cutoff():
    position = Position.starting_position()

    score, nodes = quiescence(
        position,
        alpha=-100,
        beta=-50,
    )

    assert score >= -50
    assert nodes == 1