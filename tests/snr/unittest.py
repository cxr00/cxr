import unittest
from cxr import Seq, Sig, x, Matrix, Prism, set_std_l


class SeqTestCase(unittest.TestCase):

    def test_eq(self):
        self.assertLess(Seq(0, 1), Seq(1, 2, 3))

        self.assertLessEqual(Seq(10, 11), Seq(11, 12))
        self.assertLessEqual(Seq(1, 2), Seq(1, 2))

        self.assertEqual(Seq(1, 2, 0, 1, 0), Seq(1, 2, 0, 1))

        self.assertGreaterEqual(Seq(2, 1), Seq(1, 10))
        self.assertGreaterEqual(Seq(1, 9), Seq(1, 9))

        self.assertGreater(Seq(0, 1), Seq(-1, 2))

    def test_getitem(self):
        self.assertEqual(Seq(1, 2, 3, 4, 5, 6, 7)[3], 4)
        self.assertEqual(Seq(1, 2, 3, 4, 5, 6, 7, 8)[1:-2:2], Seq(2, 4, 6))

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



class SigTestCase(unittest.TestCase):
    pass


class MatrixTestCase(unittest.TestCase):
    pass


class PrismTestCase(unittest.TestCase):
    pass



if __name__ == "__main__":
    unittest.main()
