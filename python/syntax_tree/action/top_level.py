from typing import Mapping, Sequence, TextIO

from .action import Action
from .action import Context
from .action import DuplicateFunctionError
from .action import DuplicateTypeError
from .function import Function
from .type import Type


class TopLevel(Context):
    def __init__(self) -> None:
        self._actions: list[Action] = []
        self._functions: dict[str, Function] = {}
        self._types: dict[str, Type] = {}
        self._all_actions: list[Action] = []

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
        if action.name in self.functions:
            raise DuplicateFunctionError(action.name)
        self._functions[action.name] = action
        self._all_actions.append(action)

    def add_type(self, action: Action) -> None:
        if not isinstance(action, Type):
            raise TypeError("Supplied argument is not a Type!")
        if action.name in self.types:
            raise DuplicateTypeError(action.name)
        self._types[action.name] = action
        self._all_actions.append(action)

    def add_action(self, action: Action) -> None:
        self._actions.append(action)
        self._all_actions.append(action)

    def write(self, file: TextIO, indent: int = 0) -> None:
        for action in self._all_actions:
            action.write(file, 0)
