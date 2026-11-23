import random

from chess_engine.core.position import Position
from chess_engine.core.zobrist import compute_zobrist_hash
from chess_engine.movegen.legality import generate_legal_moves


def test_random_games_preserve_incremental_zobrist_hash():
    rng = random.Random(20261123)

    number_of_games = 10
    max_plies_per_game = 100

    for _ in range(number_of_games):
        position = Position.starting_position()
        history = []

        for _ in range(max_plies_per_game):
            legal_moves = generate_legal_moves(position)

            # Stop if the game has reached a terminal position.
            if not legal_moves:
                break

            move = rng.choice(legal_moves)
            move_state = position.make_move(move)

            history.append((move, move_state))

            # Incremental hash must match a complete recomputation.
            expected_hash = compute_zobrist_hash(position)

            assert position.zobrist_hash == expected_hash

        # Undo every move and verify that the hash is restored.
        for move, move_state in reversed(history):
            position.undo_move(move, move_state)

            expected_hash = compute_zobrist_hash(position)

            assert position.zobrist_hash == expected_hash

        # The complete undo sequence must restore the starting position.
        starting_position = Position.starting_position()

        assert position.zobrist_hash == starting_position.zobrist_hash
        assert position.board.squares == starting_position.board.squares
        assert position.side_to_move == starting_position.side_to_move