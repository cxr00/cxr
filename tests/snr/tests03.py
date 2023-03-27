import itertools

from cxr import Seq, Matrix, Prism, set_std_l, x

"""

"""


def g_prism_test():

    l = set_std_l(13)
    d = [Seq(1, 1), Seq(1, 1)]
    g = [Seq(2), Seq(3, 1)]
    g_p = Prism.g_prism(d, g, l=l)
    print(g_p.f())
    sig = g_p.i().sig()
    print(sig)

    alt = Seq(0).sig()
    for d_n in d:
        alt += d_n.sig()
    for g_n in g:
        alt += (x*g_n.aerate(2)).sig() + Seq(1)
    print(alt)


def simplex_test():
    d = Seq(1, 1), Seq(1, 1), Seq(1, 1), Seq(1, 1), Seq(1, 1), Seq(1, 1)
    N = len(d)

    p = Prism.simplex(d, l=N+1)
    pf = p.f()
    pi = pf.i()
    print(pf)
    print(pi)

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

    print(output)
    print(output.f())


def triangular_prism():
    l = set_std_l(30)
    d = Seq(1, 1)
    m = Matrix.power(d, l=l)
    p = Prism([Prism([m for _ in range(30)]) for __ in range(30)])

    print(p.f())
    print(p.i())
    print(d.sig() + 1 + 1)


if __name__ == "__main__":
    # g_prism_test()
    simplex_test()
    # triangular_prism()
