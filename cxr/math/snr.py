from cxr.math.base64 import Tridozenal as Td
from cxr.math.complex import Complex
import itertools
import random

std_l = 30
NumTypes = (int, float, Td, Complex)

def set_std_l(n: int):
    global std_l
    if n > 0:
        std_l = n
    return std_l


def check_seq(f):
    """
    Auxiliary method which checks inputs to Seq methods

    Ensures that the numerical input is translated to a Seq object

    :param f: the function to be decorated
    """
    def wrapper(self, o=None):
        if o is None:
            return f(self, None)
        elif isinstance(o, NumTypes):
            return f(self, Seq(o))
        elif isinstance(o, list):
            for e in o:
                if not isinstance(e, NumTypes):
                    raise ValueError(f"Unsupported type {type(o)}")
            return f(self, Seq(o))
        elif isinstance(o, Seq):
            return f(self, o)
        elif isinstance(o, Sig):
            return f(self, o.seq)
        elif isinstance(o, Matrix) and f.__name__ == "__mul__":
            return f(self, o)
        else:
            raise ValueError(f"Unsupported type {type(o)}")

    wrapper.__name__ = f.__name__
    return wrapper


def check_sig(f):
    """
    Auxiliary method which checks inputs to Sig methods

    Ensures that the numerical input is translated to a Sig object

    :param f: the function to be decorated
    """

    def wrapper(self, o):
        if o is None:
            return f(self, Sig(Seq()))
        elif isinstance(o, NumTypes):
            return f(self, Sig(Seq(o)))
        elif isinstance(o, list):
            for e in o:
                if not isinstance(e, NumTypes):
                    raise ValueError(f"Unsupported type {type(e)}")
            return f(self, Sig(Seq(o)))
        elif isinstance(o, Seq):
            return f(self, Sig(o))
        elif isinstance(o, Sig):
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
    def __validate(lst: list[NumTypes]) -> bool:
        """
        Ensures a list contains a valid set of values before setting it in __init__
        """
        if not lst:
            return True
        t = type(lst[0])
        the_base = None
        if t is Td:
            the_base = lst[0].base
        else:
            t = (int, float, Complex)
        for e in lst[1:]:
            if not isinstance(e, t):
                print(lst)
                raise TypeError(f"Type mismatch for Seq: {t} and {type(e).__name__}")
            if t is Td:
                if e.base != the_base:
                    raise ValueError(f"Base mismatch: {e.base} and {the_base}")
        return True

    def __init__(self, *elements):
        if len(elements) == 1:
            elements = elements[0]
        else:
            elements = list(elements)

        if elements is None:
            self.elements = []
        elif isinstance(elements, NumTypes):
            self.elements = [elements]
        elif isinstance(elements, (list, tuple)):
            self.elements = []
            Seq.__validate(elements)
            for v in elements:
                if isinstance(v, float):
                    int_v = int(v)
                    self.elements.append(int_v if int_v == v else v)
                else:
                    self.elements.append(v)

        elif isinstance(elements, Seq):
            self.elements = list(elements.elements)
        elif isinstance(elements, Sig):
            self.elements = list(elements.seq.elements)
        else:
            raise ValueError(f"Unsupported type {type(elements).__name__}")

    @check_seq
    def __add__(self, o) -> "Seq":
        if isinstance(o, NumTypes):
            return self + Seq(o)
        elif isinstance(o, Seq):
            length = max(len(self), len(o))
            out = [self[k] + o[k] for k in range(length)]
            return Seq(out)
        else:
            raise ValueError(f"Unsupported type {type(o)}")

    @check_seq
    def __eq__(self, o):
        if o is None or not isinstance(o, Seq):
            return False
        elif len(self.trim()) != len(o.trim()):
            return False
        return all(self[k] == o[k] for k in range(len(self.trim())))

    @check_seq
    def __ge__(self, o):
        return self.elements >= o.elements

    def __getitem__(self, i):
        if isinstance(i, int):
            if len(self) == 0:
                return 0
            if i < 0:
                return self[i % len(self)]
            else:
                if self.elements:
                    if len(self) > i:
                        return self.elements[i]
                    else:
                        return Td.zero(self.elements[0].base) if isinstance(self.elements[0], Td) else 0
                else:
                    return 0
        elif isinstance(i, slice):
            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else len(self)

            if stop < 0:
                stop = len(self) + stop

            step = i.step if i.step is not None else 1
            if step < 0:
                start, stop = stop - 1, start - 1
            zero = Td.zero(self.base()) if self.is_td() else 0
            return Seq([self.elements[k] if len(self) > k >= 0 else zero for k in range(start, stop, step)])

    @check_seq
    def __gt__(self, o):
        return self.elements > o.elements

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
        return iter(self.elements)

    @check_seq
    def __le__(self, o):
        return self.elements <= o.elements

    def __len__(self):
        return len(self.elements)

    @check_seq
    def __lt__(self, o):
        return self.elements < o.elements

    def __mod__(self, o):
        if isinstance(o, int):
            return Seq([k % o for k in self])

    @check_seq
    def __mul__(self, o):
        """
        Improved multiplication using the Karatsuba algorithm
        """
        if isinstance(o, Matrix):
            return o * self
        elif isinstance(o, NumTypes):
            return Seq([a * o for a in self])
        elif self == Seq(0) or o == Seq(0) or (self.is_td() and self == Seq(Td.zero(self.base()))) or (o.is_td() and self == Seq(Td.zero(o.base()))):
            return Seq(Td.zero(self.base()) if self.is_td() else 0)
        elif len(self) < 25 and len(o) < 25:
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


            pt0 = [Td.zero(self.base()) if self.is_td() else 0] * m * 2
            pt0.extend(z2)
            pt0 = Seq(pt0)
            pt1 = [Td.zero(self.base()) if self.is_td() else 0] * m
            pt1.extend(z1)
            pt1 = Seq(pt1)
            return pt0 + pt1 + z0

    @check_seq
    def __school_mul__(self, o):
        """
        Former arithmetic method - used for smaller numbers where Karatsuba is unnecessary
        """
        if isinstance(o, Matrix):
            return o * self
        elif isinstance(o, NumTypes):
            return Seq([a * o for a in self])
        length = len(self) + len(o) - 1
        r = [sum(self[k] * o[n - k] for k in range(n + 1)) for n in range(length)]
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

    def __setitem__(self, key: int, value: NumTypes):
        self.elements[key] = value

    @check_seq
    def __sub__(self, o):
        return self + o.neg()

    def __str__(self):
        return ", ".join([str(n) for n in self.trim().elements])

    def __truediv__(self, o):
        if isinstance(o, NumTypes):
            o = Seq(o)

        # Remove leading zeroes, which is basically factoring out x
        temp_self = Seq(list(self.elements))
        temp_o = Seq(list(o.elements))
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
            return Seq(0)

        r = Seq(temp_self[0]/temp_o[0])

        # Tds are computationally expensive, so limit their size
        if isinstance(r[0], Td):
            length = max([len(temp_self), len(temp_o)])
        else:
            length = std_l
        for n in range(1, length):
            r.append((temp_self[n] - sum(r[k] * temp_o[n-k] for k in range(n))) / temp_o[0])
        r = ([k if isinstance(k, (Td, Complex)) else int(k) if int(k) == k else k for k in r])
        return Seq(r).trim()

    def aerate(self, a: int=2) -> "Seq":
        """
        Transform a sequence into its aerated version
        Eg [1, 1] to [1, 0, 1] or [1, 1, 1] to [1, 0, 0, 1, 0, 0, 1]

        :param a: the aeration coefficient
        :return: the aerated sequence
        """
        if a == 1:
            return self
        out = Seq([0 for k in range(len(self) * a)])
        for k in range(0, len(self) * a, a):
            out[k] = self[k // a]
        return out

    def append(self, v: NumTypes):
        """
        Add a value to the end of the sequence

        :param v: the value to be added
        """
        if self.elements:
            if isinstance(self.elements[0], (int, float)) and not isinstance(v, (int, float)):
                raise ValueError(f"Seq contains {type(self.elements[0]).__name__}, not {type(v).__name__}")
        self.elements.append(int(v) if int(v) == v else v)

    def base(self) -> int:
        if self.is_td():
            return self[0].base
        else:
            return 10

    def concat(self, other) -> "Seq":
        return Seq(self.elements + other.elements)

    def dot_product(self, other: "Seq") -> int:
        l = min(len(self), len(other))
        out = Td.zero(self.base()) if self.is_td() else 0
        for i in range(l):
            out += self[i] * other[i]
        return out

    def partial_dot_product(self, other: "Seq") -> "Seq":
        """
        The results of Matrix.dot_product without being summed at the end
        """
        l = min(len(self), len(other))
        out = Seq()
        for i in range(l):
            out.append(self[i]*other[i])
        return out

    def f(self, l: int=-1, seed = None) -> "Seq":
        """
        The recursive signature function

        :param l: the length of the sequence
        :param seed: an alternate beginning to the sequence
        :return: the sequence F_d
        """
        if l == -1:
            l = std_l
        if seed:
            r = Seq(seed)
        else:
            if self.is_td():
                r = Seq(Td.one(self.base()))
            else:
                r = Seq(1)
        l_r = len(r)
        for x in range(l_r, l):
            if self.is_td():
                n = Td.zero(self.base())
            else:
                n = 0
            for k in range(len(self)):
                if x-k-1 < 0:
                    break
                else:
                    n += self[k] * r[x-k-1]
            r.append(n)
        return r

    def f_generator(self, l: int=-1, seed = None):
        """
        The recursive signature function

        :param l: the length of the sequence
        :param seed: an alternate beginning to the sequence
        :return: the sequence F_d
        """
        if l == -1:
            l = std_l
        if seed:
            r = Seq(seed)
        else:
            if self.is_td():
                r = Seq(Td.one(self.base()))
            else:
                r = Seq(1)
        l_r = len(r)
        for x in range(l_r, l):
            if self.is_td():
                n = Td.zero(self.base())
            else:
                n = 0
            for k in range(len(self)):
                if x-k-1 < 0:
                    break
                else:
                    n += self[k] * r[x-k-1]
            r.append(n)
            yield n
        return r

    def i(self) -> "Seq":
        """
        The inverse signature function
        Only works for sequences which begin with 1

        :return: the sequence F^(-1)_d
        """
        if self.is_td():
            if self[0] != Td.one(self.base()):
                raise ValueError(f"non-invertible: Td is {self[0]}, not 1")
        elif self[0] != 1:
            raise ValueError("non-invertible: arg d must begin with 1")
        r = Seq(self[1])
        for x in range(2, len(self)):
            n = self[x]
            for k in range(1, x):
                n -= r[k-1] * self[x-k]
            r.append(n)
        return r.trim()

    def is_td(self) -> bool:
        if len(self) == 0:
            return False
        return isinstance(self[0], Td)

    def neg(self) -> "Seq":
        """
        Converts the given sequence to its additive inverse
        """
        out = [-k for k in self]
        return Seq(out)

    def polynomial(self, var: str="x", fps: bool=False, use_ss: bool=False) -> str:
        """
        Represent the sequence as a polynomial

        :param var: The variable name to use
        :param fps: Whether the polynomial is a formal power series
        :param use_ss: Whether or not to use superscripts
        """
        def is_lt_zero(n):
            if isinstance(n, Td):
                return n < Td.zero(n.base)
            return n < 0

        output = ""
        if use_ss:
            ss = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        for i in range(len(self)) if fps else range(len(self) - 1, -1, -1):
            if self[i] != 0:
                if use_ss:
                    t = var if i == 1 else (var + "".join([ss[int(j)] for j in str(i)])) if i != 0 else ""
                else:
                    t = var if i == 1 else f"{var}^{i}" if i != 0 else ""
                si = self[i] if fps else self[len(self) - i - 1]
                if si != 0:
                    if fps and i == 0:
                        output = str(si)
                    elif not fps and i == len(self) - 1:
                        if isinstance(si, Complex):
                            output = f"({si}){t}"
                        else:
                            output = f"{si}{t}" if si != 1 else t
                    else:
                        if isinstance(si, Complex):
                            output += f" + ({si}){t}"
                        else:
                            is_td = isinstance(si, Td)
                            if ((is_td and si.abs() == Td.one(si.base)) or (not is_td and abs(si) == 1)) and t:
                                output += f" - {t}" if is_lt_zero(si) else f" + {t}"
                            else:
                                output += f" - {si.abs() if is_td else abs(si)}{t}" if is_lt_zero(si) else f" + {si}{t}"
        return output

    def pop(self, index: int=0):
        return self.elements.pop(index)

    def reverse(self) -> "Seq":
        return Seq(self.elements[::-1])

    def sig(self) -> "Sig":
        return Sig(self)

    def sqrt(self, l: int=-1) -> "Seq":
        """
        Computes the square root of the sequence
        :param l: the length of the output
        :return: the square root
        """
        if l == -1:
            l = std_l
        output = Seq(self[0].root(2) if self.is_td() else float(Td(self[0], base=10).root(2)))
        for n in range(1, l):
            _diff = self[n]
            for k in range(1, n):
                _diff -= output[n-k] * output[k]
            _diff /= 2 * output[0]
            output.append(_diff)
        return output

    def trim(self, to_zero: bool=False) -> "Seq":
        """
        Removes trailing zeroes from a sequence

        :param to_zero: Whether to reduce the sequence to at most length 1 (False) or length 0 (True)
        """
        out = list(self.elements)
        while len(out) > (0 if to_zero else 1):
            current_val = out[-1]
            if isinstance(current_val, Td):
                if current_val.abs() == Td.zero(current_val.base):
                    out.pop(-1)
                else:
                    break
            elif current_val == Complex():
                out.pop(-1)
            elif current_val == 0:
                out.pop(-1)
            else:
                break
        return Seq(out)

    def td(self, base: int=-1) -> "Seq":
        """
        Converts the sequence into a sequence of base64 numbers
        :param base: the new base of the sequence
        :return: the updated sequence
        """
        if self.is_td():
            return self
        else:
            return Seq([Td(k, base=base) for k in self])


x = Seq(0, 1)


class Sig:
    """
    The Sig class implements the signature left near-ring's
    operations of signature addition and signature convolution.
    """

    def __init__(self, *seq):
        if len(seq) == 1:
            seq = seq[0]
        else:
            seq = list(seq)

        if seq is None:
            self.seq = Seq()
        elif isinstance(seq, NumTypes):
            self.seq = Seq(seq)
        elif isinstance(seq, list):
            self.seq = Seq(seq)
        elif isinstance(seq, Seq):
            self.seq = Seq(list(seq.elements))
        elif isinstance(seq, Sig):
            self.seq = Seq(list(seq.seq.elements))
        else:
            raise ValueError(f"Unsupported type {type(seq)}")

    @check_sig
    def __add__(self, o):
        return Sig(self.seq + o.seq - x * self.seq * o.seq)

    @check_sig
    def __eq__(self, o):
        return self.seq == o.seq

    @check_sig
    def __floordiv__(self, b):
        """Computes the non-distributive left-inverse of multiplication"""
        l = max(len(self), len(b))
        s = Seq(self[0] / b[0])
        block = ([Seq(s**(x+1)) for x in range(l)])

        for x in range(1, l):
            v = [(block[k][x - k]) * (b[k]) for k in range(1, x + 1)]
            v = (self[x] - sum(v)) / b[0]
            block[0].append(v)
            for k in range(1, l):
                block[k].append(sum([block[0][len(block[0])-t-1] * block[k-1][t] for t in range(len(block[0]))]))
        out = block[0].elements
        return Sig(out).trim()

    @check_sig
    def __ge__(self, o):
        return self.seq >= o.seq

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.seq[i]
        elif isinstance(i, slice):
            return self.seq[i].sig()

    @check_sig
    def __gt__(self, o):
        return self.seq > o.seq

    @check_sig
    def __iadd__(self, o):
        return self + o

    @check_sig
    def __imul__(self, o):
        return self * o

    @check_sig
    def __isub__(self, o):
        return self - o

    def __iter__(self):
        return iter(self.seq)

    @check_sig
    def __le__(self, o):
        return self.seq <= o.seq

    def __len__(self):
        return len(self.seq)

    @check_sig
    def __lt__(self, o):
        return self.seq < o.seq

    @check_sig
    def __mul__(self, o):
        is_td = self.is_td()
        if is_td:
            base = self.base()
            out = Seq(o[0])
            g = Seq(Td.one(base))
        else:
            out = Seq(o[0])
            g = Seq(1)
        a = self.seq
        aw = a * x
        for k in range(1, len(o)):
            g *= aw
            out += g * o[k]
        out *= a
        return Sig(out)

    def __neg__(self):
        return Sig(-self.seq)

    def __pow__(self, power: int, modulo=None):
        out = Sig(Td.one(self.base()) if self.is_td() else 1)
        a = Sig(self)
        for k in range(power):
            out *= a
        return out

    @check_sig
    def __radd__(self, o):
        return o + self

    @check_sig
    def __rmul__(self, o):
        return o * self

    @check_sig
    def __rsub__(self, o):
        return o - self

    def __setitem__(self, key: int, value: (int, float)):
        self.seq[key] = value

    @check_sig
    def __sub__(self, o):
        return Sig((self.seq - o.seq) * o.f())

    def __str__(self):
        return ", ".join([str(n) for n in self.trim().seq])

    @check_sig
    def __truediv__(self, a):
        """Computes the distributive right-inverse of multiplication"""
        out = []
        ap = Seq(self)
        bp = Seq(a)
        l = max(len(self), len(a), std_l)
        for n in range(l):
            out.append(ap[n] / bp[n])
            ap -= bp*out[n]
            bp *= x * a
        return Sig(out).trim()

    def aerate(self, a: int) -> "Sig":
        return Sig(self.seq.aerate(a))

    def append(self, i: NumTypes):
        """
        Add a value to the end of the sequence
        """
        self.seq.append(i)

    def base(self) -> int:
        """
        Gets the base of the signature
        """
        return self.seq.base()

    def f(self, l: int=-1, seed=None) -> "Sig":
        """
        The recursive signature function

        :param l: the length of the sequence
        :return: the signature F_d
        """
        return self.seq.f(l=l if l != -1 else std_l, seed=seed).sig()

    def first_nonzero(self) -> int:
        """
        Get the position of the first non-zero digit of the signature
        """
        for e in range(1, len(self)):
            if self[e] != 0:
                return e
        return -1

    def i(self) -> "Sig":
        """
        The inverse signature function
        Only works for sequences which begin with 1

        :return: the signature F^(-1)_d
        """
        return Sig(self.seq.i())

    def is_td(self) -> bool:
        """
        :return: whether or not the sequence contains arbitrary-base numbers from base64
        """
        return self.seq.is_td()

    def iter_add(self, n: int) -> "Sig":
        """
        Perform iterated signature addition of the signature
        :param n: the number of times to add the signature
        """
        out = Sig(Td.zero(self.base()) if self.is_td() else 0)
        if n == 0:
            return out
        else:
            for k in range(n if n > 0 else -n):
                if n < 0:
                    out -= Sig(self.seq)
                else:
                    out += Sig(self.seq)
            return out

    def multiplicative_inverse(self, l: int=-1) -> "Sig":
        """
        Computes the inverse of d
        This is technically computing a left inverse,
        but the left and right inverses are equal,
        and this is the faster of the two.

        To prevent being caught in an infinite loop due to floating point errors,
        this process will halt when the inverse stops increasing in size. This
        results in incomplete inverses. The easiest way to avoid this
        is to make d one-beginning

        :param l: The length of the output
        :return: the multiplicative inverse of the signature
        """
        # This is the fast one, see below comment
        inverse = Seq(1 / self[0])
        length_of_previous_inverse = 0
        length_of_current_inverse = -1

        if l == -1:
            l = std_l

        while len(inverse) < l and length_of_previous_inverse != length_of_current_inverse:
            product = (Sig(inverse) * self)[:l]
            x_pow = product.first_nonzero()

            inverse -= ((x ** x_pow) * product[x_pow]) / self[0]
            length_of_previous_inverse = length_of_current_inverse
            length_of_current_inverse = len(inverse)

        return Sig(inverse)[:length_of_current_inverse]

    def neg(self) -> "Sig":
        """
        Converts the given sequence to its additive inverse
        """
        return -self

    def reverse(self) -> "Sig":
        return Sig(self.seq.reverse())

    def trim(self) -> "Sig":
        """
        Removes trailing zeroes from a sequence
        """
        return Sig(self.seq.trim())


class Matrix:
    """
    The Matrix class allows for the construction of various
    matrices in order to experiment with antidiagonal summation
    """

    @staticmethod
    def blank(l: int=-1, w: int=-1, base: int=-1) -> "Matrix":
        """
        Generates a matrix consisting entirely of zeroes

        :param l: the length and width of the matrix
        :return: a blank matrix
        """
        if l == -1:
            l = std_l
        if w == -1:
            w = std_l
        if base != -1:
            zero = Td.zero(base)
        else:
            zero = 0
        return Matrix([Seq([zero for k in range(w)]) for n in range(l)])

    @staticmethod
    def g_matrix(s: "Matrix", g: list[Seq], l: int=-1, w: int=-1) -> "Matrix":
        """
        The matrix S_d^p is defined in section 4.5 of SNR

        :param s: the initial matrix to be transformed
        :param g: the set of signatures to transform s
        :return: the transformed matrix S_d^p
        """

        def generate_next_matrix(s_prev: "Matrix", g_p: Seq) -> "Matrix":
            """
            Generate the next matrix S_d^p

            :param s_prev: the matrix to be transformed
            :param g_p: the transforming signature
            :return: the transformed matrix
            """
            f_g_p = g_p.f(l)
            out = Matrix.blank(l, w, base=f_g_p.base() if f_g_p.is_td() else -1)

            zero = Td.zero(f_g_p.base()) if f_g_p.is_td() else 0
            for n in range(l):
                for y in range(w):
                    _sum = zero
                    for k in range(n + 1):
                        _sum += s_prev[k][y] * f_g_p[n - k]
                    out[n][y] = _sum

            return out

        s_next = s

        if l == -1:
            l = std_l
        if w == -1:
            w = std_l

        for g_p in g:
            s_next = generate_next_matrix(s_next, g_p)

        return s_next

    @staticmethod
    def identity(l: int=-1, base: int=-1) -> "Matrix":
        """
        The identity matrix. Also M^0 for a matrix M

        :param l: the length of the matrix
        :return: the identity matrix
        """
        if l == -1:
            l = std_l
        out = Matrix.blank(l=l, w=l, base=base)
        one = Td.one(base) if base != -1 else 1
        for n in range(l):
            out[n][n] = one
        return out

    @staticmethod
    def power(d: Seq, l: int=-1, w: int=-1, taper: bool=False) -> "Matrix":
        """
        The power triangle d^n_y

        :param d: the sequence base of the triangle
        :param l: the length of the triangle
        :param taper: whether or not to extend the triangle in a way amenable to antidiagonal summation
        :return: the power triangle of d
        """
        d = Seq(d)
        if l == -1:
            l = std_l
        if w == -1:
            w = l * (len(d) - 1) + 1
        if d.is_td():
            out = [Seq(Td.one(d.base()))]
        else:
            out = [Seq(1)]
        for k in range(1, l):
            out.append((out[-1] * d)[:w])
        # Tapering maximizes efficiency of computing f()
        if taper:
            t = len(out[-1].trim()) - 1
            for k in range(t):
                out.append((out[-1] * d)[:t - k])
        return Matrix(out)

    @staticmethod
    def sen(d: Seq, l: int=-1, w: int=-1) -> "Matrix":
        """
        The initial triangular matrix in 4.5

        :param d: the generating sequence for the matrix
        :param l: the length of the matrix
        :return: the generated sen matrix
        """
        if l == -1:
            l = std_l
        if w == -1:
            w = std_l
        if l == 1:
            if d.is_td():
                return Matrix(Seq(Td.one(d.base())))
            else:
                return Matrix(Seq(1))

        if d.is_td():
            b = Matrix.blank(l, base=d.base())
        else:
            b = Matrix.blank(l)

        if d.is_td():
            b[0] = Seq(Td.one(d.base()))
        else:
            b[0] = Seq(1)

        b[1] = Seq(d[0] - 1)

        for n in range(2, l):
            b[n] = d[:n:-1][:w]
        return b

    @staticmethod
    def riordan(s: Seq, d: Seq, l: int=-1, left: bool=False) -> "Matrix":
        """
        Construct a Riordan array

        :param s: the sequence which fills the first column
        :param d: the recurrence relation for each row
        :param l: the length of the matrix
        :return: the riordan matrix
        """
        if l == -1:
            l = std_l

        if l == 1:
            if s.is_td():
                return Matrix(Seq(Td.one(s.base())))
            else:
                return Matrix(Seq(1))

        if s.is_td():
            b = Matrix.blank(l, base=s.base())
        else:
            b = Matrix.blank(l)


        if s.is_td():
            b = [Seq(Td.one(s.base())), Td([1, 1], base=s.base())]
        else:
            b = [Seq(1), Seq(s[1], s[0]*d[0])]

        for i in range(2, l):
            to_add = Seq(s[i])
            for k in range(1, i+1):
                to_add.append(b[-1][k-1:k+len(d)-1].dot_product((d)[::-1]))
            b.append(to_add)

        return Matrix(b)

    def __init__(self, *rows):
        if len(rows) == 1:
            rows = rows[0]
        else:
            rows = list(rows)

        self.rows = []
        if rows is None:
            self.rows.append(Seq(0))
        elif isinstance(rows, (int, float)):
            self.rows.append(Seq(int(rows) if int(rows) == rows else rows))
        elif isinstance(rows, Td):
            self.rows.append(Seq(rows))
        elif isinstance(rows, list):
            for e in rows:
                if isinstance(e, (Seq, Sig)):
                    self.rows.append(Seq(e))
                elif isinstance(e, list):
                    self.rows.append(Seq(e))
        elif isinstance(rows, Seq):
            self.rows.append(rows)
        elif isinstance(rows, Sig):
            self.rows.append(rows.seq)
        elif isinstance(rows, Matrix):
            self.rows = rows.rows
        else:
            raise ValueError(f"Unsupported type {type(rows)}")

    def __add__(self, other: "Matrix"):
        length = max(len(self), len(other))
        width = max(self.width(), other.width())
        out = Matrix([Seq([0 for k in range(width)]) for x in range(width)])
        for x in range(length):
            for y in range(width):
                out[x][y] = self[x][y] + other[x][y]
        return out

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        if len(self) != len(other):
            return False
        for n in range(len(self)):
            if self[n] != other[n]:
                return False
        return True

    def __getitem__(self, i: [int, slice]):
        if isinstance(i, int):
            if i < 0:
                return self[len(self) + i]
            else:
                return self.rows[i] if len(self) > i else Seq(Td.zero(self.rows[0].base()) if self.rows[0].is_td() else 0)
        elif isinstance(i, slice):
            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else len(self)

            if stop < 0:
                stop = len(self) + stop

            step = i.step if i.step is not None else 1
            if step < 0:
                start, stop = stop - 1, start - 1

            return Matrix([self[k] for k in range(start, stop, step)])

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __mod__(self, modulo):
        return Matrix([s % modulo for s in self])

    def __mul__(self, other):
        if isinstance(other, (Seq, int, float)):
            return Matrix([other * g for g in self])
        elif isinstance(other, Sig):
            return Matrix([Seq(Sig(g) * other) for g in self])
        elif isinstance(other, Matrix):
            width = max(self.width(), other.width())
            length = max(len(self), len(other))
            out = Matrix.blank(length, width, self[0].base())
            other_t = other.transpose()
            for n in range(length):
                for y in range(width):
                    out[n][y] = self[n].dot_product(other_t[y])
            return out.trim()
        else:
            raise ValueError(f"Incompatible type {type(other)}; must be int, float, Seq, or Matrix")

    def __pow__(self, power: int, modulo=None):
        if power == 0:
            return Matrix.identity(len(self))
        out = self[:]
        for k in range(1, power):
            out = out * self
        return out

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        out = ""
        for e in self.trim():
            out += str(e) + "\n"
        return out

    def __setitem__(self, key: int, value):
        if isinstance(value, int):
            self.rows[key] = Seq(value)
        else:
            self.rows[key] = Seq(*value)

    def __sub__(self, other: "Matrix"):
        return (self + other.neg()).trim()

    def __truediv__(self, num):
        if isinstance(num, (int, Seq)):
            out = []
            for n in range(len(self)):
                out.append(self[n] / num)
            return Matrix(out)
        else:
            raise ValueError(f"Incompatible type {type(num).__name__}; must be int or Seq")

    def append(self, line: Seq):
        """
        Adds a line to the end of the block

        :param line: the line to be added to the block
        """
        self.rows.append(line)

    def base_sequence(self, b: int) -> Seq:
        """
        Interprets each row as a base-b number, and returns a sequence
        where a(n) = M(n)_b

        This only works for non-Td matrices at present. I'll add it eventually.
        :param b: the base to interpret the matrix in
        :return: the matrix's base sequence
        """
        if self.rows and self.rows[0].is_td():
            raise TypeError(f"Cannot construct base sequence from Td matrix at present.")
        if b == 0:
            return Seq([row.trim()[-1] for row in self])
        elif b == 1:
            output = Seq()
            for row in self:
                output.append(sum(row))
            return output
        else:
            output = Seq()
            for row in self:
                output.append(int(Td(row.trim().elements, base=b)))
            return output

    def column(self, c: int) -> Seq:
        return Seq([self[n][c] for n in range(len(self))])

    def column_slice(self, start: int, stop: int, step: int) -> "Matrix":
        return Matrix([self[n][start:stop:step] for n in range(len(self))])

    def diagonalise(self, direction: bool=True) -> "Matrix":
        """
        Construct a matrix using the diagonals of the given matrix

        :param direction: whether to go from top-right to bottom-left (True) or the other way
        :return: the diagonalised matrix
        """
        output = Matrix.blank(len(self), len(self))
        for n in range(len(self)):
            for k in range(n + 1):
                if direction:
                    output[n][k] = self[n - k][k]
                else:
                    output[n][k] = self[k][n - k]
        return output

    def f(self, a: int=1, g: Seq=Seq(1)) -> Seq:
        """
        Enables aerated signature convolution
        Defaults to plain signature function

        :param a: the aeration coefficient
        :param g: the signature convolution coefficient
        :return: the sequence result of antidiagonal summation
        """
        g_f = g.f(len(self))
        out = Seq([0 for k in range(len(self))])
        for n in range(len(self)):
            _sum = 0
            for k in range(n+1):
                if n-a*k < 0:
                    break
                else:
                    _sum += self[n-a*k][k] * g_f[n-a*k]
            out[n] = _sum
        return out

    def i(self, a: int=1, g: Seq=Seq(1)) -> Seq:
        """
        Performs signature function then inverse signature function

        :param a: the aeration coefficient for f()
        :param g: the signature convolution coefficient for f()
        :return: the sequence result of the operation
        """
        return self.f(a, g).i()

    def reverse(self) -> "Matrix":
        return Matrix([self[n].trim()[::-1] for n in range(len(self))])

    def sieve(self, sieve_factor: int) -> "Matrix":
        return Matrix([self[i][::sieve_factor] for i in range(len(self))])

    def transpose(self) -> "Matrix":
        l = max([len(self)] + [len(row) for row in self])
        return Matrix([Seq([self[k][n] for k in range(len(self))]) for n in range(l)])

    def transposition_product(self, other: "Matrix") -> "Matrix":
        return self * other.transpose()

    def trim(self) -> "Matrix":
        """
        Remove trailing zero sequences from the matrix
        :return: the trimmed matrix
        """
        out = self
        while len(out) > 0:
            if len(out[-1].trim(to_zero=True)) == 0:
                out = out[:-1]
            else:
                return out
        return out

    def neg(self) -> "Matrix":
        out = [-v for v in self]
        return Matrix(out)

    def truncate(self, l: int) -> "Matrix":
        out = Matrix([s[:l] for s in self.rows[:l]])
        return out

    def width(self) -> int:
        return max([len(k) for k in self.rows])


def num_dims(d) -> int:
    """
    Count the number of dimensions in a matrix or prism
    :param d: the multi-dimensional object
    :return: the number of dimensions
    """
    if isinstance(d, NumTypes):
        return 1
    output = 1
    tmp = d
    while True:
        tmp = tmp[0]
        if not isinstance(tmp, NumTypes):
            output += 1
        else:
            break
    return output


class Prism:

    @staticmethod
    def blank(dim: int=4, l: int=-1, w: int=-1) -> "Prism":
        """
        Create a blank prism
        :param dim: the number of dimensions of the prism
        :param l: the length of each matrix in the prism
        :param w: the width of each matrix in the prism
        :return:
        """
        if l == -1:
            l = std_l
        if w == -1:
            w = std_l
        if dim == 1:
            return Seq([0] * l)
        if dim == 2:
            return Prism(Matrix.blank(l=l, w=w))

        output = []
        for i in range(l):
            output.append(Prism.blank(dim=dim-1, l=l, w=w))
        return Prism(output)

    @staticmethod
    def canonical(ds: list[Seq], l: int=5, coordinates=None, current=None) -> "Prism":
        """
        Produces a canonical one-beginning object whose dimensions express the given list of signatures

        :param ds: The signatures to express
        :param l: The length of each dimension
        :param coordinates: current location within the structure; do not set manually
        :param current: the current sub-Prism being used in recursive calculations; do not set manually
        :return: the canonical prism
        """

        if len(ds) == 1:
            return Prism(Matrix.power(ds[0], l))

        output = []

        if current is None:
            current = Matrix.power(ds[0], l=l)
            for i in range(len(ds) - 1):
                current = Prism([current] * l)

        if coordinates is None:
            coordinates = []

        if len(coordinates) == len(ds) - 1:
            output = Seq(1)
            for i, d in enumerate(ds[1:]):
                output *= d ** coordinates[i]
            return Prism(output * current)
        else:
            for n in range(l):
                get = Prism.canonical(ds, l, coordinates + [n], current[n])
                output.append(get)
        return Prism(output)

    @staticmethod
    def power(d: Seq, dim: int=4, l: int=10, coordinates=None, block=None) -> "Prism":
        """
        The canonical one-beginning object in higher dimensions

        :param d: The signature base of the structure
        :param dim: The number of dimensions of the structure
        :param l: The length of the output
        :param coordinates: current location within the structure; do not set manually
        :param block: For memoization purposes; do not set manually
        :return: The N-dimensional canonical object
        """
        out = []

        if not block:
            block = Matrix.power(d, l)

        if not coordinates:
            coordinates = []

        if dim == 1:
            return block.f()
        elif dim == 2:
            return Prism(d ** (sum(coordinates)) * block)

        else:
            for n in range(l):
                out.append(Prism.power(d, dim=dim - 1, l=l, coordinates=coordinates + [n], block=block))
        return Prism(out)

    @staticmethod
    def g_prism(d: list[Seq], g: list[Seq], l: int=10) -> "Prism":
        """
        Construct a G-prism, as outlined in SNR 2.2.4
        :param d: The signatures used to construct right operands
        :param g: The signatures which are used to construct left operands
        :param l: the length of the G-prism
        :return: the constructed G-prism
        """

        g = [g_n.f() for g_n in g]
        d = [Matrix.power(d_n, l=l) for d_n in d]

        output = Prism.blank(dim=len(d) + len(g) + 1, l=l)
        prev = None
        prev_prod = None
        l_g = len(g)
        for coordinates in itertools.product(range(l), repeat=len(d)+len(g)):
            skip_g_multiplication = True
            if prev is not None and prev_prod is not None:
                if prev == coordinates[:l_g]:
                    g_prod = prev_prod
                else:
                    skip_g_multiplication = False
            else:
                skip_g_multiplication = False

            if not skip_g_multiplication:
                tmp = [g[i][:coord + 1] for i, coord in enumerate(coordinates[:l_g])]
                g_prod = 1
                for t in tmp:
                    g_prod *= t
                prev_prod = g_prod

            obj = output
            for c in coordinates[:-1]:
                obj = obj[c]

            d_prod = 1
            for i, coord in enumerate(coordinates[l_g:]):
                d_prod *= d[i][coord]
            obj[coordinates[-1]] = g_prod * d_prod
            prev = coordinates[:l_g]
        return output

    @staticmethod
    def simplex(d: list[Seq], l: int=10) -> "Prism":
        """
        Construct an arbitrary-dimensional simplex prism
        :param d: the 2-digit sequences to construct the simplex with
        :param l: the length of the simplex
        :return: the constructed simplex
        """
        if len(d) < 2:
            raise ValueError(f"Can only construct simplex with 2 or more signatures.")
        if any([len(d_n) != 2 for d_n in d]):
            raise ValueError(f"Can only construct simplex with signatures of length 2.")
        m = [Matrix.power(d_n, l) for d_n in d]
        p = Prism.blank(dim=len(m) + 1, l=l, w=l)

        def get(coords):
            output = p
            for coord in coords:
                output = output[coord]
            return output

        prev = None
        prev_prod = None
        for r_n in itertools.product(range(l), repeat=len(m) + 1):
            prod = 1
            obj = get(r_n[:-1])
            skip_multiplication = False
            if prev is not None and prev_prod is not None:
                if prev == r_n[:-1]:
                    skip_multiplication = True
                    prod = prev_prod

            if not skip_multiplication:
                for i, r_s in enumerate(zip(r_n, r_n[1:-1])):
                    prod *= m[i][r_s[0]][r_s[1]]
            prev_prod = prod
            prod *= m[-1][r_n[-3] - r_n[-2]][r_n[-1]] if r_n[-3] >= r_n[-2] else 0
            obj[r_n[-1]] = prod
            prev = r_n[:-1]

        return p

    def __init__(self, structure, l: int=10):
        if isinstance(structure, Matrix):
            self.val = structure
        elif isinstance(structure, list):
            self.val = structure
        elif isinstance(structure, Prism):
            self.val = structure.val
        elif isinstance(structure, Seq):
            self.val = Matrix.power(structure, l)
        else:
            raise TypeError(f"Prism must be constructed via Matrix, list, or Prism, not {type(structure).__name__}")

    def __getitem__(self, i: [int, slice]):
        if isinstance(i, int):
            return self.val[i]
        elif isinstance(i, slice):

            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else len(self)

            if stop < 0:
                stop = len(self) + stop

            step = i.step if i.step is not None else 1
            if step < 0:
                start, stop = stop - 1, start - 1
            return Prism([self[k] if len(self) > k >= 0 else 0 for k in range(start, stop, step)])

    def __len__(self):
        return len(self.val)

    def __iter__(self):
        return iter(self.val)

    def __mod__(self, modulo):
        dims = num_dims(self)
        if dims == 2:
            return Prism(self.val % modulo)
        else:
            output = Prism.blank(dims, len(self), len(self[0]))
            for i in range(len(self)):
                output[i] = self.val[i] % modulo
            return output

    def __mul__(self, other):
        """
        Takes two Prisms and constructs their prismatic product
        """

        def get(d, coordinates: list[int]):
            output = d
            for k in range(len(coordinates)):
                output = output[coordinates[k]]
            return output

        def nested_array(dims: int, length: int):
            if dims == 2:
                return Matrix.blank(length)
            else:
                output = []
                for k in range(length):
                    output.append(nested_array(dims - 1, length))
                return output

        l = min(len(self), len(other))

        N = num_dims(self)
        K = num_dims(other)

        output = nested_array(N + K - 1, l)

        NK = N + K - 1

        for args in itertools.product(range(l), repeat=NK-1):
            get(output, args[:NK - 2])[args[NK - 2]] = get(self, args[:N-1]) * get(other, args[N - 1: NK - 1])

        return Prism(output)

    def __setitem__(self, key: int, value):
        self.val[key] = value

    def __str__(self):
        if num_dims(self) == 2:
            return str(self.val)
        else:
            output = []
            for i in self:
                if isinstance(i, list):
                    output.append(str(Prism(i)))
                    output.append("---\n")
                else:
                    output.append(str(i))
            while output[-1] == "---\n":
                output.pop(-1)
            return "\n".join(output)

    def f(self, g: list[Seq]=None, a: int=1) -> Seq:
        """
        Performs the general signature function on an N-dimensional structure

        :param g: the signatures to convolve along the antidiagonals
        :param a: the aeration coefficient
        """

        def generate_next(structure, g=None, n: int=0, coordinates: list[int]=None) -> int:
            """
            Generate the next value of the signature function at n

            :param structure: The structure to be examined
            :param n: The index of the signature function
            :param coordinates: Current location within structure; do not set manually
            :return: The value F_(structure) (n)
            """
            if not coordinates:
                coordinates = []

            if isinstance(structure, Seq):
                raise ValueError("General signature function cannot accept Seq")

            elif num_dims(structure) == 2:
                _sum = 0
                sum_coords = sum(coordinates)
                for y in range(len(structure)):
                    if sum_coords + y > n:
                        break
                    for t in range(len(structure[y])):
                        if sum_coords + y + t > n:
                            break
                        elif sum_coords + y + t == n:
                            multiplicand = 1
                            for i in range(len(g) - 1):
                                multiplicand *= g[-i-1][coordinates[i]]
                            multiplicand *= g[0][y]
                            _sum += multiplicand * structure[y][t]
                return _sum

            elif isinstance(structure, (Prism, list)):
                _sum = 0
                sum_coords = sum(coordinates)
                for i, each in enumerate(structure):
                    if sum_coords + i > n:
                        break
                    _sum += generate_next(each, g, n, coordinates + [i])

                return _sum

        aerated_prism = self.aerate(a)

        out = []

        dims = num_dims(self)
        l = len(self)

        if isinstance(g, (Seq, Sig)):
            g = [g]

        if not g:
            g = [Seq([1 for __ in range(l)]) for _ in range(dims - 1)]
        elif len(g) < dims - 1:
            if g[0].is_td():
                g = [sig.f(l) for sig in g] + [Seq(Td.one(g[0].base())).f(l) for _ in range(dims - 1 - len(g))]
            else:
                g = [sig.f(l) for sig in g] + [Seq(1).f(l) for _ in range(dims - 1 - len(g))]
        elif len(g) > dims - 1:
            raise ValueError(f"Number of signatures in g set must be equal to {dims - 1}, not {len(g)}")
        else:
            g = [sig.f(l) for sig in g]

        for n in range(l):
            out.append(generate_next(aerated_prism, g, n))

        return Seq(out)

    def i(self, g: list[Seq]=None) -> Seq:
        """
        Compute the inverse signature function of the prism
        :param g: the signatures to convolve along the antidiagonals
        :return: the signature of the prism
        """
        return self.f(g=g).i()

    def aerate(self, a: int=2) -> "Prism":
        """
        The aeration function of a prism

        Note that a prism can only accept a single aeration coefficient

        :param a: the aeration coefficient
        :return: the aerated Prism
        """
        if a < 1:
            raise ValueError(f"Aeration coefficient must be 1 or greater, not {a}")

        if a == 1:
            return self

        dims = num_dims(self)
        output = []
        for item in self:
            if isinstance(item, Matrix):
                output.append(Matrix([s.aerate(a) for s in item]))
            else:
                output.append(Prism(item).aerate(a))

        return Prism(output)

    def base_prism(self, b: int):
        """
        Construct a prism using base interpretations of rows

        :param b: the base to use in constructing the prism
        """
        dims = num_dims(self)
        if dims == 2:
            return self.val.base_sequence(b)
        elif dims == 3:
            return Matrix([p.base_prism(b) for p in self])
        else:
            return Prism([p.base_prism(b) for p in self])

    def signary_prism(self, s: int, sf=None):
        """
        Constructs a prism using U-representations of rows

        :param s: the signature to use in constructing the prism
        """
        dims = num_dims(self)
        if sf is None:
            sf = s.f(l=len(self))
        if dims == 2:
            return Seq([n.trim()[::-1].dot_product(sf) for n in self.val])
        elif dims == 3:
            return Matrix([p.signary_prism(s, sf) for p in self])
        else:
            return Prism([p.signary_prism(s, sf) for p in self])

    def size(self) -> int:
        output = 1
        k = self[0]
        while not isinstance(k, Matrix):
            output *= len(k)
            k = k[0]
        output *= len(k)
        return output


def signature_dot_product(g: list[Seq], S: list[Seq]) -> Seq:
    if isinstance(g, Seq):
        g = [g]
    if isinstance(S, Seq):
        S = [S]

    while len(S) < len(g):
        S.append(Seq(1))

    while len(g) < len(S):
        g.append(Seq(0))

    return sum([(g[k].sig() * S[k].sig()) for k in range(len(g))]).seq


def g_prism_identity(d: list[Seq], g: list[Seq]):
    alt = Seq(0).sig()
    for d_n in d:
        alt += d_n.sig()
    for g_n in g:
        alt += (x * g_n.aerate(2)).sig() + Seq(1)
    return alt


def simplex_identity(d: list[Seq]):
    if len(d) < 2:
        raise ValueError(f"Can only construct simplex with 2 or more signatures.")
    if any([len(d_n) != 2 for d_n in d]):
        raise ValueError(f"Can only construct simplex with signatures of length 2.")

    N = len(d)
    output = Seq(0)
    for k in range(N-2):
        prod = x**k
        for t in range(k):
            prod *= d[t][1]
        prod *= d[k][0]
        output += prod

    prod = x**(N-2)
    for k in range(N-2):
        prod *= d[k][1]
    for k in range(N-2, N):
        prod *= d[k][0]
    output += prod

    prod = x**(N-1)
    for k in range(N-2):
        prod *= d[k][1]
    output += prod * (d[N-2][0] * d[N-1][1] + d[N-2][1])
    return output


def random_seq(min: int=1, max: int=7, min_digits: int=2, max_digits: int=5) -> Seq:
    if min_digits > max_digits:
        max_digits = min_digits
    return Seq([random.randint(min, max) for _ in range(random.randint(min_digits, max_digits))])


def random_matrix(l: int=10) -> Matrix:
    return Matrix(Seq(1), *[random_seq() for _ in range(l)])
