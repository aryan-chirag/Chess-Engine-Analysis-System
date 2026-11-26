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

    assert table.probe(1) is not None
    assert table.probe(5) is None


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

    assert entry.depth == 8
    assert entry.score == 40
    assert entry.bound == Bound.LOWERBOUND


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

    assert table.probe(1) is not None
    assert table.probe(5) is None


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



def test_shallower_entry_does_not_replace_deeper_entry():
    table = TranspositionTable(size=10)

    table.store(100, 8, 50, Bound.LOWERBOUND)
    table.store(100, 4, 20, Bound.EXACT)

    entry = table.probe(100)

    assert entry.depth == 8
    assert entry.score == 50


def test_equal_depth_exact_entry_replaces_non_exact_entry():
    table = TranspositionTable(size=10)

    table.store(100, 5, 30, Bound.LOWERBOUND)
    table.store(100, 5, 40, Bound.EXACT)

    entry = table.probe(100)

    assert entry.bound == Bound.EXACT
    assert entry.score == 40


def test_shallower_entry_updates_best_move_without_replacing_score():
    table = TranspositionTable(size=10)

    old_move = Move(100, 101)
    new_move = Move(100, 102)

    table.store(100, 8, 50, Bound.EXACT, old_move)
    table.store(100, 4, 20, Bound.LOWERBOUND, new_move)

    entry = table.probe(100)

    assert entry.depth == 8
    assert entry.score == 50
    assert entry.best_move == new_move


def test_shallower_entry_refreshes_generation():
    table = TranspositionTable(size=10)

    table.store(100, 8, 50, Bound.EXACT)

    table.new_search()
    table.store(100, 4, 20, Bound.LOWERBOUND)

    entry = table.probe(100)

    assert entry.depth == 8
    assert entry.generation == table.generation


def test_shallower_collision_does_not_replace_deeper_entry_from_old_generation():
    table = TranspositionTable(size=10)

    table.store(100, 8, 50, Bound.EXACT)

    table.new_search()

    # 110 collides with 100 because the table size is 10.
    table.store(110, 3, 20, Bound.EXACT)

    assert table.probe(100) is not None
    assert table.probe(110) is None


def test_equal_depth_collision_replaces_old_generation_entry():
    table = TranspositionTable(size=10)

    table.store(100, 5, 50, Bound.EXACT)

    table.new_search()
    table.store(110, 5, 20, Bound.EXACT)

    assert table.probe(100) is None
    assert table.probe(110) is not None


def test_invalid_key_is_rejected():
    table = TranspositionTable(size=10)

    with pytest.raises(ValueError):
        table.store(-1, 5, 20, Bound.EXACT)

    with pytest.raises(ValueError):
        table.probe(1 << 64)


def test_boolean_key_is_rejected():
    table = TranspositionTable(size=10)

    with pytest.raises(ValueError):
        table.store(True, 5, 20, Bound.EXACT)


def test_invalid_score_is_rejected():
    table = TranspositionTable(size=10)

    with pytest.raises(ValueError):
        table.store(100, 5, 20.5, Bound.EXACT)


def test_boolean_depth_is_rejected():
    table = TranspositionTable(size=10)

    with pytest.raises(ValueError):
        table.store(100, True, 20, Bound.EXACT)

def test_probe_statistics():
    table = TranspositionTable(size=10)

    table.store(123, 2, 50, Bound.EXACT)

    table.probe(123)
    table.probe(456)

    stats = table.get_stats()

    assert stats["probes"] == 2
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 50.0


def test_store_statistics():
    table = TranspositionTable(size=10)

    table.store(123, 2, 50, Bound.EXACT)

    stats = table.get_stats()

    assert stats["stores"] == 1
    assert stats["replacements"] == 0


def test_replacement_statistics():
    table = TranspositionTable(size=10)

    table.store(123, 1, 50, Bound.LOWERBOUND)
    table.store(123, 3, 80, Bound.EXACT)

    stats = table.get_stats()

    assert stats["stores"] == 2
    assert stats["replacements"] == 1


def test_cutoff_statistics():
    table = TranspositionTable(size=10)

    table.record_cutoff()

    assert table.get_stats()["cutoffs"] == 1


def test_reset_statistics_preserves_entries():
    table = TranspositionTable(size=10)

    table.store(123, 2, 50, Bound.EXACT)
    table.probe(123)

    table.reset_stats()

    assert table.probe(123) is not None
    assert table.get_stats()["probes"] == 1
    assert table.get_stats()["hits"] == 1
    assert table.get_stats()["stores"] == 0

def test_probe_rejects_different_search_configuration():
    table = TranspositionTable(size=16)

    table.store(
        123,
        5,
        30,
        Bound.EXACT,
        search_config=(True, 16),
    )

    assert table.probe(
        123,
        search_config=(False, 0),
    ) is None


def test_probe_accepts_matching_search_configuration():
    table = TranspositionTable(size=16)

    table.store(
        123,
        5,
        30,
        Bound.EXACT,
        search_config=(True, 8),
    )

    entry = table.probe(
        123,
        search_config=(True, 8),
    )

    assert entry is not None
    assert entry.score == 30


def test_different_search_configuration_replaces_existing_entry():
    table = TranspositionTable(size=16)

    table.store(
        123,
        10,
        100,
        Bound.EXACT,
        search_config=(True, 16),
    )

    table.store(
        123,
        2,
        20,
        Bound.EXACT,
        search_config=(False, 0),
    )

    entry = table.probe(
        123,
        search_config=(False, 0),
    )

    assert entry is not None
    assert entry.depth == 2
    assert entry.score == 20
    assert entry.search_config == (False, 0)


@pytest.mark.parametrize(
    "search_config",
    [
        (1, 16),
        (True, 0),
        (False, 16),
        (True, -1),
        (True, True),
        (True,),
        [True, 16],
    ],
)
def test_invalid_search_configuration_is_rejected(search_config):
    table = TranspositionTable(size=16)

    with pytest.raises(ValueError):
        table.store(
            123,
            5,
            30,
            Bound.EXACT,
            search_config=search_config,
        )

    with pytest.raises(ValueError):
        table.probe(
            123,
            search_config=search_config,
        )