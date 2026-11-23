
"""
Chess Engine
Zobrist Hashing

Generates unique probabilistic fingerprints for chess positions.
"""

import random

from chess_engine.core.pieces import EMPTY


# ============================================================
# HASH CONFIGURATION
# ============================================================

RANDOM_SEED = 20261123

random_generator = random.Random(RANDOM_SEED)

MASK_64 = (1 << 64) - 1


# ============================================================
# ZOBRIST KEYS
# ============================================================

# Piece-square keys.
# Each piece encoding has a key for every possible mailbox square.
PIECE_KEYS = {
    piece: [
        random_generator.getrandbits(64)
        for _ in range(128)
    ]
    for piece in range(1, 15)
}


# Side-to-move key.
SIDE_KEY = random_generator.getrandbits(64)


# Castling-rights keys.
CASTLING_KEYS = [
    random_generator.getrandbits(64)
    for _ in range(16)
]


# En passant file keys.
EN_PASSANT_KEYS = [
    random_generator.getrandbits(64)
    for _ in range(8)
]


# ============================================================
# FULL POSITION HASH
# ============================================================

def compute_zobrist_hash(position) -> int:
    """
    Calculates the Zobrist hash of a complete chess position.

    Includes:
        - Piece placement
        - Side to move
        - Castling rights
        - En passant file
    """

    zobrist_hash = 0

    # --------------------------------------------------------
    # PIECE PLACEMENT
    # --------------------------------------------------------

    for square in position.board.iter_squares():

        piece = position.board.get_piece(square)

        if piece != EMPTY:

            zobrist_hash ^= PIECE_KEYS[piece][square]

    # --------------------------------------------------------
    # SIDE TO MOVE
    # --------------------------------------------------------

    # White is the default side.
    # XOR the key when Black is to move.
    if position.side_to_move.value == 1:

        zobrist_hash ^= SIDE_KEY

    # --------------------------------------------------------
    # CASTLING RIGHTS
    # --------------------------------------------------------

    castling_index = int(position.castling_rights)

    zobrist_hash ^= CASTLING_KEYS[castling_index]

    # --------------------------------------------------------
    # EN PASSANT
    # --------------------------------------------------------

    if position.en_passant_square is not None:

        file_index = position.en_passant_square & 7

        zobrist_hash ^= EN_PASSANT_KEYS[file_index]

    return zobrist_hash & MASK_64



def update_zobrist_hash(position, move, move_state) -> int:
    """
    Updates a position hash incrementally after a move.

    Uses the previous hash and applies XOR operations only
    to the pieces and metadata affected by the move.

    The position must already contain the executed move.
    """

    if move_state.previous_zobrist_hash is None:
        raise ValueError("Previous Zobrist hash is unavailable.")

    zobrist_hash = move_state.previous_zobrist_hash

    # --------------------------------------------------------
    # REMOVE THE ORIGINAL MOVING PIECE
    # --------------------------------------------------------

    moved_piece = move_state.moved_piece

    zobrist_hash ^= PIECE_KEYS[moved_piece][move.from_square]

    # --------------------------------------------------------
    # REMOVE THE CAPTURED PIECE
    # --------------------------------------------------------

    if move_state.captured_piece != EMPTY:

        zobrist_hash ^= PIECE_KEYS[
            move_state.captured_piece
        ][move_state.captured_square]

    # --------------------------------------------------------
    # ADD THE PIECE AT ITS NEW SQUARE
    # --------------------------------------------------------

    placed_piece = position.board.get_piece(move.to_square)

    zobrist_hash ^= PIECE_KEYS[placed_piece][move.to_square]

    # --------------------------------------------------------
    # UPDATE THE CASTLING ROOK
    # --------------------------------------------------------

    if move.is_castling:

        if move.to_square > move.from_square:

            rook_from = move.from_square + 3
            rook_to = move.from_square + 1

        else:

            rook_from = move.from_square - 4
            rook_to = move.from_square - 1

        rook = position.board.get_piece(rook_to)

        zobrist_hash ^= PIECE_KEYS[rook][rook_from]
        zobrist_hash ^= PIECE_KEYS[rook][rook_to]

    # --------------------------------------------------------
    # UPDATE SIDE TO MOVE
    # --------------------------------------------------------

    zobrist_hash ^= SIDE_KEY

    # --------------------------------------------------------
    # UPDATE CASTLING RIGHTS
    # --------------------------------------------------------

    old_castling = int(move_state.previous_castling_rights)
    new_castling = int(position.castling_rights)

    zobrist_hash ^= CASTLING_KEYS[old_castling]
    zobrist_hash ^= CASTLING_KEYS[new_castling]

    # --------------------------------------------------------
    # UPDATE EN PASSANT STATE
    # --------------------------------------------------------

    old_en_passant = move_state.previous_en_passant_square
    new_en_passant = position.en_passant_square

    if old_en_passant is not None:

        zobrist_hash ^= EN_PASSANT_KEYS[old_en_passant & 7]

    if new_en_passant is not None:

        zobrist_hash ^= EN_PASSANT_KEYS[new_en_passant & 7]

    return zobrist_hash & MASK_64