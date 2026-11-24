"""FEN parsing and generation."""

from chess_engine.core.board import Board
from chess_engine.core.constants import (
    CastlingRights,
    parse_square,
    square_name,
)
from chess_engine.core.pieces import (
    EMPTY,
    Color,
    PieceType,
    make_piece,
)
from chess_engine.core.position import Position


FEN_TO_PIECE = {
    "P": (Color.WHITE, PieceType.PAWN),
    "N": (Color.WHITE, PieceType.KNIGHT),
    "B": (Color.WHITE, PieceType.BISHOP),
    "R": (Color.WHITE, PieceType.ROOK),
    "Q": (Color.WHITE, PieceType.QUEEN),
    "K": (Color.WHITE, PieceType.KING),
    "p": (Color.BLACK, PieceType.PAWN),
    "n": (Color.BLACK, PieceType.KNIGHT),
    "b": (Color.BLACK, PieceType.BISHOP),
    "r": (Color.BLACK, PieceType.ROOK),
    "q": (Color.BLACK, PieceType.QUEEN),
    "k": (Color.BLACK, PieceType.KING),
}

PIECE_TO_FEN = {
    make_piece(color, piece_type): symbol
    for symbol, (color, piece_type) in FEN_TO_PIECE.items()
}

CASTLING_TO_FEN = {
    CastlingRights.WHITE_KINGSIDE: "K",
    CastlingRights.WHITE_QUEENSIDE: "Q",
    CastlingRights.BLACK_KINGSIDE: "k",
    CastlingRights.BLACK_QUEENSIDE: "q",
}


def parse_fen(fen: str) -> Position:
    """Creates a Position from a six-field FEN string."""

    if not isinstance(fen, str):
        raise ValueError("FEN must be a string.")

    fields = fen.split()

    if len(fields) != 6:
        raise ValueError("FEN must contain exactly six fields.")

    placement, active_color, castling, en_passant, halfmove, fullmove = fields

    board = Board()

    # Parse piece placement.
    ranks = placement.split("/")

    if len(ranks) != 8:
        raise ValueError("FEN piece placement must contain eight ranks.")

    for fen_rank, rank_text in enumerate(ranks):

        file = 0
        board_rank = 7 - fen_rank

        for symbol in rank_text:

            if symbol.isdigit():

                if symbol not in "12345678":
                    raise ValueError("Invalid empty-square count in FEN.")

                file += int(symbol)

            elif symbol in FEN_TO_PIECE:

                if file >= 8:
                    raise ValueError("Too many squares in FEN rank.")

                color, piece_type = FEN_TO_PIECE[symbol]
                piece = make_piece(color, piece_type)

                square = board_rank * 16 + file
                board.set_piece(square, piece)

                file += 1

            else:
                raise ValueError(f"Invalid FEN piece symbol: {symbol}")

            if file > 8:
                raise ValueError("Too many squares in FEN rank.")

        if file != 8:
            raise ValueError("Every FEN rank must describe eight squares.")

    # Validate kings.
    white_kings = 0
    black_kings = 0

    for square in board.iter_squares():

        piece = board.get_piece(square)

        if piece == make_piece(Color.WHITE, PieceType.KING):
            white_kings += 1

        elif piece == make_piece(Color.BLACK, PieceType.KING):
            black_kings += 1

    if white_kings != 1 or black_kings != 1:
        raise ValueError("FEN must contain exactly one king of each color.")

    # Parse active color.
    if active_color == "w":
        side_to_move = Color.WHITE

    elif active_color == "b":
        side_to_move = Color.BLACK

    else:
        raise ValueError("Invalid FEN active color.")

    # Parse castling rights.
    castling_rights = CastlingRights.NONE

    if castling != "-":

        if not castling or any(symbol not in "KQkq" for symbol in castling):
            raise ValueError("Invalid FEN castling rights.")

        if len(set(castling)) != len(castling):
            raise ValueError("Duplicate FEN castling rights.")

        for right, symbol in CASTLING_TO_FEN.items():

            if symbol in castling:
                castling_rights |= right

    # Parse en passant square.
    if en_passant == "-":
        en_passant_square = None

    else:
        try:
            en_passant_square = parse_square(en_passant)
        except ValueError as error:
            raise ValueError("Invalid FEN en passant square.") from error

        expected_rank = "6" if side_to_move == Color.WHITE else "3"

        if en_passant[1] != expected_rank:
            raise ValueError("Invalid FEN en passant rank.")

        if board.get_piece(en_passant_square) != EMPTY:
            raise ValueError("FEN en passant target must be empty.")

    # Parse move counters.
    try:
        halfmove_clock = int(halfmove)
        fullmove_number = int(fullmove)

    except ValueError as error:
        raise ValueError("Invalid FEN move counters.") from error

    if halfmove_clock < 0:
        raise ValueError("Halfmove clock cannot be negative.")

    if fullmove_number < 1:
        raise ValueError("Fullmove number must be at least one.")

    position = Position(
        board=board,
        side_to_move=side_to_move,
        castling_rights=castling_rights,
        en_passant_square=en_passant_square,
        halfmove_clock=halfmove_clock,
        fullmove_number=fullmove_number,
    )

    return position


def generate_fen(position: Position) -> str:
    """Converts a Position into a six-field FEN string."""

    ranks = []

    for rank in range(7, -1, -1):

        empty_count = 0
        rank_text = ""

        for file in range(8):

            square = rank * 16 + file
            piece = position.board.get_piece(square)

            if piece == EMPTY:
                empty_count += 1

            else:

                if empty_count:
                    rank_text += str(empty_count)
                    empty_count = 0

                if piece not in PIECE_TO_FEN:
                    raise ValueError(f"Invalid piece encoding: {piece}")

                rank_text += PIECE_TO_FEN[piece]

        if empty_count:
            rank_text += str(empty_count)

        ranks.append(rank_text)

    placement = "/".join(ranks)

    active_color = (
        "w"
        if position.side_to_move == Color.WHITE
        else "b"
    )

    castling = "".join(
        symbol
        for right, symbol in CASTLING_TO_FEN.items()
        if position.castling_rights & right
    )

    if not castling:
        castling = "-"

    en_passant = (
        square_name(position.en_passant_square)
        if position.en_passant_square is not None
        else "-"
    )

    return (
        f"{placement} "
        f"{active_color} "
        f"{castling} "
        f"{en_passant} "
        f"{position.halfmove_clock} "
        f"{position.fullmove_number}"
    )