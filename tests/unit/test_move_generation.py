from chess_engine.core.position import Position
from chess_engine.movegen.generator import generate_pseudo_legal_moves
from chess_engine.movegen.legality import generate_legal_moves


def test_starting_position_has_twenty_pseudo_legal_moves():
    assert len(generate_pseudo_legal_moves(Position.starting_position())) == 20


def test_starting_position_has_twenty_legal_moves():
    assert len(generate_legal_moves(Position.starting_position())) == 20
