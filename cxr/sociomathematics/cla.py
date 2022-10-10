"""
Command line arithmetic performed with left-associativity

This process eliminates the need to use Jupyter Notebooks for lengthier arithmetic
"""

from cxr.sociomathematics.clq import Clq, UndefinedError, InvalidStringError


def show_help():
    print()
    print("Type in equations (eg 10d + 4p, __2013 - -01d)")
    print("h/help: view this message")
    print("d: descriptive mode")
    print("p: permutative mode")
    print("v: view mode: see full report of a particular string")
    print("c: complation mode: see compilation of a particular string")
    print()


def div_up(s, mode):
    l = list(s)
    clqs = []
    ops = []
    spool = None
    normal_form_marker = None
    state = 2

    def is_op(c):
        return c in ("+", "-", "*", "/")

    def is_mode(c):
        return c in ("p", "d")

    try:
        for ls in l + [" "]:
            if state == 0:  # Seeking operation, normal form, or standard form
                if ls == "_":
                    normal_form_marker = ls
                    state = 1
                    spool = list()
                elif is_op(ls):
                    ops.append(ls)
                    state = 2
                elif ls.isnumeric():
                    spool = list()
                    spool.append(ls)
                    state = 1
            elif state == 1:  # Seeking end of string
                if ls == " ":
                    if normal_form_marker is None:
                        raise ValueError(f"Cannot determine operand type, as spool {''.join(spool)} contains no mode or assessment")
                    clqs.append(Clq.decompile(normal_form_marker + "".join(spool)))
                    spool = None
                    normal_form_marker = None
                    state = 0
                elif ls.isnumeric() or ls == "-":
                    spool.append(ls)
                elif is_op(ls):
                    if normal_form_marker is None:
                        raise ValueError(f"Cannot determine operand type, as spool {''.join(spool)} contains no mode or assessment")
                    clqs.append(Clq.decompile(normal_form_marker + "".join(spool)))
                    spool = None
                    normal_form_marker = None
                    ops.append(ls)
                    state = 0
                elif is_mode(ls):
                    spool.append(ls)
                    clqs.append(Clq("".join(spool)))
                    state = 0
            elif state == 2:  # have op
                if ls == "_":
                    normal_form_marker = ls
                    state = 1
                    spool = list()
                elif ls.isnumeric() or ls == "-":
                    spool = list()
                    spool.append(ls)
                    state = 1
    except InvalidStringError as exc:
        print()
        print(type(exc).__name__, "-", exc)
        print()
        return

    try:
        output = clqs.pop(0)
        while clqs:
            op = ops.pop(0)
            if op == "+":
                output += clqs.pop(0)
            elif op == "-":
                output -= clqs.pop(0)
            elif op == "*":
                output *= clqs.pop(0)
            elif op == "/":
                output /= clqs.pop(0)
        print("\n", "=", output if mode == output.mode else output.convert())
        print()
    except UndefinedError as exc:
        print()
        print(type(exc).__name__, "-", exc)
        print()

def run():
    mode = "d"
    inp = input(f"{mode} >>> ")
    while inp:
        if inp in ("p", "d", "v", "c"):
            mode = inp
        elif inp in ("h", "help"):
            show_help()
        else:
            try:
                if mode == "v":
                    if inp.startswith("_"):
                        print()
                        print(repr(Clq.decompile(inp)))
                        print()
                    else:
                        print()
                        print(repr(Clq(inp)))
                        print()
                elif mode == "c":
                    print()
                    print(Clq(inp).compile())
                    print()
                else:
                    div_up(inp, mode)
            except InvalidStringError as exc:
                print()
                print(type(exc).__name__, "-", exc)
                print()
            except ValueError as exc:
                print()
                print(type(exc).__name__, "-", exc)
                print()
        inp = input(f"{mode} >>> ")


if __name__ == "__main__":
    run()