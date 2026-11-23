from chess_engine.core.board import Board
from chess_engine.core.constants import CastlingRights
from chess_engine.core.pieces import Color, PieceType, make_piece


from chess_engine.core.constants import parse_square
from chess_engine.core.move import Move, MoveFlag
from chess_engine.core.position import Position
from chess_engine.core.zobrist import compute_zobrist_hash

def create_test_position(
    pieces,
    side_to_move=Color.WHITE,
    castling_rights=CastlingRights.NONE,
    en_passant_square=None,
):
    """Creates a minimal position for isolated hashing tests."""

    board = Board()

    for square, color, piece_type in pieces:
        board.set_piece(
            parse_square(square),
            make_piece(color, piece_type),
        )

    return Position(
        board=board,
        side_to_move=side_to_move,
        castling_rights=castling_rights,
        en_passant_square=(
            parse_square(en_passant_square)
            if en_passant_square is not None
            else None
        ),
    )





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


#Castling and undo
def test_hash_matches_recalculation_after_castling_and_undo():

    position = create_test_position(
        pieces=[
            ("e1", Color.WHITE, PieceType.KING),
            ("h1", Color.WHITE, PieceType.ROOK),
            ("e8", Color.BLACK, PieceType.KING),
        ],
        castling_rights=CastlingRights.WHITE_KINGSIDE,
    )

    original_hash = position.zobrist_hash

    move = Move(
        parse_square("e1"),
        parse_square("g1"),
        flags=MoveFlag.CASTLING,
    )

    state = position.make_move(move)

    assert position.zobrist_hash == compute_zobrist_hash(position)

    position.undo_move(move, state)

    assert position.zobrist_hash == original_hash
    assert position.zobrist_hash == compute_zobrist_hash(position)



#En passant and undo
def test_hash_matches_recalculation_after_en_passant_and_undo():

    position = create_test_position(
        pieces=[
            ("e1", Color.WHITE, PieceType.KING),
            ("e8", Color.BLACK, PieceType.KING),
            ("e5", Color.WHITE, PieceType.PAWN),
            ("d5", Color.BLACK, PieceType.PAWN),
        ],
        en_passant_square="d6",
    )

    original_hash = position.zobrist_hash

    move = Move(
        parse_square("e5"),
        parse_square("d6"),
        flags=MoveFlag.CAPTURE | MoveFlag.EN_PASSANT,
    )

    state = position.make_move(move)

    assert position.zobrist_hash == compute_zobrist_hash(position)

    position.undo_move(move, state)

    assert position.zobrist_hash == original_hash
    assert position.zobrist_hash == compute_zobrist_hash(position)



#Promotion and undo
def test_hash_matches_recalculation_after_promotion_and_undo():

    position = create_test_position(
        pieces=[
            ("e1", Color.WHITE, PieceType.KING),
            ("e8", Color.BLACK, PieceType.KING),
            ("a7", Color.WHITE, PieceType.PAWN),
        ],
    )

    original_hash = position.zobrist_hash

    move = Move(
        parse_square("a7"),
        parse_square("a8"),
        promotion=PieceType.QUEEN,
        flags=MoveFlag.PROMOTION,
    )

    state = position.make_move(move)

    assert position.zobrist_hash == compute_zobrist_hash(position)

    position.undo_move(move, state)

    assert position.zobrist_hash == original_hash
    assert position.zobrist_hash == compute_zobrist_hash(position)



#Capture and undo
def test_hash_restored_after_capture_and_undo():

    position = create_test_position(
        pieces=[
            ("e1", Color.WHITE, PieceType.KING),
            ("e8", Color.BLACK, PieceType.KING),
            ("e4", Color.WHITE, PieceType.ROOK),
            ("e5", Color.BLACK, PieceType.BISHOP),
        ],
    )

    original_hash = position.zobrist_hash

    move = Move(
        parse_square("e4"),
        parse_square("e5"),
        flags=MoveFlag.CAPTURE,
    )

    state = position.make_move(move)

    position.undo_move(move, state)

    assert position.zobrist_hash == original_hash
    assert position.zobrist_hash == compute_zobrist_hash(position)



#Multiple moves and complete undo
def test_hash_restored_after_multiple_moves_and_undos():

    position = Position.starting_position()

    original_hash = position.zobrist_hash

    moves = [
        Move(
            parse_square("e2"),
            parse_square("e4"),
            flags=MoveFlag.DOUBLE_PAWN_PUSH,
        ),
        Move(
            parse_square("e7"),
            parse_square("e5"),
            flags=MoveFlag.DOUBLE_PAWN_PUSH,
        ),
        Move(
            parse_square("g1"),
            parse_square("f3"),
        ),
    ]

    history = []

    for move in moves:

        state = position.make_move(move)

        history.append((move, state))

        assert position.zobrist_hash == compute_zobrist_hash(position)

    for move, state in reversed(history):

        position.undo_move(move, state)

        assert position.zobrist_hash == compute_zobrist_hash(position)

    assert position.zobrist_hash == original_hash


#