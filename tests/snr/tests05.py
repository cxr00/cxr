from cxr import set_std_l, Seq, x, Matrix, Prism, random_seq, SDP, Td
from cxr.math import base64

"""
sen_regularisation_test - showcases regularisation identities
randomisation_test - shows preservation of signature properties when using g-operation
prism_randomisation_test - shows that this does not work
sen_like_test - contains a few identities when using power triangles instead of sen
constant_addition_test - demonstrates addition of a constant or elements of a sequence at each step of the signature function
matricial_right_near_ring_identity_test - showcases identities of MNR, the matricial right near-ring
conv_not_sig_add_test - showcases rational expansion of signature function of convolved rather than sig-added signatures
derivative_of_signatures - showcases derivative identity
integral_of_signatures - showcases integration. Uses 1 instead of general C
"""


def sen_regularisation_test():
    """
    Showcases the straight and diagonal regularisation identities
    """
    l = set_std_l(15)
    d = Seq(1, 1)
    g = Seq(1, 1)
    one = Seq(1)
    m = Matrix.sen(d, l=l, w=l) ** l
    mt = Matrix.blank(l=l, w=l)

    # Construct regularised matrix using straight identity
    for n in range(l):
        for k in range(n+1):
            # mt[k][n-k] = m[n-k][0]  # m ** (n-k)
            mt[n-k][k] = m[k][0]

    mtf = mt.f(g=g)
    print("# Straight identity")
    print(mtf.i())
    print(d.sig() + (g-1)*Seq(1).f())
    print()

    # Construct regularised matrix using diagonal identity
    m = Matrix.sen(d, l=l, w=l)
    mt2 = Matrix.blank(l=l, w=l)
    for n in range(l):
        _m = Matrix.identity(l=l)
        for k in range(l):
            mt2[k][n-k] = _m[n-k][0]
            # mt2[n-k][k] = (m**(n-k))[k][0]
            _m *= m


    print(mt2)
    mt2f = mt2.f(g=g)
    print("# Diagonal identity")
    print("f :", mt2f)
    print("i :", mt2f.i())

    # This identity only works when g is a single digit
    alt1 = g.sig() + x**2 * (x.f() + ((g-1)*g.f()*one.f()).aerate(2))
    print("a :", alt1[:l-1])
    print()


def randomisation_test():
    """
    Signatures are preserved across random g-matrices

    This means once the signature of the random matrix is known,
    its g-matrix is accurate to the structure of the matrix.

    Note that the matrix MUST begin with 1
    """
    l = set_std_l(25)
    s = Seq(1, 1, 2, 4, 6)
    m = Matrix([Seq(1).concat(random_seq(min_digits=0, max_digits=9))] + [random_seq(min_digits=1, max_digits=10) for _ in range(l-1)])

    print("# Random matrix")
    print("f:", m.f())
    print("i:", m.i())
    print()

    mg2 = m.f(g=s)
    print("# Signature convolution (does not work)")
    print("f:", mg2)
    print("i:", mg2.i())
    print("a:", m.i() * s)
    print()

    mg = Matrix.g_matrix(m, g=s, l=l)
    print("# G-matrix")
    print("f:", mg.f())
    alt = s.sig() + m.i()
    print("a:", alt)
    print("i:", mg.i())
    print()


def prism_randomisation_test():
    """
    This exercise demonstrates that the coherence of signature
    convolution does not extend to prisms with a random matrix base
    """
    def random_matrix(l, with_one=False):
        output = [random_seq(min_digits=1, max_digits=10) for _ in range(l)]
        if with_one:
            return Matrix([Seq(1)] + output)
        else:
            return Matrix(output)

    g = [Seq(1), Seq(2)]
    l = set_std_l(20)
    m = random_matrix(l, True)

    p = Prism([m * m[n] for n in range(10)])

    print("# Matrix")
    print(m.f())
    print(m.i())
    print()

    pfg = p.f(g)
    print("# Prism")
    print(pfg)
    print(pfg.i())
    print()

    print("# SDP")
    print(SDP([m.i(), m.i()], g))
    print()



def sen_like_test():
    """
    Even a non-Sen matrix can be subjected to the sum used to yield
    d + sum(g_k) with some interesting results

    d = 1
        straight: 2, -1
        diagonal: 1, 1, 0, -1, -1, 0, 1, 1, 0, -1, -1, 0, ...

    d = n
        straight: n \oplus 1

    d = 1, 1
        straight: A060946 - Trace of Vandermonde matrix
        diagonal: 1 + xA026898 - sum_{k=0..n} (n-k+1)^k

    d = 1, -1
        straight/diagonal: 1, 1, -1

    d = 2, -1
        straight: A052992 - signature 1, 4, -4
        diagonal: A001045 - Jacobsthal numbers, signature 1, 2

    d = n, -1
        straight: 1, n**2, -(n**2)

    d = 2, 1
        diagonal: A349970 - sum_{k=0..n} (2k)^(n-k)
    """
    d = Seq(2)
    l = set_std_l(25)
    S = Matrix.power(d, l)

    output = Seq([0 for _ in range(l)])
    output2 = Seq(output)
    p = [Matrix.identity(l)]
    for n in range(l):
        p.append(S * p[-1])
        if not (n+1) % 10:
            print(f"{n+1} complete...")
    print()

    # print("\n".join([str(p_k) for p_k in p]))

    for n in range(l):
        for k in range(n + 1):
            output[n] += p[k+1][k][0]
            output2[n] += p[n-k][k][0]

    print("# Straight")
    print(output)
    print(output.i())
    print()

    print("# Diagonal")
    print(output2)
    print(output2.i())


def constant_addition_test():
    """
    Not sure why I didn't think of this sooner
    """
    l = set_std_l(100)
    d = random_seq()

    C = random_seq()
    print("d  :", d)
    print("C  :", C)
    output = [1]
    for n in range(1, l):
        _sum = 0
        for k in range(1, n+1):
            _sum += output[n-k] * d[k-1]
        _sum += C[(n-1) % len(C)]
        output.append(_sum)

    so = Seq(output)
    print("F'd:", so)
    print("inv:", so.i())
    alt = Seq(C) * Seq(x**(len(C) - 1) - C).f()
    alt = alt.sig() + d
    print("alt:", alt[:l-1])
    print("yes:", alt[:l-1] == so.i())


def matricial_right_near_ring_identity_test():
    l = set_std_l(40)
    d = random_seq()
    g = random_seq()

    td = Matrix.power(d)
    tg = Matrix.power(g)

    diff = td - tg
    output = []
    for n in range(l):
        _sum = 0
        for k in range(n+1):
            div = diff[k+1] / (d - g)
            _sum += div[n-k]
        output.append(_sum)

    print("# Difference identity")
    print(Seq(output).i())
    print(d.sig() + g)
    print()

    prod = (td * tg)[:l // (len(d) - 1)]
    print("# Matrix product")
    print(prod)
    print(prod.i())
    print(sum([d_k * g**k for k, d_k in enumerate(d)]))


def conv_not_sig_add_test():
    """
    Slightly more complex than the signature sum identity,
    but with the same mechanism for B_P^{-1}
    """
    d = Seq(1, 1)
    g = Seq(1, 1)
    seed = Seq(2, -1, 1)
    b = 10
    base64.default_base = b

    pt0 = Td(b ** len(d)) - Td(d.elements)
    pt1 = pt0 * b ** (len(g) - 1)
    pt2 = pt1 - Td((d * (g-1)).elements)
    # print(pt2)

    pt0 = Td(b ** len(g)) - Td(g.elements)
    pt1 = pt0 * b ** (len(d) - 1)
    pt2 = pt1 - Td((g * (d-1)).elements)
    # print(pt2)

    pt0 = b ** (len(d) + len(g) - 1)
    pt1 = pt0 - Td(g.elements) * (b ** (len(d) - 1) + Td((d-1).elements))
    # print(pt1)

    fsg = (d*g).f(seed=seed)
    print("seq   :", fsg)

    output = Td.zero()
    for n in range(len(fsg)):
        output += Td(fsg[n]) / b ** (n + len((d*g)))

    P = seed
    for n in range(1, len(d) + len(g)):
        _prod = x ** n * (d*g)[n - 1]
        _sum = 0
        for k in range(len(seed) - n):
            _sum += seed[k] * x ** k
        P -= _prod * _sum

    BP = Td.zero(b)
    for n in range(len(P)):
        BP += Td(P[n]) / (b ** n)

    print("bp", BP)

    print("o:", output)
    print("a:", BP / pt1)
    print()


def derivative_of_signatures():
    """
    What a quirky li'l identity!
    """
    def get_derivative(s):
        output = []
        for i, s_i in enumerate(s[1:]):
            output.append(s_i * (i+1))
        return Seq(output)

    def get_genfunc(s):
        output = s
        for i in range(1, len(s)):
            output += x**i * s[i] * i
        return output * s.f()**2

    l = set_std_l(30)
    for i in range(100):
        d = random_seq(min_digits=15)
        deriv = get_derivative(d.f())
        print(deriv)
        gen_func = get_genfunc(d)[:l-1]
        print(gen_func)
        print(deriv == gen_func)
        print()


def integral_of_signatures():
    def get_integral(s):
        output = [1]  # Assume the result is a one-beginning sequence
        for i, s_i in enumerate(s):
            output.append(s_i / (i+1))
        return Seq(output)

    d = Seq(1, 4, 9, 20, 40, 78, 147, 272, 495, 890, 1584, 2796, 4901)
    print(get_integral(d))
    d = Seq(1, 1).f()
    print(get_integral(d))
    print(get_integral(d).i())


if __name__ == "__main__":
    # sen_regularisation_test()
    constant_addition_test()
    # conv_not_sig_add_test()
    # derivative_of_signatures()
    # integral_of_signatures()
