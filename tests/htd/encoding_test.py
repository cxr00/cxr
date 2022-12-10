from cxr.math.base64 import Tridozenal as Td
from cxr.math.htd import Htd

from cxr.math import htd, base64

import random
import time


def random_data():
    base = 3

    d = [Td(random.randint(0, 255)) for _ in range(10)]
    for each in d:
        print(each, end=", ")
    print()

    d = [k.convert(base=base) for k in d]
    for each in d:
        print(each, end=", ")
    print()

    for each in d:
        print(chr(int(each)), end="")
    print()


def get_from_string_test():

    htd.round_to = 10
    htd.default_hyperbase = 7
    base64.default_base = 2

    s = "1,11,10"

    s = Htd.get_from_string(s, 4, base64.default_base)
    print(s)

    s = s.convert(htd.default_hyperbase) / Td(4, base=2)

    print(s)
    print()

    print(Htd.get_from_string(str(s)))

    print(int(s[-1]))

    print(int(s))


def encode_decode_test():
    base64.default_base = 22
    s = Td.encode("Just checking to make sure\nthat everything works")
    print(s)

    s = Td.decode(s)
    print(s)

    base64.default_base = 9
    htd.default_hyperbase = 25

    s = Htd.encode("Hello world")
    print(s)

    s = Htd.decode(s)
    print(s)
    print()


def htd_encryption_test():

    t_start = time.time()

    # s = [chr(random.randint(0, 255)) for _ in range(100)]
    # s = "".join(s)
    s = "The quick brown fox jumped over the lazy dog"

    print(s)
    print()

    # Generate the passwords
    hyperbases = [random.randint(3, 50) for _ in range(random.randint(5, 20))]
    implicit_bases = []
    for e in range(len(hyperbases)):
        implicit_bases.append(random.randint(2, min(hyperbases[e] - 1, 36)))

    print(hyperbases)
    print(implicit_bases)
    print()

    # Encrypt using the passwords
    s_enc = Htd.encrypt(s, hyperbases=hyperbases, implicit_bases=implicit_bases)
    print(s_enc)

    # Successfully decrypt using the passwords
    s_de = Htd.decrypt(s_enc, hyperbases=hyperbases, implicit_bases=implicit_bases)
    print(s_de)
    print("match:", s == s_de)
    print()

    # randomize the hyperbase password
    hyperbases = [random.randint(3, 50) for _ in range(len(hyperbases))]

    # randomize the implicit base password
    implicit_bases = []
    for e in range(len(hyperbases)):
        implicit_bases.append(random.randint(2, min(hyperbases[e] - 1, 36)))

    print(hyperbases)
    print(implicit_bases)

    # Fail to decrypt due to incorrect passwords
    try:
        s_de_fail = Htd.decrypt(s_enc, hyperbases=hyperbases, implicit_bases=implicit_bases)
        print(s_de_fail)
        print("match:", s_de_fail == s)
        print("len:", len(s_de_fail))
    except ValueError as exc:
        # This happens when the primitive value exceeds the character range
        print("Decryption failed:", exc)
    print()

    t_end = time.time()

    print("execution time:", t_end - t_start)
    print()


def htd_encode_test():
    s = "https://complexor.wordpress.com"
    h = 9
    b = 4

    s = Htd.encode(s, h, b)

    # Check for Benford's Law
    count = [0 for _ in range(b)]
    for e in s:
        if e.isnumeric():
            count[int(e)] += 1

    print(s)
    print(count)
    print("Benford's Law:", count.index(max(count)) == 1)

    s = Htd.decode(s, h, b)

    print(s)
    print()


def tests():
    random_data()
    # get_from_string_test()
    # encode_decode_test()
    htd_encryption_test()
    htd_encode_test()


if __name__ == "__main__":
    tests()

