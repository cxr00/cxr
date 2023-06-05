from cxr import Seq, Matrix, x, set_std_l

"""
Interesting constructed triangles compiled during SNR1 exploration.
The triangles' formulas may be found in SNR3.6
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


def catalan_triangles():
    l = set_std_l(18)

    def catalan():
        output = Seq(1)
        for i in range(1, l):
            output = output.f(l=i+1)
        return output

    j = 3
    a = 2
    m = Matrix.blank()
    m[0][0] = 1
    c = catalan()

    for n in range(1, l):
        for k in range(n+1):
            m[n][k] = m[n-1][k-1] + j * m[n-1][k+1]

    print(m.f(a=a))
    # print(m.i(a=a))

    r_j = Seq([c[n] * j**(n+1) for n in range(l)])
    alt = x**a + x * r_j.aerate(2)
    print(alt.f())
    print()

    m = Matrix.blank()

    for n in range(l):
        m[n][0] = 1
        m[n][1] = n
        for k in range(2, n+1):
            m[n][k] = m[n][k-1] + m[n-1][k]

    print(m.i(a=a))

    alt = 1 + x**a * catalan().aerate(a+1)
    print(alt)
    print()


def hankel():
    l = set_std_l(40)
    d = Seq(1, 1)
    f_d = d.f(l*2)

    m = Matrix([f_d[n:n+l] for n in range(l)])

    for a in range(1, 6):
        print(m.i(a=a))

        alt = Seq(1)
        for k in range(1, len(d)):
            alt += d[k-1] * k * x**(a*k+1)

        aer = d.aerate(a) * x**(a-1)
        alt *= (d.sig() + aer).f().seq
        print(alt.i()[:l-1])
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
    catalan_triangles()
    hankel()
