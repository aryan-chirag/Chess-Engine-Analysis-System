"""Stores the information required to undo a chess move."""

from dataclasses import dataclass

from chess_engine.core.constants import CastlingRights, is_valid_square
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    is_valid_piece,
)


@dataclass(frozen=True, slots=True)
class MoveState:
    """Snapshot of position information before a move is executed."""

    moved_piece: int
    captured_piece: int = EMPTY
    captured_square: int | None = None

    previous_side_to_move: Color = Color.WHITE
    previous_castling_rights: CastlingRights = CastlingRights.NONE
    previous_en_passant_square: int | None = None
    previous_halfmove_clock: int = 0
    previous_fullmove_number: int = 1
    previous_zobrist_hash: int | None = None

    def __post_init__(self):
        if not is_valid_piece(self.moved_piece):
            raise ValueError("MoveState must contain a valid moved piece.")

        if self.captured_piece != EMPTY and not is_valid_piece(
            self.captured_piece
        ):
            raise ValueError("Invalid captured piece.")

        if not isinstance(self.previous_side_to_move, Color):
            raise ValueError("Invalid previous side to move.")

        if not isinstance(
            self.previous_castling_rights, CastlingRights
        ):
            raise ValueError("Invalid previous castling rights.")

        if self.previous_en_passant_square is not None:
            if not is_valid_square(self.previous_en_passant_square):
                raise ValueError("Invalid previous en passant square.")

        if self.captured_piece == EMPTY:
            if self.captured_square is not None:
                raise ValueError(
                    "Captured square must be None when no piece was captured."
                )
        elif self.captured_square is None:
            raise ValueError(
                "Captured square is required when a piece was captured."
            )

        if self.captured_square is not None:
            if not is_valid_square(self.captured_square):
                raise ValueError("Invalid captured square.")

        if self.previous_halfmove_clock < 0:
            raise ValueError("Halfmove clock cannot be negative.")

        if self.previous_fullmove_number < 1:
            raise ValueError("Fullmove number must be at least 1.")

        if self.previous_zobrist_hash is not None:
            if not isinstance(self.previous_zobrist_hash, int):
                raise ValueError("Invalid Zobrist hash.")