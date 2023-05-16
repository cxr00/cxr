
class Complex:
    """
    A basic complex number class
    """
    def __init__(self, r: (int, float)=0, i: (int, float)=0):
        self.r = r if isinstance(r, float) and int(r) != r else int(r)
        self.i = i if isinstance(i, float) and int(i) != i else int(i)

    def __eq__(self, other):
        if isinstance(other, Complex):
            return self.r == other.r and self.i == other.i
        elif isinstance(other, (int, float)):
            if self.i != 0:
                return False
            return self.r == other

    def __str__(self):
        if self.r == self.i == 0:
            return "0"
        if self.r == 0:
            if self.i == 1:
                return "i"
            if self.i == -1:
                return "-i"
            return str(self.i) + "i"
        if self.i == 0:
            return str(self.r)
        i_part = "i" if self.i == 1 else str(abs(self.i)) + "i"
        r_part = str(self.r)
        return r_part + (" - " if self.i < 0 else " + ") + i_part

    def __neg__(self):
        return Complex(-self.r, -self.i)

    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self.r + other.r, self.i + other.i)
        if isinstance(other, (int, float)):
            return Complex(self.r + other, self.i)
        return other + self

    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(self.r - other.r, self.i - other.i)
        if isinstance(other, (int, float)):
            return Complex(self.r - other, self.i)

    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(self.r * other.r - self.i * other.i, self.r * other.i + self.i * other.r)
        if isinstance(other, (int, float)):
            return Complex(self.r * other, self.i * other)
        return other * self

    def __truediv__(self, other):
        if isinstance(other, Complex):
            denom = other.r ** 2 + other.i ** 2
            r = self.r * other.r + self.i * other.i
            i = self.i * other.r - self.r * other.i
            r /= denom
            i /= denom
            return Complex(r, i)
        if isinstance(other, (int, float)):
            return Complex(self.r / other, self.i / other)

    def __iadd__(self, o):
        return self + o

    def __radd__(self, other):
        return self + other

    def __imul__(self, o):
        return self * o

    def __rmul__(self, other):
        return self * other

    def __isub__(self, o):
        return self - o