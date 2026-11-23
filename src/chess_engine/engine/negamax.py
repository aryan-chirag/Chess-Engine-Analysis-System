"""Reference Negamax chess search implementation."""

from chess_engine.core.attacks import is_in_check
from chess_engine.engine.evaluation import evaluate
from chess_engine.engine.minimax import MATE_SCORE
from chess_engine.engine.search_result import SearchResult
from chess_engine.movegen.legality import generate_legal_moves


def _negamax(position, depth, nodes):
    """Recursively search a position using Negamax."""

    nodes[0] += 1

    legal_moves = generate_legal_moves(position)

    # Handle checkmate and stalemate.
    if not legal_moves:
        if is_in_check(position):
            return -MATE_SCORE, None

        return 0, None

    # Evaluate the position when the search depth is reached.
    if depth == 0:
        return evaluate(position), None

    best_score = float("-inf")
    best_move = None

    for move in legal_moves:
        state = position.make_move(move)

        try:
            child_score, _ = _negamax(position, depth - 1, nodes)
        finally:
            position.undo_move(move, state)

        score = -child_score

        if score > best_score:
            best_score = score
            best_move = move

    return best_score, best_move


def negamax(position, depth: int) -> SearchResult:
    """Search a position using the Negamax algorithm."""

    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("Search depth must be a non-negative integer.")

    nodes = [0]

    score, best_move = _negamax(position, depth, nodes)

    return SearchResult(
        best_move=best_move,
        score=int(score),
        depth=depth,
        nodes=nodes[0],
    )