from cxr.snr import x
from cxr.snr import Seq, Sig, Block
from cxr.snr import signature_function, g_prism_identity, g_prism
import random


class PrismaticSeq:
    """
    Implements prismatic signature addition
    """

    def __init__(self, val, dim=2):
        if isinstance(val, PrismaticSeq):
            self.val = val.val
        else:
            self.val = Seq(val)
        if dim < 2:
            raise ValueError("Dimension must be 2 or greater")
        else:
            self.dim = dim

    def __add__(self, other):
        if isinstance(other, (int, float, list)):
            addend = Seq(other)
        elif isinstance(other, Seq):
            addend = other
        elif isinstance(other, Sig):
            addend = other.seq
        elif isinstance(other, PrismaticSeq):
            addend = other.val
        else:
            raise TypeError(f"Invalid type {type(other).__name__}, must be int, float, list, Seq, or PrismaticSeq")

        addend = addend.aerate(self.dim - 1)

        root = self.val.sig() + Sig(1).iter_add(self.dim - 2)
        return PrismaticSeq(root + addend)

    def __eq__(self, other):
        if isinstance(other, (PrismaticSeq, Sig)):
            return self.val == other.seq
        elif isinstance(other, Seq):
            return self.val == other
        else:
            return False

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.val[item]
        elif isinstance(item, slice):
            return PrismaticSeq(self.val[item])
        else:
            raise TypeError(f"Invalid __getitem__ type {type(item).__name__}")

    def __iadd__(self, other):
        return self + other

    def __iter__(self):
        return iter(self.val)

    def __str__(self):
        return str(self.val)


def random_seq():
    return Seq([random.randint(-7, 7) for _ in range(random.randint(2, 5))])


def random_one_beginning_block():
    return Block([Seq([1] + random_seq().elements)] + [random_seq() for _ in range(9)])


def apex_test():
    d = Seq([1, 1])
    g0 = Seq([1, 1, 1])
    g1 = Seq([1])

    print(g_prism_identity(d, [g0, g1]))
    print(g_prism_identity(d, [g1, g0]))
    print()

    print(g_prism_identity(d, [g_prism_identity(g0, [g1])]))
    print(g_prism_identity(d, [g_prism_identity(g1, [g0])]))
    print()

    print(g_prism_identity(d, [g1]))
    print()


def prismatic_test_1():
    d = PrismaticSeq(Seq([1, 1]))
    g0 = Seq([1, 1, 1])
    g1 = Seq([1])

    print(g_prism_identity(d.val, [g0, g1, Seq(1)]))
    print(d + g0 + g1 + Seq(1))
    print(d + Seq(1) + g0 + g1)
    print()

    print(d + Seq(0))
    print()

    d += g0
    d += g1
    d += Seq(1)
    print(d)
    print()


def prismatic_test_2():
    """
    Tests whether prismatic signature addition always
    outputs a signature whose sum is 1
    """

    print("Testing prismatic signature addition with random signatures")
    for _ in range(1, 10001):
        d = PrismaticSeq(random_seq())
        g = random_seq()
        if sum(d + g) != 1:
            print("Counterexample found:")
            print("d:", d)
            print("g:", g)
            break
        elif not _ % 100:
            print(".", end="")
            if not _ % 10000:
                print()

    print()


def iterative_prismatic_test():
    s = Seq([1, 1, 2, 1])
    d = PrismaticSeq(s)

    # print(Seq([1, 4, 13, 40, 121, 364, 1093, 3280]).i())
    print(Seq([4, -3]).f(seed=Seq([len(s), 3*len(s) + 1])))

    for _ in range(7):
        t = d.val.trim()
        print(len(t))
        d += t
    print()


def flexible_test():
    """
    Unsurprising that (sd)s =/= s(ds)
    """
    s = Seq([1, 1])
    d = Seq([2, 1])

    print(PrismaticSeq(s) + (PrismaticSeq(d) + s).val)
    print((PrismaticSeq(s) + d) + s)
    print()


def identity_test_1():
    """
    Tests whether psa has pseudo-associativity
    """
    s = Seq([1, 1])

    d = PrismaticSeq(s) + s

    print(d + s)
    print((PrismaticSeq(s) + d))
    print()


def alternativity_test():
    s = Seq([1, 1])
    d = Seq([2, 1])

    print(PrismaticSeq(s) + s + d)
    print(PrismaticSeq(s) + (PrismaticSeq(s) + d))
    print()


def misc_sig_tests():
    d = random_seq().sig()
    g = random_seq().sig()

    print(d)
    print(g)
    print(d + g)
    print(sum(d + g))
    print(sum(d) + sum(g) - sum(d)*sum(g))
    print()


def distributivity_test():
    d = Seq([1, 1])
    a = Seq([1, 1])
    b = Seq([2, -1])

    # Check if d * (a o b) = (d * a) o (d * b)
    print(PrismaticSeq(d) + (a.sig() * b.sig()).seq)

    p0 = PrismaticSeq(d) + a
    p1 = PrismaticSeq(d) + b
    print(p0.val.sig() * p1.val.sig())
    print()

    # Check if a o (d * b) = (a o d) * (a o b)
    p0 = PrismaticSeq(d) + b
    print(a.sig() * p0.val.sig())

    d0 = a.sig() * d.sig()
    d1 = a.sig() * b.sig()
    print(PrismaticSeq(d0.seq) + d1.seq)
    print()

    # Check if (d * a) o b = (d o b) * (a o b)
    p0 = PrismaticSeq(d) + a
    print(p0.val.sig() * b.sig())

    d0 = d.sig() * b.sig()
    d1 = a.sig() * b.sig()
    print(PrismaticSeq(d0.seq) + d1.seq)
    print()


def mediality_test():
    dx = PrismaticSeq(random_seq())
    dy = PrismaticSeq(random_seq())

    du = PrismaticSeq(random_seq())
    dv = PrismaticSeq(random_seq())

    print(dx)
    print(dy)
    print(du)
    print(dv)
    print()

    # Check whether (x + y) + (u + v) = (x + u) + (y + v)
    a = (dx + dy) + (du + dv)
    b = (dx + du) + (dy + dv)

    # Verify the lesser condition (x + y) + (u + v) = (x + (u + v)) + y
    c = (dx + (du + dv)) + dy

    print(a)
    print(b)
    print(c)
    print("a == b == c :", a == b == c)
    print()


def full_g_prism_construction_test():
    d = Seq([1, 1])
    g0 = Seq([1, 1])
    g1 = Seq([2, -1])

    p = g_prism(Block.power(d, l=15), [g0, g1], l=15)

    print(signature_function(p).i())

    print(g_prism_identity(d, [g0, g1]))
    print()


def g_prism_of_matrix_test():
    """
    Demonstration that any one-beginning matrix
    may be subjected to prismatic addition
    """
    l = 10
    b = random_one_beginning_block()
    g = [random_seq() for _ in range(3)]
    s_p_prev = None

    for n in range(len(g) + 1):
        p = g_prism(b, g[:n], l=l)

        s_p = signature_function(p)
        print(s_p)
        print(s_p.i())

        if n == 0:
            s_p_prev = PrismaticSeq(s_p.i())
        else:
            s_p_prev = s_p_prev + g[n - 1]
            s_p_prev = s_p_prev[:l-1]
            print(s_p_prev)

        print()


def improved_prismatic_addition_identity():
    """
    Prismatic addition is just signature addition!
    """
    a = random_seq()
    b = random_seq()

    d = PrismaticSeq(a)
    d += b
    print(a)
    print(b)
    print()

    print(d)

    d = a.sig() + b.aerate(2).sig() + Sig(1)
    print(d)
    print()


def medial_substitution_test():
    g = Seq([2, 1])
    s = Seq([1, 1])
    f = Seq([2, -1])

    a = 4

    sub_calc = (s.sig() + Sig(1).iter_add(a - 2) + f.aerate(a).sig()).seq.aerate(a)
    id_a = g.aerate(a).sig() + sub_calc

    sub_calc = (g.sig() + Sig(1).iter_add(a - 2) + f.aerate(a).sig()).seq.aerate(a)
    id_b = s.aerate(a).sig() + sub_calc

    print(id_a)
    print(id_b)
    print()


def medial_substitution_test_2():
    d = random_seq()
    g = random_seq()
    s = random_seq()
    f = random_seq()

    print(PrismaticSeq(d) + g + (PrismaticSeq(s) + f))
    print(PrismaticSeq(d) + s + (PrismaticSeq(g) + f))
    print()


def dimensional_prismatic_addition_test():
    d = random_seq()
    g = random_seq()
    s = random_seq()
    f = random_seq()

    N = random.randint(2, 5)
    K = random.randint(2, 5)

    print("N:", N, "K:", K)
    print("d:", d)
    print("g:", g)
    print("s:", s)
    print("f:", f)
    print()

    id_a = PrismaticSeq(PrismaticSeq(d, N) + g, K) + s
    id_b = PrismaticSeq(PrismaticSeq(d, K) + s, N) + g

    print("Right cross-commutativity")
    print("d *N g *K s = d *K s *N g")
    print(id_a)
    print(id_b)
    print()

    id_a = PrismaticSeq(PrismaticSeq(d, K) + g, K) + (PrismaticSeq(s, N) + f)
    id_b = PrismaticSeq(PrismaticSeq(d, K) + s, K) + (PrismaticSeq(g, N) + f)

    print("N-mediality")
    print("(d *K g) *K (s *N f) = (d *K s) *K (g *N f)")
    print(id_a)
    print(id_b)
    print()

    id_a = PrismaticSeq(d, K) + g
    id_a += PrismaticSeq(s, N) + f

    id_b = PrismaticSeq(d, K) + g
    id_b = PrismaticSeq(id_b, N) + (PrismaticSeq(f, K) + s)

    print("(d *K g) *K (s *N f) =/= (d *K g) *N (f *K s)")
    print(id_a)
    print(id_b)
    print()


def aeration_experiment():
    d = Seq([1, 1])
    g = Seq([2, -1])
    s = Seq([2])

    N = 3
    print(d.aerate(N).sig() + g.aerate(N).sig())
    print((d.sig() + g.sig()).aerate(N))

    M = 3
    print(d.aerate(N).aerate(M))
    print(d.aerate(M).aerate(N))
    print(d.aerate(M*N))


def aeration_multiplication_test():
    d = Seq([1, 1])
    g = Seq([2, -1])
    s = Seq([2])
    f = Seq([1, -1])

    N = 2
    M = 2
    K = 2

    id_a = PrismaticSeq(d, N) + g
    id_a = PrismaticSeq(id_a, M) + (PrismaticSeq(s, K) + f)

    id_b = PrismaticSeq(d, N) + g
    id_b = PrismaticSeq(id_b, M) + (PrismaticSeq(s, K) + Seq(0))
    id_b = id_b.val.sig() + f.sig().aerate(M*K - K - M + 1)

    print(id_a)
    print(id_b)

    id_c = d.sig() + Sig(1).iter_add(N-2) + Sig(1).iter_add(M-2) + g.aerate(N-1).sig()
    id_c += (s.sig() + Sig(1).iter_add(K-2)).aerate(M-1) + f.aerate((M-1)*(K-1)).sig()

    print(id_c)


def main():
    # apex_test()
    # prismatic_test_1()
    # prismatic_test_2()
    # iterative_prismatic_test()
    # flexible_test()
    # identity_test_1()
    # alternativity_test()
    # misc_sig_tests()
    # distributivity_test()
    # mediality_test()
    # full_g_prism_construction_test()
    # g_prism_of_matrix_test()
    # improved_prismatic_addition_identity()
    # medial_substitution_test()
    # medial_substitution_test_2()
    # dimensional_prismatic_addition_test()
    # aeration_experiment()
    aeration_multiplication_test()


if __name__ == "__main__":
    main()
