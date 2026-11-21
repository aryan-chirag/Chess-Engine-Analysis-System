"""
Chess Engine
Move Representation

Defines the structure and metadata of a chess move.
"""

from dataclasses import dataclass
from enum import IntFlag

from chess_engine.core.constants import (
    is_valid_square,
    square_name,
)

from chess_engine.core.pieces import PieceType


# ============================================================
# MOVE FLAGS
# ============================================================

class MoveFlag(IntFlag):

    QUIET = 0

    CAPTURE = 1

    DOUBLE_PAWN_PUSH = 2

    EN_PASSANT = 4

    CASTLING = 8

    PROMOTION = 16


# ============================================================
# PROMOTION PIECES
# ============================================================

PROMOTION_PIECES = {
    PieceType.QUEEN,
    PieceType.ROOK,
    PieceType.BISHOP,
    PieceType.KNIGHT,
}


PROMOTION_SYMBOLS = {
    PieceType.QUEEN: "q",
    PieceType.ROOK: "r",
    PieceType.BISHOP: "b",
    PieceType.KNIGHT: "n",
}


# ============================================================
# MOVE CLASS
# ============================================================

@dataclass(frozen=True, slots=True)
class Move:

    from_square: int

    to_square: int

    promotion: PieceType | None = None

    flags: MoveFlag = MoveFlag.QUIET

    def __post_init__(self):

        # Validate starting square.
        if not is_valid_square(self.from_square):
            raise ValueError(
                f"Invalid starting square: {self.from_square}"
            )

        # Validate destination square.
        if not is_valid_square(self.to_square):
            raise ValueError(
                f"Invalid destination square: {self.to_square}"
            )

        # A move cannot start and end on the same square.
        if self.from_square == self.to_square:
            raise ValueError(
                "Starting and destination squares cannot be identical."
            )

        # Validate flags.
        if not isinstance(self.flags, MoveFlag):
            raise ValueError("Invalid move flags.")

        known_flags = (
            MoveFlag.CAPTURE
            | MoveFlag.DOUBLE_PAWN_PUSH
            | MoveFlag.EN_PASSANT
            | MoveFlag.CASTLING
            | MoveFlag.PROMOTION
        )

        if int(self.flags) & ~int(known_flags):
            raise ValueError("Unknown move flag.")

        # Validate promotion.
        if self.promotion is not None:

            if not isinstance(self.promotion, PieceType):
                raise ValueError("Invalid promotion piece.")

            if self.promotion not in PROMOTION_PIECES:
                raise ValueError(
                    "Promotion must be to a queen, rook, bishop or knight."
                )

        # Promotion flag and promotion piece must agree.
        has_promotion_flag = bool(
            self.flags & MoveFlag.PROMOTION
        )

        if has_promotion_flag != (self.promotion is not None):
            raise ValueError(
                "Promotion flag and promotion piece must agree."
            )

        # En passant is always a capture.
        if self.flags & MoveFlag.EN_PASSANT:

            if not self.flags & MoveFlag.CAPTURE:
                raise ValueError(
                    "En passant must also have the capture flag."
                )

        # Castling cannot be a capture.
        if self.flags & MoveFlag.CASTLING:

            if self.flags & (
                MoveFlag.CAPTURE
                | MoveFlag.PROMOTION
                | MoveFlag.EN_PASSANT
                | MoveFlag.DOUBLE_PAWN_PUSH
            ):
                raise ValueError(
                    "Invalid combination of castling flags."
                )

        # A double pawn push cannot also be a capture.
        if self.flags & MoveFlag.DOUBLE_PAWN_PUSH:

            if self.flags & (
                MoveFlag.CAPTURE
                | MoveFlag.PROMOTION
                | MoveFlag.EN_PASSANT
                | MoveFlag.CASTLING
            ):
                raise ValueError(
                    "Invalid combination of double pawn push flags."
                )

    # ========================================================
    # MOVE PROPERTIES
    # ========================================================

    @property
    def is_capture(self) -> bool:

        return bool(self.flags & MoveFlag.CAPTURE)

    @property
    def is_promotion(self) -> bool:

        return bool(self.flags & MoveFlag.PROMOTION)

    @property
    def is_en_passant(self) -> bool:

        return bool(self.flags & MoveFlag.EN_PASSANT)

    @property
    def is_castling(self) -> bool:

        return bool(self.flags & MoveFlag.CASTLING)

    @property
    def is_double_pawn_push(self) -> bool:

        return bool(self.flags & MoveFlag.DOUBLE_PAWN_PUSH)

    # ========================================================
    # UCI REPRESENTATION
    # ========================================================

    def to_uci(self) -> str:

        """
        Converts the move into UCI coordinate notation.

        Examples:
            e2e4
            g1f3
            e7e8q
        """

        result = (
            square_name(self.from_square)
            + square_name(self.to_square)
        )

        if self.promotion is not None:

            result += PROMOTION_SYMBOLS[self.promotion]

        return result

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __str__(self):

        return self.to_uci()