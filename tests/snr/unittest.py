import unittest
from cxr import Seq, Sig, x, Matrix, Prism, set_std_l
from cxr.math import g_prism_identity, simplex_identity


class SeqTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertLess(Seq(0, 1), Seq(1, 2, 3))

        self.assertLessEqual(Seq(10, 11), Seq(11, 12))
        self.assertLessEqual(Seq(1, 2), Seq(1, 2))

        self.assertEqual(Seq(1, 2, 0, 1, 0), Seq(1, 2, 0, 1))

        self.assertGreaterEqual(Seq(2, 1), Seq(1, 10))
        self.assertGreaterEqual(Seq(1, 9), Seq(1, 9))

        self.assertGreater(Seq(0, 1), Seq(-1, 2))

    def test_get_setitem(self):
        self.assertEqual(Seq(1, 2, 3, 4, 5, 6, 7)[3], 4)
        self.assertEqual(Seq(1, 2, 3, 4, 5, 6, 7, 8)[1:-2:2], Seq(2, 4, 6))
        s = Seq(1, 2, 3, 4, 5)
        s[1] = 0
        self.assertEqual(s, Seq(1, 0, 3, 4, 5))

    def test_mod(self):
        self.assertEqual(Seq(1, 2, 4, 7, 11, 16, 22) % 3, Seq(1, 2, 1, 1, 2, 1, 1))

    def test_arithmetic(self):
        self.assertEqual(Seq(1, 1) + Seq(1, 0, 1), Seq(2, 1, 1))

        self.assertEqual(Seq(3, 2, 1) - Seq(0, 1, 2), Seq(3, 1, -1))

        self.assertEqual(Seq(1, 0, 1) * Seq(1, 1), Seq(1, 1, 1, 1))

        self.assertEqual(-Seq(1, 2, -1, -2), Seq(-1, -2, 1, 2))

        self.assertEqual(Seq(2, 1) ** 4, Seq(16, 32, 24, 8, 1))

        self.assertEqual(Seq(1, 2, 3, 3, 2, 1) / Seq(1, 1, 1), Seq(1, 1, 1, 1))
        self.assertEqual(Seq(0, 1, 1) / x, Seq(1, 1))

        self.assertEqual(Seq(1, 2, 1).sqrt(), Seq(1, 1))

    def test_utilities(self):
        s = Seq(1, 1, 2, 0)
        s.append(-3)
        self.assertEqual(s, Seq(1, 1, 2, 0, -3))

        self.assertEqual(s.aerate(3), Seq(1, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, -3))

        self.assertEqual(s.base(), 10)

        self.assertEqual(s.concat(s), Seq(1, 1, 2, 0, -3, 1, 1, 2, 0, -3))

        self.assertEqual(s.dot_product(s), 15)
        self.assertEqual(s.partial_dot_product(s), Seq(1, 1, 4, 0, 9))

        self.assertEqual(s.polynomial(use_ss=True), "x⁴ + 2x² - 3")

        p = s.pop(3)
        self.assertEqual(p, 0)
        self.assertEqual(s, Seq(1, 1, 2, -3))

        self.assertEqual(s.reverse(), Seq(-3, 2, 1, 1))

        self.assertEqual(Seq(1, 0, 0, 0, 0, 1, 0, 0).trim(), Seq(1, 0, 0, 0, 0, 1))

    def test_signature_function(self):
        l = set_std_l(15)
        self.assertEqual(Seq(1, 1).f(), Seq(1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610))
        self.assertEqual(Seq(1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610).i(), Seq(1, 1))
        self.assertEqual(Seq(1, 1).f(seed=Seq(2, 1)), Seq(2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843))



class SigTestCase(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(Sig(1, 1) + Sig(2, 1), Sig(3, 0, -3, -1))

        s = Sig(3, 0, -3, -1) - Sig(2, 1)
        self.assertEqual(s[:len(s)-3], Sig(1, 1))

        self.assertEqual(Sig(1, 1) * Seq(1, 2, -1), Sig(1, 3, 3, -1, -3, -1))

        self.assertEqual(Sig(1, 3, 3, -1, -3, -1) / Sig(1, 1), Sig(1, 2, -1))
        self.assertEqual(Sig(1, 3, 3, -1, -3, -1) // Sig(1, 2, -1), Sig(1, 1))

        self.assertEqual(Sig(1, 1, 1) ** 2, Sig(1, 2, 4, 6, 8, 8, 6, 3, 1))

        self.assertEqual(Sig(1, 1).iter_add(3), Sig(3, 0, -5, 0, 3, 1))

        self.assertEqual(Sig(1, 1).multiplicative_inverse(l=15), Sig(1, -1, 2, -5, 14, -42, 132, -429, 1430, -4862, 16796, -58786, 208012, -742900, 2674440))

    def test_utilities(self):
        self.assertEqual(Sig(0, 0, 1, 1, 1).first_nonzero(), 2)



class MatrixTestCase(unittest.TestCase):
    def test_arithmetic(self):
        l = set_std_l(15)
        s1 = Seq(1, 1)
        s2 = Seq(2, 0, 1)
        m1 = Matrix.power(s1)
        m2 = Matrix.power(s2)
        mf = (m1 + m2).f()[:l]
        self.assertEqual(mf, m1.f() + m2.f())

        mf = (m1 * m2).f()
        self.assertEqual(mf, sum([s1[k] * s2**k for k in range(len(s1))]).f())

        bs = m1.base_sequence(2)
        self.assertEqual(bs, Seq(3).f())

        self.assertEqual(m1.i(), Seq(1, 1))


    def test_utilities(self):
        l = set_std_l(15)
        m = Matrix.power(Seq(1, 1))
        self.assertEqual(m[5][3], 10)
        m[5][3] = 9
        self.assertEqual(m[5][3], 9)
        m[5][3] = 10

        ml = len(m)
        m.append(Seq(1, 1, 1, 1))
        self.assertEqual(ml+1, len(m))
        m = m[:-1]

        col = m.column(2)
        self.assertEqual(col, Seq(0, 0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91))
        diag = m.diagonalise()
        self.assertEqual(diag.f(), Seq(1, 1, 1, 2, 3, 4, 6, 9, 13, 19, 28, 41, 60, 88, 129))

        self.assertEqual(m.transpose().transpose().trim(), m)


class PrismTestCase(unittest.TestCase):
    def test_prism_signatures(self):
        l = set_std_l(8)

        # Canonical identity
        s1 = Seq(1, 1)
        s2 = Seq(3, 0, 1)
        p = Prism.canonical([s1, s2], l=l)
        self.assertEqual(p.f(), (s1.sig() + s2).f())

        ppow = Prism.power(s1, l=l)
        self.assertEqual(ppow.f(), (s1.sig().iter_add(3)).f())

        # G-prism identity
        pg = Prism.g_prism([s1, s2], [s2, s1], l=l)
        d = [s1, s2]
        g = [s2, s1]
        self.assertEqual(pg.f(), g_prism_identity(d, g).f())

        # Simplex identity
        d = [s1, s1+1, s1-1]
        ps = Prism.simplex(d, l=l)
        self.assertEqual(ps.f(), simplex_identity(d).f())


if __name__ == "__main__":
    unittest.main()
