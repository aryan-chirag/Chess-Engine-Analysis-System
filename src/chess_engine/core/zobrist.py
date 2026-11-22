
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
