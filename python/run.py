import re
import sys
import typing
from collections.abc import Sequence

from syntax_tree.action import TopLevel
from syntax_tree.action import Function
from syntax_tree.action import Context
from syntax_tree.action import CType
from syntax_tree.action import Parameter
from syntax_tree.action import TypeParameter

LINE_PATTERN = re.compile(r"^(\t*)(.*?)\s*(?:#\s*(.*))?$")
EMPTY_PATTERN = re.compile(r"^\s*$")
FUNCTION_PATTERN = re.compile(r"^([A-z][A-z\d_]*)\s*(?:\((.*)\))?\s*(?:->\s+(.*))?:\s*$")
PARAM_SPLIT_PATTERN = re.compile(r"\s*,\s*")

SCOPE_KEYWORDS = (
    'else',
    'if'
)


class SourceCodeError(Exception):
    pass


class LineParseError(SourceCodeError):
    def __init__(self, line: str, row: int) -> None:
        super().__init__(f"Line {row} could not be parsed!\n\t\"{line}\"")


def build_function(name: str, params: Sequence[str], return_type: str | None) -> Function:
    p: list[Parameter] = []
    for i, param in enumerate(params):
        match param.rsplit(maxsplit=1):
            case [t, n]:
                p.append(TypeParameter(CType(t), n))
            case [t]:
                p.append(TypeParameter(CType(t), f"param_{i}_unused_", True))
            case _:
                raise SourceCodeError("Param parse")
    return Function(name, CType("void"), *p)


def pop_context_to(indent: int, context_stack: list[Context]) -> None:
    while indent < len(context_stack) - 1:
        context_stack.pop()


def build_tree(file: typing.TextIO) -> TopLevel:
    top = TopLevel()

    context_stack: list[Context] = [top]

    for i, line in enumerate(file):
        if EMPTY_PATTERN.match(line):
            continue

        if line_match := LINE_PATTERN.match(line):
            # print(
            #     f"{repr(line_match[1]):10}"
            #     f"{repr(line_match[2]):40}"
            #     f"{repr(line_match[3]):40}"
            #     f"{repr(line_match[0]):50}"
            # )

            indent = len(line_match[1])

            pop_context_to(indent, context_stack)

            if function_match := FUNCTION_PATTERN.match(line_match[2]):
                # print(function_match[1], "|", function_match[2], "|", function_match[3])
                name, param_string, type_string = function_match[1], function_match[2], function_match[3]
                f = build_function(
                    name,
                    PARAM_SPLIT_PATTERN.split(param_string) if param_string else (),
                    type_string if type_string else None
                )
                context_stack[-1].add_function(f)
                context_stack.append(f)
                continue

        # should not be reached
        # raise LineParseError(line, i)

    return top


def main(*args: str) -> int:
    match args:
        case [_, filepath]:
            with open(filepath, 'r') as file:
                tree = build_tree(file)
            tree.write(sys.stdout)
        case [exec_name, *_]:
            print(f"Usage: {exec_name} SOURCE_FILE", file=sys.stderr)
            return 1
        case _:
            print("Invalid call to main function!", file=sys.stderr)
            return 2
    return 0


if __name__ == '__main__':
    exit(main(*sys.argv))
