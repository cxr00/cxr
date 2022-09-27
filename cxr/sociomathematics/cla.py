# Command line arithmetic performed via left-associativity
from cxr.sociomathematics.clq import Clq, UndefinedError, InvalidStringError



def div_up(s, mode):
    l = list(s)
    clqs = []
    ops = []
    spool = None
    assessment = None
    state = 2

    def is_op(c):
        return c in ("+", "-", "*", "/")

    def is_mode(c):
        return c in ("p", "d")

    try:
        for ls in l + [" "]:
            if state == 0:  # Seeking operation, normal form, or standard form
                if ls == "_":
                    assessment = ls
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
                if assessment is not None and ls in ("_"):
                    assessment = assessment + ls
                elif ls == " ":
                    assessment = assessment or "__"
                    clqs.append(Clq.decompile(assessment + "".join(spool)))
                    spool = None
                    assessment = ""
                    state = 0
                elif ls.isnumeric() or ls == "-":
                    spool.append(ls)
                elif is_op(ls):
                    assessment = assessment or "__"
                    clqs.append(Clq.decompile(assessment + "".join(spool)))
                    spool = None
                    assessment = None
                    ops.append(ls)
                    state = 0
                elif is_mode(ls):
                    spool.append(ls)
                    clqs.append(Clq("".join(spool)))
                    state = 0
            elif state == 2:  # have op
                if ls == "_":
                    assessment = ls
                    state = 1
                    spool = list()
                elif ls.isnumeric() or ls == "-":
                    spool = list()
                    spool.append(ls)
                    state = 1
    except InvalidStringError as exc:
        print(exc)
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
        print(exc)
        print()

def run():
    mode = "d"
    inp = input(f"{mode} >>> ")
    while inp:
        if inp in ("p", "d"):
            mode = inp
        else:
            div_up(inp, mode)
        inp = input(f"{mode} >>> ")


if __name__ == "__main__":
    run()