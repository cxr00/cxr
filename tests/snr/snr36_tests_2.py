from cxr import base36
from cxr.base36 import Tridozenal as Td
from cxr.snr import Seq, Block, Prism, random_seq, signature_dot_product, x


def test0():

    base36.round_to = 200

    td = Td(2, 0, 3).root(power=2, perfect=True, log=True)

    num_digits = [0, 0, 0]
    for index, digit in enumerate(str(td)[2:]):
        num_digits[int(digit)] += 1
        if num_digits[0] == num_digits[1] or num_digits[0] == num_digits[2] or num_digits[1] == num_digits[2]:
            print(index+1, num_digits)

    print(num_digits)
    print()

    print(Td(2).root(log=True))
    print()


def test1():
    l = 15

    d = random_seq()
    d = Block.power(d, l)
    # d = random_block(l)

    g = random_seq()
    g = Block.power(g, l)
    # g = random_block(l)

    print(d[1])
    print(g[1])

    pd = Prism(d)
    pg = Prism(g)

    pdg = pd * pg
    pdg_f = pdg.f(g=Seq(1, 1))

    print(pdg_f)
    print(pdg_f.i())
    print(signature_dot_product([d[1], g[1]], Seq(1, 1)))
    print()


def test2():
    l = 100
    base36.round_to = l
    base36.default_base = 10

    g = Seq(1, 1, 1).f(length=l)
    g2 = Seq(1, 1, 1).f(seed=Seq(1, 1, 1), length=l)

    print(g[-1] / g[-2])
    print(g2[-1] / g2[-2])
    print()

    g = Seq(Td.one(), Td.one(), Td.one())
    g, g2 = g.f(length=l), g.f(seed=g, length=l)

    print(g)
    print(g2)
    print()

    print(g[-1] / g[-2])
    print(g2[-1] / g2[-2])
    print()


def test3():
    l = 7
    d = Seq(Td.one(), Td.one())
    b = Block.power(d, l)

    print(b[-1])
    print()

    print(b.i())
    print(b.i(a=2))
    print()

    print("Generating prism...")
    p = Prism(b) * Prism(b)
    print("Prism generated.")

    print(p.f())
    print(p.i())
    print()


def snr_36_test():
    d = Seq(Td.one(), Td.one().negative())
    l = 50

    d = d.f(length=l)
    print(d)

    for n in range(l):
        d = d.f(length=n + 1)
        print(d)


def signature_product_test():
    d = Seq(1, 1)
    l = 35

    # print(signature_dot_product([d, d], [d, d]))

    b = Block.blank(l)
    for n in range(l):
        b[n] = signature_dot_product([d for _ in range(n+1)], [d for _ in range(n+1)])

    print(b)
    print(b.f())
    print(b.i())


def transpose_products():
    p = 1
    d = Seq(1).f(length=p)
    g = d
    l = 35

    bd = Block.power(d, l)
    bg = Block.power(g, l)

    b2 = bg.transpose()

    print(b2)
    print()

    prod = bd * b2
    print(prod)

    diff = prod.f()
    print(diff)
    print(diff.i())

    alt_id = Seq(p-1).f().sig() + 1
    print(alt_id)
    print()


def ndf_seq_test():

    d = random_seq(max=6, min_digits=6).td()

    b = random_seq(max=6).td()
    t = random_seq(max=6).td()

    print("d:", d)
    print("b:", b)
    print("t:", t)
    print()

    a = sum([d[k] * (b**k - t**k) for k in range(1, len(d))])
    a = a / (b - t)

    for i, each in enumerate(a):
        each.round(place=20)

    print(a)

    a = Seq(0)
    for n in range(1, len(d)):
        for k in range(n):
            a += d[n] * b**k * t**(n-k-1)

    print(a)
    print()

    # print([7**k for k in range(10)])

    print(b.sig() + t.sig())
    print(b.sig() * t.sig())


def prism_test_again():
    d = random_seq(max_digits=3)
    g = random_seq(max_digits=3)
    s = random_seq(max_digits=3)
    l = 10

    print(Block(Td.one()))

    print(Block.power(d) * Block.power(g))

    print(d)
    print(g)
    print(s)
    print()

    p = Prism(d, l) * Prism(g, l) * Prism(s, l)

    p_f = p.f(g=[d, d, s])
    print(p_f)
    print(p_f.i())

    print(signature_dot_product([d.td(), g.td(), s.td()], [d.td(), d.td(), s.td()]))


def transpose_product_test_2():
    base36.default_base = 10
    d = Seq(Td(1), Td(1))
    g = random_seq().td()
    l = 10
    bd = Block.power(d, l)
    bg = Block.power(g, l).transpose()
    print(bd)

    print(bg)
    print()

    prod = bd * bg
    print(prod)

    prod_f = prod.f()
    print(prod_f)
    print(prod_f.i())

    alt = d[:1].sig() + g[:1]
    alt = alt.seq()

    for i in range(1, len(g)):
        alt += d[:1].f(length=l) ** (i - 1) * g[i] * (d[1] * x) ** i

    print(alt)

    diff = prod_f.i() - alt
    print(diff)


def mod_test():
    l = 20
    base36.default_base = 7
    d = Block.power(Seq(1, 1), l)

    for i in range(len(d)):
        d[i] = d[i] % base36.default_base

    print(d)

    # for each in d:
    #     print(Td(each.elements).convert(10))

    print(d.i())


def random_test():

    d = Seq(1, 1).td()
    g = Seq(1, 1).td()
    l = 10

    print(d)
    print(g)

    df = d.sig() * g.f(length=l)
    print(df)

    print((d * (d.sig() * g).f())[:l])

    out = Seq(0)
    g_f = g.f(length=l)
    for n in range(l):
        out += (d*x)**n * g_f[n]

    print((out[:l] * d) / d)


def make_sure_it_isnt_broken():
    d = Td.pi(base=10, log=True, perfect=True)
    l = 7

    d = Seq(Td([1, -1, 0], [0, -1, 1]))
    print(d.f())

    d = Seq(Td([1, 3], [1]))
    print(d.f())

    print(Seq(1, 1).td().sig() + Seq(1, 1).td())

    p = Prism(Seq(1, 1).td(), l) * Prism(Seq(1, 1).td(), l)

    print(p.f())
    print(p.i())


def main():
    # test0()
    # test1()
    # test2()
    # test3()
    # snr_36_test()
    # signature_product_test()
    # transpose_products()
    # ndf_seq_test()
    # prism_test_again()
    # transpose_product_test_2()
    # mod_test()
    # random_test()
    make_sure_it_isnt_broken()


if __name__ == "__main__":
    main()
