
# This module enables the construction and manipulation of numbers in bases 2 through 36
# The only methods we will be using are rebase and convert
from cxr.base36 import Tridozenal as Td

import datetime
import time
import os

"""
This module explores the rebase-convert iteration function R(c, r, k)

c is the base of the starting value c ** k. It is also the base which the current value is converted to after every rebase.
Unlike rebasing, converting preserves the quantity represented by the original base interpretation.
For example, 100 in base 10 converts to 202 in base 7. Same quantity, different representations.

r is the rebasing base. To rebase a number means to treat the digits of the number as if they are in base r.
When this is done, the quantity the number represents fundamentally changes.
100 in base 10 means 100, but if we rebase it to 7 then its digits are still 100, but its equivalent base 10 value is 49.
When c > r, N > R(N, r) 

The algorithm takes the starting value and rebases it to base r. It then converts the result back to base c.
The process is repeated until the value is less than c ** (k-1) - 1, meaning it is a base c number with k-1 or fewer digits, and
that value is the result of the function.

While originally testing the iteration, I would use a starting value of c ** 2 and would iterate until reaching c-1 or less,
but decided to add a parameter k to replace 2. Then I started selecting a particular k, then looping through every c from 3 to 36, and every r from 2 to c-1.
I noticed that, as c increased, the results of this nested loop started to look like 2**k, 3**k, 4**k, and so on.
I also noticed that the first time this would happen for a particular value of r, it would always be with converting base r+1.
So I wondered: For any c with r=c-d for some value of d, what is the minimum value of k where R(c, r, k) = r ** k ?

The convergence point for a given c, or C(c, d, n) is precisely that. It is computed by compute_convergence_sequence(d, n).
Due to the limitations of cxr.base36, we can only analyze up to c = 36. Once d reaches 4, the sequence increases by 1 each time. 

count_steps can be used to track the total number of times a number is (rebased then converted) before it reaches the target value.
Fun fact: when k=2, the number of steps of R(c, c-2, k) is always c-2, and the steps of R(c, c-1, k) is always c-1. No idea why, though.
"""


def rebase_and_convert(c: int, r: int, k: int, count_steps=False):
    """
    Perform the rebase-convert-repeat algorithm

    :param c: base to convert to after rebase
    :param r: base to rebase to
    :param k: determines the starting value and target value
    :param count_steps: Whether to return the number of steps the algorithm takes, rather than the final value
    :return: the final value after iteration, or the number of steps if count_steps is True
    """
    if c > 36 or c < 3:
        raise ValueError(f"Value of first parameter c must be between 3 and 36, not {c}")
    elif r >= c:
        raise ValueError(f"Value of second parameter r ({r}) must be less than c ({c})")
    elif k <= 1:
        raise ValueError(f"Value of third parameter k ({k}) must be greater than 1, not {k}")
    else:
        val = Td(c ** k, base=c)
        target = Td(c ** (k-1) - 1, base=c)
        steps = 0
        while val > target:
            val = val.rebase(r)
            val = val.convert(c)
            steps += 1
        return steps if count_steps else val.primitive()


def compute_convergence_sequence(d, n, save=False):
    """
    This function computes the next n elements of the convergence sequence.

    :param d: the difference between c and r
    :param n: the number of new elements of the convergence sequence to compute
    :param d: The difference between c and r used to calculate the convergence sequence
    :param filename: the name of the file to load and save to
    :param save: whether or not to even save in the first place
    """
    filename = f"local\\rebase_convert\\{d}.csv"

    # Create a save filename if one doesn't already exist
    if not os.path.exists(filename):
        convergence_sequence = [2 + d]
    else:
        print(f"Loading from {filename}")

        with open(filename, "r+") as f:
            line = f.readlines()[0]
            convergence_sequence = [int(v) for v in line.strip().split(",")]

    def display_convergence_sequence():
        print(f"Convergence sequence: {convergence_sequence}")
        print(f"Partial difference sequence: {[convergence_sequence[i] - convergence_sequence[i - 1] for i in range(1, len(convergence_sequence))]}")
        print()

    to_exit = False

    if 2 + d + len(convergence_sequence) > 36:
        print("Convergence sequence is already computed to the highest possible base supported by cxr.base36")
        to_exit = True

    display_convergence_sequence()

    if to_exit:
        return

    for i in range(n):
        # The conversion base which will yield the next element of the convergence sequence
        c = 2 + d + len(convergence_sequence)

        if c > 36:
            break

        # The rebasing base
        r = c-d

        # The starting value for k. It is increased by 1 at the beginning of each iteration of the while loop
        k = convergence_sequence[-1]

        search_time = 0.0
        FOUND = False

        print(f"Testing ({c}, {r}, k) with k starting at {k + 1}")
        while True:
            k += 1

            start_time = time.time()

            a = rebase_and_convert(c, r, k)

            r_pow = r ** k
            if a == r_pow:
                convergence_sequence.append(k)
                FOUND = True

            exec_time = round(time.time() - start_time, 3)

            print(f"k={k} completed in {exec_time} seconds at {datetime.datetime.now().strftime('%H:%M:%S')}.", end=" ")
            search_time += exec_time

            # When a new element is found, report the findings and break the loop
            if FOUND:
                print(f"\n\nSuccess! C({c}, {d}, {len(convergence_sequence)}) = {k}.")

                # Save the updated convergence_sequence if directed to
                if save:
                    with open(filename, "w+") as f:
                        f.write(",".join([str(i) for i in convergence_sequence]))
                    print(f"Updated convergence sequence saved to {filename}")
                print()
                break
            else:
                print(f"No new element of the convergence sequence was found for k={k}.")

        print(f"Completed program with a search time of {int(round(search_time // 60, 0))} minutes and {int(round(search_time % 60, 0))} seconds.")

        # Report the new convergence sequence
        print(f"convergence sequence: {convergence_sequence}")
        print("\n###################\n")


if __name__ == "__main__":
    compute_convergence_sequence(3, 30, save=True)
