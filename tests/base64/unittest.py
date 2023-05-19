import unittest
from cxr import Td


class TdTestCase(unittest.TestCase):
    def test_eq(self):
        a, b = Td([1, 1], [3, 1, 0, 2], 5), Td([1, 0], [0, 2, 2], 5)
        self.assertEqual(a, a)
        self.assertLess(b, a)
        self.assertGreater(a, b)

    def test_arithmetic(self):
        a, b = Td([1, 1], [3, 1, 0, 2], 7), Td([1, 0], [0, 2, 2], 7)

        self.assertEqual(a + b, Td([2, 1], [3, 3, 2, 2], 7))
        self.assertEqual(b - a, Td([1], [2, 5, 5, 2], 7, is_negative=True))

        self.assertEqual(a * b, Td([1, 1, 3], [3, 5, 4, 1, 2, 4, 4], 7))
        self.assertEqual(a / b, Td(1, [1, 2, 5, 2, 0, 4, 6, 1, 2, 5, 5, 5, 3, 4, 5, 2, 3, 6], 7))
        self.assertEqual(b / a, Td(0, [5, 5, 6, 0, 2, 0, 2, 3, 2, 2, 0, 6, 3, 0, 1, 0, 3, 5], 7))

    def test_constants(self):
        pi = Td.pi(15, perfect=True)
        self.assertEqual(pi, Td(3, [2, 1, 12, 13, 1, 13, 12, 4, 6, 12, 2, 11, 7, 14, 5, 0, 8, 4], 15))

        e = Td.exp(3, perfect=True)
        self.assertEqual(e, Td(2, [2, 0, 1, 1, 0, 1, 1, 2, 1, 2, 2, 1, 1, 0, 2, 0, 0, 2], 3))

        e2 = Td.exp(23, 2, perfect=True)
        self.assertEqual(e2, Td(7, [8, 21, 18, 14, 19, 11, 10, 21, 19, 8, 2, 15, 10, 5, 6, 17, 17, 17], 23))

    def test_log(self):
        a = Td(7, [0, 1, 2, 3], 5)

        self.assertEqual(a.ln(perfect=True), Td(1, [4, 3, 4, 1, 2, 4, 4, 4, 1, 3, 4, 4, 2, 2, 1, 4, 0, 4], 5))

        self.assertEqual(a.logarithm(2, log=False, perfect=True), Td(2, [4, 0, 2, 2, 1, 4, 4, 1, 3, 3, 2, 2, 0, 0, 2, 1, 1, 1], 5))


    def test_utils(self):
        s = Td.encode("Hello, world!", 16, 2)
        self.assertEqual(Td.decode(s, 16, 2), "Hello, world!")


if __name__ == "__main__":
    unittest.main()
