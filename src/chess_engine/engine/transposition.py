"""Transposition table for storing previously searched positions."""

from dataclasses import dataclass
from enum import Enum, auto


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
    best_move: object | None
    generation: int


class TranspositionTable:

    def __init__(self, size=1_000_000):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Table size must be a positive integer.")

        self.size = size
        self.entries = [None] * size
        self.generation = 0
        self.entry_count = 0

    def _index(self, key):
        return key % self.size

    def probe(self, key):
        """Retrieve an entry if its complete key matches."""
        entry = self.entries[self._index(key)]

        if entry is not None and entry.key == key:
            return entry

        return None

    def store(self, key, depth, score, bound, best_move=None):
        """Store a search result using depth-preferred replacement."""

        if depth < 0:
            raise ValueError("Search depth cannot be negative.")

        if not isinstance(bound, Bound):
            raise ValueError("Invalid transposition table bound.")

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

        if existing is None:
            self.entries[index] = new_entry
            self.entry_count += 1
            return

        # Always replace an entry for the same position when:
        # - The new search is at least as deep.
        # - The new result is exact.
        if existing.key == key:
            if depth >= existing.depth or bound == Bound.EXACT:
                self.entries[index] = new_entry
            return

        # For collisions, prefer entries from a newer generation
        # or entries searched at least as deeply.
        if (
            existing.generation != self.generation
            or depth >= existing.depth
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
        """Return approximate table occupancy in per-mille."""
        if self.size == 0:
            return 0

        return min(1000, self.entry_count * 1000 // self.size)