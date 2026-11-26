"""Transposition table for storing previously searched positions."""

from dataclasses import dataclass
from enum import Enum, auto

from chess_engine.core.move import Move


DEFAULT_SEARCH_CONFIG = (True, 16)


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
    search_config: tuple[bool, int] = DEFAULT_SEARCH_CONFIG


class TranspositionTable:

    def __init__(self, size=1_000_000):
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("Table size must be a positive integer.")

        self.size = size
        self.entries = [None] * size
        self.generation = 0
        self.entry_count = 0

        self.reset_stats()

    def reset_stats(self):
        """Reset performance counters without clearing stored entries."""

        self.probes = 0
        self.hits = 0
        self.misses = 0
        self.cutoffs = 0
        self.stores = 0
        self.replacements = 0

        self.depth_hits = 0
        self.shallow_hits = 0
        self.exact_hits = 0
        self.bound_hits = 0
        self.move_ordering_hits = 0

    def record_cutoff(self):
        """Record a cutoff caused by a transposition table bound."""

        self.cutoffs += 1

    def _validate_key(self, key):
        if isinstance(key, bool) or not isinstance(key, int):
            raise ValueError("Transposition key must be an integer.")

        if not 0 <= key < (1 << 64):
            raise ValueError(
                "Transposition key must be an unsigned 64-bit integer."
            )

    @staticmethod
    def _validate_search_config(search_config):
        if (
            not isinstance(search_config, tuple)
            or len(search_config) != 2
        ):
            raise ValueError("Invalid search configuration.")

        use_quiescence, max_quiescence_ply = search_config

        if not isinstance(use_quiescence, bool):
            raise ValueError("Invalid quiescence setting.")

        if (
            isinstance(max_quiescence_ply, bool)
            or not isinstance(max_quiescence_ply, int)
            or max_quiescence_ply < 0
        ):
            raise ValueError("Invalid maximum quiescence ply.")

        if use_quiescence and max_quiescence_ply < 1:
            raise ValueError(
                "Quiescence Search requires a positive maximum ply."
            )

        if not use_quiescence and max_quiescence_ply != 0:
            raise ValueError(
                "Disabled Quiescence Search must use maximum ply zero."
            )

    def _index(self, key):
        return key % self.size

    def probe(self, key, search_config=DEFAULT_SEARCH_CONFIG):
        """Retrieve an entry if its key and search configuration match."""

        self._validate_key(key)
        self._validate_search_config(search_config)

        self.probes += 1

        entry = self.entries[self._index(key)]

        if (
            entry is not None
            and entry.key == key
            and entry.search_config == search_config
        ):
            self.hits += 1
            return entry

        self.misses += 1
        return None

    def store(
        self,
        key,
        depth,
        score,
        bound,
        best_move=None,
        search_config=DEFAULT_SEARCH_CONFIG,
    ):
        """Store a search result using depth and generation preferences."""

        self._validate_key(key)
        self._validate_search_config(search_config)

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
            search_config=search_config,
        )

        if existing is None:
            self.entries[index] = new_entry
            self.entry_count += 1
            self.stores += 1
            return

        if existing.key == key:

            # Results from different search configurations are incompatible.
            if existing.search_config != search_config:
                self.entries[index] = new_entry
                self.stores += 1
                self.replacements += 1
                return

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
                self.stores += 1
                self.replacements += 1

            else:
                existing.generation = self.generation

                if best_move is not None:
                    existing.best_move = best_move

            return

        if (
            depth > existing.depth
            or (
                depth == existing.depth
                and existing.generation != self.generation
            )
        ):
            self.entries[index] = new_entry
            self.stores += 1
            self.replacements += 1

    def new_search(self):
        """Advance the generation for replacement management."""

        self.generation += 1

    def clear(self):
        """Remove all entries and reset statistics."""

        self.entries = [None] * self.size
        self.generation = 0
        self.entry_count = 0
        self.reset_stats()

    def hashfull(self):
        """Return approximate occupied table capacity in per-mille."""

        return min(1000, self.entry_count * 1000 // self.size)

    def get_stats(self):
        """Return a snapshot of transposition table statistics."""

        return {
            "probes": self.probes,
            "hits": self.hits,
            "misses": self.misses,
            "cutoffs": self.cutoffs,
            "stores": self.stores,
            "replacements": self.replacements,
            "depth_hits": self.depth_hits,
            "shallow_hits": self.shallow_hits,
            "exact_hits": self.exact_hits,
            "bound_hits": self.bound_hits,
            "move_ordering_hits": self.move_ordering_hits,
            "hashfull": self.hashfull(),
            "entries": self.entry_count,
            "capacity": self.size,
            "hit_rate": (
                self.hits / self.probes * 100
                if self.probes else 0.0
            ),
        }