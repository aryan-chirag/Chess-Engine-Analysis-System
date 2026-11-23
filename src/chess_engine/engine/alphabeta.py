"""Alpha-Beta Pruning chess search implementation."""

from chess_engine.core.attacks import is_in_check
from chess_engine.engine.evaluation import evaluate
from chess_engine.engine.minimax import MATE_SCORE
from chess_engine.engine.search_result import SearchResult
from chess_engine.movegen.legality import generate_legal_moves


def _alphabeta(position, depth, alpha, beta, nodes):
    """Recursively search a position using Alpha-Beta pruning."""

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
            child_score, _ = _alphabeta(
                position,
                depth - 1,
                -beta,
                -alpha,
                nodes,
            )
        finally:
            position.undo_move(move, state)

        score = -child_score

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)

        # Stop searching when this branch cannot improve the result.
        if alpha >= beta:
            break

    return best_score, best_move


def alphabeta(position, depth: int) -> SearchResult:
    """Search a position using Alpha-Beta pruning."""

    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("Search depth must be a non-negative integer.")

    nodes = [0]

    score, best_move = _alphabeta(
        position,
        depth,
        float("-inf"),
        float("inf"),
        nodes,
    )

    return SearchResult(
        best_move=best_move,
        score=int(score),
        depth=depth,
        nodes=nodes[0],
    )