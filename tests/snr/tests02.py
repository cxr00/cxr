from cxr import Seq, Matrix, Prism, x, set_std_l
from cxr import Td
from cxr.math import base64
from cxr.math.snr import random_seq

import cxr

"""
Verification of identities found during procedural
exploration of base interpretation sequences of
transposition products.

Identities and information are compiled into SNR 3.

Functions of the form b_#_# are legacy numbering during
initial compilation of identities.
"""

b = 3
set_std_l(15)


def diagonalised_transposition_product(s, g):
    m_s = Matrix.power(s)
    m_g = Matrix.power(g)
    return m_s.transposition_product(m_g).diagonalise()


def b_1_1():
    print("1.1")
    n0 = 1
    n1 = 3
    n2 = 1
    n3 = 2
    s = Seq(n0, n1)
    g = Seq(n2, n3)

    r = diagonalised_transposition_product(s, g)
    print(r.base_sequence(b))
    print(Seq(n0*b + n2, b*(n1*n3 - n0*n2)).f())
    print()


def b_1_2():
    print("1.2")
    n = 5
    s = Seq(1, 1, n)
    g = Seq(1, 1)

    r = diagonalised_transposition_product(s, g)
    print(r.base_sequence(b))
    print((b + 1 + b * n*x**2 * Seq(1).f()).f())
    print()


def b_1_3():
    print("1.3")
    n = 3
    s = Seq(1, 1)
    g = Seq(1, 1, n)

    r = diagonalised_transposition_product(s, g)
    print(r.base_sequence(b))
    print((n*(Seq(b).f() - b*x - 1) + b + 1).f())
    print()


def b_1_4():
    print("1.4 (two parts)")
    n = [1, 2, 1]
    s = Seq(1, 1)
    g = Seq(1, 1, *n)

    def S():
        output = Seq(0)
        for k in range(len(n)):
            output += n[k] * x**(k+2) * Seq(1).f() ** (k+1)
        return output

    def dot(a, b):
        return Seq([a[n] * b[n] for n in range(max(len(a), len(b)))])

    r1 = diagonalised_transposition_product(s, g)
    print(r1.base_sequence(b))
    print((dot(Seq(b).f(), S()) + b + 1).f())
    print()

    r2 = diagonalised_transposition_product(g, s)
    print(r2.base_sequence(b))
    print((dot(b*Seq(1).f(), S()) + b + 1).f())
    print()


def b_1_5():
    print("1.5 (two parts)")
    n = 2
    s = Seq(1, 1, n)
    g = Seq(1, 1, 1)

    r1 = diagonalised_transposition_product(s, g)
    print(r1.base_sequence(b))
    alt = Seq(b, (n-1) * b).f()
    alt = alt.f(seed=Seq(b, n*b)) + 1
    alt = alt.f()
    print(alt)
    print()

    s = Seq(1, 1, 1)
    g = Seq(1, 1, 2)
    r2 = diagonalised_transposition_product(s, g)
    print(r2.base_sequence(b))
    alt = Seq(b, b).f().f(seed=Seq(b, b**2 + b))
    alt = alt + 1 - b*x*(b-1)
    alt = alt.f()
    print(alt)
    print()


def b_2_stirling():
    print("2 Stirling")
    l = set_std_l(10)
    m = Matrix.blank()
    m[0][0] = 1
    f = 3
    b = 2
    for n in range(1, l):
        for k in range(n+1):
            m[n][k] = m[n-1][k-1] + (n + f - 1)*m[n-1][k]

    print(m)
    print(m.base_sequence(b))

    out = Seq(1)
    for i in range(1, l):
        out.append(out[-1] * (b*(f+i-1)+1))
    print(out)
    print()

    m = Matrix.blank()
    m[0][0] = 1
    f = 0
    b = 2
    for n in range(1, l):
        for k in range(n+1):
            m[n][k] = m[n-1][k-1] + (k-f) * m[n-1][k]

    print(m)
    print(m.base_sequence(b))
    print()


def b_3():
    """
    Demonstrates the results of constructing a base prism
    and its resultant identity
    """
    print("3 Base prisms")
    b = 13
    s0 = Seq(2, 1, 4)
    s1 = Seq(1, 1, 1)
    s2 = Seq(1, 1, 1)
    s3 = Seq(4, 1, 1)
    p = Prism.canonical([s0, s1, s2, s3], l=6)
    pf = (p.base_prism(b).f().i())
    print(pf)
    b0 = int(Td(s0.elements, base=b))
    b1 = int(Td(s1.elements, base=b))
    b2 = int(Td(s2.elements, base=b))
    b3 = int(Td(s3.elements, base=b))

    print(Seq(b0).sig() + b1 + b2 + b3)
    print()


def b_4():
    """
    Showcases identities for sieved:
    {1,1,1}
    {1,1,2}
    {1,2,1}
    {1,2,2}
    {2,1,1}
    """
    print("4 Sieved matrices")
    l = set_std_l(31)

    for s in [Seq(1, 1, 1), Seq(1, 1, 2), Seq(1, 2, 1), Seq(1, 2, 2), Seq(2, 1, 1)]:
        print(s)
        m = Matrix.power(s).sieve(len(s) - 1)

        b = 2
        bs = m.base_sequence(b)
        print(bs)

        cxr.math.base64.round_to = 35

        if s == Seq(1, 1, 1):
            subseq = [-(b-2) * (b+1)**n for n in range(25)]
            struct = (m.base_sequence(b - 1) * Seq(1, -(b-1), *subseq))[:l - 1] * b + 1
            print(struct.f())

        if s == Seq(1, 1, 2):
            b = Td(b, base=10)
            b_root = b.root(2)
            print(Seq([(((b+2+b_root)**k + (b+2-b_root)**k)/2).rounded(0) for k in range(l)]))

        if s == Seq(1, 2, 1):
            print((Seq(1, -(b+1)) * Seq(2*(b+1), -(b-1)**2).f(l=l+1))[:l])

        if s == Seq(1, 2, 2):
            b = Td(b, base=10)
            two_b_root = 2*b.root(2)
            print(Seq([(((b + 2 + two_b_root) ** k + (b + 2 - two_b_root) ** k) / 2).rounded(0) for k in range(l)]))

        if s == Seq(2, 1, 1):
            b = Td(b, base=10)
            b_root = b.root(2)
            print(Seq([(((2*b + 1 + b_root)**k + (2*b + 1 - b_root)**k)/2).rounded(0) for k in range(l)]))
        print()


def b_5():
    print("5 Rational forms of the signature function")
    """
    Every result of the signature function corresponds to a rational number in base b.

    * Take a signature s0, s1, ... sn.
    * Make it the mantissa of a base-b number and resolve accordingly
    * divide the base-b number by b**n
    * Then the result is equal to 1 / (b**n - s)
        * Note that s as a base-b number is interpreted s0*b**n + ... + s(n-1)*b + sn
    * See section 5 for seeded identity
    """

    l = 25
    set_std_l(l)
    base64.round_to = l
    b = 10

    seqs = Seq(1, 1),
    seeds = Seq(1), *[random_seq(max_digits=4) for _ in range(4)]

    for s in seqs:
        for g in seeds:
            print("g:", g)
            a = s.f(l=l, seed=g)
            output = Td(0, base=b)
            for n in range(len(a)):
                output += Td([a[n]], base=b) / b ** (n + len(s))
            print("output:", float(output))
            print("reciprocal:", 1 / float(output))
            identity = Td(1, base=b) / (Td(b ** len(s), base=b) - Td(s.elements, base=b))
            print("identity:", identity)
            r = len(s) + 1
            K = g
            for n in range(1, r):
                for k in range(len(g) - n):
                    K -= x ** n * s[n - 1] * g[k] * x ** k
            K = Td([K[0]], K[1:].elements, base=b)
            print("seed ratio:", K)
            print("identity:", output / K)
            print()


if __name__ == "__main__":
    # b_1_1()
    # b_1_2()
    # b_1_3()
    # b_1_4()
    # b_1_5()
    # b_2_stirling()
    # b_3()
    # b_4()
    b_5()
