from cxr import Seq, Matrix, Prism, SDP
import time


def test_4_5_identities():
    """
    Let the record show it works. I swear.
    STOP TESTING THIS IDENTITY FOR THE LOVE OF gOD
    """
    print("## 4.5 identities test")
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
    print()

    print(output2)
    right_side = Seq(-1) + sum([e.sig() for e in g]).seq
    right_side = right_side.sig() + (d * d.neg().f()).sig()
    print(right_side.f().f())
    print()

    a = Matrix.power(Seq(1, 1))
    b = Matrix.power(Seq(1, 1))

    print((a + b).f())
    print(Seq(1, 1).f(seed=Seq(2, 2)))
    print()


def mnr_identities():
    """
    Demonstrates identities from SNR part 2 section 1.3

    We arrive at the implication of signature arithmetic
    without an explicit signature function
    """
    print("## MNR identities")
    l = 12
    m = []

    a = Seq(1, 1)
    b = Seq(0, 1, 1)

    ak1 = 1
    bk1 = 1
    for i in range(l):
        ak1 *= a
        bk1 *= b
        m.append((ak1 - bk1) / (a-b))

    m = Matrix(m)
    print(m)
    print()
    print(m.i())
    print(a.sig() + b.sig())
    print()

    am = Matrix.power(a, l=l)
    bm = Matrix.power(b, l=l)

    print((am*bm).i())
    print(sum([a[k] * b**k for k in range(len(a))]))
    print()

    print((am * Matrix.power(b*Seq(0, 1), l=l)).i())
    print((b.sig() * a.sig()).seq / b)
    print()


def prismatic_convolution_vs_sdp():
    print("## Prismatic convolution vs SDP")
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
    print()


def generalized_motzkin_numbers(M_factor=1):
    """

    :param M_factor: value of 1 produces A001006
    """
    print(f"Generalized Motzkin numbers for M_factor of {M_factor}")
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
    print()


def A356891(length):
    """
    The Borrow from Tomorrow sequence, ungeneralized
    """
    output = [1] * length
    for n in range(2, length):
        output[n] += output[n-3] if n % 2 else output[n-1] * output[n-2]
    return output


def main():
    mnr_identities()
    test_4_5_identities()


if __name__ == "__main__":
    main()
