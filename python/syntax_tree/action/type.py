from abc import ABC
from typing import TextIO

from .action import Action


class Type(Action, ABC):
    @property
    def name(self) -> str:
        raise NotImplementedError


class CType(Type):
    _name: str

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def write(self, file: TextIO, indent: int) -> None:
        pass
