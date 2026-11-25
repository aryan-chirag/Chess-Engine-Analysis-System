import pytest

from chess_engine.core.position import Position
from chess_engine.engine.alphabeta import alphabeta
from chess_engine.engine.transposition import Bound, TranspositionTable
from chess_engine.notation.fen import generate_fen

def test_tt_search_matches_search_without_tt():
    position = Position.starting_position()
    table = TranspositionTable()

    normal_result = alphabeta(position, 2)
    tt_result = alphabeta(
        position,
        2,
        transposition_table=table,
    )

    assert tt_result.score == normal_result.score
    assert tt_result.best_move == normal_result.best_move


def test_tt_stores_root_position():
    position = Position.starting_position()
    table = TranspositionTable()

    result = alphabeta(
        position,
        2,
        transposition_table=table,
    )

    entry = table.probe(position.zobrist_hash)

    assert entry is not None
    assert entry.depth == 2
    assert entry.best_move == result.best_move
    assert entry.bound in Bound


def test_exact_tt_entry_reduces_nodes():
    position = Position.starting_position()
    table = TranspositionTable()

    first_result = alphabeta(
        position,
        2,
        transposition_table=table,
    )

    second_result = alphabeta(
        position,
        2,
        transposition_table=table,
    )

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

    alphabeta(
        position,
        3,
        transposition_table=table,
    )

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

    alphabeta(
        position,
        2,
        transposition_table=table,
    )

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
        alphabeta(
            position,
            2,
            transposition_table="not a table",
        )