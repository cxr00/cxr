"""
This module deciphers base-ten permutative and descriptive sociomathematical strings
"""

roles = {
    "0": "Colloquialist",    # groks vibes
    "1": "Analyst",          # crunches "numbers"
    "2": "Catastrophist",    # expects the worst
    "3": "Interventionist",  # makes it work
    "4": "Contrarian",       # devil's advocate
    "5": "Interrogator",     # active decolloquialisation
    "6": "Therapist",        # active recolloquialisation
    "7": "Dreamer",          # recontextualises artfully
    "8": "Interpreter",      # makes sense of dreams
    "9": "Historian"         # indicates to clq
}

abbrevs = {
    "0": "clq",
    "1": "an",
    "2": "cat",
    "3": "intv",
    "4": "con",
    "5": "intr",
    "6": "th",
    "7": "dr",
    "8": "inp",
    "9": "hist"
}


class InvalidStringError(ValueError):
    """
    This error is thrown during instantiation of Clq instances, when the string submitted
    is not a valid sociomathematical string.

    When they are raised following Clq.arith, an UndefinedError is raised in turn
    """


class UndefinedError(ValueError):
    """
    This error is thrown when the result of a sociomathematical operation is undefined
    """


class Clq:
    """
    Flexible representations of sociomathematical teams via bimodal imbued strings
    """
    def __init__(self, string, abbrev=False):
        if len(string) < 2:
            raise InvalidStringError(f"Invalid sociomathematical string {string}; must have at least one role designation and a mode.")
        if len(string) > 11:
            raise InvalidStringError(f"Invalid sociomathematical string {string}; has {len(string)} characters but must be no more than 11 characters")

        self.string = string[:-1]
        for i, s in enumerate(self.string):
            if not (s.isnumeric() or s == "-"):
                raise InvalidStringError(f"Invalid sociomathematical string {string}; character {s} at index {i}; must be numeric or '-'")
        for s in self.string:
            c = self.string.count(s)
            if s != "-" and c > 1:
                raise InvalidStringError(f"Invalid sociomathematical string {string}; has {c} instances of {s}, when at most 1 is allowed.")

        self.mode = string[-1]
        if self.mode not in ("p", "d"):
            raise InvalidStringError(f"Invalid mode {self.mode}; must be 'p' or 'd'.")

        while len(self.string) > 1 and self.string[-1] == "-":  # Trim
            self.string = self.string[:-1]

        self.analysis = None
        self.to_compile = None
        self._create_report(abbrev)

    @staticmethod
    def __arith__(a, b, plus):
        """
        See socioarithmetic.md for details on inclusion and rejection

        :param plus: whether inclusion (True) or rejection (False) is performed
        """

        sc = a.compile()
        oc = b.compile()

        remap = {
            (t0 if plus else t1): (t1 if plus else t0) for t0, t1 in zip(oc[2::2], oc[3::2])
        }

        output = list(sc)
        for i in range(2, len(sc), 2):
            if output[i+1] in remap: # check - incl: f = r', rej: f = f'
                if not plus and output[i] == remap[output[i+1]]:  # check - rej: r = r'
                    output[i] = output[i+1] = "-" # remove - rej
                else:
                    output[i+1] = remap[output[i+1]]  # set - incl: f = f', rej: f = r'

        if plus:
            odds = output[2::2]
            evens = output[3::2]
            for k, v in remap.items():
                if k not in odds and v not in evens:  # add - incl
                    output += [k, v]
        try:
            return Clq.decompile("".join(output))
        except InvalidStringError:
            raise UndefinedError(f"The solution to {a} {'+' if plus else '-'} {b} is undefined; yields {''.join(output)}")

    @staticmethod
    def __metic__(a, b, convo):
        ac = a.compile()
        bc = b.compile()

        bc = {
            (t0 if convo else t1): (t1 if convo else t0) for t0, t1 in zip(bc[2::2], bc[3::2])
        }

        output = list(ac)
        funcs = output[3::2]
        for i in range(2, len(ac), 2):
            if output[i+1] in bc:  # check - iso: f = r', red: f = f'
                if convo:
                    output[i+1] = bc[output[i+1]]  # set - iso: f = f'
                else:
                    try:
                        k = 2 + funcs.index(bc[output[i+1]]) * 2  # find r'f''
                    except ValueError as exc:
                        raise UndefinedError(f"The solution to {a} / {b} is undefined; cannot reduce {output[i+1]} to {bc[output[i+1]]}")
                    output[k], output[k+1], output[i+1] = "-", "-", bc[output[i+1]] # red - remove: r'f''; set: f = r'
            else:
                if convo:
                    output[i+1] = output[i] = "-"  # remove - iso

        try:
            return Clq.decompile("".join(output))
        except InvalidStringError:
            raise UndefinedError(f"The solution to {a} {'*' if convo else '/'} {b} is undefined; yields {''.join(output)}")

    @staticmethod
    def decompile(s, mode="d"):
        """
        Decompile a sociomathematical string from normal form
        """
        s = s[2:]
        if all([st == "-" for st in s]):
            output = "-d"
        else:
            string_roles, string_funcs = [st for st in s[::2] if st != "-"], [st for st in s[1::2] if st != "-"]
            number_of_roles = sorted([(e, string_roles.count(e)) for e in string_roles], key=lambda x: x[1])
            number_of_functions = sorted([(e, string_funcs.count(e)) for e in string_funcs], key=lambda x: x[1])
            if number_of_roles[-1][1] > 1:
                raise InvalidStringError(f"Invalid string {''.join(s)}; contains multiple {roles[number_of_roles[-1][0]]} ({number_of_roles[-1][0]}) roles")
            if number_of_functions[-1][1] > 1:
                raise InvalidStringError(f"Invalid string {''.join(s)}; contains multiple {roles[number_of_functions[-1][0]]} ({number_of_functions[-1][0]}) functions")

            output = ["-"] * (max([int(st) for st in s[::2] if st.isnumeric()] + [0]) + 1)
            for n in range(0, len(s) - 1, 2):
                if s[n].isnumeric():
                    output[int(s[n])] = s[n+1]
            output = "".join(output) + "d"
        return Clq(output) if mode == "d" else Clq(output).convert()

    def __add__(self, other):
        # Also called "inclusion"
        if isinstance(other, str):
            return Clq.__arith__(self, Clq(other), True)
        elif isinstance(other, int):
            out = ["-"] * (other + 1) + ["d"]
            out[other] = str(other)
            return Clq.__arith__(self, Clq("".join(out)), True)
        return Clq.__arith__(self, other, True)

    def __sub__(self, other):
        # Also called "rejection"
        if isinstance(other, str):
            return Clq.__arith__(self, Clq(other), False)
        elif isinstance(other, int):
            out = ["-"] * (other + 1) + ["d"]
            out[other] = str(other)
            return Clq.__arith__(self, Clq("".join(out)), False)
        return Clq.__arith__(self, other, False)

    def __iadd__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def __mul__(self, other):
        # Also called "isolation"
        if isinstance(other, str):
            return Clq.__metic__(self, Clq(other), True)
        elif isinstance(other, int):
            out = ["-"] * (other + 1) + ["d"]
            out[other] = str(other)
            return Clq.__metic__(self, Clq("".join(out)), True)
        return Clq.__metic__(self, other, True)

    def __truediv__(self, other):
        # Also called "reduction"
        if isinstance(other, str):
            return Clq.__metic__(self, Clq(other), False)
        elif isinstance(other, int):
            out = ["-"] * (other + 1) + ["d"]
            out[other] = str(other)
            return Clq.__metic__(self, Clq("".join(out)), False)
        return Clq.__metic__(self, other, False)

    def __imul__(self, other):
        return self * other

    def __itruediv__(self, other):
        return self / other

    def __eq__(self, other):
        if self.mode != other.mode:
            return self == other.convert()
        if str(self) == str(other):
            return True
        return False

    def __repr__(self):
        # Yes, this isn't how it's typically used but it's otherwise useless
        output = "".join([self.string, self.mode])
        output += "\n* ".join(self.analysis)
        output += "\n"
        return output

    def __str__(self):
        return self.string + self.mode

    def _create_report(self, abbrev):
        """
        Create a human-readable long form report of the sociomathematical string
        """
        self.analysis = [":"]
        self.to_compile = []
        draw = abbrevs if abbrev else roles
        st = list(self.string)
        n = 0
        while st:
            s = st.pop(0)
            if s != "-":
                n = str(n)
                if s == n:
                    self.to_compile.append([s, s])
                    role = draw[s]
                else:
                    self.to_compile.append([s, n][::1 if self.mode == "p" else -1])
                    role = " ".join([draw[s], "->", draw[n]][::1 if self.mode == "p" else -1])
                self.analysis.append(role)
            n = int(n) + 1

    def compile(self, assessment=None):
        """
        Compile a sociomathematical string into normal form
        """
        if assessment is not None and assessment not in ("L-", "L+", "W-", "W+"):
            raise ValueError(f"Invalid assessment {assessment}; must be L or W, - or +")
        return (assessment or "__") + "".join(["".join(s) for s in sorted(self.to_compile, key=lambda x: x[1])])

    def convert(self):
        """
        Converts a string between permutative and descriptive modes
        """
        output_str = ["-"] * (max([int(s) for s in self.string if s != "-"] + [0]) + 1)

        for n, s in enumerate(self.string):
            if s != "-":
                output_str[int(s)] = str(n)

        return Clq("".join([*output_str, "d" if self.mode == "p" else "p"]))

    def is_involution(self):
        """
        Determine if a string has the same representation regardless of mode
        """
        return self.string == self.convert().string
