"""
 Chess Engine
Pawn Move Generation

Generates pseudo-legal pawn moves for the side to move.

Legal king-safety filtering will be implemented separately.
"""

from chess_engine.core.constants import (
    is_valid_square,
)

from chess_engine.core.move import (
    Move,
    MoveFlag,
)

from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    make_piece,
    piece_color,
    piece_type,
)


PROMOTION_PIECES = (
    PieceType.QUEEN,
    PieceType.ROOK,
    PieceType.BISHOP,
    PieceType.KNIGHT,
)


def _add_pawn_move(
    moves,
    from_square,
    to_square,
    promotion=None,
    flags=MoveFlag.QUIET,
):
    """Adds a normal pawn move or all promotion variants."""

    if promotion is not None:

        for promotion_piece in PROMOTION_PIECES:

            moves.append(
                Move(
                    from_square=from_square,
                    to_square=to_square,
                    promotion=promotion_piece,
                    flags=flags | MoveFlag.PROMOTION,
                )
            )

    else:

        moves.append(
            Move(
                from_square=from_square,
                to_square=to_square,
                flags=flags,
            )
        )


def generate_pawn_moves(position):
    """
    Generates pseudo-legal pawn moves for the current player.

    Includes:
        - Single-square advances.
        - Double-square advances.
        - Diagonal captures.
        - Promotions.
        - Promotion captures.
        - En passant.

    Does not filter moves that leave the moving side's king
    in check. That belongs to the legality module.
    """

    board = position.board
    color = position.side_to_move

    moves = []

    if color == Color.WHITE:
        direction = 16
        starting_rank = 1
        promotion_rank = 7

    else:
        direction = -16
        starting_rank = 6
        promotion_rank = 0

    own_pawn = make_piece(color, PieceType.PAWN)
    enemy_color = color.opposite

    # Find every pawn belonging to the current player.
    for from_square in board.iter_squares():

        if board.get_piece(from_square) != own_pawn:
            continue

        current_rank = from_square >> 4

        # ====================================================
        # 1. FORWARD MOVEMENT
        # ====================================================

        one_step = from_square + direction

        if not is_valid_square(one_step):
            continue

        # A pawn cannot move forward into an occupied square.
        if board.get_piece(one_step) == EMPTY:

            # Promotion on the final rank.
            if (one_step >> 4) == promotion_rank:

                _add_pawn_move(
                    moves,
                    from_square,
                    one_step,
                    promotion=True,
                )

            else:

                _add_pawn_move(
                    moves,
                    from_square,
                    one_step,
                )

                # ============================================
                # 2. DOUBLE PAWN ADVANCE
                # ============================================

                if current_rank == starting_rank:

                    two_steps = from_square + (2 * direction)

                    if (
                        is_valid_square(two_steps)
                        and board.get_piece(two_steps) == EMPTY
                    ):

                        _add_pawn_move(
                            moves,
                            from_square,
                            two_steps,
                            flags=MoveFlag.DOUBLE_PAWN_PUSH,
                        )

        # ====================================================
        # 3. DIAGONAL CAPTURES
        # ====================================================

        for offset in (direction - 1, direction + 1):

            target = from_square + offset

            if not is_valid_square(target):
                continue

            target_piece = board.get_piece(target)

            if target_piece != EMPTY:

                # Pawns cannot capture their own pieces.
                if piece_color(target_piece) == color:
                    continue

                # The king is never captured in chess.
                if piece_type(target_piece) == PieceType.KING:
                    continue

                flags = MoveFlag.CAPTURE

                if (target >> 4) == promotion_rank:

                    _add_pawn_move(
                        moves,
                        from_square,
                        target,
                        promotion=True,
                        flags=flags,
                    )

                else:

                    _add_pawn_move(
                        moves,
                        from_square,
                        target,
                        flags=flags,
                    )

            # =================================================
            # 4. EN PASSANT
            # =================================================

            elif (
                target == position.en_passant_square
                and position.board.get_piece(target) == EMPTY
            ):




                # The captured pawn is not on the destination.
                # It is directly behind the en passant target.
                captured_square = target - direction

                if not is_valid_square(captured_square):
                    continue

                captured_piece = board.get_piece(captured_square)

                expected_enemy_pawn = make_piece(
                    enemy_color,
                    PieceType.PAWN,
                )

                # Verify that the actual opposing pawn exists.
                if captured_piece != expected_enemy_pawn:
                    continue

                moves.append(
                    Move(
                        from_square=from_square,
                        to_square=target,
                        flags=(
                            MoveFlag.CAPTURE
                            | MoveFlag.EN_PASSANT
                        ),
                    )
                )

    return moves