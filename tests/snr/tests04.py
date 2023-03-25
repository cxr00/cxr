from cxr import set_std_l, Seq, x
from cxr.math.snr import random_seq

"""
Identities from SNR3 (pending)
"""


def perturbation_identity():
    """
    Formula for computing the signature of a perturbed sequence
    """

    print("Perturbed sequence demonstration")
    l = set_std_l(50)
    root = Seq(1, 1)
    pert = random_seq()
    s = root.f()
    n = 2
    tmp = s + x**n * pert

    print(tmp)
    print(tmp.i()[:l-21])

    o = root
    i_add = root.sig()
    pert_pwr = pert
    x_pwr = x**(n - 1)
    for k in range(1, l-20):
        i_add = i_add + root
        to_add = (-1)**(k+1) * x_pwr * pert_pwr * (1 - x * i_add.seq)
        o += to_add
        pert_pwr *= pert
        x_pwr *= x ** n
    print(o[:l-21])
    print()


def perturbation_by_one_beginning_sequence():
    """
    Alternate perturbation identity when one-beginning sequence is added
    """
    print("Perturbation by one-beginning sequence")
    l = set_std_l(30)
    d = Seq(1, 1)
    g = Seq(1, 2, 1)
    n = 3

    N = d.f() + x**n * g.f()
    print(N.i()[:l-1])
    N = d*d.f() + x**(n-1) * g.f()
    N = N * N.neg().f()
    print(N[:l-1])
    print()


def subtraction_identity():
    """
    Memoized identity for signature subtraction
    """
    print("Subtraction identity demonstration")
    l = set_std_l(25)
    d = Seq(1, 1, 1)
    p = Seq(1, 1)

    g = d.sig() - p
    print(g.f())

    f_g = Seq(1)
    for n in range(1, l):
        _sum = d[n-1] - p[n-1]
        for k in range(1, n):
            _sum += f_g[n-k] * d[k-1]
        f_g.append(_sum)
    print(f_g)
    print()


def convolution_identity():
    """
    Memoized identity for convolution
    """
    print("Convolution identity demonstration")
    l = set_std_l(30)
    a = Seq(1, 1, 1)
    b = Seq(2, -1)

    print((a.f() * b.f())[:l])

    f_a = a.f()
    f_ab = Seq(1)
    for n in range(1, l):
        _sum = f_a[n]
        for k in range(1, n+1):
            _sum += f_ab[n-k] * b[k-1]
        f_ab.append(_sum)
    print(f_ab)

    f_b = b.f()
    f_ab = Seq(1)
    for n in range(1, l):
        _sum = f_b[n]
        for k in range(1, n+1):
            _sum += f_ab[n-k] * a[k-1]
        f_ab.append(_sum)
    print(f_ab)
    print()


def repsequences():
    print("Repsequences identity demonstration")
    l = set_std_l(30)
    a = 2
    d = Seq(2, 1, 1, 1, 1, 1, 1)
    df = d.f().aerate(a)
    df = sum([df * x**i for i in range(a)])
    print(df[:l])
    print(df.i()[:l])

    one = Seq(1).f()
    alt = 1 + x**(a-1) * (one * (d - 1)).aerate(a) - x**a * (one * (d - 1)).aerate(a)
    print(alt[:l])
    alt = Seq(1).sig() + x**(a-1) * (one * (d-1)).aerate(a)
    print(alt[:l])
    print()


def create_self_similar(t, g, r, p):
    l = 50
    print(t, g, r, p)

    q = Seq(t)
    for n in range(1, l):
        q.append(q.f(l=n)[n-g] * r**(n+p))
    return q


def self_similar_signature_test():
    print("Self-similar signature")
    t, g, r, p = 0, 2, 1, 1
    q = create_self_similar(t, g, r, p)

    print(q)
    print(q.f())
    print()


def N(S, a, b, c, l=20):
    """
    Compute the Noah's Diamond sequence of a sequence
    """
    out = [S[0]]
    for n in range(1, l):
        _sum = a*S[0] + b*S[n]
        _sum2 = 0
        binoms = Seq(1)
        for x in range(1, n):
            for k in range(x):
                _sum2 += binoms[k] * (S[k+1] + S[n-x+k])
            binoms *= Seq(1, 1)
        _sum += c * _sum2
        out.append(_sum)
    return Seq(out)


def noah_s_diamond_test():
    print("Noah's Diamond self-similar sequence test")
    s = Seq(2)
    F_inv_p = N(s.f(l=20), 2, 2, 2).i()
    print(F_inv_p)
    print(F_inv_p.f(l=20))
    print()


def seeded_sequence_convolution():
    """
    Demonstrates seeded sequence convolution.
    """
    print("Seeded sequence convolution")
    l = set_std_l(35)
    s0 = random_seq()
    s1 = random_seq()
    seed0 = random_seq()
    seed1 = random_seq()
    print("s0:", s0.f(l=l, seed=seed0)[:l])
    print("s1:", s1.f(l=l, seed=seed1)[:l])
    print()
    print("product:")
    print((s0.f(seed=seed0) * s1.f(seed=seed1))[:l])

    # Identity
    m = len(seed0) + len(seed1) - 1
    K = (s0.f(seed=seed0) * s1.f(seed=seed1))[:m]
    print((s0.sig() + s1).f(l=l, seed=K))
    print()


if __name__ == "__main__":
    perturbation_identity()
    perturbation_by_one_beginning_sequence()
    subtraction_identity()
    convolution_identity()
    repsequences()
    self_similar_signature_test()
    noah_s_diamond_test()
    seeded_sequence_convolution()
