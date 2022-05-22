import re
import sys
import typing
import os.path

import actions

params_pattern = re.compile(r"^\((.*)\)$")
param_split_pattern = re.compile(r", ?")
param_ind_split_pattern = re.compile(r"\s+")


def add_function(
        line: str,
        i: int,
        context_stack: list[actions.Context],
        function_name: str,
        return_type: str,
        args: list[str]
) -> bool:
    function_context: actions.Function

    parameters: list[actions.Parameter] = []

    if args:
        param_str = " ".join(args)
        m2 = params_pattern.match(param_str)
        if not m2:
            print(
                f"Line {i} parameters incorrectly formatted:"
                f"\n{line.rstrip()}", file=sys.stderr
            )
            return False

        # params: list[tuple[str, str]] = []
        for param in param_split_pattern.split(m2[1]):
            match param_ind_split_pattern.split(param):
                case [t]:
                    parameters.append(actions.Parameter(f"unused_{t}_{len(parameters)}_", t, True))
                case [t, n]:
                    parameters.append(actions.Parameter(n, t))
                case _:
                    print(
                        f"Line {i} parameters incorrectly formatted:"
                        f"\n{line.rstrip()}", file=sys.stderr
                    )

    if return_type[-1] != ':':
        print(
            f"Line {i} function definition needs to end with ':':"
            f"\n{line.rstrip()}", file=sys.stderr
        )
        return False

    return_type = return_type[:-1]
    if return_type == "none":
        return_type = "void"

    function_context = actions.Function(i, function_name, return_type, tuple(parameters))
    # top_level.add_action(function_context)
    context_stack.append(function_context)
    return True


def add_normal_flow(
        context_stack: list[actions.Context],
        top_level: actions.TopLevel,
        line: str,
        i: int,
        args: list[str]
) -> bool:
    match args:
        case ["return", value]:
            if context_stack[-1] == top_level:
                print(
                    f"Line {i} return may not be used outside a function:"
                    f"\n{line.rstrip()}", file=sys.stderr
                )
                return False
            context_stack[-1].add_action(actions.Return(i, value))

        case ["return"]:
            if context_stack[-1] == top_level:
                print(
                    f"Line {i} return may not be used outside a function:"
                    f"\n{line.rstrip()}", file=sys.stderr
                )
                return False
            context_stack[-1].add_action(actions.Return(i))

        case ["C::>", *c_args]:
            c_cmd = " ".join(c_args)
            context_stack[-1].add_action(actions.CCommand(i, c_cmd))

        case _:
            print(f"Line {i} invalid:\n{line.rstrip()}", file=sys.stderr)
            return False
    return True


def pop_context_to(indent: int, context_stack: list[actions.Context], top_level: actions.TopLevel) -> None:
    while indent < len(context_stack) - 1:
        ctx = context_stack.pop()
        if isinstance(ctx, actions.Function) and not isinstance(ctx, actions.Main):
            top_level.add_action(ctx)


def transpile(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    comment_pattern = re.compile(r"^(\t*)#\s*(.*?)\n?$")
    action_pattern = re.compile(r"^(\t*)(\S.*?)\s*(?:#\s?(\S.*?))?\n?$")
    empty_pattern = re.compile(r"^\s*?\n?$")

    # param_pattern = re.compile(r"\w[_\w\d]*")

    top_level = actions.TopLevel(-1)
    context_stack: list[actions.Context] = [top_level]

    line: str
    for i, line in enumerate(input_file):
        # print(line, file=output_file, end='')
        if empty_pattern.match(line):
            continue

        if m := comment_pattern.match(line):
            context_stack[-1].add_action(actions.Comment(i, m[2]))
            continue

        if m := action_pattern.match(line):
            pop_context_to(len(m[1]), context_stack, top_level)

            match m[2].split():
                # special flow
                case ["main:"]:
                    main_context = actions.Main(i)
                    top_level.entry_point = main_context
                    context_stack.append(main_context)

                case [function_name, *args, "->", return_type]:
                    if not add_function(line, i, context_stack, function_name, return_type, args):
                        return

                case [value] if value[-1] == ':' and value[:-1] not in ("else",):
                    function_context = actions.Function(i, value[:-1])
                    # top_level.add_action(function_context)
                    context_stack.append(function_context)

                case ["C::import", "local", *args]:
                    filename = " ".join(args)
                    directive = actions.CPreprocessorDirective(i, f"include \"{filename}\"")
                    context_stack[-1].add_action(directive)
                case ["C::import", "global", *args]:
                    filename = " ".join(args)
                    directive = actions.CPreprocessorDirective(i, f"include <{filename}>")
                    context_stack[-1].add_action(directive)
                case ["C::import", *args]:
                    filename = " ".join(args)
                    directive = actions.CPreprocessorDirective(i, f"include <{filename}>")
                    context_stack[-1].add_action(directive)

                # normal flow
                case args:
                    if m[3]:
                        context_stack[-1].add_action(actions.Comment(i, m[3]))
                    if not add_normal_flow(context_stack, top_level, line, i, args):
                        return
            continue

        print(f"Line {i} did not match any pattern:\n{line.rstrip()}", file=sys.stderr)
        return

    pop_context_to(0, context_stack, top_level)

    top_level.write(output_file)


def transpile_files(input_filepath: str, output_filepath: str) -> None:
    with open(input_filepath, 'r') as i_file:
        with open(output_filepath, 'w') as o_file:
            transpile(i_file, o_file)


def main(*args: str) -> int:
    match args:
        case []:
            print("Invalid call to main!")
            return 1
        case [_, input_filepath]:
            output_filepath: str = os.path.splitext(input_filepath)[0]
            transpile_files(input_filepath, output_filepath)
            print(f"OK, {input_filepath}!")
        case [_, input_filepath, output_filepath]:
            transpile_files(input_filepath, output_filepath)
            print(f"OK, {input_filepath}, {output_filepath}!")
        case [executable_file, *_]:
            print(f"Usage: {executable_file} SOURCE_FILE [OUTPUT_FILE]")
    return 0


if __name__ == '__main__':
    exit(main(*sys.argv))
