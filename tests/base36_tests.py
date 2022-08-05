from cxr.base36 import Tridozenal as Td
from cxr.snr import Seq, Sig
from cxr import base36

import random


def basic_test():
    print("Basic test")
    d = Td([1, 1], [1, 1], 15)

    print(d * d)
    print(((d * d) / d))
    print()

    d_root = d.root(log=True)

    print(d_root)
    print((d_root ** 2))
    print((d_root * d_root))
    print()

    d_reciprocal = d.multiplicative_inverse()

    print(d_reciprocal)
    print()


def pi_test():
    print("Computing pi in multiple bases")

    all_pi = []

    for base in range(2, 12):
        all_pi.append(Td.pi(base, place=50, log=True, perfect=True))

    for pi in all_pi:
        pi.round(30)
        print(pi)

    print()


def e_test():
    print("Construct e in an arbitrary base")

    base = 10

    e = Td.exp(base, place=100, log=True, perfect=True)

    print(e)
    print()


def root_test():
    print("Root test")
    d = Td(2, 0, 12)
    power = 3
    place = 50

    d_root = d.root(power=power, place=place, log=True)

    print(d)
    print(d_root)

    d_root_squared = (d_root ** power)
    d_root_squared.round(place-5)
    print(d_root_squared)

    d = Td(2, 0, 18)
    d_root = d.root(power=2, num_iterations=15, place=150, log=True)
    print(d_root)

    d_root_squared = (d_root ** 2)
    d_root_squared.round(place=149)
    print(d_root_squared)


def larsen_pi_test():
    """
    Eric Larsen's definition of a base-12 pi
    """

    def larsen_pi_identity():
        """
        The division that yields Larsen pi
        """
        a = Td([0, 5], 0, 12)
        b = Td([7, 1], 0, 12)
        return a.divide_by(b, place=120)

    def from_string(s):
        def get_num(n):
            if n.isnumeric():
                return int(n)
            elif n == "a" or n == "A":
                return 10
            elif n == "b" or n == "B":
                return 11

        if "." in s:
            s = s.split(".")

            integer_part = Seq([get_num(char) for char in s[0]]).reverse()
            mantissa_part = Seq([get_num(char) for char in s[1]])

            return Td(integer_part.seq, mantissa_part.elements, 12)
        else:
            integer_part = Seq([get_num(char) for char in s]).reverse()
            return Td(integer_part, 0, 12)

    print("Larsen pi test")
    d = from_string("9.B80171918415674679410921168B84B052288614905B97343559980B203BA4A2A37A65475427AB29AA530370B6")
    d = d.root(place=51, log=True)

    print(d)

    print(larsen_pi_identity())
    print()


def negative_test():
    print("Negative test")
    d = Td(1, 2, 12, True)
    g = Td(1, 1, 12, False)
    f = Td(2, 0, 12, True)

    print("Display")
    print("d", d)
    print("g", g)
    print("f", f)
    print()

    print("order builtins")
    print("d < g", d < g)
    print("d > f", d > f)
    print()

    print("product")
    print("d*g", d * g)
    print("d*f", d * f)
    print("f^2", f ** 2)
    print()

    print("sum and difference")
    print("d+g", d + g)
    print("g+d", g + d)
    print("d-g", d - g)
    print("g-d", g - d)
    print("f-d", f - d)
    print("g-f", g - f)
    print()

    print("Pi and e test")
    pi = Td.pi(10, log=True)
    e = Td.exp(10, log=True)

    print(pi + e)
    print(e - pi)
    print()


def log_test():
    print("Logarithm test")

    d = Td(10, 0)
    place = 25

    # WARNING - This is perfect!
    d_ln = d.ln(place=place, log=True, perfect=True)
    d_log2 = d.logarithm(Td(2, 1), place=place, perfect=True)

    print()
    print(d_ln)
    print(d_log2)


def misc_test():
    d = Td.exp(36, place=115, log=True)
    print(d)
    # print(d.root(power=3, num_iterations=20))

    d = Td([1, 1], 0)
    g = Td([2, 1], [1, 2])

    print(d.logarithm(g, place=20, perfect=True))


def random_ln_test():
    t = Td(5, 0, 10).root(perfect=True)
    print(t)

    a = Td(5, 0, 12)
    b = Td(2, 0, 12)
    place = 25

    ln_a = a.ln(place=place, log=True)
    ln_b = b.ln(place=place, log=True)

    print(ln_a)
    print(ln_b)

    ln_div = ln_a / ln_b
    ln_div.round(place - 1)

    print(ln_div)

    print(ln_a - ln_b)


def exp_test():
    power = Td(2, 1, 12)

    print(Td.exp(12, power, log=True))


def better_power_test():
    power = Td(1, 5, 12)
    x = Td(2, 2, 12)

    print(x ** power)


def perfect_test():
    p = Td.pi(36, place=30, log=True, perfect=True)
    print(p)
    p = Td.exp(base=36, power=1, log=True, perfect=True)
    print(p)


def snr_tridozenal_test():
    b = Td(2, 0, 7)
    g = Td(1, 0, 7)

    s = Seq([b, g])
    s2 = Seq([2, 1])

    print(s * s)
    print(s2 * s2)
    print()

    s = Sig([b, b, g])
    s2 = Sig([2, 2, 1])
    print(s + s)
    print(s2 + s2)
    print()

    print(s * s)
    print(s2 * s2)
    print()

    td = Td(1, 0, 17)
    s = Sig([td, td])
    s = s + s

    print(s.f())
    print(s)
    print()


def readme_tests():
    td0 = Td(integer=10, base=2)
    td1 = Td(integer=3, base=2)

    print(td0 + td1)
    print(td0 - td1)
    print(td0 * td1)
    print(td0 / td1)
    print(td0 ** 2)
    print()

    td0 = Td.get_from_string("1.A078315B12B", base=12)

    print(td0)  # Displays 1.A078315B12B

    td0 = Td(integer=5, base=4)

    print(td0.root())  # Gives square root, 2.03301232330313023332211033200...
    print(td0.root(power=3))  # Gives cubic root, 1.231130003323303332301031032302...
    print()

    td0 = Td(integer=10, base=5)

    print(td0.ln(log=True))  # Displays 2.12240242122332442313

    td1 = Td(integer=3, base=5)

    print(td0.logarithm(td1, log=True))
    print()

    pi = Td.pi(base=12, log=True)
    print(pi)

    e = Td.exp(base=2, log=True)
    print(e)


def td_conversion_test():
    a = random.randint(10, 150)
    b = 10
    td0 = Td(a)
    td1 = Td(b)

    print("td0:", td0)
    print("td1:", td1)
    print("td0 // td1:", td0 // td1)
    print("td0 % td1:", td0 % td1)
    print()

    print("((td0 // td1) * td1) + (td0 % td1)")
    print(((td0 // td1) * td1) + (td0 % td1))
    print()

    print("Convert from default base to base 5 then base 10")
    print(td0.convert(5).convert(10))
    print(a)


def conversion_test():
    b0 = 7
    b1 = 3

    td = Td(90, base=b0)
    print(td)

    td = td.convert(b1)
    print(td)

    td = td.convert(b0)
    print(td)

    td = td.convert(b1)
    print(td)
    print()


def near_divisible_form_lemma():

    base36.default_base = 36
    a = random.randint(10000, 11000)
    td0 = Td(a)
    place = 15

    print(f"Near divisible forms of {td0}")
    print()

    first_form = (td0 - sum(td0.integer)) / (base36.default_base - 1)
    first_form.round(place=place)
    print("t = 1:", (td0 - sum(td0.integer)), "/", base36.default_base - 1, "=", first_form)

    for t in range(2, base36.default_base):

        print("t =", t, end=": ")
        td1 = td0.rebase(t).convert()
        solution = (td0 - td1) / (base36.default_base - t)
        solution.round(place=place)
        print(td0 - td1, "/", base36.default_base - t, "=", solution)
    print()


def ndf_2():
    a = random.randint(10000, 11000)
    td0 = Td(a)
    place = 15

    print(f"Near divisible forms of {td0}")
    print()

    for t in range(2, base36.default_base):
        print("t =", t, end=": ")
        td1 = td0.convert(t).rebase()
        solution = (td1 - td0) / (base36.default_base - t)
        solution.round(place=place)
        print(td1 - td0, "/", base36.default_base - t, "=", solution)
    print()


def ndf_3():
    a = random.randint(10000, 11000)
    td0 = Td(a)
    place = 15

    print(f"Near divisible forms of {td0}")
    print()

    for t in range(2, base36.default_base):
        print("t =", t, end=": ")
        td1 = td0.rebase(t).rebase()
        solution = (td1 - td0) / (base36.default_base - t)
        solution.round(place=place)
        print(td1 - td0, "/", base36.default_base - t, "=", solution)
    print()


def main():
    # basic_test()
    # pi_test()
    # e_test()
    # root_test()
    # larsen_pi_test()
    # negative_test()
    # log_test()
    # misc_test()
    # snr_tridozenal_test()
    # readme_tests()
    # td_conversion_test()
    near_divisible_form_lemma()
    # conversion_test()
    ndf_2()
    ndf_3()


if __name__ == "__main__":
    main()
