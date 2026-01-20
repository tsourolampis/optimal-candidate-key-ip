from __future__ import annotations
from dataclasses import dataclass
from typing import Set, Iterable, TypeVar, FrozenSet

T = TypeVar("T")


@dataclass(frozen=True)
class FunctionalDependency:
    """
    Represents a functional dependency X -> Y,
    where X and Y are sets of attributes.

    By construction, Y \\ X is stored to avoid redundancy.
    """
    keys: FrozenSet[T]
    values: FrozenSet[T]

    def __init__(self, X: Iterable[T], Y: Iterable[T]):
        X_set = frozenset(X)
        Y_set = frozenset(Y) - X_set
        object.__setattr__(self, "keys", X_set)
        object.__setattr__(self, "values", Y_set)

    # --- Convenience constructors ---

    @classmethod
    def from_sets(cls, X: Set[T], Y: Set[T]) -> "FunctionalDependency":
        return cls(X, Y)

    @classmethod
    def from_lists(cls, X: Iterable[T], Y: Iterable[T]) -> "FunctionalDependency":
        return cls(X, Y)

    @classmethod
    def singleton(cls, x: T, y: T) -> "FunctionalDependency":
        return cls({x}, {y})

    @classmethod
    def empty_lhs(cls, y: T) -> "FunctionalDependency":
        return cls(set(), {y})

    @classmethod
    def lhs_to_singleton(cls, X: Iterable[T], y: T) -> "FunctionalDependency":
        return cls(X, {y})

    @classmethod
    def empty_to_set(cls, Y: Iterable[T]) -> "FunctionalDependency":
        return cls(set(), Y)

    # --- Accessors ---

    def lhs(self) -> FrozenSet[T]:
        return self.keys

    def rhs(self) -> FrozenSet[T]:
        return self.values

    # --- Ordering (for deterministic output / testing) ---

    def __lt__(self, other: "FunctionalDependency") -> bool:
        def _less(A: FrozenSet[T], B: FrozenSet[T]) -> bool:
            return len(A) < len(B) or sorted(A) < sorted(B)

        return (
            _less(self.keys, other.keys)
            or (self.keys == other.keys and _less(self.values, other.values))
        )

    def __repr__(self) -> str:
        def fmt(S):
            return "{" + ", ".join(map(str, S)) + "}"
        return f"FD : {fmt(self.keys)} ⟹ {fmt(self.values)}"

FD = FunctionalDependency

def get_all_vars(fds: Iterable[FunctionalDependency]) -> Set[T]:
    """
    Return the set of all attributes appearing in a collection of FDs.
    """
    all_keys: Set[T] = set()
    all_values: Set[T] = set()

    for fd in fds:
        all_keys |= set(fd.keys)
        all_values |= set(fd.values)

    return all_keys | all_values
