import cxr.base36
from cxr.snr import Seq, Sig, Block, Prism
from cxr.snr import x, signature_dot_product, random_seq, random_block
from cxr.base36 import Tridozenal as Td


def basic_prism_class_test():
    d = Seq(1, 1)
    g = Seq(1, -1)
    f = Seq(2, -1)
    l = 12

    p = Prism.power(d, dim=3)

    print(p.f())
    print(p.i())
    print(d.sig().iter_add(2))
    print()

    pp_f = (p * Prism.power(d, dim=2)).f()
    print(pp_f)
    print(pp_f.i())
    print(d.sig().iter_add(3))
    print()

    p = Prism.power(d, dim=2, l=l) * Prism.power(g, dim=2, l=l)
    p = p * Prism.power(f, dim=2, l=l)

    p_f = p.f(g=[d, g])
    print(p_f)
    print(p_f.i())
    print(signature_dot_product([d, g, f], [d, g]))
    print()


def fib_signature_triangle():

    def sig_add_block(d):

        b = Block.blank(l)
        tmp = d.sig()
        for n in range(l):
            b[n] = tmp
            tmp += d.sig()
        return b

    l = 25

    for N in range(1, 10):
        d = Seq([1 for _ in range(N)])

        b = sig_add_block(d)
        b_i = b.i()

        print(b_i)

        p = 2 - x**(N-1) - x**N
        p = p * (d[1:]).neg().f()
        p = p.sig() + 1

        print(p)
        print()


def weird_sen_like_identity():
    """
    This also gave me incentive to re-examine and improve slices
    """
    d = random_seq().sig()
    l = 15

    print(d)

    d_alt = Seq(1) / d[1:].neg().f()
    d_alt += d[0] - 1

    print(d_alt)
    print()

    print(Block.sen(d, l)[:-5])


def prism_aeration_test():
    """
    Showcases the identity over canonical objects
    """
    d = Seq(1, 1)
    g = Seq(1, 1)
    s = Seq(2, -1)
    l = 20
    n = 2
    k = 2

    p = Prism(d, l=20) * Prism(g, l=20)

    print(p.f())
    print(p.i())
    print(d.sig() + g.sig())
    print()

    sieved = p.aerate([n, k])

    print(sieved.f(g=[s, s]))
    print(sieved.i(g=[s, s]))
    print((signature_dot_product([d**n, g**k], [s, s])))
    print()

    calc = g.sig() * (x**(k-1))
    calc = calc.seq() / x**(k-1)
    print(calc)
    print(g**k)
    print()


def sen_power_test():
    """
    REMEMBER: Matrix powers start at M^0, which is the identity block

    This is the SECOND TIME that this specific improper implementation
    has cost me quite a bit of time
    """

    def special_sig_sum(d, g):
        output = Sig(0)
        for sig in g:
            output += sig.sig()
        output = output.seq() - 1
        return (output.sig() - (-d).sig()).f()

    l = 15
    p = 1
    d = Seq(1, 1)
    g = [Seq(1, 1) for _ in range(p)]
    g_f = [sig.f(l) for sig in g]
    b = Block.sen(d, l)

    b2 = [b] + [Block.blank(l) for _ in range(p)]
    for p in range(p):
        for n in range(l):
            for y in range(l):
                _sum = 0
                for k in range(n+1):
                    _sum += b2[p][k][y] * g_f[p][n-k]
                b2[p+1][n][y] = _sum

    print("S_d^p")
    print(b2[-1])
    print()

    bb = [Block.identity(l)]
    for n in range(l):
        bb.append(bb[-1] * b2[-1])

    b4 = Block.blank(l)
    b5 = Block.blank(l)
    output = []
    for n in range(l):
        _sum = 0
        for k in range(n+1):
            _sum += bb[k][k][0]
            b4[n][k] = bb[k][k][0]
            b5[n][k] = bb[n-k][k][0]
        output.append(_sum)

    output = Seq(output)
    print("Column sum")
    print(b4)
    print(output)
    print(output.i())
    print(d + sum([s.sig() for s in g]).seq())
    print()

    print("Antidiagonal sum")
    print(b5)
    output = []
    for n in range(l):
        output.append(sum(b5[n]))

    output = Seq(output)
    print(output)
    print(output.i())
    print(special_sig_sum(d, g))
    print()


def sen_power_prism_test():
    d = Seq(1)
    l = 20
    p = 1
    g_f = [Seq(1).f() for _ in range(p)]

    b = Block.sen(d, l)

    b2 = [b] + [Block.blank(l) for _ in range(p)]
    for p in range(p):
        for n in range(l):
            for y in range(l):
                _sum = 0
                for k in range(n+1):
                    _sum += b2[p][k][y] * g_f[p][n-k]
                b2[p+1][n][y] = _sum

    bb = [Block.identity(l)]
    for n in range(l):
        bb.append(bb[-1] * b2[-1])

    p = Prism([Prism(b) for b in bb])

    print(p.f())
    print(p.i())
    print()


l = 20


def block_powers(b, initial=None):
    output = [initial if initial else Block.identity(l)]
    for n in range(l - 1):
        output += [b * output[-1]]
    return Prism(output)


def misc_constructed_prisms_test():
    # A prism where F_p = A304357 when d = [1, 1]
    d = Seq(1, 1)
    b = Block.power(d, l)
    p = block_powers(b)

    print(p.f())
    print(p.i())
    print()

    b = Block.sen(d, l)
    p = block_powers(b)

    print(p.f())
    print(p.i())
    print()

    # Produces the fibonacci numbers...almost.
    # Tentatively calling these the glitch fibonacci numbers
    d = Seq(1, 1)
    g = Seq(1, -1)
    bd = Block.power(d, l)
    bg = Block.power(g, l)

    p = block_powers(bg, bd)

    print(f"{g} * {d}")
    print(p.f())
    print(d * d.f(length=l) - (x ** 3) * (x ** 3).f(length=l))
    print()

    d = Seq(1, 1)
    g = Seq(1)
    bd = Block.power(d, l)
    bg = Block.power(g, l)

    p = block_powers(bg, bd)

    print(p.f())
    print(p.i())
    print()

    d = Seq(1, 1)
    g = Seq(1, -1)
    bd = Block.sen(d, l)
    bg = Block.sen(g, l)

    p = block_powers(bd, bg)

    print(p.f())
    print(p.i())
    print()

    p = block_powers(bg, bd)

    print("bg * bd")
    print(p.f())
    print(p.i())
    print()

    bg = Block.power(Seq(1, -1), l)
    bd = Block.power(Seq(0, 1), l)

    p = block_powers(bg, bd)

    print(p.f())

    p = block_powers(bg, Block.power(Seq(1, -1)))

    print(1 + x*(p.f() + x*x.f()))
    print()

    print(p.f())
    print()


def sen_instrumentality_tests():
    d = Seq(1, 1)

    l = 20
    p = 4
    g_f = [Seq(1, 1, 1).f(length=l) for _ in range(p)]



    b = Block.sen(d, l)

    b2 = [b] + [Block.blank(l) for _ in range(p)]
    for p in range(p):
        for n in range(l):
            for y in range(l):
                _sum = 0
                for k in range(n+1):
                    _sum += b2[p][k][y] * g_f[p][n-k]
                b2[p+1][n][y] = _sum

    b_for_p = [Block.identity(l)]
    prod = Block.identity(l)
    for i in range(l):
        prod = b2[-1] * prod
        b_for_p.append(prod)

    p = Prism(b_for_p)

    s = Seq([0 for _ in range(l)])
    for n in range(l):
        _sum = 0
        for k in range(n+1):
            _sum += p[k+1][k][0]
        s[n] = _sum

    print(s)
    print(s.i())
    print(d + sum([sig.i().sig() for sig in g_f]).seq())
    print()

    s = Seq([0 for _ in range(l)])
    for n in range(l):
        _sum = 0
        for k in range(n+1):
            _sum += p[n-k][k][0]
        s[n] = _sum

    print(s)
    print(s.i())
    print(((-1 + sum([sig.i().sig() for sig in g_f]).seq()).sig() - (-d).sig()).f())
    print()


def block_sen_test():
    d = Seq(Td.one(), Td.one())
    l = 10
    b = Block.sen(d, l)

    g = [Seq(Td.one()) for _ in range(2)]

    print(sum([sig.sig() for sig in g]))
    print()

    print(b)
    print([str(each) for each in g])
    print()

    print("Generating g-matrix...")
    g_mat = Block.g_matrix(b, g, l)
    print("g-matrix generated.")
    print()

    s = []
    g_mat_power = g_mat
    _sum = Td.zero()
    for i in range(l):
        print(i, "...")
        _sum += g_mat_power[i][0]
        g_mat_power *= g_mat
        s.append(_sum)

    print()
    print(g_mat)

    print(Seq(s).i())
    print(d + sum([sig.sig() for sig in g]))
    print()


def main():
    # basic_prism_class_test()
    # fib_signature_triangle()
    # weird_sen_like_identity()
    # prism_aeration_test()
    # sen_power_test()
    # sen_power_prism_test()
    # misc_constructed_prisms_test()
    # sen_instrumentality_tests()
    block_sen_test()


if __name__ == "__main__":
    main()
