import pytest

from chess_engine.core.constants import parse_square
from chess_engine.core.move import Move
from chess_engine.core.position import Position
from chess_engine.engine.alphabeta import alphabeta, _alphabeta
from chess_engine.engine.transposition import Bound, TranspositionTable
from chess_engine.movegen.legality import generate_legal_moves
from chess_engine.notation.fen import generate_fen


def test_tt_search_matches_search_without_tt():
    position = Position.starting_position()
    table = TranspositionTable()

    normal_result = alphabeta(position, 2)
    tt_result = alphabeta(position, 2, transposition_table=table)

    assert tt_result.score == normal_result.score
    assert tt_result.best_move == normal_result.best_move


def test_tt_stores_root_position():
    position = Position.starting_position()
    table = TranspositionTable()

    result = alphabeta(position, 2, transposition_table=table)

    entry = table.probe(position.zobrist_hash)

    assert entry is not None
    assert entry.depth == 2
    assert entry.best_move == result.best_move
    assert entry.bound in Bound


def test_exact_tt_entry_reduces_nodes():
    position = Position.starting_position()
    table = TranspositionTable()

    first_result = alphabeta(position, 2, transposition_table=table)
    second_result = alphabeta(position, 2, transposition_table=table)

    assert second_result.score == first_result.score
    assert second_result.best_move == first_result.best_move
    assert second_result.nodes == 1
    assert second_result.nodes < first_result.nodes


def test_tt_search_preserves_position():
    position = Position.starting_position()
    table = TranspositionTable()

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash
    original_side = position.side_to_move
    original_castling = position.castling_rights
    original_ep = position.en_passant_square
    original_halfmove = position.halfmove_clock
    original_fullmove = position.fullmove_number

    alphabeta(position, 3, transposition_table=table)

    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash
    assert position.side_to_move == original_side
    assert position.castling_rights == original_castling
    assert position.en_passant_square == original_ep
    assert position.halfmove_clock == original_halfmove
    assert position.fullmove_number == original_fullmove


def test_tt_stores_valid_bound_types():
    position = Position.starting_position()
    table = TranspositionTable()

    alphabeta(position, 2, transposition_table=table)

    for entry in table.entries:
        if entry is not None:
            assert entry.bound in (
                Bound.EXACT,
                Bound.LOWERBOUND,
                Bound.UPPERBOUND,
            )


def test_invalid_transposition_table_is_rejected():
    position = Position.starting_position()

    with pytest.raises(ValueError):
        alphabeta(position, 2, transposition_table="not a table")


def test_tt_records_shallow_hits():
    position = Position.starting_position()
    table = TranspositionTable()

    alphabeta(position, 1, transposition_table=table)
    alphabeta(position, 2, transposition_table=table)

    stats = table.get_stats()

    assert stats["hits"] >= 1
    assert stats["shallow_hits"] >= 1


def test_tt_records_exact_hits():
    position = Position.starting_position()
    table = TranspositionTable()

    alphabeta(position, 2, transposition_table=table)
    alphabeta(position, 2, transposition_table=table)

    assert table.get_stats()["exact_hits"] >= 1


def test_tt_records_move_ordering_hits():
    position = Position.starting_position()
    table = TranspositionTable()

    alphabeta(position, 2, transposition_table=table)
    alphabeta(position, 2, transposition_table=table)

    assert table.get_stats()["move_ordering_hits"] >= 1


def test_tt_statistics_reset():
    position = Position.starting_position()
    table = TranspositionTable()

    alphabeta(position, 2, transposition_table=table)

    table.reset_stats()
    stats = table.get_stats()

    assert stats["probes"] == 0
    assert stats["hits"] == 0
    assert stats["exact_hits"] == 0
    assert table.entry_count > 0


def test_lower_bound_entry_can_cause_cutoff():
    position = Position.starting_position()
    table = TranspositionTable()

    legal_move = generate_legal_moves(position)[0]

    table.store(
        position.zobrist_hash,
        depth=3,
        score=1000,
        bound=Bound.LOWERBOUND,
        best_move=legal_move,
    )

    nodes = [0]

    score, best_move, principal_variation = _alphabeta(
        position,
        depth=2,
        alpha=0,
        beta=100,
        nodes=nodes,
        transposition_table=table,
    )

    stats = table.get_stats()

    assert score == 1000
    assert best_move == legal_move
    assert principal_variation == (legal_move,)
    assert nodes[0] == 1
    assert stats["bound_hits"] == 1
    assert stats["cutoffs"] == 1


def test_upper_bound_entry_can_cause_cutoff():
    position = Position.starting_position()
    table = TranspositionTable()

    legal_move = generate_legal_moves(position)[0]

    table.store(
        position.zobrist_hash,
        depth=3,
        score=-1000,
        bound=Bound.UPPERBOUND,
        best_move=legal_move,
    )

    nodes = [0]

    score, best_move, principal_variation = _alphabeta(
        position,
        depth=2,
        alpha=-100,
        beta=0,
        nodes=nodes,
        transposition_table=table,
    )

    stats = table.get_stats()

    assert score == -1000
    assert best_move == legal_move
    assert principal_variation == (legal_move,)
    assert nodes[0] == 1
    assert stats["bound_hits"] == 1
    assert stats["cutoffs"] == 1


def test_shallow_tt_entry_does_not_cause_cutoff():
    position = Position.starting_position()
    table = TranspositionTable()

    legal_move = generate_legal_moves(position)[0]

    table.store(
        position.zobrist_hash,
        depth=1,
        score=1000,
        bound=Bound.LOWERBOUND,
        best_move=legal_move,
    )

    result = alphabeta(position, 2, transposition_table=table)
    stats = table.get_stats()

    assert result.nodes > 1
    assert stats["shallow_hits"] == 1
    assert stats["bound_hits"] == 0
    assert stats["cutoffs"] == 0


def test_tt_search_matches_search_without_tt_at_multiple_depths():
    position = Position.starting_position()
    table = TranspositionTable()

    for depth in (1, 2):
        normal_result = alphabeta(position, depth)
        tt_result = alphabeta(
            position,
            depth,
            transposition_table=table,
        )

        assert tt_result.score == normal_result.score
        assert tt_result.best_move == normal_result.best_move


def test_tt_entry_with_illegal_move_does_not_return_exact_result():
    position = Position.starting_position()
    table = TranspositionTable()

    illegal_move = Move(
        from_square=parse_square("a1"),
        to_square=parse_square("a8"),
    )

    table.store(
        position.zobrist_hash,
        depth=3,
        score=9999,
        bound=Bound.EXACT,
        best_move=illegal_move,
    )

    result = alphabeta(position, 2, transposition_table=table)

    assert result.nodes > 1
    assert result.score != 9999


def test_tt_search_preserves_position_after_cutoff():
    position = Position.starting_position()
    table = TranspositionTable()

    legal_move = generate_legal_moves(position)[0]

    original_fen = generate_fen(position)
    original_hash = position.zobrist_hash

    table.store(
        position.zobrist_hash,
        depth=3,
        score=1000,
        bound=Bound.LOWERBOUND,
        best_move=legal_move,
    )

    alphabeta(position, 2, transposition_table=table)

    assert generate_fen(position) == original_fen
    assert position.zobrist_hash == original_hash


def test_upper_bound_window_narrowing_preserves_exact_classification(
    monkeypatch,
):
    position = Position.starting_position()
    table = TranspositionTable()

    legal_move = generate_legal_moves(position)[0]

    table.store(
        position.zobrist_hash,
        depth=2,
        score=50,
        bound=Bound.UPPERBOUND,
        best_move=legal_move,
    )

    monkeypatch.setattr(
        "chess_engine.engine.alphabeta.evaluate",
        lambda position: -50,
    )

    stored_bounds = []
    original_store = table.store

    def recording_store(key, depth, score, bound, best_move=None):
        stored_bounds.append((score, bound))
        original_store(key, depth, score, bound, best_move)

    monkeypatch.setattr(table, "store", recording_store)

    nodes = [0]

    _alphabeta(
        position,
        depth=1,
        alpha=0,
        beta=100,
        nodes=nodes,
        transposition_table=table,
        use_quiescence=False,
)
    

    assert stored_bounds
    assert stored_bounds[-1] == (50, Bound.EXACT)
    