import pytest

from chess_engine.core.constants import CastlingRights
from chess_engine.core.pieces import Color
from chess_engine.core.position import Position
from chess_engine.notation.fen import parse_fen, generate_fen


STARTING_FEN = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/"
    "RNBQKBNR w KQkq - 0 1"
)


def test_parse_starting_position():
    position = parse_fen(STARTING_FEN)

    assert position.side_to_move == Color.WHITE
    assert position.castling_rights == CastlingRights.ALL
    assert position.en_passant_square is None
    assert position.halfmove_clock == 0
    assert position.fullmove_number == 1


def test_starting_position_fen_round_trip():
    position = parse_fen(STARTING_FEN)

    assert generate_fen(position) == STARTING_FEN


def test_parse_black_to_move():
    fen = "8/8/8/8/8/8/4k3/4K3 b - - 12 25"
    position = parse_fen(fen)

    assert position.side_to_move == Color.BLACK
    assert position.halfmove_clock == 12
    assert position.fullmove_number == 25


def test_parse_castling_rights():
    fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
    position = parse_fen(fen)

    assert position.castling_rights == CastlingRights.ALL


def test_parse_en_passant_square():
    fen = "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2"
    position = parse_fen(fen)

    assert generate_fen(position) == fen


def test_parse_custom_position_round_trip():
    fen = "4k3/8/8/8/3Q4/8/8/4K3 b - - 7 19"

    position = parse_fen(fen)

    assert generate_fen(position) == fen


@pytest.mark.parametrize(
    "fen",
    [
        "",
        "8/8/8/8/8/8/8/8 w - - 0 1",
        "8/8/8/8/8/8/8/4K2k w - - 0",
        "8/8/8/8/8/8/8/4K2k x - - 0 1",
        "8/8/8/8/8/8/8/4K2k w Z - 0 1",
        "8/8/8/8/8/8/8/4K2k w - z9 0 1",
        "8/8/8/8/8/8/8/4K2k w - - -1 1",
        "8/8/8/8/8/8/8/4K2k w - - 0 0",
        "8/8/8/8/8/8/8/4K2k w KK - 0 1",
    ],
)
def test_invalid_fen_is_rejected(fen):
    with pytest.raises(ValueError):
        parse_fen(fen)