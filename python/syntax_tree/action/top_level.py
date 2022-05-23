from typing import Mapping, Sequence, TextIO

from . import Action
from .action import Context
from .function import Function
from .type import Type


class TopLevel(Context):
    _actions: list[Action]
    _functions: dict[str, Function]
    _types: dict[str, Type]
    _functions_and_types: list[Function | Type]

    def __init__(self) -> None:
        self._actions = []
        self._functions = {}
        self._types = {}
        self._functions_and_types = []

    @property
    def actions(self) -> Sequence[Action]:
        return self._actions

    @property
    def functions(self) -> Mapping[str, Action]:
        return self._functions

    @property
    def types(self) -> Mapping[str, Action]:
        return self._types

    def add_function(self, action: Action) -> None:
        if not isinstance(action, Function):
            raise TypeError("Supplied argument is not a function!")
        self._functions[action.name] = action
        self._functions_and_types.append(action)

    def add_type(self, action: Action) -> None:
        if not isinstance(action, Type):
            raise TypeError("Supplied argument is not a Type!")
        self._types[action.name] = action
        self._functions_and_types.append(action)

    def add_action(self, action: Action) -> None:
        self._actions.append(action)

    def write(self, file: TextIO, indent: int) -> None:
        for ft in self._functions_and_types:
            ft.write(file, 0)
        for a in self.actions:
            a.write(file, 0)
