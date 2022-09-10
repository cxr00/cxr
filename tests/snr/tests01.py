from cxr import Seq, Matrix, Prism, SDP
import time


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


def prismatic_convolution_vs_sdp():
    d = Seq(1, 1)
    n = 3
    l = 13

    t = time.time()
    p = Prism.canonical([d] * n, l=l)
    # p, count = Prism.canonical([d]*n, l=l)
    pf = p.f([d] * (n + 1))
    pi = pf.i()
    # print(count)
    print()
    print(pf)
    print(pi)
    print(time.time() - t)
    print()

    t = time.time()
    a = SDP([d] * n, [d] * n)
    print(len(a))
    print(a)
    print(time.time() - t)


def generalized_motzkin_numbers(M_factor=1):
    """

    :param M_factor: value of 1 produces A001006
    """
    a = Seq(*[1 for _ in range(M_factor + 2)])

    t = time.time()
    for i in range(M_factor + 2, 15):
        n = 0
        for k in range(i - M_factor):
            if i - k - 1 < 0:
                break
            else:
                n += a[k] * a[i - k - 1]
        a.append(n)
    print(a)
    print(time.time() - t)


def A356891(length):
    """
    The Borrow from Tomorrow sequence
    """
    output = [1] * length
    for n in range(2, length):
        output[n] += output[n-3] if n % 2 else output[n-1] * output[n-2]
    return output


def main():
    test_4_5_identities()


if __name__ == "__main__":
    main()
