from abc import ABC
from collections.abc import Mapping, Sequence
from typing import TextIO, Union

from .action import Action, Context
from .type import Type


class Parameter(ABC):
    @property
    def type(self) -> Type:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def unused(self) -> bool:
        return False

    def formatted(self) -> str:
        return f"{self.type.name} {self.name}"


class TypeParameter(Parameter):
    def __init__(self, t: Type, n: str, unused: bool = False):
        self._type = t
        self._name = n
        self._unused = unused

    @property
    def type(self) -> Type:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @property
    def unused(self) -> bool:
        return self._unused


class Function(Context):
    def __init__(self, name: str, return_type: Type, *parameters: Parameter):
        self._name = name
        self._return_type = return_type
        self._parameters = parameters
        self._actions: list[Action] = []
        self._functions: dict[str, Function] = {}
        self._types: dict[str, Type] = {}
        self._functions_and_types: list[Type | Function] = []

    @property
    def actions(self) -> Sequence[Action]:
        return self._actions

    @property
    def functions(self) -> Mapping[str, Action]:
        return self._functions

    @property
    def types(self) -> Mapping[str, Action]:
        return self._types

    @property
    def name(self) -> str:
        return self._name

    @property
    def parameters(self) -> Sequence[Parameter]:
        return self._parameters

    @property
    def return_type(self) -> Type:
        return self._return_type

    def add_function(self, action: Action) -> None:
        if not isinstance(action, Function):
            raise TypeError("Supplied argument is not a function!")
        self._functions[action.name] = action
        self._functions_and_types.append(action)

    def add_type(self, action: Action) -> None:
        if not isinstance(action, Type):
            raise TypeError("Supplied argument is not a type!")
        self._types[action.name] = action
        self._functions_and_types.append(action)

    def add_action(self, action: Action) -> None:
        self._actions.append(action)

    def write(self, file: TextIO, indent: int) -> None:
        for ft in self._functions_and_types:
            ft.write(file, 0)

        print(
            "{} {}({})".format(
                self.return_type.name, self.name,
                ', '.join((p.formatted() for p in self.parameters))
            ),
            file=file
        )
        print("{", file=file)
        unused = " ".join(f"(void){p.name};" for p in self._parameters if p.unused)
        if unused:
            print("/* unused parameters */", file=file)
            print(unused, file=file)
        for action in self.actions:
            action.write(file, 1)
        print("}", file=file)
