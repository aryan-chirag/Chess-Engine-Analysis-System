
from chess_engine.core.constants import parse_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.position import Position
from chess_engine.core.zobrist import compute_zobrist_hash


def test_starting_position_has_valid_hash():
    position = Position.starting_position()

    assert isinstance(position.zobrist_hash, int)
    assert 0 <= position.zobrist_hash < 2**64


def test_same_positions_have_same_hash():
    first = Position.starting_position()
    second = Position.starting_position()

    assert first.zobrist_hash == second.zobrist_hash


def test_hash_matches_full_recalculation():
    position = Position.starting_position()

    assert position.zobrist_hash == compute_zobrist_hash(position)


def test_different_piece_positions_have_different_hashes():
    first = Position.starting_position()

    second = Position.starting_position()

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    second.make_move(move)

    assert first.zobrist_hash != second.zobrist_hash


def test_side_to_move_changes_hash():
    position = Position.starting_position()

    original_hash = position.zobrist_hash

    position.side_to_move = position.side_to_move.opposite

    position.zobrist_hash = compute_zobrist_hash(position)

    assert position.zobrist_hash != original_hash


def test_castling_rights_change_hash():
    from chess_engine.core.constants import CastlingRights

    position = Position.starting_position()

    original_hash = position.zobrist_hash

    position.castling_rights = CastlingRights.NONE

    position.zobrist_hash = compute_zobrist_hash(position)

    assert position.zobrist_hash != original_hash


def test_en_passant_changes_hash():
    position = Position.starting_position()

    original_hash = position.zobrist_hash

    position.en_passant_square = parse_square("e3")

    position.zobrist_hash = compute_zobrist_hash(position)

    assert position.zobrist_hash != original_hash


def test_hash_restored_after_move_and_undo():
    position = Position.starting_position()

    original_hash = position.zobrist_hash

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    state = position.make_move(move)

    position.undo_move(move, state)

    assert position.zobrist_hash == original_hash


def test_hash_matches_recalculation_after_move():
    position = Position.starting_position()

    move = Move(
        parse_square("e2"),
        parse_square("e4"),
        flags=MoveFlag.DOUBLE_PAWN_PUSH,
    )

    position.make_move(move)

    assert position.zobrist_hash == compute_zobrist_hash(position)


def test_hash_matches_recalculation_after_capture():
    from chess_engine.core.board import Board
    from chess_engine.core.pieces import Color, PieceType, make_piece
    from chess_engine.core.position import Position

    board = Board()

    board.set_piece(
        parse_square("e1"),
        make_piece(Color.WHITE, PieceType.KING),
    )
    board.set_piece(
        parse_square("e8"),
        make_piece(Color.BLACK, PieceType.KING),
    )
    board.set_piece(
        parse_square("e4"),
        make_piece(Color.WHITE, PieceType.ROOK),
    )
    board.set_piece(
        parse_square("e5"),
        make_piece(Color.BLACK, PieceType.BISHOP),
    )

    position = Position(board=board)

    move = Move(
        parse_square("e4"),
        parse_square("e5"),
        flags=MoveFlag.CAPTURE,
    )

    position.make_move(move)

    assert position.zobrist_hash == compute_zobrist_hash(position)
