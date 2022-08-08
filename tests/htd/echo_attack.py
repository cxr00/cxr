from cxr.htd import Htd
from tests.htd.character_attack import minimum_implicit_base, minimum_hyperbase

from cxr.htd import default_encryption_sep

import random
import math


def minimum_bases(s, start, step=2):
    """
    Determine the minimum hyperbase and implicit base of a slice of Htds.

    This is used to search for a pattern in every n-th Htd of s

    :param s: the list of Htds to be decrypted
    :param start: the starting index of s
    :param step: slice parameter
    :return: The minimum hyperbase and implicit base of the slice
    """
    min_h = 2
    min_b = 2

    for each in s[start::step]:
        b = minimum_implicit_base(each)
        h = minimum_hyperbase(each, b)

        if b > min_b:
            min_b = b
        if h > min_h:
            min_h = h

    return min_h, min_b


def get_echoes(s, step=2):
    """
    Generate possible decryptions of the slices of s

    These are partial decryptions that attempt to exploit the
    modular nature of the encryption algorithm by predicting the
    cycle length of the keys


    :param s: The Htd ciphertext
    :param step: slice parameter
    :return: a list of slice decryptions
    """

    s = s.split(default_encryption_sep)

    echoes = []

    for start in range(step):
        min_h, min_b = minimum_bases(s, start, step)

        for b in range(min_b, 10):
            for h in range(min_h, 15):
                g = ""
                for i, each in enumerate(s):
                    if i % step == start:
                        g += Htd.decode(each, h, b)
                    else:
                        g += "_"
                echoes.append(g)

    return echoes


def double_encrypt():
    """
    Showcases double encryption using the same keys

    There is also an effort to gather information
    to employ an echo attack
    """

    sep_a = ";"

    b = [4, 3, 2, 3]
    h = [random.randint(5, 10) for _ in range(random.randint(2, 10))]

    s = "Hello world"

    s = Htd.encrypt(s, h, b, sep=sep_a)

    print(s)
    print(len(s))
    print()

    s = Htd.encrypt(s, h, b)

    print(s)
    print(len(s))
    print()

    # Find the most common Htd
    s_split = s.split(default_encryption_sep)
    count = {}
    for each in s_split:
        if each in count:
            count[each] += 1
        else:
            count[each] = 1

    sorted_count = sorted(count.items(), key=lambda x: x[1])

    for key, value in sorted_count:
        print(key, value)
    print()

    # How many words in the double encryption?
    print(sum(count.values()))
    print()

    # Get indices of the most common Htd
    indices = []
    for i, each in enumerate(s_split):
        if each == sorted_count[-1][0]:
            indices.append(s_split[i:].index(each) + i)
            print(indices[-1])
    print()

    # Find minimal cycle
    gcd = 0
    for i in range(1, len(indices)):
        # Specifically ignore one-cycles just in case
        if indices[i] - indices[i-1] > 1:
            gcd = math.gcd(gcd, indices[i] - indices[i - 1])
    print("gcd:", gcd)
    print("key lengths:", len(b), len(h))
    print("length determined:", gcd == len(h) or gcd == len(b))

    print(Htd.decrypt(Htd.decrypt(s, h, b), h, b, sep=sep_a))
    print()


def main():
    s = "The quick brown fox jumped over the lazy dog"

    # s_enc = Htd.encode(s, 7, 3)
    # for each in get_echoes(s_enc, step=3):
    #     print(each)
    # print()

    double_encrypt()


if __name__ == "__main__":
    main()
