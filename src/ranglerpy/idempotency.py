from __future__ import annotations

from abc import ABC, abstractmethod


class IdempotencyStore(ABC):
    @abstractmethod
    def claim(self, key: str) -> bool:
        """Return True if the key was newly claimed, False if it already exists."""


class InMemoryIdempotencyStore(IdempotencyStore):
    def __init__(self) -> None:
        self._keys: set[str] = set()

    def claim(self, key: str) -> bool:
        if key in self._keys:
            return False
        self._keys.add(key)
        return True
