# Chess-Engine-Analysis-System
An independently developed chess engine and comprehensive analysis platform featuring intelligent move evaluation, explainable AI decision-making, interactive search visualization, game analysis, and performance benchmarking. Building, understanding and advancing chess intelligence.



```text
Chess-Engine-and-Analysis-System/
│
├── src/
│   └── chess_platform/
│       │
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── constants.py
│       │   ├── pieces.py
│       │   ├── board.py
│       │   ├── move.py
│       │   ├── position.py
│       │   ├── state.py
│       │   ├── zobrist.py
│       │   └── attacks.py
│       │
│       ├── movegen/
│       │   ├── __init__.py
│       │   ├── generator.py
│       │   ├── pawns.py
│       │   ├── knights.py
│       │   ├── sliders.py
│       │   ├── kings.py
│       │   ├── legality.py
│       │   └── castling.py
│       │
│       ├── rules/
│       │   ├── __init__.py
│       │   ├── game_status.py
│       │   ├── draw_rules.py
│       │   ├── repetition.py
│       │   └── validation.py
│       │
│       ├── notation/
│       │   ├── __init__.py
│       │   ├── fen.py
│       │   ├── pgn.py
│       │   ├── san.py
│       │   └── uci.py
│       │
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── search.py
│       │   ├── minimax.py
│       │   ├── negamax.py
│       │   ├── alphabeta.py
│       │   ├── iterative.py
│       │   ├── quiescence.py
│       │   ├── move_ordering.py
│       │   ├── transposition.py
│       │   ├── evaluation.py
│       │   ├── evaluation_terms.py
│       │   ├── principal_variation.py
│       │   ├── time_manager.py
│       │   └── search_result.py
│       │
│       ├── optimization/
│       │   ├── __init__.py
│       │   ├── killer_moves.py
│       │   ├── history_heuristic.py
│       │   ├── null_move.py
│       │   ├── late_move_reduction.py
│       │   ├── aspiration.py
│       │   └── pvs.py
│       │
│       ├── protocols/
│       │   ├── __init__.py
│       │   │
│       │   ├── uci/
│       │   │   ├── __init__.py
│       │   │   ├── parser.py
│       │   │   ├── handler.py
│       │   │   └── commands.py
│       │   │
│       │   └── api/
│       │       ├── __init__.py
│       │       └── engine_service.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   ├── game.py
│       │   ├── session.py
│       │   ├── analysis.py
│       │   ├── tournament.py
│       │   │
│       │   ├── api/
│       │   │   └── __init__.py
│       │   │
│       │   └── services/
│       │       └── __init__.py
│       │
│       ├── interface/
│       │   ├── __init__.py
│       │   │
│       │   ├── desktop/
│       │   │   └── __init__.py
│       │   │
│       │   └── web/
│       │       └── __init__.py
│       │
│       └── data/
│           ├── __init__.py
│           ├── opening_book.py
│           ├── tablebase.py
│           └── datasets.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── board/
│   │   ├── analysis/
│   │   ├── visualization/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── cpp_engine/
│   ├── CMakeLists.txt
│   │
│   ├── include/
│   │   └── chess_engine/
│   │       ├── board.hpp
│   │       ├── move.hpp
│   │       ├── position.hpp
│   │       ├── move_generator.hpp
│   │       ├── evaluation.hpp
│   │       ├── search.hpp
│   │       └── transposition.hpp
│   │
│   ├── src/
│   │   ├── main.cpp
│   │   ├── board.cpp
│   │   ├── move.cpp
│   │   ├── position.cpp
│   │   ├── move_generator.cpp
│   │   ├── evaluation.cpp
│   │   ├── search.cpp
│   │   └── transposition.cpp
│   │
│   ├── tests/
│   │   ├── test_board.cpp
│   │   ├── test_movegen.cpp
│   │   └── test_search.cpp
│   │
│   └── benchmarks/
│       └── benchmark_engine.cpp
│
├── tests/
│   │
│   ├── unit/
│   │   ├── test_board.py
│   │   ├── test_position.py
│   │   ├── test_move.py
│   │   ├── test_pawns.py
│   │   ├── test_knights.py
│   │   ├── test_sliders.py
│   │   ├── test_kings.py
│   │   ├── test_castling.py
│   │   ├── test_en_passant.py
│   │   ├── test_promotion.py
│   │   ├── test_check.py
│   │   ├── test_fen.py
│   │   └── test_evaluation.py
│   │
│   ├── integration/
│   │   ├── test_complete_games.py
│   │   ├── test_game_state.py
│   │   ├── test_engine_search.py
│   │   └── test_uci.py
│   │
│   ├── perft/
│   │   ├── test_initial_position.py
│   │   ├── test_special_positions.py
│   │   └── positions/
│   │
│   ├── regression/
│   │   └── test_known_bugs.py
│   │
│   └── fixtures/
│       ├── positions.py
│       └── games.py
│
├── benchmarks/
│   │
│   ├── move_generation/
│   ├── search/
│   ├── evaluation/
│   ├── memory/
│   ├── cpp_comparison/
│   └── reports/
│
├── experiments/
│   │
│   ├── evaluation_tuning/
│   ├── self_play/
│   ├── tournaments/
│   └── machine_learning/
│       ├── nnue/
│       └── reinforcement_learning/
│
├── scripts/
│   ├── run_engine.py
│   ├── run_perft.py
│   ├── run_benchmark.py
│   └── run_tournament.py
│
├── docs/
│   │
│   ├── research/
│   │   │
│   │   ├── chess_rules/
│   │   │   ├── 01_board_and_pieces.md
│   │   │   ├── 02_pawn_movement.md
│   │   │   ├── 03_en_passant.md
│   │   │   ├── 04_castling.md
│   │   │   ├── 05_promotion.md
│   │   │   ├── 06_check_and_king_safety.md
│   │   │   ├── 07_draw_rules.md
│   │   │   └── 08_game_termination.md
│   │   │
│   │   ├── chess_engine/
│   │   │   ├── 01_board_representation.md
│   │   │   ├── 02_move_generation.md
│   │   │   ├── 03_attack_maps.md
│   │   │   ├── 04_make_unmake.md
│   │   │   ├── 05_position_identity.md
│   │   │   └── 06_perft_testing.md
│   │   │
│   │   └── references/
│   │       ├── official_rules.md
│   │       ├── technical_references.md
│   │       └── test_positions.md
│   │
│   ├── architecture/
│   ├── algorithms/
│   ├── benchmarks/
│   ├── decisions/
│   └── development/
│
├── assets/
│   ├── diagrams/
│   └── screenshots/
│
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── lint.yml
│
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
└── SECURITY.md
```

