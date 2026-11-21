"""
Chess Engine
Piece Representation

Defines piece types, colors and piece encoding utilities.
"""

from enum import IntEnum


# ============================================================
# PIECE COLORS
# ============================================================

class Color(IntEnum):

    WHITE = 0
    BLACK = 1

    @property
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE


# ============================================================
# PIECE TYPES
# ============================================================

class PieceType(IntEnum):

    NONE = 0

    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6


# ============================================================
# PIECE ENCODING
# ============================================================

EMPTY = 0

BLACK_PIECE_OFFSET = 8


def make_piece(color: Color, piece_type: PieceType) -> int:
    """
    Encodes a piece into an integer.

    White pieces: 1-6
    Black pieces: 9-14
    Empty square: 0
    """

    if piece_type == PieceType.NONE:
        raise ValueError("Cannot create a piece of type NONE.")

    if not isinstance(color, Color):
        raise ValueError("Invalid piece color.")

    if not isinstance(piece_type, PieceType):
        raise ValueError("Invalid piece type.")

    if color == Color.WHITE:
        return int(piece_type)

    return int(piece_type) + BLACK_PIECE_OFFSET


def piece_color(piece: int) -> Color:
    """Returns the color of an encoded piece."""

    if piece == EMPTY:
        raise ValueError("Empty squares do not have a color.")

    if not is_valid_piece(piece):
        raise ValueError(f"Invalid piece encoding: {piece}")

    if piece >= BLACK_PIECE_OFFSET:
        return Color.BLACK

    return Color.WHITE


def piece_type(piece: int) -> PieceType:
    """Returns the type of an encoded piece."""

    if piece == EMPTY:
        return PieceType.NONE

    if not is_valid_piece(piece):
        raise ValueError(f"Invalid piece encoding: {piece}")

    return PieceType(piece & 7)


def is_valid_piece(piece: int) -> bool:
    """Checks whether an integer represents a valid piece."""

    return piece in {
        1, 2, 3, 4, 5, 6,
        9, 10, 11, 12, 13, 14
    }


# ============================================================
# PIECE SYMBOLS
# ============================================================

PIECE_SYMBOLS = {

    EMPTY: ".",

    make_piece(Color.WHITE, PieceType.PAWN): "P",
    make_piece(Color.WHITE, PieceType.KNIGHT): "N",
    make_piece(Color.WHITE, PieceType.BISHOP): "B",
    make_piece(Color.WHITE, PieceType.ROOK): "R",
    make_piece(Color.WHITE, PieceType.QUEEN): "Q",
    make_piece(Color.WHITE, PieceType.KING): "K",

    make_piece(Color.BLACK, PieceType.PAWN): "p",
    make_piece(Color.BLACK, PieceType.KNIGHT): "n",
    make_piece(Color.BLACK, PieceType.BISHOP): "b",
    make_piece(Color.BLACK, PieceType.ROOK): "r",
    make_piece(Color.BLACK, PieceType.QUEEN): "q",
    make_piece(Color.BLACK, PieceType.KING): "k",
}


def piece_symbol(piece: int) -> str:
    """Returns a human-readable symbol for a piece."""

    if not is_valid_piece(piece) and piece != EMPTY:
        raise ValueError(f"Invalid piece encoding: {piece}")

    return PIECE_SYMBOLS[piece]