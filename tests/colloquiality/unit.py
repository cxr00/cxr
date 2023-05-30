from cxr import Clq, UndefinedError


def clq_test():
    c = Clq("210d")
    print(c)
    print(c.convert())
    print("is involution:", c.is_involution())
    print()

    c = Clq("--90-521-3d", abbrev=True)
    print(c)
    print(c.convert())

    print(repr(Clq("1056p").convert().convert()))
    print(repr(Clq("67d").convert().convert()))
    print()

    print(Clq("210d") == Clq("210p"))
    print(Clq("1056p") == Clq("10---23d"))
    print()

    print(Clq("7268d").compile())
    print()

    print(Clq.decompile(Clq("7268p").compile(), "p"))
    print(Clq.decompile(Clq("7268d").compile(), "d"))


def arith_test():
    a = Clq("01d") + Clq("102-3d")
    print("sum:", a.compile())
    a -= Clq("102-3d")
    print("diff", a.compile())
    a -= Clq("----4d")
    print("diff", a.compile())
    print()

    c = Clq("0d") + Clq("-1d") + Clq("--34p")
    print("sum:", c.compile())
    print()

    b = Clq("120d")
    print("b:", b.compile())
    print("identity:", b + Clq("-p"))
    print("b first:", b + Clq("10d"))
    print("b last:", Clq("10d") + b)
    print("sub:", b - Clq("-d") - Clq("-p"))
    print()

    # Associativity test
    a, b, c = Clq("120d"), Clq("360d"), Clq("415d")
    print("a + b:", a + b)
    print("left assoc:", repr((a + b) + c))

    print("b + c:", b + c)
    print("right assoc:", repr(a + (b + c)))


def inclusion_test():
    print("### INCLUSION TEST ###")
    a = Clq("01d")
    b = Clq("10p")
    ab = a + b
    print("ab:", ab, ab.compile())
    abb = a + b + b
    print("abb:", abb, abb.compile())
    print()

    a = Clq("0123d")
    print("a:", a.compile())
    b = Clq("10234p")
    print("b:", b.compile())
    ab = a + b
    print("ab:", ab.compile(), ab, ab.convert())
    c = Clq("-----9d")
    ab_c = ab + c
    print("ab_c:", ab_c, ab_c.convert())

    d = Clq("0246d")
    try:
        ab_c_d = ab_c + d
        print("ab_c_d:", ab_c_d, ab_c_d.compile())
    except UndefinedError:
        print(f"Inclusion {ab_c} + {d} is undefined")
    print()


def reduction_test():
    print("### REDUCTION TEST ###")
    a = Clq("013254d")
    b = Clq("0132p")
    ab = a - b
    print("ab:", ab, ab.convert())
    print()

    a = Clq("1023d")
    b = Clq("102p")
    ab = a - b
    print("ab:", ab.compile(), ab, ab.convert())
    print()

    a = Clq("1234p")
    b = Clq("213p")
    try:
        a_b = a - b
        print(a.convert(), b, a_b, a_b.convert())
    except UndefinedError:
        print(f"Reduction {a} - {b} is undefined")
    print()


def integrity_test():
    print("### INTEGRITY TEST ###")
    a = Clq("1032d")
    b = Clq("0213d")
    c = Clq("-12-45d")
    Z = Clq("-d")
    E = Clq("0123456789d")
    print("a:", a)
    print("b:", b)
    print("c:", c)
    print()

    print("add1:", a + b)
    print("add_assoc", (a + b) + c, a + (b + c))
    print("addZ:", a + Z, Z + a)
    print()

    print("sub1:", a - b)
    print()

    print("subZ:", a - Clq("-p"))
    print()

    print("a-c:", a - c)
    print("a+c:", a + c)

    t_a = a
    for i in range(10):
        t_a = t_a + a
        if a == b:
            print(f"Iterated addition of {a} yielded original string in {i+1} iterations")
            break
    print()


def readme_tests():
    print("### README TESTS ###")
    a = Clq("103254p")
    print(a.compile())

    a = Clq("02143d")
    print(a + a)

    a = Clq("-12-45d")
    b = Clq("1032d")
    print(a + b)

    a = Clq("102349d")
    b = Clq("0246d")
    try:
        print(a + b)  # UndefinedError
    except UndefinedError:
        print(f"Failed to perform {a} + {b}; undefined")
    print()

    a = Clq("013254d")
    b = Clq("0132p")
    print(a - b)  # --2354d

    a = Clq("1023d")
    b = Clq("102p")
    print(a - b)  # 01-3d

    a = Clq("1234p")
    b = Clq("213p")
    try:
        print(a - b)  # UndefinedError
    except UndefinedError:
        print(f"Failed to perform {a} - {b}; undefined")

    a = Clq("01234d")
    print(a - Clq("01p"))
    print(a - Clq("012p"))  # --34d
    print(a - Clq("0123p"))  # ---4d
    print(a - Clq("01234d"))  # -d
    print(a - Clq("1032547698p"))  # -d
    print()


def convo_test():
    print("### DE/CONVOLUTION TEST ###")

    a = Clq("0213d")
    b = a * "-1-3d"
    print(a, a.compile())
    print(b, b.compile())
    print()

    a = Clq("0231d")
    print("a", a.compile())
    b = a / "-2d"
    print(b, b.compile())
    print()

    a = Clq("1402d")
    print("a", a.compile())
    b = a / "24d"
    print(b, b.compile())
    print()

    a = Clq("-1-3-56d")
    print(a.compile())
    b = a / "-5-6d"
    print(b, b.compile())
    print()

    a = Clq("8564-1d")
    print(a.compile())
    b = a / "-8--6d"
    print(b, b.compile())
    print()


def potential_ringlike_test():
    print("### RINGLIKE TEST ###")
    a = Clq("1032547698d")
    b = Clq("120d")
    # c = Clq("230154d")
    c = Clq("201453p")
    print(a * (b + c))
    print(a * b + a * c)
    print()
    print(a * b)
    print((b * a).convert())
    print(b + c, c + b)
    print("assoc", (a * b) * c, a * (b * c))
    E = Clq("0123456789d")
    print("w/ E", a * E, E * a)
    E = Clq("-d")
    print("w/ E", a * E, E * a)
    print()

    try:
        print((a*b) / a)
    except UndefinedError as exc:
        print(f"{exc}")


if __name__ == "__main__":
    inclusion_test()
    reduction_test()
    integrity_test()
    readme_tests()
    convo_test()
    potential_ringlike_test()
