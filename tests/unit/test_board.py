import pytest

from chess_engine.core.constants import (
    is_valid_square,
    make_square,
    parse_square,
    square_name,
)

from chess_engine.core.pieces import (
    Color,
    PieceType,
    make_piece,
    piece_color,
    piece_type,
)

from chess_engine.core.position import Position


def test_all_64_squares_are_valid():

    for rank in range(8):

        for file in range(8):

            square = make_square(file, rank)

            assert is_valid_square(square)


def test_invalid_0x88_squares():

    assert not is_valid_square(8)
    assert not is_valid_square(15)
    assert not is_valid_square(128)


def test_square_conversion():

    assert parse_square("a1") == 0
    assert parse_square("e4") == 52
    assert parse_square("h8") == 119

    assert square_name(0) == "a1"
    assert square_name(52) == "e4"
    assert square_name(119) == "h8"


def test_all_square_names_round_trip():

    files = "abcdefgh"
    ranks = "12345678"

    for rank in ranks:

        for file in files:

            name = file + rank

            square = parse_square(name)

            assert square_name(square) == name


def test_invalid_square_notation():

    with pytest.raises(ValueError):
        parse_square("z9")

    with pytest.raises(ValueError):
        parse_square("e")


def test_piece_encoding():

    white_queen = make_piece(Color.WHITE, PieceType.QUEEN)

    black_knight = make_piece(Color.BLACK, PieceType.KNIGHT)

    assert white_queen == 5
    assert black_knight == 10

    assert piece_color(white_queen) == Color.WHITE
    assert piece_color(black_knight) == Color.BLACK

    assert piece_type(white_queen) == PieceType.QUEEN
    assert piece_type(black_knight) == PieceType.KNIGHT


def test_starting_position():

    position = Position.starting_position()

    assert position.validate()

    assert position.board.count_pieces() == 32

    assert position.side_to_move == Color.WHITE

    assert position.king_square(Color.WHITE) == parse_square("e1")

    assert position.king_square(Color.BLACK) == parse_square("e8")


def test_initial_piece_placement():

    position = Position.starting_position()

    assert position.board.get_piece(parse_square("a1")) == make_piece(
        Color.WHITE, PieceType.ROOK
    )

    assert position.board.get_piece(parse_square("e1")) == make_piece(
        Color.WHITE, PieceType.KING
    )

    assert position.board.get_piece(parse_square("e2")) == make_piece(
        Color.WHITE, PieceType.PAWN
    )

    assert position.board.get_piece(parse_square("a8")) == make_piece(
        Color.BLACK, PieceType.ROOK
    )

    assert position.board.get_piece(parse_square("e8")) == make_piece(
        Color.BLACK, PieceType.KING
    )

    assert position.board.get_piece(parse_square("e7")) == make_piece(
        Color.BLACK, PieceType.PAWN
    )


def test_0x88_padding():

    position = Position.starting_position()

    assert position.board.validate_padding()


def test_position_counters():

    position = Position.starting_position()

    assert position.halfmove_clock == 0
    assert position.fullmove_number == 1