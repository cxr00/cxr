from cxr import Seq, Matrix


def test_4_5_identities():
    """
    Let the record show it works. I swear.
    STOP TESTING THIS IDENTITY FOR THE LOVE OF gOD
    """
    d = Seq(1, 1)
    l = 10
    g = [Seq(1), Seq(2, 1), Seq(1, 1)]

    S = Matrix.g_matrix(Matrix.sen(d, l), g, l)

    output2 = Seq([0 for _ in range(l)])
    output = Seq(output2)
    for n in range(l):
        for k in range(n + 1):
            p = S ** (k + 1)
            r = S ** (n - k)
            output[n] += p[k][0]
            output2[n] += r[k][0]

    print(output)
    right_side = d + sum([e.sig() for e in g]).seq
    print(right_side.f())

    print(output2)
    right_side = Seq(-1) + sum([e.sig() for e in g]).seq
    right_side = right_side.sig() + (d * d.neg().f()).sig()
    print(right_side.f().f())

    a = Matrix.power(Seq(1, 1))
    b = Matrix.power(Seq(1, 1))

    print((a + b).f())
    print(Seq(1, 1).f(seed=Seq(2, 2)))


def main():
    test_4_5_identities()


if __name__ == "__main__":
    main()
