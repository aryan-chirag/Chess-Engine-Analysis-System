"""
Chess Engine
Board Representation

Implements the 0x88 mailbox board.
"""

from chess_engine.core.constants import (
    MAILBOX_SIZE,
    is_valid_square,
    square_name,
)

from chess_engine.core.pieces import (
    EMPTY,
    is_valid_piece,
    piece_symbol,
)


class Board:

    def __init__(self):

        # 128 entries for the 0x88 representation.
        self.squares = [EMPTY] * MAILBOX_SIZE

    def get_piece(self, square: int) -> int:
        """Returns the piece occupying a square."""

        if not is_valid_square(square):
            raise ValueError(f"Invalid board square: {square}")

        return self.squares[square]

    def set_piece(self, square: int, piece: int):
        """Places a piece on a square."""

        if not is_valid_square(square):
            raise ValueError(f"Invalid board square: {square}")

        if not is_valid_piece(piece) and piece != EMPTY:
            raise ValueError(f"Invalid piece encoding: {piece}")

        self.squares[square] = piece

    def clear(self):
        """Removes all pieces from the board."""

        self.squares = [EMPTY] * MAILBOX_SIZE

    def iter_squares(self):
        """Iterates over all 64 valid chessboard squares."""

        for rank in range(8):

            for file in range(8):

                square = rank * 16 + file

                yield square

    def count_pieces(self) -> int:
        """Returns the total number of pieces on the board."""

        return sum(
            self.squares[square] != EMPTY
            for square in self.iter_squares()
        )

    def validate_padding(self) -> bool:
        """
        Ensures all invalid 0x88 mailbox positions remain empty.
        """

        for square in range(MAILBOX_SIZE):

            if not is_valid_square(square):

                if self.squares[square] != EMPTY:
                    return False

        return True

    def display(self) -> str:
        """Returns a human-readable chessboard."""

        lines = []

        lines.append("  +------------------------+")

        for rank in range(7, -1, -1):

            row = f"{rank + 1} |"

            for file in range(8):

                square = rank * 16 + file

                piece = self.get_piece(square)

                row += f" {piece_symbol(piece)}"

            row += " |"

            lines.append(row)

        lines.append("  +------------------------+")
        lines.append("    a b c d e f g h")

        return "\n".join(lines)

    def __str__(self):

        return self.display()