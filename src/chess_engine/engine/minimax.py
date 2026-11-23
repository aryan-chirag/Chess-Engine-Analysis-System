"""Reference Minimax chess search implementation."""

from chess_engine.core.attacks import is_in_check
from chess_engine.core.pieces import Color
from chess_engine.engine.evaluation import evaluate
from chess_engine.engine.search_result import SearchResult
from chess_engine.movegen.legality import generate_legal_moves


MATE_SCORE = 100000


def _evaluate_white_perspective(position):
    """Convert side-to-move evaluation into White's perspective."""
    score = evaluate(position)

    if position.side_to_move == Color.WHITE:
        return score

    return -score


def _minimax(position, depth, nodes):
    """Recursively search a position using Minimax."""

    nodes[0] += 1

    legal_moves = generate_legal_moves(position)

    # Handle checkmate and stalemate.
    if not legal_moves:
        if is_in_check(position):
            if position.side_to_move == Color.WHITE:
                return -MATE_SCORE, None

            return MATE_SCORE, None

        return 0, None

    # Evaluate the position when the search depth is reached.
    if depth == 0:
        return _evaluate_white_perspective(position), None

    if position.side_to_move == Color.WHITE:
        best_score = float("-inf")
    else:
        best_score = float("inf")

    best_move = None

    for move in legal_moves:
        state = position.make_move(move)

        try:
            score, _ = _minimax(position, depth - 1, nodes)
        finally:
            position.undo_move(move, state)

        if position.side_to_move == Color.WHITE:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    return best_score, best_move


def minimax(position, depth: int) -> SearchResult:
    """Search a position using the reference Minimax algorithm."""

    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("Search depth must be a non-negative integer.")

    nodes = [0]

    score, best_move = _minimax(position, depth, nodes)

    # Return the score from the original side-to-move perspective.
    if position.side_to_move == Color.BLACK:
        score = -score

    return SearchResult(
        best_move=best_move,
        score=int(score),
        depth=depth,
        nodes=nodes[0],
    )