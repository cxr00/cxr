from cxr.math.base36 import Tridozenal as Td
import itertools
import random

std_l = 30
NumTypes = (int, float, Td)


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
    def __validate(lst: list[NumTypes]):
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
            t = (int, float)
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
    def __add__(self, o):
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
            if i < 0:
                return self.elements[len(self) + i]
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
        elif self == Seq(0) or o == Seq(0):
            return Seq(0)
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


            pt0 = [0] * m * 2
            pt0.extend(z2)
            pt0 = Seq(pt0)
            pt1 = [0] * m
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

    def __setitem__(self, key: int, value: (int, float)):
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
        r = ([k if isinstance(k, Td) else int(k) if int(k) == k else k for k in r])
        return Seq(r).trim()

    def aerate(self, a=2):
        """
        Transform a sequence into its aerated version
        Eg [1, 1] to [0, 1, 0, 1] or [1, 1, 1] to [0, 0, 1, 0, 0, 1, 0, 0, 1]

        :param a: the aeration coefficient
        :return: the aerated sequence
        """
        if a == 1:
            return self
        out = Seq([0 for k in range(len(self) * a)])
        for k in range(0, len(self) * a, a):
            out[k] = self[k // a]
        return out * (x ** (a - 1))

    def append(self, v: (int, float)):
        """
        Add a value to the end of the sequence

        :param v: the value to be added
        """
        self.elements.append(v)

    def base(self):
        if self.is_td():
            return self[0].base
        else:
            return 10

    def concat(self, other):
        return Seq(self.elements + other.elements)

    def f(self, l=-1, seed: "Seq" = None):
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

    def i(self):
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

    def is_td(self):
        return isinstance(self[0], Td)

    def neg(self):
        """
        Converts the given sequence to its additive inverse
        """
        out = [-k for k in self]
        return Seq(out)

    def polynomial(self, var="x", fps=False, use_ss=False):
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
                if fps and i == 0:
                    output = str(si)
                elif not fps and i == len(self) - 1:
                    output = f"{si}{t}" if si != 1 else t
                else:
                    is_td = isinstance(si, Td)
                    if ((is_td and si.abs() == Td.one(si.base)) or (not is_td and abs(si) == 1)) and t:
                        output += f" - {t}" if is_lt_zero(si) else f" + {t}"
                    else:
                        output += f" - {si.abs() if is_td else abs(si)}{t}" if is_lt_zero(si) else f" + {si}{t}"
        return output

    def pop(self, index=0):
        return self.elements.pop(index)

    def reverse(self):
        return Seq(self.elements[::-1])

    def sig(self):
        return Sig(self)

    def trim(self, to_zero=False):
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
            elif current_val == 0:
                out.pop(-1)
            else:
                break
        return Seq(out)

    def td(self, base=-1):
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
        # Commutative signature addition
        return Sig(self.seq + o.seq - x * self.seq * o.seq)

    @check_sig
    def __eq__(self, o):
        return self.seq == o.seq

    @check_sig
    def __floordiv__(self, b):
        """ The non-distributive left-inverse of multiplication"""
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
        # Signature convolution
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

    def __pow__(self, power, modulo=None):
        # Signature convolution powers
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
        """ The distributive right-inverse of multiplication"""
        out = []
        ap = Seq(self)
        bp = Seq(a)
        l = max(len(self), len(a), std_l)
        for n in range(l):
            out.append(ap[n] / bp[n])
            ap -= bp*out[n]
            bp *= x * a
        return Sig(out).trim()

    def aerate(self, a):
        return Sig(self.seq.aerate(a))

    def append(self, i: (int, float)):
        """
        Add a value to the end of the sequence
        """
        self.seq.append(i)

    def base(self):
        return self.seq.base()

    def f(self, l=-1, seed=None):
        """
        The recursive signature function

        :param l: the length of the sequence
        :return: the signature F_d
        """
        return self.seq.f(l=l if l != -1 else std_l, seed=seed).sig()

    def first_nonzero(self):
        """
        Get the position of the first non-zero digit of the signature
        """
        for e in range(1, len(self)):
            if self[e] != 0:
                return e
        return -1

    def i(self):
        """
        The inverse signature function
        Only works for sequences which begin with 1

        :return: the signature F^(-1)_d
        """
        return Sig(self.seq.i())

    def is_td(self):
        return self.seq.is_td()

    def iter_add(self, n):
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

    def multiplicative_inverse(self, l=-1):
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

    def neg(self):
        """
        Converts the given sequence to its additive inverse
        """
        out = [-k for k in self]
        return Sig(out)

    def reverse(self):
        return Sig(self.seq.reverse())

    def trim(self):
        """
        Removes trailing zeroes from a sequence

        :return: the sequence without trailing zeroes
        """

        return Sig(self.seq.trim())


class Matrix:
    """
    The Matrix class allows for the construction of various
    matrices in order to experiment with antidiagonal summation
    """

    @staticmethod
    def blank(l=-1, w=-1, base=-1):
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
        return Matrix([Seq([zero for k in range(l)]) for n in range(l)])

    @staticmethod
    def g_matrix(s, g, l=-1, w=-1):
        """
        The matrix S_d^p is defined in section 4.5 of SNR

        :param s: the initial matrix to be transformed
        :param g: the set of signatures to transform s
        :return: the transformed matrix S_d^p
        """

        def generate_next_matrix(s_prev, g_p):
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
                for y in range(n + 1):
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
    def identity(l=-1, base=-1):
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
    def power(d, l=-1, w=-1, taper=False):
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
    def sen(d: Seq, l=-1, w=-1):
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
        else:
            raise ValueError(f"Unsupported type {type(rows)}")

    def __add__(self, other):
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

    def __getitem__(self, i):
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

    def __mul__(self, other):
        if isinstance(other, (Seq, int, float)):
            return Matrix([other * g for g in self])
        elif isinstance(other, Sig):
            return Matrix([Seq(Sig(g) * other) for g in self])
        elif isinstance(other, Matrix):
            width = max(self.width(), other.width())
            length = max(len(self), len(other))
            out = Matrix([Seq([0 for k in range(width)]) for n in range(length)])
            for n in range(length):
                for y in range(width):
                    out[n][y] = sum([self[n][k] * other[k][y] for k in range(len(self[n]))])
            return out.trim()
        else:
            raise ValueError("Incompatible type; must be int, float, Seq, or Matrix")

    def __pow__(self, power, modulo=None):
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

    def __sub__(self, other):
        return (self + other.neg()).trim()

    def __truediv__(self, num):
        if isinstance(num, (int, Seq)):
            out = []
            for n in range(len(self)):
                out.append(self[n] / num)
            return Matrix(out)
        else:
            raise ValueError("Incompatible type; must be int or Seq")

    def append(self, line: Seq):
        """
        Adds a line to the end of the block

        :param line: the line to be added to the block
        """
        self.rows.append(line)

    def f(self, a=1, g=Seq(1)):
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

    def i(self, a=1, g=Seq(1)):
        """
        Performs signature function then inverse signature function

        :param a: the aeration coefficient for f()
        :param g: the signature convolution coefficient for f()
        :return: the sequence result of the operation
        """
        return self.f(a, g).i()

    def transpose(self):
        l = max([len(self)] + [len(row) for row in self])
        return Matrix([Seq([self[k][n] for k in range(len(self))]) for n in range(l)])

    def trim(self):
        out = self
        while len(out) > 0:
            if len(out[-1].trim(to_zero=True)) == 0:
                out = out[:-1]
            else:
                return out
        return out

    def neg(self):
        out = [v.neg() for v in self]
        return Matrix(out)

    def truncate(self, l):
        out = Matrix([s[:l] for s in self.rows[:l]])
        return out

    def width(self):
        return max([len(k) for k in self.rows])


def num_dims(d):
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
    def canonical(ds: list[Seq], l=5, coordinates=None, current=None):
        """
        Produces a canonical one-beginning object whose dimensions express the given list of signatures

        :param ds: The signatures to express
        :param l: The length of each dimension
        :param coordinates: current location within the structure; do not set manually
        :param current: the current sub-Prism being used in recursive calculations; do not set manually
        :return:
        """

        if len(ds) == 1:
            return Prism(Matrix.power(ds[0], l))

        output = []
        # output2 = 0

        if current is None:
            current = Matrix.power(ds[0], l=l)
            for i in range(len(ds) - 1):
                current = Prism([current] * l)

        if coordinates is None:
            coordinates = []

        if len(coordinates) == len(ds) - 1:
            output = Seq(1)
            for i, d in enumerate(ds[1:]):
                # tmp_len = 1
                # for j in range(coordinates[i]+1):
                #     output2 += (2*tmp_len + 1)
                #     tmp_len += len(d) - 1
                output *= d ** coordinates[i]
            # output2 += (2*len(output) + 1) * len(current)
            return Prism(output * current)
            # return Prism(output * current), output2
        else:
            for n in range(l):
                get = Prism.canonical(ds, l, coordinates + [n], current[n])
                output.append(get)
                # output.append(get[0])
                # output2 += get[1]
        return Prism(output)
        # return Prism(output), output2

    @staticmethod
    def power(d: Seq, dim=4, l=10, coordinates=None, block=None):
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

    def __init__(self, structure, l=10):
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

    def __getitem__(self, i):
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

    def __mul__(self, other):
        """
        Takes two Prisms and constructs their prismatic product
        """

        def get(d, coordinates):
            output = d
            for k in range(len(coordinates)):
                output = output[coordinates[k]]
            return output

        def nested_array(dims, length):
            if dims == 2:
                return Matrix.blank(length)
            else:
                output = []
                for k in range(length):
                    output.append(nested_array(dims - 1, length))
                return output

        l = min(len(self), len(other))

        dim_d = num_dims(self)
        dim_g = num_dims(other)

        output = nested_array(dim_d + dim_g - 1, l)

        new_dim = dim_d + dim_g - 1

        for args in itertools.product(range(l), repeat=new_dim):
            _sum = get(self, args[:dim_d - 1])
            _sum = _sum * get(other, args[dim_d - 1:new_dim - 1])
            get(output, args[:new_dim - 2])[args[new_dim - 2]] = _sum

        return Prism(output)

    def __setitem__(self, key, value):
        self.val[key] = value

    def __str__(self):
        return "\n".join([str(i) for i in self])

    def f(self, g=None):
        """
        Performs the general signature function on an N-dimensional structure
        """

        def generate_next(structure, g=None, n=0, coordinates=None):
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
                                multiplicand *= g[i][coordinates[i]]
                            multiplicand *= g[-1][y]
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

        out = []

        dims = num_dims(self)
        l = len(self)

        if isinstance(g, (Seq, Sig)):
            g = [g]

        if not g:
            g = [Seq(1).f(l) for _ in range(dims - 1)]
        elif len(g) < dims - 1:
            if g[0].is_td():
                g = [sig.f(l) for sig in g] + [Seq(Td.one(g[0].base())).f(l) for _ in range(dims - 1 - len(g))]
            else:
                g = [sig.f(l) for sig in g] + [Seq(1).f(l) for _ in range(dims - 1 - len(g))]
        else:
            g = [sig.f(l) for sig in g]

        for n in range(l):
            out.append(generate_next(self, g, n))

        return Seq(out)

    def i(self, g=None):
        return self.f(g=g).i()

    # def aerate(self, a):
    #     """
    #     The aeration function of a prism
    #
    #     Note that this only behaves consistently for power objects
    #
    #     :param a: the list of aeration coefficients
    #     """
    #     dims = num_dims(self)
    #     if not isinstance(a, list):
    #         raise TypeError(f"Can only sieve with list")
    #     elif len(a) < dims - 1:
    #         a = a + [1 for _ in range(dims - 2)]
    #
    #     self.val = self[::a[0]]
    #
    #     for i, each in enumerate(self):
    #         if isinstance(each, Matrix):
    #             self[i] = each[::a[1]]
    #         else:
    #             self[i] = each.aerate(a[1:])
    #
    #     return self

    def size(self):
        output = 1
        k = self[0]
        while not isinstance(k, Matrix):
            output *= len(k)
            k = k[0]
        output *= len(k)
        return output


def signature_dot_product(g, S):
    if isinstance(g, Seq):
        g = [g]
    if isinstance(S, Seq):
        S = [S]

    while len(S) < len(g):
        S.append(Seq(1))

    while len(g) < len(S):
        g.append(Seq(0))

    return sum([(g[k].sig() * S[k].sig()) for k in range(len(g))]).seq


def random_seq(min=1, max=7, min_digits=2, max_digits=5):
    if min_digits > max_digits:
        max_digits = min_digits
    return Seq([random.randint(min, max) for _ in range(random.randint(min_digits, max_digits))])


def random_block(l=10):
    return Matrix(Seq(1), *[random_seq() for _ in range(l)])
