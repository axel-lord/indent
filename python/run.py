import sys

from syntax_tree import action

if __name__ == '__main__':
    top = action.TopLevel()

    top.add_function(
        action.Function(
            "Main", action.CType("int"),
            action.TypeParameter(action.CType("int"), "argc", True),
            action.TypeParameter(action.CType("char**"), "argv", True)
        )
    )

    top.write(sys.stdout, 0)
