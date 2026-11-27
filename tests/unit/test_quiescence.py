import pytest

from chess_engine.engine.quiescence import _quiescence
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


def test_quiescence_stops_at_maximum_ply_in_quiet_position():
    position = Position.starting_position()

    score, nodes = quiescence(position, max_ply=1)

    assert isinstance(score, int)
    assert nodes == 1


def test_quiescence_continues_when_in_check_at_maximum_ply():
    position = parse_fen(
        "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1"
    )

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    score, nodes = quiescence(position, max_ply=1)

    assert isinstance(score, int)
    assert nodes > 1
    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_quiescence_detects_checkmate_at_maximum_ply():
    position = parse_fen(
        "7k/6Q1/5K2/8/8/8/8/8 b - - 0 1"
    )

    score, nodes = quiescence(position, max_ply=1)

    assert score == -MATE_SCORE
    assert nodes == 1


def test_quiescence_validates_maximum_ply():
    position = Position.starting_position()

    for invalid_value in (0, -1, 1.5, True, "16"):
        with pytest.raises(ValueError):
            quiescence(position, max_ply=invalid_value)

def test_quiescence_restores_repetition_counts_after_search():
    position = Position.starting_position()
    repetition_counts = {}

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    score, nodes = _quiescence(
        position,
        float("-inf"),
        float("inf"),
        ply=0,
        max_ply=1,
        repetition_counts=repetition_counts,
    )

    assert isinstance(score, int)
    assert nodes >= 1
    assert repetition_counts == {}
    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_quiescence_detects_third_position_occurrence():
    position = Position.starting_position()
    position_hash = position.zobrist_hash

    repetition_counts = {
        position_hash: 2,
    }

    score, nodes = _quiescence(
        position,
        float("-inf"),
        float("inf"),
        ply=0,
        max_ply=16,
        repetition_counts=repetition_counts,
    )

    assert score == 0
    assert nodes == 1
    assert repetition_counts[position_hash] == 2


def test_quiescence_continues_when_check_evasion_gives_check():
    from chess_engine.core.attacks import is_in_check
    from chess_engine.movegen.legality import generate_legal_moves

    position = parse_fen(
        "k3r3/8/8/8/8/5B2/8/4K3 w - - 0 1"
    )

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    # White is initially in check.
    assert is_in_check(position)

    # Find the bishop's blocking move: f3-e4.
    blocking_move = next(
        move
        for move in generate_legal_moves(position)
        if move.from_square == 37 and move.to_square == 52
    )

    state = position.make_move(blocking_move)

    try:
        # The blocking move also checks the black king.
        assert is_in_check(position)
    finally:
        position.undo_move(blocking_move, state)

    # Search with a maximum of one ply.
    score, nodes = quiescence(position, max_ply=1)

    assert isinstance(score, int)
    assert nodes > 2
    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_quiescence_handles_consecutive_check_evasions():
    from chess_engine.core.attacks import is_in_check
    from chess_engine.movegen.legality import generate_legal_moves

    position = parse_fen(
        "k3r3/8/8/8/8/5B2/8/4K3 w - - 0 1"
    )

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    # White blocks the rook check and checks the black king.
    white_move = next(
        move
        for move in generate_legal_moves(position)
        if move.from_square == 37 and move.to_square == 52
    )

    state = position.make_move(white_move)

    try:
        assert is_in_check(position)

        # Black must have legal check evasions.
        black_evasions = generate_legal_moves(position)
        assert black_evasions

        saw_countercheck = False

        for black_move in black_evasions:
            black_state = position.make_move(black_move)

            try:
                if is_in_check(position):
                    saw_countercheck = True

            finally:
                position.undo_move(black_move, black_state)

        assert saw_countercheck

    finally:
        position.undo_move(white_move, state)

    score, nodes = quiescence(position, max_ply=1)

    assert isinstance(score, int)
    assert nodes > 2
    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash

