from cxr.base36 import Tridozenal as Td
from cxr.htd import Htd

from cxr import htd
from cxr import base36

import time

implicit_base = 3
htd.default_hyperbase = 10
base36.default_base = implicit_base
base36.round_to = 13
htd.round_to = 13


def obfuscated_str(self):
    return str(self).replace(",", "").replace(".", "")


def init_test():

    def count_digits(string):
        output = [0 for _ in range(implicit_base)]
        for c in string:
            if c.isnumeric():
                output[int(c)] += 1
        return output

    s = Htd([Td(1), Td(1)], is_negative=True)

    print(s)
    print(s + Td(1))
    print(s - Td(1))
    print()

    print("s == s", s == s)
    print("s + s", s + s)
    print("s - s", s - s)
    print("s * 2", s * Td(2))
    print("s / 2", end=" ")
    print(s / Td(2))
    print("s // 2", end=" ")
    print(s // Td(2))
    print()

    print("powers of s")
    p = Htd(Td(1))
    for i in range(1, 8):
        p = p * s
        print(p)
    print()

    print(obfuscated_str(p))
    print(count_digits(obfuscated_str(p)))

    t = Td(100, base=10, is_negative=True)
    print(t)
    print(t // Td(3, base=10))
    print(t % Td(3, base=10))
    print()

    print(Td(-100, base=7))
    print()


def htd_mod_test():
    t = Htd(Td([1, 6, 3, 1]))
    g = Htd(Td([1, 1]))

    print(t % g)

    print(g % t)

    print(t / g)

    for p in range(5):
        print(g ** p)
    print()


def exp_test():
    e = Htd.exp(10, 10, log=True)

    print(e)


def pi_test():
    pi = Htd.pi(10, 10, log=True)

    print(pi)


def exp_test_2():

    e = Td.exp(implicit_base, Td(3, base=implicit_base), log=True)
    print(e)

    e = Htd.exp(htd.default_hyperbase, implicit_base, Td(3, base=implicit_base), log=True)

    print(e)


def convert_test():
    e = Htd([Td(1), Td(1), Td(1)])

    e = e.convert(hyperbase=6)

    print(e)

    e = e.divide_by(Td(2))

    print(e)


def ln_test():
    e = Htd(Td(2))
    print(e.ln(log=True))


def log_test():
    t = Td(2)

    e = Htd(t)

    print(e.logarithm(base=3))


def root_test():
    t = Htd(Td(2))

    print(t.root(log=True))


def main():
    t = time.time()

    init_test()
    htd_mod_test()
    exp_test()
    pi_test()
    exp_test_2()
    convert_test()
    ln_test()
    log_test()
    root_test()

    t2 = time.time()
    print("execution time:", t2 - t)


if __name__ == "__main__":
    main()
