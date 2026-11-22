"""
Chess Engine
Position Management

Maintains the complete state of a chess position.
"""

from chess_engine.core.board import Board

from chess_engine.core.constants import (
    CastlingRights,
    is_valid_square,
)

from chess_engine.core.move import Move, MoveFlag

from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    make_piece,
    piece_color,
    piece_type,
)

from chess_engine.core.state import MoveState


class Position:

    def __init__(
        self,
        board=None,
        side_to_move=Color.WHITE,
        castling_rights=CastlingRights.ALL,
        en_passant_square=None,
        halfmove_clock=0,
        fullmove_number=1,
    ):

        self.board = board if board is not None else Board()

        self.side_to_move = Color(side_to_move)

        self.castling_rights = CastlingRights(castling_rights)

        self.en_passant_square = en_passant_square

        self.halfmove_clock = halfmove_clock

        self.fullmove_number = fullmove_number

    @classmethod
    def starting_position(cls):
        """Creates the standard initial chess position."""

        board = Board()

        back_rank = [
            PieceType.ROOK,
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.QUEEN,
            PieceType.KING,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
        ]

        # White back rank and pawns.
        for file, current_piece_type in enumerate(back_rank):

            board.set_piece(
                file,
                make_piece(Color.WHITE, current_piece_type)
            )

            board.set_piece(
                16 + file,
                make_piece(Color.WHITE, PieceType.PAWN)
            )

        # Black back rank and pawns.
        for file, current_piece_type in enumerate(back_rank):

            board.set_piece(
                112 + file,
                make_piece(Color.BLACK, current_piece_type)
            )

            board.set_piece(
                96 + file,
                make_piece(Color.BLACK, PieceType.PAWN)
            )

        return cls(board=board)

    def king_square(self, color: Color):
        """Returns the square occupied by the specified king."""

        target_piece = make_piece(color, PieceType.KING)

        for square in self.board.iter_squares():

            if self.board.get_piece(square) == target_piece:

                return square

        return None

    def make_move(self, move: Move) -> MoveState:
        """
        Executes a normal move, capture, promotion,
        double pawn push or en passant capture.

        Returns the previous position state for undo.
        """

        if not isinstance(move, Move):
            raise TypeError("Expected a Move object.")

        if move.is_castling:
            raise ValueError("Castling is not supported yet.")

        moving_piece = self.board.get_piece(move.from_square)

        if moving_piece == EMPTY:
            raise ValueError("Cannot move from an empty square.")

        if piece_color(moving_piece) != self.side_to_move:
            raise ValueError("Cannot move an opponent's piece.")

        moving_piece_type = piece_type(moving_piece)

        destination_piece = self.board.get_piece(move.to_square)

        # En passant validation.
        captured_square = move.to_square
        captured_piece = destination_piece

        if move.is_en_passant:

            if moving_piece_type != PieceType.PAWN:
                raise ValueError("Only pawns can capture en passant.")

            if move.to_square != self.en_passant_square:
                raise ValueError("Invalid en passant target square.")

            if destination_piece != EMPTY:
                raise ValueError("En passant destination must be empty.")

            direction = 16 if self.side_to_move == Color.WHITE else -16

            captured_square = move.to_square - direction

            captured_piece = self.board.get_piece(captured_square)

            if captured_piece != make_piece(
                self.side_to_move.opposite,
                PieceType.PAWN,
            ):
                raise ValueError("No opponent pawn available for en passant.")

            if not move.is_capture:
                raise ValueError("En passant must be marked as a capture.")

            # Verify that the pawn moves diagonally one square.
            if abs(move.to_square - move.from_square) not in (15, 17):
                raise ValueError("Invalid en passant movement.")

        else:

            # Validate ordinary captures.
            if move.is_capture:

                if destination_piece == EMPTY:
                    raise ValueError(
                        "Capture move must target an occupied square."
                    )

                if piece_color(destination_piece) == self.side_to_move:
                    raise ValueError("Cannot capture a friendly piece.")

                if piece_type(destination_piece) == PieceType.KING:
                    raise ValueError("A king cannot be captured.")

            elif destination_piece != EMPTY:

                raise ValueError(
                    "Quiet move cannot target an occupied square."
                )

        # Validate promotion.
        destination_rank = move.to_square >> 4

        promotion_rank = (
            7 if self.side_to_move == Color.WHITE else 0
        )

        reaches_promotion_rank = (
            moving_piece_type == PieceType.PAWN
            and destination_rank == promotion_rank
        )

        if reaches_promotion_rank and not move.is_promotion:
            raise ValueError(
                "Pawn reaching the final rank must promote."
            )

        if move.is_promotion:

            if moving_piece_type != PieceType.PAWN:
                raise ValueError("Only pawns can promote.")

            if not reaches_promotion_rank:
                raise ValueError(
                    "Promotion is only allowed on the final rank."
                )

        # Validate double pawn push.
        if move.is_double_pawn_push:

            if moving_piece_type != PieceType.PAWN:
                raise ValueError("Only pawns can move two squares.")

            starting_rank = (
                1 if self.side_to_move == Color.WHITE else 6
            )

            direction = (
                16 if self.side_to_move == Color.WHITE else -16
            )

            if (move.from_square >> 4) != starting_rank:
                raise ValueError(
                    "Double pawn push must start from the pawn's initial rank."
                )

            if move.to_square != move.from_square + (2 * direction):
                raise ValueError("Invalid double pawn push distance.")

            intermediate_square = move.from_square + direction

            if self.board.get_piece(intermediate_square) != EMPTY:
                raise ValueError(
                    "Cannot jump over an occupied square."
                )

            if destination_piece != EMPTY:
                raise ValueError(
                    "Double pawn push destination must be empty."
                )

        # Save the previous position state.
        previous_state = MoveState(
            moved_piece=moving_piece,
            captured_piece=captured_piece,
            captured_square=(
                captured_square if captured_piece != EMPTY else None
            ),
            previous_side_to_move=self.side_to_move,
            previous_castling_rights=self.castling_rights,
            previous_en_passant_square=self.en_passant_square,
            previous_halfmove_clock=self.halfmove_clock,
            previous_fullmove_number=self.fullmove_number,
        )

        # Remove the moving piece.
        self.board.set_piece(move.from_square, EMPTY)

        # Remove the captured piece.
        if captured_piece != EMPTY:
            self.board.set_piece(captured_square, EMPTY)

        # Handle promotion.
        if move.is_promotion:

            placed_piece = make_piece(
                self.side_to_move,
                move.promotion,
            )

        else:

            placed_piece = moving_piece

        self.board.set_piece(move.to_square, placed_piece)

        # Update the halfmove clock.
        if (
            moving_piece_type == PieceType.PAWN
            or captured_piece != EMPTY
        ):

            self.halfmove_clock = 0

        else:

            self.halfmove_clock += 1

        # Set en passant target after a double pawn push.
        self.en_passant_square = None

        if move.is_double_pawn_push:

            self.en_passant_square = (
                move.from_square
                + (
                    16 if self.side_to_move == Color.WHITE else -16
                )
            )

        # Increment fullmove number after Black's move.
        if self.side_to_move == Color.BLACK:
            self.fullmove_number += 1

        # Switch sides.
        self.side_to_move = self.side_to_move.opposite

        return previous_state







    

    def validate(self):
        """
        Checks fundamental position invariants.

        This is structural validation, not full chess legality.
        """

        if not self.board.validate_padding():
            raise ValueError("Invalid pieces found in 0x88 padding.")

        if not isinstance(self.side_to_move, Color):
            raise ValueError("Invalid side to move.")

        if self.halfmove_clock < 0:
            raise ValueError("Halfmove clock cannot be negative.")

        if self.fullmove_number < 1:
            raise ValueError("Fullmove number must be at least 1.")

        if self.en_passant_square is not None:

            if not is_valid_square(self.en_passant_square):
                raise ValueError("Invalid en passant square.")

            expected_rank = (
                5 if self.side_to_move == Color.WHITE else 2
            )

            if (self.en_passant_square >> 4) != expected_rank:
                raise ValueError("Invalid en passant target rank.")

        # A valid chess position must contain exactly one king
        # belonging to each side.
        white_kings = 0
        black_kings = 0

        for square in self.board.iter_squares():

            piece = self.board.get_piece(square)

            if piece == EMPTY:
                continue

            if piece_type(piece) == PieceType.KING:

                if piece == make_piece(Color.WHITE, PieceType.KING):
                    white_kings += 1

                else:
                    black_kings += 1

        if white_kings != 1:
            raise ValueError(
                "Position must contain exactly one white king."
            )

        if black_kings != 1:
            raise ValueError(
                "Position must contain exactly one black king."
            )

        return True

    def display(self):
        """Displays the current position."""

        print(self.board)

        print(f"\nSide to move: {self.side_to_move.name}")

        print(f"Castling rights: {self.castling_rights}")

        print(f"En passant square: {self.en_passant_square}")

        print(f"Halfmove clock: {self.halfmove_clock}")

        print(f"Fullmove number: {self.fullmove_number}")