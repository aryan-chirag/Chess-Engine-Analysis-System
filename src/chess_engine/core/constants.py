"""
Chess Engine
Core Constants

Defines board dimensions, square utilities and castling rights.
"""

from enum import IntFlag


# ============================================================
# BOARD CONSTANTS
# ============================================================

BOARD_SIZE = 8
MAILBOX_SIZE = 128

FILES = "abcdefgh"
RANKS = "12345678"


# ============================================================
# 0x88 BOARD REPRESENTATION
# ============================================================

def is_valid_square(square: int) -> bool:
    """
    Determines whether an internal square index represents
    a valid chessboard square.
    """

    return 0 <= square < MAILBOX_SIZE and (square & 0x88) == 0


def make_square(file: int, rank: int) -> int:
    """
    Converts file and rank coordinates into a 0x88 square index.

    Both coordinates are zero-based.
    """

    if not 0 <= file < 8:
        raise ValueError(f"Invalid file: {file}")

    if not 0 <= rank < 8:
        raise ValueError(f"Invalid rank: {rank}")

    return rank * 16 + file


def file_of(square: int) -> int:
    """Returns the file index of a valid square."""

    if not is_valid_square(square):
        raise ValueError(f"Invalid square: {square}")

    return square & 7


def rank_of(square: int) -> int:
    """Returns the rank index of a valid square."""

    if not is_valid_square(square):
        raise ValueError(f"Invalid square: {square}")

    return square >> 4


def parse_square(name: str) -> int:
    """
    Converts algebraic notation into an internal square index.

    Example:
        'e4' -> 52
    """

    if not isinstance(name, str) or len(name) != 2:
        raise ValueError(f"Invalid square notation: {name}")

    file_char = name[0].lower()
    rank_char = name[1]

    if file_char not in FILES or rank_char not in RANKS:
        raise ValueError(f"Invalid square notation: {name}")

    file = FILES.index(file_char)
    rank = RANKS.index(rank_char)

    return make_square(file, rank)


def square_name(square: int) -> str:
    """
    Converts an internal square index into algebraic notation.

    Example:
        52 -> 'e4'
    """

    if not is_valid_square(square):
        raise ValueError(f"Invalid square: {square}")

    return FILES[file_of(square)] + RANKS[rank_of(square)]


# ============================================================
# CASTLING RIGHTS
# ============================================================

class CastlingRights(IntFlag):

    NONE = 0

    WHITE_KINGSIDE = 1
    WHITE_QUEENSIDE = 2

    BLACK_KINGSIDE = 4
    BLACK_QUEENSIDE = 8

    ALL = 15