from cxr import Seq, Matrix, x, set_std_l

"""
Interesting constructed triangles compiled during SNR1 exploration
"""


l = set_std_l(20)
d = Seq(1, 1, 1)
a = 3
df = Matrix.power(d.f())
md = Matrix.power(d, l=l+1)


def t1():
    Kd = Matrix([Seq(d.f(l=n+1)) for n in range(l)])
    # print(Kd)

    print(Kd.f(a))
    alt = Seq(1).sig() + (x**a * d.aerate(a+1))
    print(alt.f())
    print()


def t2():
    Qd = Matrix([d.f(l=n+1)[::-1] for n in range(l)])
    # print(Qd)

    print(Qd.f(a))
    alt = d.sig() + x**a
    print(alt.f())
    print()


def t3():
    Gd = Matrix([Seq([df[y+1][n-y] for y in range(n+1)]) for n in range(l)])
    # print(Gd)

    print(Gd.f(a))
    alt = d + x**a
    print(alt.f())
    print()


def t4():
    Bd = Matrix([Seq([df[n-y+1][y] for y in range(n+1)]) for n in range(l)])
    # print(Bd)

    print(Bd.f(a))
    alt = 1 + x**a * d.aerate(a+1)
    print(alt.f())
    print()


def t5():
    Pd = Matrix([Seq([md[y][n-y] for y in range(n+1)]) for n in range(l)])
    # print(Pd)

    print(Pd.f(a))
    alt = d*x**a
    print(alt.f())
    print()


def t6():
    Pprimed = Matrix([Seq([md[y+1][n-y] for y in range(n+1)]) for n in range(l)])
    # print(Pprimed)

    print(Pprimed.f(a))
    alt = d * x**a
    print((alt.f() * d)[:l])
    print()


def t7():
    Jd = Matrix([Seq([md[n-y][y] for y in range(n+1)]) for n in range(l)])
    # print(Jd)

    print(Jd.f(a))
    alt = d.aerate(a+1)
    print(alt.f())
    print()


def t8():
    Jprimed = Matrix([Seq([md[n-y+1][y] for y in range(n+1)]) for n in range(l)])
    # print(Jprimed)

    print(Jprimed.f(a))
    alt = d.aerate(a+1)
    print((alt.f() * alt)[:l])
    print()


if __name__ == "__main__":
    t1()
    t2()
    t3()
    t4()
    t5()
    t6()
    t7()
    t8()
