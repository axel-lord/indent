from abc import ABC
from collections.abc import Mapping, Sequence
from typing import Optional, TextIO


class Action(ABC):
    _level: int
    _context: 'Context'

    @property
    def line(self) -> int:
        return self._level if hasattr(self, "_level") else -1

    @line.setter
    def line(self, value: int) -> None:
        self._level = value

    @property
    def context(self) -> Optional['Context']:
        return self._context if hasattr(self, '_context') else None

    @context.setter
    def context(self, value: 'Context') -> None:
        self._context = value

    def write(self, file: TextIO, indent: int) -> None:
        raise NotImplementedError


class Context(Action, ABC):
    @property
    def actions(self) -> Sequence[Action]:
        raise NotImplementedError

    @property
    def functions(self) -> Mapping[str, Action]:
        raise NotImplementedError

    @property
    def types(self) -> Mapping[str, Action]:
        raise NotImplementedError

    def add_action(self, action: Action) -> None:
        raise NotImplementedError

    def add_function(self, action: Action) -> None:
        raise NotImplementedError

    def add_type(self, action: Action) -> None:
        raise NotImplementedError
