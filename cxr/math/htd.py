from cxr.math.base36 import Tridozenal as Td

from cxr.math import base36
import copy


std_l = 30


def check_seq(f):
    """
    Auxiliary method which checks inputs to Seq methods

    Ensures that the numerical input is translated to a Seq object

    :param f: the function to be decorated
    """
    def wrapper(self, o=None):
        if o is None:
            return f(self, None)
        elif isinstance(o, (int, float, Td)):
            return f(self, Seq(o))
        elif isinstance(o, list):
            for e in o:
                if not isinstance(e, (int, float, Td)):
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

    @staticmethod
    def __validate(lst):
        """
        Ensures a list contains a valid set of values before setting it in __init__
        """
        if not lst:
            return True
        base = None
        for t in lst:
            if not isinstance(t, Td):
                raise TypeError(f"Detected value of type {t}, must be Tridozenal")
            else:
                if base is None:
                    base = t.base
                elif base != t.base:
                    raise ValueError(f"Base mismatch: {base} and {t.base}")
        return True

    def __init__(self, *seq):
        if len(seq) == 1:
            seq = seq[0]
        else:
            seq = list(seq)

        if seq is None:
            self.seq = []
        elif isinstance(seq, (int, float, Td)):
            self.seq = [seq]
        elif isinstance(seq, (list, tuple)):
            self.seq = []
            Seq.__validate(seq)
            for v in seq:
                if isinstance(v, float):
                    self.seq.append(int(v) if int(v) == v else v)
                else:
                    self.seq.append(v)

        elif isinstance(seq, Seq):
            self.seq = copy.deepcopy(seq.seq)
        else:
            raise ValueError(f"Unsupported type {type(seq).__name__}")

    @check_seq
    def __add__(self, o):
        if isinstance(o, (int, float, Td)):
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
        if o is None or not isinstance(o, Seq):
            return False
        elif len(self.trim()) != len(o.trim()):
            return False
        return all(self[k] == o[k] for k in range(len(self.trim())))

    @check_seq
    def __ge__(self, o):
        return self.seq >= o.seq

    def __getitem__(self, i):
        if isinstance(i, int):
            if i < 0:
                return self.seq[len(self) + i]
            else:
                if self.seq:
                    return self.seq[i] if len(self) > i else (Td.zero(self.seq[0].base) if isinstance(self.seq[0], Td) else 0)
                else:
                    return 0
        elif isinstance(i, slice):
            start = i.start if i.start else 0
            stop = i.stop if i.stop else len(self)

            if stop < 0:
                stop = len(self) + stop

            step = i.step if i.step else 1
            if step < 0:
                start, stop = stop - 1, start - 1
            zero = Td.zero(self.base()) if self.is_td() else 0
            return Seq([self.seq[k] if len(self) > k >= 0 else zero for k in range(start, stop, step)])

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
    def __mul__(self, o):
        l = len(self) + len(o) - 1
        r = [sum(self[k] * o[x - k] for k in range(x + 1)) for x in range(l)]
        return Seq(r)

    def __neg__(self):
        return self.neg()

    def __pow__(self, power, modulo=None):
        a = Seq(self)
        if self.is_td():
            out = Seq(Td.one(self.base()))
        else:
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

    def __truediv__(self, o):
        if isinstance(o, Td):
            o = Seq(o)
        elif not isinstance(o, Htd):
            raise TypeError(f"Can only divide by Td or Htd")

        # Remove leading zeroes, which is basically factoring out x
        temp_self = copy.deepcopy(self)
        temp_o = copy.deepcopy(o)
        while len(temp_o) > 0 and len(temp_self) > 0:
            if temp_self[0] == temp_o[0] == 0:
                temp_self.pop(0)
                temp_o.pop(0)
            elif temp_self.is_td() and temp_o.is_td():
                if temp_self[0].abs() == temp_o[0].abs() == Td.zero(temp_self.base()):
                    temp_self.pop(0)
                    temp_o.pop(0)
                else:
                    break
            else:
                break

        # If either sequence is blank after zero removal, division will fail
        if len(temp_o) == 0:
            raise ValueError("Cannot divide by zero or null sequence")
        elif len(temp_self) == 0:
            raise ValueError("Cannot divide zero or null sequence")

        r = Seq(temp_self[0]/temp_o[0])

        # Tds are computationally expensive, so limit their size
        if isinstance(r[0], Td):
            l = max([len(temp_self), len(temp_o)])
        else:
            l = std_l
        for n in range(1, l):
            r.append((temp_self[n] - sum(r[k] * temp_o[n-k] for k in range(n))) / temp_o[0])
        r = ([k if isinstance(k, Td) else int(k) if int(k) == k else k for k in r])
        return Seq(r).trim()

    def append(self, v: (int, float)):
        """
        Add a value to the end of the sequence

        :param v: the value to be added
        """
        self.seq.append(v)

    def base(self):
        if self.is_td():
            return self[0].base
        else:
            return -1

    def concat(self, other):
        return Seq(self.seq + other.seq)

    def is_td(self):
        if not len(self):
            return False
        return isinstance(self[0], Td)

    def neg(self):
        """
        Converts the given sequence to its additive inverse
        """
        out = [-k for k in self]
        return Seq(out)

    def pop(self, index=0):
        return self.seq.pop(index)

    def reverse(self):
        return Seq(self.seq[::-1])

    def trim(self, to_zero=True):
        """
        Removes trailing zeroes from a sequence
        """
        out = copy.deepcopy(self.seq)
        while len(out) > (0 if to_zero else 1):
            current_seq = out[-1]
            if isinstance(current_seq, Td):
                if current_seq.abs() == Td.zero(current_seq.base):
                    out.pop(-1)
                else:
                    break
            elif current_seq == 0:
                out.pop(-1)
            else:
                break
        return Seq(out)


"""
An implementation of arbitrary base arithmetic up to base 36.

Htd numbers include:

Equality testing
Rounding
Addition & Subtraction
Multiplication & Division
N-th Root using Newton Iteration
Pi and e
Logarithms
"""

# Default value to round to when place is not set (-1)
round_to = 10

# Determines whether the log shows during __pow__ when power is Htd
log_power = True

# Decides the default base for a Htd. I prefer 7.
default_hyperbase = 7

# The default separator for an Htd
default_sep = ","

# The default separator for obfuscated Htd strings
default_encryption_sep = ":"

# The mantissa point for an Htd
mantissa_point = "."


def convert_td(num, base):
    """
    Converts primitive ints to the given base

    Only used in __init__ to escape base 10,
    hence why it is disfluent.
    """
    output = []
    while num > Td.zero(num.base):
        modulo = num % base
        output.append(modulo)
        num = num // base

    return output


class Htd:
    def __init__(self, hyperbase, implicit_base, integer=None, mantissa=None, is_negative=False):
        self.base = hyperbase

        self.implicit_base = implicit_base

        if not integer:
            self.integer = Seq()
        elif isinstance(integer, Seq):
            self.integer = integer
        elif isinstance(integer, Td):
            if integer.base != self.implicit_base:
                integer = integer.convert(self.implicit_base)
            self.integer = Seq(convert_td(integer, self.base))
        elif isinstance(integer, list):
            self.integer = Seq([i.convert(self.implicit_base) for i in integer[::-1]])
        else:
            raise ValueError(f"Invalid integer type {type(integer).__name__}; must be Td or Seq")

        if not mantissa:
            self.mantissa = Seq(Td.zero(self.implicit_base))
        elif isinstance(mantissa, Seq):
            if len(mantissa) == 0:
                self.mantissa = Seq(Td.zero(self.implicit_base))
            else:
                self.mantissa = Seq([m.convert(self.implicit_base) for m in mantissa])
        elif isinstance(mantissa, Td):
            if mantissa.base != self.implicit_base:
                mantissa = mantissa.convert(self.implicit_base)
            self.mantissa = Seq(mantissa)
        elif isinstance(mantissa, list):
            self.mantissa = Seq([m.convert(self.implicit_base) for m in mantissa])
        else:
            raise ValueError(f"Invalid mantissa type {type(mantissa).__name__}; must be Td, list or Seq")

        self.implicit_zero = Td.zero(self.implicit_base)
        self.implicit_one = Td.one(self.implicit_base)

        self.is_negative = is_negative

        # No unresolved numbers
        self.__resolve()

        # Default rounding behavior
        self.round(place=round_to)

    def __add__(self, other):
        if isinstance(other, Td):
            if other < self.implicit_zero:
                return self + Htd(self.base, self.implicit_base, -other, 0, is_negative=True)
            else:
                return self + Htd(self.base, self.implicit_base, other, 0)
        elif isinstance(other, Htd):
            if self.is_negative:
                if other.is_negative:
                    return Htd(self.base, self.implicit_base, self.integer + other.integer,
                               self.mantissa + other.mantissa, is_negative=True)
                else:
                    if self.abs() > other:
                        return Htd(self.base, self.implicit_base, self.integer - other.integer,
                                   self.mantissa - other.mantissa, is_negative=True)
                    else:
                        return Htd(self.base, self.implicit_base, other.integer - self.integer,
                                   other.mantissa - self.mantissa)
            elif other.is_negative:
                if other.abs() > self:
                    return Htd(self.base, self.implicit_base, other.integer - self.integer,
                               other.mantissa - self.mantissa, is_negative=True)
                else:
                    return Htd(self.base, self.implicit_base, self.integer - other.integer,
                               self.mantissa - other.mantissa)
            else:
                return Htd(self.base, self.implicit_base, self.integer + other.integer,
                           self.mantissa + other.mantissa)
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Htd):
            self.trim()
            return self.integer == other.integer \
                   and self.mantissa == other.mantissa \
                   and self.base == other.base \
                   and self.implicit_base == other.implicit_base \
                   and self.is_negative == other.is_negative
        else:
            return False

    def __floordiv__(self, other):
        if isinstance(other, Td):
            return self // Htd(self.base, self.implicit_base, other, 0)
        elif isinstance(other, Htd):
            if other.base != self.base:
                raise ValueError(f"Base mismatch: {self.base} and {other.base}")

            power = other.abs()
            current_power = 0
            base_td = Td(self.base, 0, self.implicit_base)
            while power < self.abs():
                power *= base_td
                current_power += 1

            tmp = self.abs()
            output = [self.implicit_zero for _ in range(current_power)]
            while tmp >= other.abs():
                if tmp < power:
                    current_power -= 1
                    power /= base_td
                    power.round(place=round_to-2)
                else:
                    tmp -= power
                    output[current_power] += self.implicit_one

            return Htd(tmp.base, tmp.implicit_base, Seq(output), 0,
                       is_negative=self.is_negative ^ other.is_negative)

        else:
            return NotImplemented

    def __ge__(self, other):
        if not isinstance(other, Htd):
            raise ValueError(f"Cannot compare with {type(other).__name__}, only Tridozenals")
        if not self.base == other.base:
            raise ValueError(f"Base mismatch for Htd numbers: {self.base} and {other.base}")
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
        if not isinstance(other, Htd):
            raise ValueError(f"Cannot compare with {type(other).__name__}, only Tridozenals")
        if not self.base == other.base:
            raise ValueError(f"Base mismatch for Htd numbers: {self.base} and {other.base}")

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

    def __le__(self, other):
        return not self > other

    def __lt__(self, other):
        return not self >= other

    def __mod__(self, other):
        if isinstance(other, Td):
            return self % Htd(self.base, self.implicit_base, other, 0)
        elif isinstance(other, Htd):
            if other.base != self.base:
                raise ValueError(f"Base mismatch: {self.base} and {other.base}")

            power = [Htd.one(self.base, self.implicit_base)]
            other_abs = other.abs()
            current_power = 0
            while power[-1] < self.abs():
                power.append(power[-1] * other_abs)
                current_power += 1

            if self.is_negative:
                tmp = self + power[-1]
            else:
                tmp = copy.deepcopy(self)

            while tmp >= other_abs:
                if tmp < power[current_power]:
                    current_power -= 1
                else:
                    tmp -= power[current_power]

            return tmp
        else:
            return NotImplemented

    def __mul__(self, other):

        def pad_mantissa(mantissa, desired_length):
            return Seq([self.implicit_zero for _ in range(desired_length - len(mantissa))]).concat(mantissa)

        def split_into_parts(d, mantissa_point, is_negative):
            return Htd(self.base, self.implicit_base, d.seq[:len(d) - mantissa_point],
                       d.seq[len(d) - mantissa_point:], is_negative)

        if isinstance(other, Td):
            if other == self.implicit_zero:
                return Htd(self.base, self.implicit_base, self.implicit_zero, 0)
            elif other.is_negative:
                return Htd(self.base, self.implicit_base, self.integer * -other, self.mantissa * -other,
                           is_negative=not self.is_negative)
            else:
                return Htd(self.base, self.implicit_base, self.integer * other, self.mantissa * other,
                           is_negative=self.is_negative)
        elif isinstance(other, Htd):
            if self.base != other.base:
                raise ValueError(f"Base mismatch for Htd numbers: {self.base} and {other.base}")

            if other == Htd(self.base, self.implicit_base, self.implicit_one, 0):
                return self
            elif other == Htd(self.base, self.implicit_base, self.implicit_one, 0, is_negative=True):
                return self.negative()

            # Mantissa lengths
            s_m = len(self.mantissa)
            o_m = len(other.mantissa)

            # Multiply parts using the FOIL method
            pt_1 = self.integer * other.integer
            pt_2 = self.integer.reverse() * other.mantissa
            pt_3 = self.mantissa * other.integer.reverse()
            pt_4 = self.mantissa * other.mantissa

            # Construct tridozenal representations of parts
            duo_1 = Htd(self.base, self.implicit_base, pt_1, 0, is_negative=self.is_negative ^ other.is_negative)
            duo_2 = split_into_parts(pt_2, o_m, self.is_negative ^ other.is_negative)
            duo_3 = split_into_parts(pt_3, s_m, self.is_negative ^ other.is_negative)
            duo_4 = Htd(self.base, self.implicit_base, 0, pad_mantissa(pt_4, s_m + o_m),
                        is_negative=self.is_negative ^ other.is_negative)

            # Put it all together
            out = duo_1 + duo_2 + duo_3 + duo_4

            return out

        else:
            return NotImplemented

    def __neg__(self):
        return self.negative()

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            if power == 0:
                return Htd.one(self.base, self.implicit_base)
            elif power == 1:
                return self

            out = Htd(self.base, self.implicit_base, self.integer, self.mantissa, is_negative=self.is_negative)
            for p in range(1, power):
                out *= self
            return out
        else:
            return NotImplemented

    def __radd__(self, other):
        return self + other

    def __rdiv__(self, other):
        return self / other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return self - other

    def __str__(self):
        def get_char(num):
            # Temporary fix
            return str(num)
            # if 0 <= num < 10:
            #     return str(num)
            # elif 10 <= num < 36:
            #     if num == 24:
            #         return "o"
            #     elif num == 18:
            #         return "i"
            #     else:
            #         return chr(num + 55)

        if len(self.integer):
            out_integer = default_sep.join([get_char(self.integer[n]) for n in range(len(self.integer) - 1, -1, -1)])
        else:
            out_integer = "0"
        if len(self.mantissa):
            out_mantissa = default_sep.join([get_char(self.mantissa[n]) for n in range(len(self.mantissa))])
        else:
            out_mantissa = ""
        return ("-" if self.is_negative else "") + out_integer + (mantissa_point if len(out_mantissa) else "") + out_mantissa

    def __sub__(self, other):
        if isinstance(other, Td):
            if other.is_negative:
                return self + Htd(self.base, self.implicit_base, other, 0)
            else:
                return self - Htd(self.base, self.implicit_base, other, 0)
        elif isinstance(other, Htd):
            return self + other.negative()
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Td):
            if other == self.implicit_zero:
                raise ValueError("Division by zero error")
            if other == self.implicit_one:
                return self
            elif other < self.implicit_zero:
                return self / Htd(self.base, self.implicit_base, -other, 0, is_negative=True)
            elif other > self.implicit_zero:
                return self / Htd(self.base, self.implicit_base, other, 0)
        elif isinstance(other, Htd):
            if other == Htd(self.base, self.implicit_base, self.implicit_one, 0):
                return self
            elif other == Htd(self.base, self.implicit_base, self.implicit_one, 0, is_negative=True):
                return self.negative()
            elif other.abs() == Htd(self.base, self.implicit_base, self.implicit_zero, 0):
                raise ValueError("Division by zero error")
            else:
                # The heavy lifting is done by computing the multiplicative inverse
                m = other.multiplicative_inverse()
                return m * self
        else:
            return NotImplemented

    @staticmethod
    def get_from_string(s, hyperbase, implicit_base, sep=None, mantissa_pt=None):
        if not sep:
            sep = default_sep
        if not mantissa_pt:
            mantissa_pt = mantissa_point

        def read(s):
            output = []
            for each in s.split(sep):
                output.append(Td.get_from_string(each, implicit_base))
            return output

        if mantissa_pt in s:
            s = s.split(mantissa_pt)
            int_output = read(s[0])
            man_output = read(s[1])
        else:
            int_output = read(s)
            man_output = []

        return Htd(hyperbase=hyperbase, implicit_base=implicit_base, integer=int_output, mantissa=man_output)

    @staticmethod
    def encode(s, hyperbase, implicit_base, sep=None):
        """
        Convert a string into a sequence of Htds

        :param s: the string to be encoded
        :param hyperbase
        :param implicit_base
        :param sep: hypernumber separator
        :return: string representation of the sequence of Htds
        """
        if not sep:
            sep = default_encryption_sep

        out = [Htd(hyperbase=hyperbase, implicit_base=implicit_base, integer=Td(ord(e), base=implicit_base)) for e in s]

        out = sep.join([str(e) for e in out])

        return out

    @staticmethod
    def decode(s, hyperbase, implicit_base, sep=None):
        """
        Decode an encoded Htd string

        :param s: the string to be decoded
        :param hyperbase
        :param implicit_base
        :param sep: hypernumber separator
        :return: the decoded string
        """
        if not sep:
            sep = default_encryption_sep

        out = s.split(sep)

        out = [Htd.get_from_string(e, hyperbase, implicit_base) for e in out]

        out = "".join([chr(e.primitive()) for e in out])

        return out

    @staticmethod
    def encrypt(s, hyperbases=None, implicit_bases=None, sep=None):
        """
        Htd obfuscation turns a string and two sets of bases
        into a sort of dual password.

        Obfuscation uses elements of hyperbases and implicit_bases
        to encode each byte of the string as an Htd. By iterating over both lists
        mod their length, we can use lists of differing lengths
        and still yield a consistent obfuscation.

        :param s: the string to be obfuscated
        :param hyperbases: the set of hyperbases used for obfuscation
        :param implicit_bases: the set of implicit bases used for obfuscation
        :param sep: the Htd separator
        :return: an obfuscated string
        """

        if not hyperbases:
            hyperbases = [default_hyperbase]
        if not implicit_bases:
            implicit_bases = [base36.default_base]
        if not sep:
            sep = default_encryption_sep

        l0 = len(implicit_bases)
        l1 = len(hyperbases)

        out = [Htd(hyperbase=hyperbases[i % l1], implicit_base=implicit_bases[i % l0],
                   integer=Td(ord(s[i]), base=implicit_bases[i % l0])) for i in range(len(s))]
        out = sep.join([str(e) for e in out])

        return out

    @staticmethod
    def decrypt(s, hyperbases=None, implicit_bases=None, sep=None):
        """
        Use two sets of bases to deobfuscate a string

        For deobfuscation to yield anything coherent, one must take care
        to preserve the hyperbase and implicit base sets like one would a password

        :param s: the string to be deobfuscated
        :param hyperbases: the set of hyperbases used for deobfuscation
        :param implicit_bases: the set of implicit bases used for deobfuscation
        :param sep: the Htd separator
        :return: the deobfuscated string
        """

        if not hyperbases:
            hyperbases = [default_hyperbase]
        if not implicit_bases:
            implicit_bases = [base36.default_base]
        if not sep:
            sep = default_encryption_sep

        l0 = len(implicit_bases)
        l1 = len(hyperbases)

        out = s.split(sep)

        out = [Htd.get_from_string(out[i], hyperbases[i % l1], implicit_bases[i % l0]) for i in range(len(out))]

        out = "".join([chr(e.primitive()) for e in out])

        return out

    @staticmethod
    def zero(hyperbase, implicit_base):
        return Htd(hyperbase, implicit_base, Td.zero(implicit_base), 0)

    @staticmethod
    def one(hyperbase, implicit_base):
        return Htd(hyperbase, implicit_base, Td.one(implicit_base), 0)

    @staticmethod
    def exp(hyperbase, implicit_base, power=1, iterations=100, place=-1, log=False, perfect=False):
        """
        Get the result of the exponential function e^x
        :param hyperbase: The base of the number
        :param power: The power (x) to take e to
        :param iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        if place == -1:
            place = round_to

        one = Htd.one(hyperbase, implicit_base)
        out = one

        factorial = one
        prev_out = None

        if isinstance(power, int):
            power = Htd(hyperbase, implicit_base, Td(power, 0, implicit_base), 0)
        elif isinstance(power, Td):
            power = Htd(hyperbase, implicit_base, power, 0)
        power_of_power = one

        n = 1
        while n < iterations or perfect:
            prev_prev_out = prev_out
            prev_out = out
            factorial *= Htd(hyperbase, implicit_base, Td(n, 0, implicit_base), 0)
            power_of_power *= power
            power_of_power.round(place + 2)
            out += power_of_power / factorial
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
    def pi(hyperbase, implicit_base, iterations=25, place=-1, log=False, perfect=False):
        """
        Compute pi in the base of your choice
        :param hyperbase: The base of the number
        :param iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        if place == -1:
            place = round_to

        if log:
            print(f"Computing pi in base {hyperbase} to {place} places")

        one = Htd(hyperbase, implicit_base, Td(1, 0, implicit_base), 0)
        two = Htd(hyperbase, implicit_base, Td(2, 0, implicit_base), 0)
        four = Htd(hyperbase, implicit_base, Td(4, 0, implicit_base), 0)
        five = Htd(hyperbase, implicit_base, Td(5, 0, implicit_base), 0)
        six = Htd(hyperbase, implicit_base, Td(6, 0, implicit_base), 0)
        eight = Htd(hyperbase, implicit_base, Td(8, 0, implicit_base), 0)
        sixteen = Htd(hyperbase, implicit_base, Td(16, 0, implicit_base), 0)

        pi = Htd.zero(hyperbase, implicit_base)

        power_of_sixteen = one

        prev_pi = None

        k = 0
        while k < iterations or perfect:
            k_td = Htd(hyperbase, implicit_base, Td(k, 0, implicit_base), 0)
            eight_times_k_td = eight * k_td
            to_add_1 = one / power_of_sixteen

            to_add_2 = (four / (eight_times_k_td + one)) \
                - (two / (eight_times_k_td + four)) \
                - (one / (eight_times_k_td + five)) \
                - (one / (eight_times_k_td + six))

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
        return Htd(self.base, self.implicit_base, self.integer, self.mantissa)

    def convert(self, hyperbase):
        """
        Convert a number without a mantissa to another base
        """

        if not hyperbase >= 2:
            raise ValueError(f"Base must be greater than or equal to 2, not {hyperbase}")

        td0 = Htd(self.base, self.implicit_base, Td(hyperbase, 0, self.implicit_base), 0)
        number = self.abs()

        output = []

        while number > Htd.zero(self.base, self.implicit_base):
            modulo = number % td0

            # This line prevents floating point errors
            modulo.round(1)

            _sum = self.implicit_zero

            # The most un-fluent part of Td
            for i, digit in enumerate(modulo.integer):
                _sum += digit * modulo.base ** i
            output.append(_sum)
            number = number // td0

        return Htd(hyperbase, self.implicit_base, output[::-1], 0, is_negative=self.is_negative)

    def divide_by(self, other, place=-1):
        if place == -1:
            place = round_to

        if isinstance(other, Td):
            other = Htd(self.base, self.implicit_base, other.abs(), 0, is_negative=other.is_negative)
            return self.divide_by(other, place)
        elif isinstance(other, Htd):
            out = self * other.multiplicative_inverse(place=place)
            out.round(place)

            return out
        else:
            raise ValueError(f"Cannot divide with {type(other).__name__}, only int, float or Htd")

    def ln(self, num_iterations=100, place=20, log=False, perfect=False):
        """
        Compute the natural logarithm of the number
        :param num_iterations: the maximum number of iterations of the computation
        :param place: The number of mantissa places of the result
        :param log: Whether the log messages will be printed
        :param perfect: Whether to iterate until the mantissa is fully computed (can be slow!)
        """
        if self == Htd.zero(self.base, self.implicit_base):
            raise ValueError("Log of zero is undefined")
        # This algorithm converges quite slowly, hence the default 100 iterations for greater accuracy
        if log:
            print(f"Computing natural log of {self}")

        q = (self - Td.one(self.implicit_base)).divide_by(self + Td.one(self.implicit_base), place + 2)
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
            out += temp / Td(k, 0, self.implicit_base)
            out.round(place + 2)
            if log:
                print(f"Iteration {int((k - 1) / 2)}", out)
            if prev_out == out or prev_prev_out == out:
                if log:
                    print(f"Limit reached for {place} places")
                break
            k += 2

        out *= Td(2, 0, self.implicit_base)

        if log:
            print("final output:", out)

        out.round(place)
        return out

    def logarithm(self, base, num_iterations=100, place=20, log=True, perfect=False):
        # Setting log to True helps it show that the program isn't hanging, just slow since it computes TWO natural logs
        if isinstance(base, int):
            return self.ln(num_iterations, place, log, perfect).divide_by(
                Htd(self.base, self.implicit_base, Td(base, 0, self.implicit_base), 0).ln(num_iterations, place, log, perfect), place=place)
        elif isinstance(base, Td):
            return self.ln(num_iterations, place, log, perfect).divide_by(
                Htd(self.base, self.implicit_base, base, 0).ln(num_iterations, place, log, perfect), place=place)
        elif isinstance(base, Htd):
            return self.ln(num_iterations, place, log, perfect).divide_by(base.ln(num_iterations, place, log, perfect), place=place)
        else:
            return NotImplemented

    def multiplicative_inverse(self, place=-1):

        def is_greater(a, b):
            if len(a) > len(b):
                return True
            elif len(a) < len(b):
                return False
            else:
                return a.reverse() >= b.reverse()

        if self.abs() == Htd.one(self.base, self.implicit_base):
            return self

        if place == -1:
            place = round_to

        # construct the Seq which will be used for long division
        im_combo = self.integer.trim()
        if len(self.mantissa.trim()):
            im_combo = im_combo.reverse().concat(self.mantissa)
            im_combo = im_combo.reverse()

        adjusted_one = Seq(self.implicit_one)

        g = 0
        output = [self.implicit_zero for _ in range(place + len(im_combo))]

        while g < (place + len(im_combo)):

            # When adjusted_one hits zero, the operation is complete
            if len(adjusted_one.trim()) == 0:
                break

            if is_greater(adjusted_one, im_combo):
                # Perform a subtraction from the dividend
                adjusted_one -= im_combo
                adjusted_one = Htd(self.base, self.implicit_base, adjusted_one, 0).integer
                output[g-1] += 1
            else:
                # Extend the dividend
                adjusted_one = Seq(self.implicit_zero).concat(adjusted_one)
                g += 1

        return Htd(self.base, self.implicit_base, output[:len(self.mantissa)][::-1], output[len(self.mantissa):],
                   self.is_negative)

    def negative(self):
        return Htd(self.base, self.implicit_base, self.integer, self.mantissa, is_negative=not self.is_negative)

    def rebase(self, hyperbase):

        return Htd(hyperbase, self.implicit_base, self.integer, self.mantissa, is_negative=self.is_negative)

    def implicit_rebase(self, implicit_base):
        return Htd(self.base, self.implicit_base, [e.rebase(implicit_base) for e in self.integer],
                   [e.rebase(implicit_base) for e in self.mantissa])

    def implicit_convert(self, implicit_base):
        return Htd(self.base, self.implicit_base, [e.convert(implicit_base) for e in self.integer],
                   [e.convert(implicit_base) for e in self.mantissa])

    def __resolve(self):
        """
        Performs all carries on the Htd
        """

        def resolve_pair(a, b):
            """
            Convert the given pair into a resolved pair
            """
            output_a = (Td(self.base, 0, a.base) - (a.negative() % self.base)) if a.is_negative else a % self.base
            output_b = b + a // self.base + (-1 if a.is_negative else 0)
            return output_a, output_b

        base_td = Td(self.base, 0, self.implicit_base)

        out_int = self.integer
        out_man = self.mantissa

        if not len(out_int):
            out_int.append(self.implicit_zero)

        # Mantissa resolution
        modified = True
        while modified:
            modified = False
            out_man = out_man.concat(Seq(self.implicit_zero))

            # Resolve between integer and mantissa
            if out_man[0] < self.implicit_zero or out_man[0] >= base_td:
                modified = True
                out_man[0], out_int[0] = resolve_pair(out_man[0], out_int[0])

            # Resolve mantissa
            for n in range(len(out_man) - 1, 0, -1):
                if out_man[n] < self.implicit_zero or out_man[n] >= base_td:
                    modified = True
                out_man[n], out_man[n - 1] = resolve_pair(out_man[n], out_man[n - 1])

            out_man = out_man.trim()

        # Integer resolution
        modified = True
        while modified:
            modified = False
            out_int = out_int.concat(Seq(self.implicit_zero))

            for n in range(len(out_int) - 1):
                if (out_int[n] < self.implicit_zero and n != len(out_int) - 2) or out_int[n] >= base_td:
                    modified = True
                    out_int[n], out_int[n + 1] = resolve_pair(out_int[n], out_int[n + 1])

            out_int = out_int.trim()

        turn_negative = False

        # If the leading digit is negative, the number must turn negative
        if len(out_int) and out_int[len(out_int) - 1] < self.implicit_zero:
            out_int = out_int.neg()
            out_man = out_man.neg()
            turn_negative = True

        self.integer = out_int
        self.mantissa = out_man

        # If turn negative, rinse and repeat
        if turn_negative:
            self.is_negative = not self.is_negative
            self.__resolve()

    def root(self, power=2, num_iterations=15, place=-1, log=False, perfect=False):
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
            return Htd.zero(self.base, self.implicit_base)

        if place == -1:
            place = round_to

        if log:
            print(f"Finding square root of {self} with Newton iteration")

        out = Htd.one(self.base, self.implicit_base)
        prev = None

        k = 0
        # Newton iteration method
        while k < num_iterations or perfect:
            # n-th root
            prev_prev = prev
            prev = out
            pt_1 = out * Td(power - 1, 0, self.implicit_base)
            pt_2 = self * (out ** (power-1)).multiplicative_inverse(place=place)
            out = (pt_1 + pt_2) / Td(power, 0, self.implicit_base)
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

    def round(self, place):
        if place > len(self.mantissa):
            return

        base_td = Td(self.base, 0, self.implicit_base)
        two = Td(2, 0, self.implicit_base)
        if self.mantissa[place] >= base_td // two:
            self.mantissa[place - 1] += 1

        self.mantissa = self.mantissa[:place]
        self.__resolve()

    def trim(self):
        # remove trailing zeroes for cleaner looking numbers
        self.integer = self.integer.trim()
        self.mantissa = self.mantissa.trim()

    def primitive(self):
        output = sum([self.integer[k].primitive() * self.base ** k for k in range(len(self.integer))])
        output += sum([self.mantissa[k].primitive() * self.base ** (-k - 1) for k in range(len(self.mantissa))])
        return output
