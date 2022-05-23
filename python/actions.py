import typing
from abc import ABC


def get_indent(size: int) -> str:
    return "\t" * size


class Action(ABC):
    line: int

    def __init__(self, line: int):
        self.line = line

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        raise NotImplementedError


class Type(Action, ABC):
    supports_unsigned: bool

    @property
    def name(self) -> str:
        raise NotImplementedError


class Struct(Type):
    def write(self, output_file: typing.TextIO, indent: int) -> None:
        pass

    def __init__(self, line: int, name: str):
        Action.__init__(self, line)
        self.__name = name

    @property
    def name(self) -> str:
        return f"struct {self.__name}"


class CNativeType(Type):
    @property
    def name(self) -> str:
        return self.__name

    def __init__(self, line: int, name: str, supports_unsigned: bool = False):
        self.__name = name
        self.supports_unsigned = supports_unsigned
        Action.__init__(self, line)

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        pass


class Context(Action):
    actions: list[Action]

    def __init__(self, line: int) -> None:
        self.actions = []
        Action.__init__(self, line)

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        print(f"{get_indent(indent)}{{", file=output_file)

        for action in self.actions:
            action.write(output_file, indent + 1)

        print(f"{get_indent(indent)}}}", file=output_file, end='\n\n')

    def add_action(self, action: Action) -> None:
        self.actions.append(action)


class TopLevel(Context):
    entry_point: typing.Optional['Main']

    types: dict[str, Type]
    functions: dict[str, 'Function']

    def __init__(self, line: int) -> None:
        Context.__init__(self, line)
        self.types = {
            n: CNativeType(-1, n, True)
            for n in
            {"char", "int", "short", "long"}
        }
        self.types.update({
            n: CNativeType(-1, n)
            for n in
            {"double", "float"}
        })
        self.functions = {}
        self.entry_point = None
        breakpoint()

    def add_action(self, action: Action) -> None:
        if isinstance(action, Function):
            self.functions[action.name] = action
        if isinstance(action, Type):
            self.types[action.name] = action
        super(TopLevel, self).add_action(action)

    def write(self, output_file: typing.TextIO, indent: int = 0) -> None:
        for action in self.actions:
            action.write(output_file, indent)

        if self.entry_point:
            self.entry_point.write(output_file, indent)


class Parameter:
    unused: bool
    name: str
    parameter_type: str

    def __init__(self, name: str, parameter_type: str, unused: bool = False):
        self.parameter_type = parameter_type
        self.name = name
        self.unused = unused

    def __getitem__(self, item: int) -> str:
        match item:
            case int(0):
                return self.parameter_type
            case int(1):
                return self.name
            case int(_):
                raise IndexError(f"Invalid index {item}!")
            case _:
                raise TypeError(f"Invalid index type {type(item)}!")


class Function(Context):
    __name: str
    __return_type: str
    __parameters: tuple[Parameter, ...]

    def __init__(self, line: int, name: str, return_type: str = "void", parameters: tuple[Parameter, ...] = ()) -> None:
        Context.__init__(self, line)
        self.__name = name
        self.__return_type = return_type
        self.__parameters = parameters

        for p in parameters:
            if p.unused:
                self.actions.append(CCommand(-1, f"(void){p.name}"))

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        print(
            "{} {}({})".format(
                self.__return_type, self.__name,
                ', '.join(
                    (f'{p.parameter_type} {p.name}' for p in self.__parameters)
                )
            ),
            file=output_file
        )
        Context.write(self, output_file, indent)

    @property
    def name(self) -> str:
        return self.__name


class Main(Function):
    def __init__(self, line: int) -> None:
        Function.__init__(self, line, "main", "int")


class Comment(Action):
    message: str

    def __init__(self, line: int, message: str) -> None:
        Action.__init__(self, line)
        self.message = message

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        if not self.message:
            return
        print(f"{get_indent(indent)}/* {self.message} */", file=output_file)


class CPreprocessorDirective(Action):
    value: str

    def __init__(self, line: int, value: str = ""):
        Action.__init__(self, line)
        self.value = value

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        if not self.value:
            return
        print(f"#{self.value}", file=output_file)


class CCommand(Action):
    cmd: str

    def __init__(self, line: int, cmd: str = ""):
        Action.__init__(self, line)
        self.cmd = cmd

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        if not self.cmd:
            return
        print(f"{get_indent(indent)}{self.cmd};", file=output_file)


class Return(Action):
    value: str

    def __init__(self, line: int, value: str = "void") -> None:
        Action.__init__(self, line)
        self.value = value

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        if self.value == "void":
            print(f"{get_indent(indent)}return;", file=output_file)
        else:
            print(f"{get_indent(indent)}return {self.value};", file=output_file)
