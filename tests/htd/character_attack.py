from cxr.base36 import Tridozenal as Td
from cxr.htd import Htd, default_sep, default_encryption_sep

import time
import random

"""
This module demonstrates a basic attack against Htd encryption.

First, we determine the minimum valid implicit base and hyperbase for the Htd string

Second, we iterate over the bases and decrypt the string into
all possible (alphanumeric) characters

We repeat this process for each Htd in the encrypted string.

After this process is performed, we have a list of character sets, which
represents the set of all possible decryptions.
"""


def minimum_implicit_base(s):
    """
    Deduce the minimum base which the Htd's digits must have

    :param s: The string representation of the Htd
    :return: the minimum valid implicit base for the Htd
    """
    b = 2
    for e in s:
        if e.isnumeric():
            if int(e) >= b:
                b = int(e) + 1
        elif e.isalpha():
            if ord(e.upper()) - 55 >= b:
                b = ord(e.upper()) - 54
    return b


def minimum_hyperbase(s, implicit_base):
    """
    Deduce the minimum hyperbase given an implicit base
    :param s: the string representation of the Htd
    :param implicit_base: the presumed implicit base of the Htd
    :return: the minimum valid hyperbase for the Htd
    """
    h = implicit_base

    for e in s.split(default_sep):
        td = Td.get_from_string(e, implicit_base)
        if td.primitive() >= h:
            h = td.primitive()

    return h


def get_potential_characters(s):
    """
    Determine the possible alphanumeric characters into which an Htd can be decrypted

    :param s: the string representation of the Htd
    :return: a list of possible characters the Htd could represent
    """

    output = []

    min_b = minimum_implicit_base(s)

    for b in range(min_b, 37):
        min_h = minimum_hyperbase(s, b)
        for h in range(min_h, 100):
            try:
                new_char = Htd.decrypt(s, [h], [b])
                if ord(new_char) >= 128:
                    break
                if (new_char not in output) and (new_char.isalpha() or new_char.isnumeric() or new_char == " "):
                    output.append(new_char)
            except ValueError as exc:
                print("limit reached:", exc)
                break

    return output


def randomly_encrypt_and_analyze_hello_world():
    # randomize the hyperbase password
    h = [random.randint(3, 50) for _ in range(random.randint(5, 11))]

    # randomize the implicit base password
    b = []
    for e in range(random.randint(5, len(h))):
        b.append(random.randint(2, min(h[e] - 1, 36)))

    s = Htd.encrypt("Hello world", h, b)

    print(s)

    pot = []
    for each in s.split(default_encryption_sep):
        print("Analyzing", each)
        pot.append(get_potential_characters(each))

    for each in pot:
        print(each)

    possibilities = 1
    for each in pot:
        if len(each):
            possibilities *= len(each)

    print("Possible decryptions:", possibilities)


def main():
    t_start = time.time()
    randomly_encrypt_and_analyze_hello_world()
    t_end = time.time()
    print("execution time:", t_end - t_start)


if __name__ == "__main__":
    main()
