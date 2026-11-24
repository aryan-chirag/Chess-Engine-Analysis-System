"""Chess positions used for search benchmarking."""

from chess_engine.notation.fen import parse_fen


BENCHMARK_POSITIONS = {
    "Starting Position": (
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/"
        "RNBQKBNR w KQkq - 0 1"
    ),

    "Tactical Middlegame": (
        "r3k2r/ppp2ppp/2n1bn2/3qp3/3P4/"
        "2P1PN2/PP3PPP/RNBQKB1R w KQkq - 0 8"
    ),

    "Quiet Middlegame": (
        "r2q1rk1/pp2bppp/2n1pn2/2pp4/"
        "3P4/2P1PN2/PP1NBPPP/R2Q1RK1 w - - 0 10"
    ),

    "Promotion Position": (
        "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"
    ),

    "Endgame": (
        "8/5pk1/6p1/8/8/6P1/5PK1/8 w - - 0 1"
    ),
}


def get_benchmark_positions():
    """Return named benchmark positions."""

    return {
        name: parse_fen(fen)
        for name, fen in BENCHMARK_POSITIONS.items()
    }