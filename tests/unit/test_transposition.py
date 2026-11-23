import pytest

from chess_engine.core.move import Move
from chess_engine.engine.transposition import (
    Bound,
    TranspositionTable,
    TTEntry,
)


def test_store_and_probe():
    table = TranspositionTable(size=16)

    table.store(12345, 5, 30, Bound.EXACT)

    entry = table.probe(12345)

    assert entry is not None
    assert entry.key == 12345
    assert entry.depth == 5
    assert entry.score == 30
    assert entry.bound == Bound.EXACT


def test_probe_missing_position():
    table = TranspositionTable(size=16)

    assert table.probe(12345) is None


def test_collision_does_not_return_wrong_position():
    table = TranspositionTable(size=4)

    table.store(1, 5, 30, Bound.EXACT)
    table.store(5, 5, 50, Bound.EXACT)

    assert table.probe(1) is None
    assert table.probe(5).score == 50


def test_deeper_entry_replaces_shallower_entry():
    table = TranspositionTable(size=16)

    table.store(123, 3, 20, Bound.EXACT)
    table.store(123, 7, 40, Bound.EXACT)

    assert table.probe(123).depth == 7
    assert table.probe(123).score == 40


def test_shallower_entry_does_not_replace_deeper_entry():
    table = TranspositionTable(size=16)

    table.store(123, 8, 40, Bound.EXACT)
    table.store(123, 3, 20, Bound.LOWERBOUND)

    assert table.probe(123).depth == 8
    assert table.probe(123).score == 40


def test_exact_entry_replaces_same_position():
    table = TranspositionTable(size=16)

    table.store(123, 8, 40, Bound.LOWERBOUND)
    table.store(123, 3, 25, Bound.EXACT)

    entry = table.probe(123)

    assert entry.depth == 3
    assert entry.score == 25
    assert entry.bound == Bound.EXACT


def test_best_move_is_stored():
    table = TranspositionTable(size=16)

    move = Move(20, 36)

    table.store(123, 5, 30, Bound.EXACT, move)

    assert table.probe(123).best_move == move


def test_generation_advances():
    table = TranspositionTable(size=16)

    assert table.generation == 0

    table.new_search()

    assert table.generation == 1


def test_old_generation_entry_can_be_replaced():
    table = TranspositionTable(size=4)

    table.store(1, 10, 50, Bound.EXACT)

    table.new_search()

    table.store(5, 2, 20, Bound.EXACT)

    assert table.probe(1) is None
    assert table.probe(5) is not None


def test_clear_removes_entries():
    table = TranspositionTable(size=16)

    table.store(123, 5, 30, Bound.EXACT)
    table.clear()

    assert table.probe(123) is None
    assert table.entry_count == 0
    assert table.generation == 0


def test_hashfull():
    table = TranspositionTable(size=10)

    assert table.hashfull() == 0

    table.store(1, 3, 20, Bound.EXACT)
    table.store(2, 3, 30, Bound.EXACT)

    assert table.hashfull() == 200


def test_invalid_table_size():
    with pytest.raises(ValueError):
        TranspositionTable(size=0)


def test_invalid_depth():
    table = TranspositionTable(size=16)

    with pytest.raises(ValueError):
        table.store(123, -1, 30, Bound.EXACT)


def test_invalid_bound():
    table = TranspositionTable(size=16)

    with pytest.raises(ValueError):
        table.store(123, 5, 30, "EXACT")