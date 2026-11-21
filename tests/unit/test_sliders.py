from chess_engine.movegen.sliders import (
    generate_bishop_moves,
    generate_rook_moves,
    generate_queen_moves,
)


from chess_engine.core.constants import parse_square
from chess_engine.core.position import Position
from chess_engine.core.pieces import (
    Color,
    PieceType,
    make_piece,
)
from chess_engine.core.move import MoveFlag
from chess_engine.movegen.sliders import generate_bishop_moves


def move_set(moves):
    return {move.to_uci() for move in moves}


def empty_position():

    position = Position.starting_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    return position


def test_bishop_from_center_has_thirteen_moves():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    moves = generate_bishop_moves(position)

    assert len(moves) == 13


def test_bishop_moves_diagonally():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    moves = generate_bishop_moves(position)

    assert "d4e5" in move_set(moves)
    assert "d4c5" in move_set(moves)
    assert "d4e3" in move_set(moves)
    assert "d4c3" in move_set(moves)


def test_bishop_cannot_move_straight():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    moves = generate_bishop_moves(position)

    assert "d4d5" not in move_set(moves)
    assert "d4e4" not in move_set(moves)


def test_bishop_stops_before_friendly_piece():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    position.board.set_piece(
        parse_square("f6"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_bishop_moves(position)

    assert "d4e5" in move_set(moves)
    assert "d4f6" not in move_set(moves)
    assert "d4g7" not in move_set(moves)


def test_bishop_captures_enemy_and_stops():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    position.board.set_piece(
        parse_square("f6"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    moves = generate_bishop_moves(position)

    assert "d4e5" in move_set(moves)
    assert "d4f6" in move_set(moves)
    assert "d4g7" not in move_set(moves)

    capture = next(
        move for move in moves
        if move.to_uci() == "d4f6"
    )

    assert capture.flags & MoveFlag.CAPTURE


def test_bishop_cannot_capture_own_piece():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    position.board.set_piece(
        parse_square("e5"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_bishop_moves(position)

    assert "d4e5" not in move_set(moves)


def test_bishop_on_corner():

    position = empty_position()

    position.board.set_piece(
        parse_square("a1"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    moves = generate_bishop_moves(position)

    assert move_set(moves) == {
        "a1b2",
        "a1c3",
        "a1d4",
        "a1e5",
        "a1f6",
        "a1g7",
        "a1h8",
    }


def test_black_bishop_moves():

    position = empty_position()

    position.side_to_move = Color.BLACK

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.BLACK, PieceType.BISHOP),
    )

    moves = generate_bishop_moves(position)

    assert len(moves) == 13


def test_bishop_does_not_capture_king():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    position.board.set_piece(
        parse_square("f6"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    moves = generate_bishop_moves(position)

    assert "d4f6" not in move_set(moves)


def test_bishop_does_not_move_when_not_its_turn():

    position = empty_position()

    position.side_to_move = Color.BLACK

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.BISHOP),
    )

    assert generate_bishop_moves(position) == []



# =========================
# ROOK TESTS
# =========================

from chess_engine.movegen.sliders import generate_rook_moves


def test_rook_from_center_has_fourteen_moves():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    moves = generate_rook_moves(position)

    assert len(moves) == 14


def test_rook_moves_horizontally_and_vertically():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    moves = generate_rook_moves(position)

    generated = move_set(moves)

    assert "d4d5" in generated
    assert "d4d3" in generated
    assert "d4c4" in generated
    assert "d4e4" in generated


def test_rook_cannot_move_diagonally():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    moves = generate_rook_moves(position)

    assert "d4e5" not in move_set(moves)
    assert "d4c3" not in move_set(moves)


def test_rook_stops_before_friendly_piece():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    position.board.set_piece(
        parse_square("d6"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_rook_moves(position)

    generated = move_set(moves)

    assert "d4d5" in generated
    assert "d4d6" not in generated
    assert "d4d7" not in generated


def test_rook_captures_enemy_and_stops():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    position.board.set_piece(
        parse_square("d6"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    moves = generate_rook_moves(position)

    generated = move_set(moves)

    assert "d4d5" in generated
    assert "d4d6" in generated
    assert "d4d7" not in generated

    capture = next(
        move for move in moves
        if move.to_uci() == "d4d6"
    )

    assert capture.is_capture


def test_rook_cannot_capture_own_piece():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    position.board.set_piece(
        parse_square("d5"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_rook_moves(position)

    assert "d4d5" not in move_set(moves)


def test_rook_on_corner_has_fourteen_moves():

    position = empty_position()

    # Move kings away from the rook's rank and file.
    position.board.clear()

    position.board.set_piece(
        parse_square("c3"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("f6"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("a1"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    moves = generate_rook_moves(position)

    assert len(moves) == 14




def test_black_rook_moves():

    position = empty_position()

    position.side_to_move = Color.BLACK

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.BLACK, PieceType.ROOK),
    )

    moves = generate_rook_moves(position)

    assert len(moves) == 14


def test_rook_cannot_capture_king():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    position.board.set_piece(
        parse_square("d8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    moves = generate_rook_moves(position)

    assert "d4d8" not in move_set(moves)


def test_rook_does_not_move_when_not_its_turn():

    position = empty_position()

    position.side_to_move = Color.BLACK

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )

    moves = generate_rook_moves(position)

    assert moves == []



# =========================
# QUEEN TESTS
# =========================

def test_queen_from_center_has_twenty_seven_moves():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    moves = generate_queen_moves(position)

    assert len(moves) == 27


def test_queen_moves_diagonally():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    moves = generate_queen_moves(position)

    generated = move_set(moves)

    assert "d4e5" in generated
    assert "d4c5" in generated
    assert "d4e3" in generated
    assert "d4c3" in generated


def test_queen_moves_horizontally_and_vertically():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    moves = generate_queen_moves(position)

    generated = move_set(moves)

    assert "d4d5" in generated
    assert "d4d3" in generated
    assert "d4c4" in generated
    assert "d4e4" in generated


def test_queen_stops_before_friendly_piece():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    position.board.set_piece(
        parse_square("f6"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_queen_moves(position)

    generated = move_set(moves)

    assert "d4e5" in generated
    assert "d4f6" not in generated
    assert "d4g7" not in generated


def test_queen_captures_enemy_piece_and_stops():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    position.board.set_piece(
        parse_square("f6"),
        make_piece(Color.BLACK, PieceType.PAWN),
    )

    moves = generate_queen_moves(position)

    generated = move_set(moves)

    assert "d4e5" in generated
    assert "d4f6" in generated
    assert "d4g7" not in generated


def test_queen_cannot_capture_own_piece():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    position.board.set_piece(
        parse_square("d5"),
        make_piece(Color.WHITE, PieceType.PAWN),
    )

    moves = generate_queen_moves(position)

    assert "d4d5" not in move_set(moves)


def test_queen_on_corner_has_twenty_one_moves():

    position = empty_position()

    position.board.clear()

    position.board.set_piece(
        parse_square("c5"),
        make_piece(Color.WHITE, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("f3"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    position.board.set_piece(
        parse_square("a1"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    moves = generate_queen_moves(position)

    assert len(moves) == 21




def test_black_queen_moves():

    position = empty_position()

    position.side_to_move = Color.BLACK

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.BLACK, PieceType.QUEEN),
    )

    moves = generate_queen_moves(position)

    assert len(moves) == 27


def test_queen_cannot_capture_king():

    position = empty_position()

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    position.board.set_piece(
        parse_square("d8"),
        make_piece(Color.BLACK, PieceType.KING),
    )

    moves = generate_queen_moves(position)

    assert "d4d8" not in move_set(moves)


def test_queen_does_not_move_when_not_its_turn():

    position = empty_position()

    position.side_to_move = Color.BLACK

    position.board.set_piece(
        parse_square("d4"),
        make_piece(Color.WHITE, PieceType.QUEEN),
    )

    moves = generate_queen_moves(position)

    assert moves == []


