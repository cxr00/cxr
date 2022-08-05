from cxr.base36 import Tridozenal as Td
from cxr.data import bst


def node_with_td():
    td0 = Td(101, 0)
    td1 = Td(143, 0)
    td2 = Td(144, 0)
    td3 = Td(1728, 0)

    root = bst.Node()
    root += td0
    root += td1
    root += td2
    root += td3

    print(root)
    print(root.height())
    print()

    try:
        root += td0
    except KeyError:
        print("Failed to add duplicate Td to Node")

    print()

    print(root[td0].successor().key)
    print(root[td1].predecessor().key)

    print(root[td2].successor().key)
    print(root[td3].predecessor().key)

    print(root[td0].predecessor())
    print(root[td3].successor())

    print()

    for each in root:
        print(each.key, "-", each.data, end=", ")
    print()

    root.invert()

    for each in root:
        print(each.key, "-", each.data, end=", ")
    print("\n")

    root.invert()

    print(root.search(Td(0, 0)))
    print()

    root = root.balance()
    root.invert()

    print(root)
    print(root.search(td1).key)
    print(root)
    print()

    root.delete(td1)

    print(root)
    print(root.search(td1))
    print()

    root.invert()
    print(root)
    print()


if __name__ == "__main__":
    node_with_td()
