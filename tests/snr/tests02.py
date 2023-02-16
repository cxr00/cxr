from cxr import Seq, Matrix, Prism, x, set_std_l
from cxr import Td
from cxr.math import base64

"""
Verification of identities found during procedural
exploration of base interpretation sequences of
transposition products

Identities and information are currently being compiled
"""

b = 3
set_std_l(15)


def construct_matrix(s, g):
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

    r = construct_matrix(s, g)
    print(r.base_sequence(b))
    print(Seq(n0*b + n2, b*(n1*n3 - n0*n2)).f())
    print()


def b_1_2():
    print("1.2")
    n = 5
    s = Seq(1, 1, n)
    g = Seq(1, 1)

    r = construct_matrix(s, g)
    print(r.base_sequence(b))
    print((b + 1 + b * n*x**2 * Seq(1).f()).f())
    print()


def b_1_3():
    print("1.3")
    n = 3
    s = Seq(1, 1)
    g = Seq(1, 1, n)

    r = construct_matrix(s, g)
    print(r.base_sequence(b))
    print((n*(Seq(b).f() - b*x - 1) + b + 1).f())
    print()


def b_1_4():
    print("1.4")
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

    r1 = construct_matrix(s, g)
    print(r1.base_sequence(b))
    print((dot(Seq(b).f() + b, S()) + b + 1).f())
    print()

    r2 = construct_matrix(g, s)
    print(r2.base_sequence(b))
    print((dot(b*Seq(1).f(), S()) + b + 1).f())
    print()


def b_1_5():
    print("1.5")
    n = 2
    s = Seq(1, 1, n)
    g = Seq(1, 1, 1)

    r1 = construct_matrix(s, g)
    print(r1.base_sequence(b))
    alt = Seq(b, (n-1) * b).f()
    alt = alt.f(seed=Seq(b, n*b)) + 1
    alt = alt.f()
    print(alt)
    print()

    s = Seq(1, 1, 1)
    g = Seq(1, 1, 2)
    r2 = construct_matrix(s, g)
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
    Showcases an identity for sieved {1,1,1}
    """
    print("4 Sieved matrices")
    l = set_std_l(25)
    s = Seq(1, 1, 1)
    m = Matrix.power(s).sieve(len(s) - 1)

    b = 2
    bs = m.base_sequence(b)

    # This currently does not generalise past b=2 and s={1,1,1}
    struct = (m.base_sequence(b-1) * Seq(1, -1))[:l - 1] * b + 1
    print(bs)
    print(struct)
    print(bs.i())


def b_5():
    print("5 Sequence as float")
    """
    Every result of the signature function corresponds to a rational number in base b.

    * Take a signature s0, s1, ... sn.
    * Make it the mantissa of a base-b number and resolve accordingly
    * divide the base-b number by b**n
    * Then the result is equal to 1 / (b**n - s)
        * Note that s as a base-b number is interpreted s0*b**n + ... + s(n-1)*b + sn
    """

    l = 100
    set_std_l(l)
    base64.round_to = l
    b = 10

    seqs = Seq(0, 1, 9),

    for s in seqs:
        a = s.f(l=l)
        output = Td(0, base=b)
        for i in range(len(a)):
            output += Td([a[i]], base=b) / b ** (i + len(s))
        print(output)
        print(float(output))
        print(1 / (b ** (len(s)) - int(Td(s.elements, base=b))))
        print(1 / float(output))
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
