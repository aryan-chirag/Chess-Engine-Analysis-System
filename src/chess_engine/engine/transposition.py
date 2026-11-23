"""Transposition table for storing previously searched positions."""

from dataclasses import dataclass
from enum import Enum, auto

from chess_engine.core.move import Move


class Bound(Enum):
    EXACT = auto()
    LOWERBOUND = auto()
    UPPERBOUND = auto()


@dataclass(slots=True)
class TTEntry:
    key: int
    depth: int
    score: int
    bound: Bound
    best_move: Move | None
    generation: int


class TranspositionTable:

    def __init__(self, size=1_000_000):
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("Table size must be a positive integer.")

        self.size = size
        self.entries = [None] * size
        self.generation = 0
        self.entry_count = 0

    def _validate_key(self, key):
        if isinstance(key, bool) or not isinstance(key, int):
            raise ValueError("Transposition key must be an integer.")

        if not 0 <= key < (1 << 64):
            raise ValueError("Transposition key must be an unsigned 64-bit integer.")

    def _index(self, key):
        return key % self.size

    def probe(self, key):
        """Retrieve an entry if its complete key matches."""

        self._validate_key(key)

        entry = self.entries[self._index(key)]

        if entry is not None and entry.key == key:
            return entry

        return None

    def store(self, key, depth, score, bound, best_move=None):
        """Store a search result using depth and generation preferences."""

        self._validate_key(key)

        if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
            raise ValueError("Search depth must be a non-negative integer.")

        if isinstance(score, bool) or not isinstance(score, int):
            raise ValueError("Search score must be an integer.")

        if not isinstance(bound, Bound):
            raise ValueError("Invalid transposition table bound.")

        if best_move is not None and not isinstance(best_move, Move):
            raise ValueError("Best move must be a Move or None.")

        index = self._index(key)
        existing = self.entries[index]

        new_entry = TTEntry(
            key=key,
            depth=depth,
            score=score,
            bound=bound,
            best_move=best_move,
            generation=self.generation,
        )

        # Empty slot.
        if existing is None:
            self.entries[index] = new_entry
            self.entry_count += 1
            return

        # Same position.
        if existing.key == key:

            replace = (
                depth > existing.depth
                or (
                    depth == existing.depth
                    and bound == Bound.EXACT
                    and existing.bound != Bound.EXACT
                )
            )

            if replace:
                self.entries[index] = new_entry
            else:
                # Preserve the deeper search result, but refresh
                # its generation and retain a useful move.
                existing.generation = self.generation

                if best_move is not None:
                    existing.best_move = best_move

            return

        # Different position: prefer deeper entries.
        # At equal depth, prefer the entry from the newer generation.
        if (
            depth > existing.depth
            or (
                depth == existing.depth
                and existing.generation != self.generation
            )
        ):
            self.entries[index] = new_entry

    def new_search(self):
        """Advance the generation for replacement management."""
        self.generation += 1

    def clear(self):
        """Remove every stored entry."""
        self.entries = [None] * self.size
        self.generation = 0
        self.entry_count = 0

    def hashfull(self):
        """Return approximate occupied table capacity in per-mille."""

        return min(1000, self.entry_count * 1000 // self.size)