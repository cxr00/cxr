from cxr.data import bst
from cxr.base36 import Tridozenal as Td
import cxr.base36
from cxr.snr import Seq, Sig, std_l

import random


class TdSeq:
    """
    Supplementary class for generating sequences with Tridozenal elements
    """

    @staticmethod
    def random():
        return Seq([Td(random.randint(1, cxr.base36.default_base), 0, cxr.base36.default_base) for _ in range(random.randint(1, 4))])

    @staticmethod
    def convert(s, b=cxr.base36.default_base):
        return Seq([Td(k, 0, b) for k in s])


class SigNode(bst.Node):
    """
    A bst.Node whose data is the signature function of its key
    """

    def __init__(self, key=None, data=None, left=None, right=None, parent=None, is_inverted=False):
        if key:
            if not isinstance(key, (Seq, Sig)):
                raise TypeError(f"Key must be Seq or Sig, not {type(key).__name__}")
            else:
                super().__init__(key, data if data else key.f(std_l), left, right, parent, is_inverted)
        else:
            super().__init__(None, None, left, right, parent, is_inverted)

    def __str__(self):
        return " - ".join([str(self.key), str(self.data)])

    def isolate(self):
        """
        It is necessary to override this function because otherwise
        super().isolate returns a bst.Node instead of a SigNode
        """
        return SigNode(self.key, self.data)

    @staticmethod
    def from_sequence(s: Seq):
        return SigNode(s.i(), s)


def signode_test():
    lst = [TdSeq.random() for _ in range(10)]

    root = SigNode()

    for td in lst:
        try:
            root += SigNode(td)
        except KeyError as exc:
            print("Failed to add SigNode:", exc)
            print()

    try:
        root += SigNode(1)
    except TypeError as exc:
        print("Failed to add SigNode:", exc)
        print()

    root = root.balance()
    for node in root:
        print(node)
    print()


def td_fibonacci_numbers_test():
    for b in range(2, cxr.base36.default_base + 1):

        s = TdSeq.convert([1, 1], b).f()

        print("base", b)
        print(s)
        print(SigNode.from_sequence(s))
        print()


def seed_test():
    s = TdSeq.convert([1, 1])
    s = s.f(seed=TdSeq.convert([2, 1]))

    print(s)
    print()


def truediv_test():
    s0 = TdSeq.convert([1, 1]).f(length=15)
    s1 = TdSeq.convert([1]).f(length=15)

    print(s0 / s1)

    # Very slow...probably runs in like n^4 time!
    print(s0.sig() // s1.sig())
    print()

    print(TdSeq.convert([1, 1]).f(length=15).sig() // TdSeq.convert([2, 1]).f(length=15).sig())
    print()


def mismatch_test():
    try:
        s0 = Seq([Td.one(), Td.one(11)])
    except ValueError as exc:
        print(exc)

    try:
        s0 = Seq([1.1, Td.one()])
    except TypeError as exc:
        print(exc)

    try:
        s0 = Seq([1, Td.zero()])
    except TypeError as exc:
        print(exc)

    try:
        s0 = Seq([1, 1.0, 1])
        print(s0)
    except TypeError as exc:
        print(exc)

    print()


def global_base_test():
    td0 = Td.one()

    print(td0.base)

    cxr.base36.default_base = 10
    td0 = Td.one()

    print(td0.base)
    print()


def main():
    signode_test()
    td_fibonacci_numbers_test()
    seed_test()
    truediv_test()
    mismatch_test()
    global_base_test()


if __name__ == "__main__":
    main()
