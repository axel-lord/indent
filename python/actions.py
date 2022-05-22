import typing


def get_indent(size: int) -> str:
    return "\t" * size


class Action:
    line: int

    def __init__(self, line: int):
        self.line = line

    def write(self, output_file: typing.TextIO, indent: int) -> None:
        raise NotImplementedError


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

    def __init__(self, line: int) -> None:
        Context.__init__(self, line)
        self.entry_point = None

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
