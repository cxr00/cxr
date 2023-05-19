"""
An implementation of arbitrary base arithmetic up to base 64.

Tridozenal numbers include:

Equality testing
Rounding
Addition & Subtraction
Multiplication & Division
N-th Root using Newton Iteration
Pi and e
Logarithms
"""

# Default value to round to when place is not set (-1)
round_to = 18

# Determines whether the log shows during __pow__ when power is Tridozenal
log_power = True

# Decides the default base for a Tridozenal.
default_base = 3

# The base-64 characters used for 62 and 63
chars64 = "+/"

def set_chars64(new_chars: str):
    if len(new_chars) != 2:
        raise ValueError(f"Can only submit two characters for chars64")
    if new_chars[0] == new_chars[1]:
        raise ValueError(f"Characters cannot be equal")
    for i in range(62):
        char = str(Tridozenal([i], base=64))
        if char == new_chars[0]:
            raise ValueError(f"Cannot use {new_chars}: {new_chars[0]} is character used for 0-61")
        if char == new_chars[1]:
            raise ValueError(f"Cannot use {new_chars}: {new_chars[1]} is character used for 0-61")

    global chars64
    chars64 = new_chars

"""
The Seq class implements basic sequence arithmetic that
enables floating-point computations in an arbitrary base.
"""
std_l = 30


def check_seq(f):
    """
    Auxiliary method which checks inputs to Seq methods

    Ensures that the numerical input is translated to a Seq object

    :param f: the function to be decorated
    """
    def wrapper(self, o=None):
        if o is None:
            return f(self, Seq())
        elif isinstance(o, (int, float)):
            return f(self, Seq([o]))
        elif isinstance(o, list):
            for e in o:
                if not isinstance(e, (int, float)):
                    raise ValueError(f"Unsupported type {type(o)}")
            return f(self, Seq(o))
        elif isinstance(o, Seq):
            return f(self, o)
        else:
            raise ValueError(f"Unsupported type {type(o)}")

    wrapper.__name__ = f.__name__
    return wrapper


class Seq:
    """
    The Seq class consists of the ring of sequences, with
    addition and convolution as operations.
    """

    def __init__(self, seq=None):
        if seq is None:
            self.seq = []
        elif isinstance(seq, (int, float)):
            self.seq = [int(seq) if int(seq) == seq else seq]
        elif isinstance(seq, (list, tuple)):
            self.seq = [int(v) if int(v) == v else v for v in seq]
        elif isinstance(seq, Seq):
            self.seq = seq.seq
        else:
            raise ValueError(f"Unsupported type {type(seq)}")

    @check_seq
    def __add__(self, o):
        if isinstance(o, int):
            return self + Seq(o)
        elif isinstance(o, Seq):
            l = max(len(self), len(o))
            out = [self[k] + o[k] for k in range(l)]
            return Seq(out)
        else:
            raise ValueError(f"Unsupported type {type(o)}")

    @check_seq
    def __contains__(self, i):
        return all(i[k] == self[k] for k in range(len(i)))

    @check_seq
    def __eq__(self, o):
        if len(self.trim()) != len(o.trim()):
            return False
        return all(self[k] == o[k] for k in range(len(self.trim())))

    @check_seq
    def __ge__(self, o):
        return self.seq >= o.seq

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.seq[i] if len(self) > i >= 0 else 0
        elif isinstance(i, slice):
            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else len(self)
            step = i.step if i.step is not None else 1
            return Seq([self.seq[k] if len(self) > k >= 0 else 0 for k in range(start, stop, step)])

    @check_seq
    def __gt__(self, o):
        return self.seq > o.seq

    @check_seq
    def __iadd__(self, o):
        return self + o

    @check_seq
    def __imul__(self, o):
        return self * o

    @check_seq
    def __isub__(self, o):
        return self - o

    def __iter__(self):
        return iter(self.seq)

    @check_seq
    def __le__(self, o):
        return self.seq <= o.seq

    def __len__(self):
        return len(self.seq)

    @check_seq
    def __lt__(self, o):
        return self.seq < o.seq

    @check_seq
    # def __k_mul__(self, o):
    def __mul__(self, o):
        if len(self) < 50 and len(o) < 50:
            return self.__school_mul__(o)
        m = min(len(self), len(o))
        if m == 1:
            g = self if len(self) != 1 else o
            p = self if g != self else o
            p = p[0]
            r = [e * p for e in g]
            return Seq(r)
        else:
            m //= 2
            x0, x1 = self[:m], self[m:]
            y0, y1 = o[:m], o[m:]

            # Resort to "school" method for small sequences
            if m < 25:
                func = Seq.__school_mul__
            else:
                func = Seq.__mul__

            z2 = func(x1, y1)
            z0 = func(x0, y0)
            z1 = func((x1 + x0), (y1 + y0)) - z2 - z0

            pt0 = [0] * m * 2
            pt0.extend(z2.seq)
            pt0 = Seq(pt0)
            pt1 = [0] * m
            pt1.extend(z1.seq)
            pt1 = Seq(pt1)
            return pt0 + pt1 + z0

    @check_seq
    # def __mul__(self, o):
    def __school_mul__(self, o):
        l = len(self) + len(o) - 1
        r = [sum(self[k] * o[x - k] for k in range(x + 1)) for x in range(l)]
        return Seq(r)

    def __pow__(self, power, modulo=None):
        a = Seq(self)
        out = Seq(1)
        for k in range(power):
            out *= a
        return out

    @check_seq
    def __radd__(self, o):
        return self + o

    @check_seq
    def __rmul__(self, o):
        return self * o

    @check_seq
    def __rsub__(self, o):
        return self.neg() + o

    def __setitem__(self, key: int, value: (int, float)):
        if len(self) > key >= 0:
            self.seq[key] = value

    @check_seq
    def __sub__(self, o):
        return self + o.neg()

    def __str__(self):
        return ", ".join([str(n) for n in self.trim().seq])

    def concat(self, other: "Seq"):
        return Seq(self.seq + other.seq)

    def neg(self):
        """
        Converts the given sequence to its additive inverse
        """
        out = [-k for k in self]
        return Seq(out)

    def reverse(self):
        return Seq(self.seq[::-1])

    def trim(self, to_zero: bool=False):
        """
        Removes trailing zeroes from a sequence
        """
        out = list(self.seq)
        while len(out) > (0 if to_zero else 1) and out[-1] == 0:
            out.pop(-1)
        return Seq(out)


def convert_int(num: int, base: int):
    """
    Converts primitive ints to the given base

    Only used in __init__ to escape base 10,
    hence why it is disfluent.
    """
    output = []
    if num < 0:
        num = abs(num)
    while num > 0:
        modulo = num % base
        output.append(modulo)
        num = num // base

    return output


class Tridozenal:
    def __init__(self, integer=None, mantissa=None, base: int=-1, is_negative: bool=False):
        if not integer:
            integer = Seq(0)
        if not mantissa:
            mantissa = Seq(0)
        if base == -1:
            base = default_base

        self.is_negative = is_negative

        if isinstance(integer, Seq):
            if len(integer) == 0:
                self.integer = Seq(0)
            else:
                self.integer = integer
        elif isinstance(integer, (int, float)):
            if integer < 0:
                self.is_negative = True
            self.integer = Seq(convert_int(integer, base))
        elif isinstance(integer, list):
            self.integer = Seq(integer[::-1])
        else:
            raise ValueError(f"Invalid integer type {type(integer).__name__}; must be int, float, list or Seq")

        if isinstance(mantissa, Seq):
            if len(mantissa) == 0:
                self.mantissa = Seq()
            else:
                self.mantissa = mantissa
        elif isinstance(mantissa, (int, list)):
            self.mantissa = Seq(mantissa)
        else:
            raise ValueError(f"Invalid mantissa type {type(mantissa).__name__}; must be int, float, list or Seq")

        if 2 <= base <= 64:
            self.base = base
        else:
            raise ValueError("Base must be between 2 and 64")

        # No unresolved numbers
        self.__resolve()

        # Default rounding behavior
        self.round(place=round_to)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            if other < 0:
                return self + Tridozenal(-other, 0, self.base, True)
            else:
                return self + Tridozenal(other, 0, self.base)
        elif isinstance(other, Tridozenal):
            if self.is_negative:
                if other.is_negative:
                    return Tridozenal(self.integer + other.integer, self.mantissa + other.mantissa, self.base, True)
                else:
                    if self.abs() > other:
                        return Tridozenal(self.integer - other.integer, self.mantissa - other.mantissa, self.base, True)
                    else:
                        return Tridozenal(other.integer - self.integer, other.mantissa - self.mantissa, self.base)
            elif other.is_negative:
                if other.abs() > self:
                    return Tridozenal(other.integer - self.integer, other.mantissa - self.mantissa, self.base, True)
                else:
                    return Tridozenal(self.integer - other.integer, self.mantissa - other.mantissa, self.base)
            else:
                return Tridozenal(self.integer + other.integer, self.mantissa + other.mantissa, self.base)
        else:
            raise ValueError("Can only add Tridozenals together")

    def __eq__(self, other):
        if isinstance(other, Tridozenal):
            self.trim()
            return self.integer == other.integer \
                and self.mantissa == other.mantissa \
                and self.base == other.base \
                and self.is_negative == other.is_negative
        else:
            return False

    def __floordiv__(self, other):
        if isinstance(other, int):
            return self // Tridozenal(other, 0, self.base)
        elif isinstance(other, Tridozenal):
            if other.base != self.base:
                raise ValueError(f"Base mismatch: {self.base} and {other.base}")

            power = [other.abs()]
            current_power = 0
            while power[-1] < self.abs():
                power.append(power[-1] * self.base)
                current_power += 1

            tmp = self.abs()
            output = [0 for _ in range(len(tmp.integer))]
            while tmp >= other.abs():
                if tmp < power[current_power]:
                    current_power -= 1
                else:
                    tmp -= power[current_power]
                    output[current_power] += 1

            return Tridozenal(Seq(output), 0, tmp.base, self.is_negative ^ other.is_negative)

        else:
            raise TypeError(f"Invalid type {type(other).__name__}, must be int or Tridozenal")

    def __getitem__(self, item):
        if isinstance(item, int):
            if item >= 0:
                return self.integer[item]
            else:
                return self.mantissa[-item - 1]
        elif isinstance(item, slice):
            start = item.start if item.start is not None else -len(self.mantissa)
            stop = item.stop if item.stop is not None else len(self.integer)
            if item.step is not None:
                raise ValueError(f"Can only slice through Tridozenals with step of 1.")
            if start < 0:
                if stop < 0:
                    return Tridozenal(0, self.mantissa[-start-1:-stop-1], base=self.base)
                else:
                    return Tridozenal(self.integer.seq[:stop][::-1], self.mantissa[:-start], base=self.base)
            else:
                return Tridozenal(self.integer[start:stop], 0, base=self.base)


    def __ge__(self, other):
        if not isinstance(other, Tridozenal):
            raise ValueError(f"Cannot compare with {type(other).__name__}, only Tridozenals")
        if not self.base == other.base:
            raise ValueError(f"Base mismatch for Tridozenal numbers: {self.base} and {other.base}")
        if self.is_negative:
            if other.is_negative:
                return self.negative() <= other.negative()
            else:
                return False
        elif other.is_negative:
            return True
        elif self.integer == other.integer:
            if self.mantissa >= other.mantissa:
                return True
            else:
                return False
        elif len(self.integer) > len(other.integer):
            return True
        elif len(self.integer) < len(other.integer):
            return False
        elif self.integer.reverse() > other.integer.reverse():
            return True
        else:
            return False

    def __gt__(self, other):
        if not isinstance(other, Tridozenal):
            raise ValueError(f"Cannot compare with {type(other).__name__}, only Tridozenals")
        if not self.base == other.base:
            raise ValueError(f"Base mismatch for Tridozenal numbers: {self.base} and {other.base}")

        if self.is_negative:
            if other.is_negative:
                return self.negative() < other.negative()
            else:
                return False
        elif other.is_negative:
            return True
        elif self.integer == other.integer:
            if self.mantissa > other.mantissa:
                return True
            else:
                return False
        elif len(self.integer) > len(other.integer):
            return True
        elif len(self.integer) < len(other.integer):
            return False
        elif self.integer.reverse() > other.integer.reverse():
            return True
        else:
            return False

    def __hash__(self):
        return hash((str(self), self.base))

    def __float__(self):
        return float(self.__primitive(is_float=True))

    def __int__(self):
        return self.__primitive()

    def __le__(self, other):
        return not self > other

    def __lt__(self, other):
        return not self >= other

    def __mod__(self, other):
        if isinstance(other, int):
            return self % Tridozenal(other, 0, self.base)
        elif isinstance(other, Tridozenal):
            if other.base != self.base:
                raise ValueError(f"Base mismatch: {self.base} and {other.base}")
            return self - (self // other) * other
        else:
            raise TypeError(f"Invalid type {type(other).__name__}, must be int or Tridozenal")

    def __mul__(self, other):

        def pad_mantissa(mantissa, desired_length):
            return Seq([0 for _ in range(desired_length - len(mantissa))]).concat(mantissa)

        def split_into_parts(d, mantissa_point, base, is_negative):
            return Tridozenal(d.seq[:len(d) - mantissa_point], d.seq[len(d) - mantissa_point:], base, is_negative)

        if isinstance(other, (int, float)):
            if other == 0:
                return Tridozenal(0, 0, self.base)
            elif other < 0:
                return Tridozenal(self.integer * -other, self.mantissa * -other, self.base, not self.is_negative)
            else:
                return Tridozenal(self.integer * other, self.mantissa * other, self.base, self.is_negative)
        elif isinstance(other, Tridozenal):
            if self.base != other.base:
                raise ValueError(f"Base mismatch for Tridozenal numbers: {self.base} and {other.base}")

            if other == Tridozenal(1, 0, self.base):
                return self
            elif other == Tridozenal(1, 0, self.base, True):
                return self.negative()

            # Integer lengths
            # s_i = len(self.integer)
            # o_i = len(other.integer)

            # Mantissa lengths
            s_m = len(self.mantissa)
            o_m = len(other.mantissa)

            # Multiply parts using the FOIL method
            pt_1 = self.integer * other.integer
            pt_2 = self.integer.reverse() * other.mantissa
            pt_3 = self.mantissa * other.integer.reverse()
            pt_4 = self.mantissa * other.mantissa

            # Construct tridozenal representations of parts
            duo_1 = Tridozenal(pt_1, 0, self.base, self.is_negative ^ other.is_negative)
            duo_2 = split_into_parts(pt_2, o_m, self.base, self.is_negative ^ other.is_negative)
            duo_3 = split_into_parts(pt_3, s_m, self.base, self.is_negative ^ other.is_negative)
            duo_4 = Tridozenal(0, pad_mantissa(pt_4, s_m + o_m), self.base, self.is_negative ^ other.is_negative)

            # Put it all together
            out = duo_1 + duo_2 + duo_3 + duo_4

            return out

        else:
            return NotImplemented

    def __neg__(self):
        return self.negative()

    def __pow__(self, power, modulo=None):
        if power == 0 or power == Tridozenal.zero(self.base):
            return Tridozenal.one(self.base)
        elif power == 1 or power == Tridozenal.one(self.base):
            return self
        elif isinstance(power, int):
            out = Tridozenal(self.integer, self.mantissa, self.base, self.is_negative)
            for p in range(1, power):
                out *= self
            return out
        elif isinstance(power, Tridozenal):
            if log_power:
                print("Computing Tridozenal power (takes a little while)")
                print("(1/3) Computing natural log of self...")
            ln_self = self.ln(place=max(len(self.mantissa), round_to), log=log_power, perfect=True)
            if log_power:
                print("(2/3) Multiplying natural log by power...")
            prod = ln_self * power
            if log_power:
                print("(3/3) Getting exponential function of product...")
            exp_prod = Tridozenal.exp(self.base, prod, place=max(len(prod.mantissa), round_to), log=log_power, perfect=True)
            if log_power:
                print("Result computed.")
            return exp_prod

    def __radd__(self, other):
        return self + other

    def __rdiv__(self, other):
        return self / other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return other + self.negative()

    def __str__(self):
        def get_char(num):
            if 0 <= num < 10:
                return str(num)
            elif 10 <= num < 36:
                return chr(num + 55)
            elif 36 <= num < 62:
                return chr(num + 61)
            elif num == 62:
                return chars64[0]
            elif num == 63:
                return chars64[1]

        if len(self.integer):
            out_integer = "".join([get_char(self.integer[n]) for n in range(len(self.integer))])
        else:
            out_integer = "0"
        if len(self.mantissa):
            out_mantissa = "".join([get_char(self.mantissa[n]) for n in range(len(self.mantissa))])
        else:
            out_mantissa = ""
        return ("-" if self.is_negative else "") + out_integer[::-1] + ("." if len(out_mantissa) else "") + out_mantissa

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            if other < 0:
                return self + Tridozenal(other, 0, self.base)
            elif other >= 0:
                return self - Tridozenal(other, 0, self.base)
        elif isinstance(other, Tridozenal):
            return self + other.negative()
        else:
            raise ValueError(f"Unsupported type {type(other).__name__}; must be Tridozenal, int, or float")

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Division by zero error")
            if other == 1:
                return self
            elif other < 0:
                return self / Tridozenal(other, 0, self.base, True)
            elif other > 0:
                return self / Tridozenal(other, 0, self.base)
        elif isinstance(other, Tridozenal):
            if other == Tridozenal(1, 0, self.base):
                return self
            elif other == Tridozenal(1, 0, self.base, True):
                return self.negative()
            elif other.abs() == Tridozenal(0, 0, self.base):
                raise ValueError("Division by zero error")
            else:
                # The heavy lifting is done by computing the multiplicative inverse
                m = other.multiplicative_inverse()
                return m * self
        else:
            raise ValueError("Can only divide Tridozenal by int, float or Tridozenal")

    @staticmethod
    def zero(base: int=-1):
        if base == -1:
            base = default_base
        return Tridozenal(0, 0, base)

    @staticmethod
    def one(base: int=-1):
        if base == -1:
            base = default_base
        return Tridozenal(1, 0, base)

    @staticmethod
    def get_from_string(s: str, base: int=-1):
        """
        Translate a string into a Tridozenal of a given base.
        """
        if base == -1:
            base = default_base

        def get_num(char: str):

            ord_char = ord(char)
            if 48 <= ord_char < 58:
                return int(char)
            elif 65 <= ord_char < 91:
                return ord_char - 55
            elif 97 <= ord_char < 123:
                return ord_char - 61
            elif char == chars64[0]:
                return 62
            elif char == chars64[1]:
                return 63
            else:
                raise ValueError(f"Invalid character {char}; must be 0-9, A-Z, a-z, or {chars64}")

        if not s:
            return Tridozenal(0, 0, base)
        elif "." in s:
            s = s.split(".")
            if s[0] and s[0][0] == "-":
                is_negative = True
                s[0] = s[0][1:]
            else:
                is_negative = False

            integer_part = Seq([get_num(char) for char in s[0]]).reverse()
            mantissa_part = Seq([get_num(char) for char in s[1]])

            return Tridozenal(integer_part, mantissa_part, base, is_negative)
        else:
            if s[0] == "-":
                is_negative = True
                s = s[1:]
            else:
                is_negative = False
            integer_part = Seq([get_num(char) for char in s]).reverse()
            return Tridozenal(integer_part, 0, base, is_negative)

    @staticmethod
    def encode(s: str, base: int=-1, bits: int=8):
        if base == -1:
            base = default_base

        def pad(p, l):
            if len(p) > l:
                raise ValueError(f"Cannot encode base-{base} {p} in {l} characters")
            to_add = l - len(p)
            return "".join(["0" for _ in range(to_add)]) + p

        out = [Tridozenal(ord(e), base=base) for e in s]
        out = [pad(str(e), bits) for e in out]

        return "".join(out)

    @staticmethod
    def decode(s: str, base: int=-1, bits: int=8, as_binary_strings: bool=False):
        if base == -1:
            base = default_base

        size = 1
        b_p = base
        while b_p < 2**bits:
            b_p *= base
            size += 1

        out = [s[size*k:size*(k+1)] for k in range(len(s) // size)]
        out = [Tridozenal.get_from_string(e, base) for e in out]
        out = [str(e.convert(2)) if as_binary_strings else chr(int(e)) for e in out]

        return out if as_binary_strings else "".join(out)

    @staticmethod
    def exp(base: int=-1, power: int=1, iterations: int=100, place: int=-1, log: bool=False, perfect: bool=False):
        """
        Get the result of the exponential function e^x
        :param base: The base of the number
        :param power: The power (x) to take e to
        :param iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        if base == -1:
            base = default_base
        if place == -1:
            place = round_to

        one = Tridozenal(1, 0, base)
        out = one

        factorial = one
        prev_out = None

        if isinstance(power, int):
            power = Tridozenal(power, 0, base)
        power_of_power = power

        n = 1
        while n < iterations or perfect:
            prev_prev_out = prev_out
            prev_out = out
            factorial *= Tridozenal(n, 0, base)
            out += power_of_power / factorial
            power_of_power *= power
            power_of_power.round(place + 2)
            out.round(place + 2)
            if log:
                print(f"Iteration {n}:", out)
            if prev_out == out or prev_prev_out == out:
                if log:
                    print(f"Limit reached at {place} places")
                break
            n += 1

        out.round(place)
        return out

    @staticmethod
    def pi(base: int=-1, iterations: int=25, place: int=-1, log: bool=False, perfect: bool=False):
        """
        Compute pi in the base of your choice
        :param base: The base of the number
        :param iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        if base == -1:
            base = default_base
        if place == -1:
            place = round_to

        if log:
            print(f"Computing pi in base {base} to {place} places")

        one = Tridozenal(1, 0, base)
        two = Tridozenal(2, 0, base)
        four = Tridozenal(4, 0, base)
        five = Tridozenal(5, 0, base)
        six = Tridozenal(6, 0, base)
        eight = Tridozenal(8, 0, base)
        sixteen = Tridozenal(16, 0, base)

        pi = Tridozenal(0, 0, base)

        power_of_sixteen = one

        prev_pi = None

        k = 0
        while k < iterations or perfect:
            to_add_1 = one / power_of_sixteen

            to_add_2 = (four / (eight * k + one)) \
                - (two / (eight * k + four)) \
                - (one / (eight * k + five)) \
                - (one / (eight * k + six))

            prev_prev_pi = prev_pi
            prev_pi = pi
            pi += to_add_1 * to_add_2
            pi.round(place)

            if log:
                print(f"Iteration {k + 1}", pi)

            if prev_pi == pi or prev_prev_pi == pi:
                if log:
                    print(f"Limit reached for {place} digits")
                break

            power_of_sixteen *= sixteen
            k += 1

        if log:
            print()

        return pi

    def abs(self):
        return Tridozenal(self.integer, self.mantissa, self.base)

    def as_int(self):
        return Tridozenal(self.integer, Seq(), self.base, self.is_negative)

    def convert(self, base: int=-1):
        """
        Convert a number without a mantissa to another base
        """
        if base == -1:
            base = default_base

        if base == self.base:
            return self

        if not 36 >= base >= 2:
            raise ValueError(f"Base must be between 2 and 36")

        td0 = Tridozenal(base, 0, self.base)
        number = self.abs()
        number_mantissa = Tridozenal(Seq(), number.mantissa, number.base)

        output = []

        while number > Tridozenal.zero(number.base):
            modulo = number % td0

            # This line prevents floating point errors
            modulo.round(1)

            _sum = 0

            # The most un-fluent part of Td
            for i, digit in enumerate(modulo.integer):
                _sum += digit * modulo.base ** i
            output.append(_sum)
            number = number // td0

        output_mantissa = []
        while number_mantissa != Tridozenal.zero(number_mantissa.base) and len(output_mantissa) < round_to:
            modulo = number_mantissa * td0
            modulo = modulo.as_int()

            _sum = 0

            # The most un-fluent part of Td
            for i, digit in enumerate(modulo.integer):
                _sum += digit * modulo.base ** i
            output_mantissa.append(_sum)
            number_mantissa *= td0
            number_mantissa -= modulo

        return Tridozenal(output[::-1], output_mantissa, base, self.is_negative)

    def divide_by(self, other, place: int=-1):
        if place == -1:
            place = round_to

        if isinstance(other, (int, float)):
            is_negative = other < 0
            other = Tridozenal(abs(other), 0, self.base, is_negative)
            return self.divide_by(other, place)
        elif isinstance(other, Tridozenal):
            out = self * other.multiplicative_inverse(place=place)
            out.round(place)

            return out
        else:
            raise ValueError(f"Cannot divide with {type(other).__name__}, only int, float or Tridozenal")

    def ln(self, num_iterations: int=100, place: int=-1, log: bool=False, perfect: bool=True):
        """
        Compute the natural logarithm of the number
        :param num_iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        if self == Tridozenal(0, 0, self.base):
            raise ValueError("Log of zero is undefined")
        # This algorithm converges quite slowly, hence the default 100 iterations for greater accuracy
        if log:
            print(f"Computing natural log of {self}")
        if place == -1:
            place = round_to

        q = (self - 1).divide_by(self + 1, place + 2)
        if log:
            print("q", q)

        out = q
        temp = q
        q_squared = (q ** 2)
        q_squared.round(place + 2)

        prev_out = None
        k = 3

        # for k in range(3, num_iterations*2, 2):
        while k < num_iterations*2 or perfect:
            prev_prev_out = prev_out
            prev_out = out
            temp *= q_squared
            temp.round(place)
            out += temp / k
            out.round(place + 2)
            if log:
                print(f"Iteration {int((k - 1) / 2)}", out)
            if prev_out == out or prev_prev_out == out:
                if log:
                    print(f"Limit reached for {place} places")
                break
            k += 2

        out *= 2

        if log:
            print("final output:", out)

        out.round(place)
        return out

    def logarithm(self, base: int, num_iterations: int=100, place: int=-1, log: bool=True, perfect: bool=False):
        # Setting log to True helps it show that the program isn't hanging, just slow since it computes TWO natural logs
        if isinstance(base, int):
            return self.ln(num_iterations, place, log, perfect).divide_by(Tridozenal(base, 0, self.base).ln(num_iterations, place, log, perfect), place=place)
        elif isinstance(base, Tridozenal):
            return self.ln(num_iterations, place, log, perfect).divide_by(base.ln(num_iterations, place, log, perfect), place=place)
        else:
            raise ValueError(f"Cannot perform logarithm on {type(base).__name__}, only int or Tridozenal")

    def multiplicative_inverse(self, place: int=-1):

        def is_greater(a, b):
            if len(a) > len(b):
                return True
            elif len(a) < len(b):
                return False
            else:
                return a.reverse() >= b.reverse()

        if self == Tridozenal(1, 0, self.base) or self == Tridozenal(1, 0, self.base, True):
            return self

        if place == -1:
            place = round_to

        # construct the Seq which will be used for long division
        im_combo = self.integer.trim()
        if len(self.mantissa.trim(True)):
            im_combo = im_combo.reverse().concat(self.mantissa)
            im_combo = im_combo.reverse()

        adjusted_one = Seq(1)

        g = 0
        output = [0 for _ in range(place + len(im_combo))]

        while g < (place + len(im_combo)):

            # When adjusted_one hits zero, the operation is complete
            if len(adjusted_one.trim(True)) == 0:
                break

            if is_greater(adjusted_one, im_combo):
                # Perform a subtraction from the dividend
                adjusted_one -= im_combo
                adjusted_one = Tridozenal(adjusted_one, 0, self.base).integer
                output[g-1] += 1
            else:
                # Extend the dividend
                adjusted_one = Seq(0).concat(adjusted_one)
                g += 1

        return Tridozenal(
            Seq(output[:len(self.mantissa)]).reverse(),
            Seq(output[len(self.mantissa):]),
            self.base,
            self.is_negative
        )

    def negative(self):
        return Tridozenal(self.integer, self.mantissa, self.base, not self.is_negative)

    def rebase(self, base: int=-1):
        if base == -1:
            base = default_base

        return Tridozenal(self.integer, self.mantissa, base, self.is_negative)

    def __primitive(self, is_float: bool=False):
        """
        Convert a Tridozenal to its primitive int representation
        """
        output = sum([self.integer[k] * self.base ** k for k in range(len(self.integer))])
        if is_float:
            output += sum([self.mantissa[k] * self.base ** (-k - 1) for k in range(len(self.mantissa))])
        return output

    def __resolve(self):
        """
        Performs all carries on the Tridozenal
        """

        def resolve_pair(a, b):
            """
            Convert the given pair into a resolved pair
            """
            return a % self.base, b + a // self.base

        out_int = self.integer
        out_man = self.mantissa

        # Mantissa resolution
        modified = True
        while modified:
            modified = False
            out_man = out_man.concat(Seq(0))

            # Resolve between integer and mantissa
            if out_man[0] < 0 or out_man[0] >= self.base:
                modified = True
                out_man[0], out_int[0] = resolve_pair(out_man[0], out_int[0])

            # Resolve mantissa
            for n in range(len(out_man) - 1, 0, -1):
                if out_man[n] < 0 or out_man[n] >= self.base:
                    modified = True
                out_man[n], out_man[n - 1] = resolve_pair(out_man[n], out_man[n - 1])

            out_man = out_man.trim(True)

        # Integer resolution
        modified = True
        while modified:
            modified = False
            out_int = out_int.concat(Seq(0))

            for n in range(len(out_int) - 1):
                if (out_int[n] < 0 and n != len(out_int) - 2) or out_int[n] >= self.base:
                    modified = True
                    out_int[n], out_int[n + 1] = resolve_pair(out_int[n], out_int[n + 1])

            out_int = out_int.trim()

        turn_negative = False

        # If the leading digit is negative, the number must turn negative
        if out_int[len(out_int) - 1] < 0:
            out_int = out_int.neg()
            out_man = out_man.neg()
            turn_negative = True

        self.integer = out_int
        self.mantissa = out_man

        # If turn negative, rinse and repeat
        if turn_negative:
            self.is_negative = not self.is_negative
            self.__resolve()

    def root(self, power: int=2, num_iterations: int=15, place: int=-1, log: bool=False, perfect: bool=False):
        """
        Get the n-th root of the number, where n is a positive integer

        :param power: The (integer) power of the root to take
        :param num_iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        # This takes a while even with only 15 iterations
        if not len(self.integer) and not len(self.mantissa):
            return Tridozenal(0, 0, self.base)

        if place == -1:
            place = round_to

        if log:
            print(f"Finding square root of {self} with Newton iteration")

        out = Tridozenal(1, 0, self.base)
        prev = None

        k = 0
        # Newton iteration method
        while k < num_iterations or perfect:
            # n-th root
            prev_prev = prev
            prev = out
            pt_1 = out * (power - 1)
            pt_2 = self * (out ** (power-1)).multiplicative_inverse(place=place)
            out = (pt_1 + pt_2) / power
            out.round(place)

            if prev == out or prev_prev == out:
                if log:
                    print(f"Limit reached for {place} decimal places.")
                break
            if log:
                print(f"Iteration {k+1}:", out)

            k += 1

        if log:
            print()

        return out

    def round(self, place: int=-1):
        if place < -1:
            raise ValueError(f"Place must be greater than or equal to -1, not {place}")
        elif place == -1:
            place = round_to
        if self.mantissa[place] >= self.base / 2:
            if place == 0:
                self.integer[0] += 1
            else:
                self.mantissa[place - 1] += 1

        self.mantissa = self.mantissa[:place].trim(True)
        self.__resolve()

    def rounded(self, place: int):
        output = Tridozenal(self.integer, self.mantissa, self.base, self.is_negative)
        output.round(place)
        return output

    def integer_part(self):
        return Tridozenal(self.integer, Seq(), self.base, self.is_negative)

    def mantissa_part(self):
        return Tridozenal(Seq(), self.mantissa, self.base, self.is_negative)

    def truncated(self, place: int):
        return Tridozenal(self.integer, self.mantissa[:place], self.base, self.is_negative)

    def trim(self):
        # remove trailing zeroes for cleaner looking numbers
        self.integer = self.integer.trim()
        self.mantissa = self.mantissa.trim(True)
