"""Unified pseudo-legal move generation."""

from chess_engine.movegen.pawns import generate_pawn_moves
from chess_engine.movegen.knights import generate_knight_moves
from chess_engine.movegen.sliders import generate_bishop_moves, generate_rook_moves, generate_queen_moves
from chess_engine.movegen.kings import generate_king_moves
from chess_engine.movegen.castling import generate_castling_moves


def generate_pseudo_legal_moves(position):
    """Generate all pseudo-legal moves for the side to move."""
    moves = []
    moves.extend(generate_pawn_moves(position))
    moves.extend(generate_knight_moves(position))
    moves.extend(generate_bishop_moves(position))
    moves.extend(generate_rook_moves(position))
    moves.extend(generate_queen_moves(position))
    moves.extend(generate_king_moves(position))
    moves.extend(generate_castling_moves(position))
    return moves


# Convenient shorter alias used by callers.
generate_pseudo_moves = generate_pseudo_legal_moves
