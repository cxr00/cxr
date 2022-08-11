from cxr.math.snr import Seq
from cxr.math.base36 import Tridozenal as Td
import cxr.math.base36

import os
import threading

"""
This module explores the Choix de Bruxelles algorithm in bases between
2 and 36. You can learn about this algorithm here: https://www.youtube.com/watch?v=AeqK96UX3rA

When run, this script will compute CDB based on the given threshold, and output
each result to its appropriate location. At the end of computation, the main script
will display variants of http://oeis.org/A323289 for each base.

Note that due to the nature of the operation (doubling/halving) any base which is
a power of two will trivially yield the positive integers (http://oeis.org/A000027).
Should CDB be extended to tripling/tralving, the powers of three would be trivial.
Same goes for four-timesing, etc.
"""

output_dir = "cdb"  # output files are of the form {output_dir}\\cdb{base}\\{step}.txt

# This is the largest set size that CDBN will attempt to operate on
# It can be optionally modified at the beginning of the main function
threshold = 100


def choix_de_bruxelles(d, length, log=False):
    """
    The Brussels Choice in arbitrary base
    Set cxr.base36.default_base to set the base this is executed in
    """

    def do_one_number(substring):
        if substring[0] != "0":
            i_ss = Td.get_from_string(substring)
            # Conditions to halve selected substring
            if (
                    i_ss.base % 2 == 1 and sum(i_ss.integer) % 2 == 0  # Base is odd and digit sum is even
                ) \
                or \
                (
                        i_ss.base % 2 == 0 and i_ss.integer[0] % 2 == 0  # Base and first digit of integer are even
                ):
                quotient = i_ss * two_inverse
                quotient.round(place=cxr.base36.round_to - 7)
                quotient = quotient.integer_part()
                to_add = s_d[:i] + str(quotient) + s_d[i + substring_length:]
                td = Td.get_from_string(to_add)
                # if td not in output:
                output.add(td)
            # Can always double selected substring
            to_add = s_d[:i] + str(i_ss * two) + s_d[i + substring_length:]
            td = Td.get_from_string(to_add)
            # if td not in output:
            output.add(td)

    if not isinstance(d, list):
        d = [d]
    output = set(number for number in d)
    len_d = len(d)
    two = Td(2)
    two_inverse = two.multiplicative_inverse()

    current_threads = []

    for index, number in enumerate(d):  # Traversal of numbers loop
        if log:
            if index and index % 33 == 0:
                print(f"{index}/{len_d} done")
        s_d = str(number)
        for substring_length in range(1, length):  # Length-defining loop
            if len(s_d) < substring_length:
                break
            for i in range(len(s_d) - substring_length + 1):  # Substring-defining loop
                substring = s_d[i:i + substring_length]

                t = threading.Thread(target=do_one_number(substring), args=(substring,))
                current_threads.append(t)
                t.start()
                if len(current_threads) >= 4:
                    current_threads[0].join()

    return output


def analyze_cdb(base):
    """
    Collect lengths of each set for the given base,
    and compiles it into a Seq
    """

    analysis = []

    if not os.path.exists(f"{output_dir}\\cdb{base}"):
        os.makedirs(f"{output_dir}\\cdb{base}")

    files = os.listdir(f"{output_dir}\\cdb{base}")
    for file in range(len(files)):
        with open(f"{output_dir}\\cdb{base}\\{file}.txt", "r") as f:
            lines = f.readlines()
            analysis.append(len(lines))

    return Seq(analysis)


def compute_next_cdb_in_base(base):
    """
    Perform the next step of Choix de Bruxelles for the given base.

    Saves the results in the appropriate directory
    """

    cxr.math.base36.default_base = base

    os.makedirs(f"{output_dir}\\cdb{base}", exist_ok=True)

    def open_step(step):
        output = []
        with open(f"{output_dir}\\cdb{base}\\{step}.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                output.append(Td.get_from_string(line.strip()))
        return output

    files = os.listdir(f"{output_dir}\\cdb{base}")
    current_step = len(files)

    # Set initial step if necessary
    if current_step == 0:
        with open(f"{output_dir}\\cdb{base}\\0.txt", "w+") as f:
            f.write("1\n")
        current_step += 1

    # Get previous steps
    g = open_step(current_step - 1)
    s = open_step(current_step - 2) if current_step > 1 else []

    # Get difference, which is the set on which CDB will be performed
    s = set(s)
    g = set(g).difference(s)
    g = list(sorted(g))
    l_g = len(g)
    print(f"Difference yields set of size {l_g} for base {base}")

    if l_g <= threshold:
        # Perform CDBN if consistent with threshold
        max_length = max([len(k.integer) for k in g]) + 1
        g = choix_de_bruxelles(g, max_length, log=True)

        # Recombine with previous step to get full set
        g = set(g).union(s)
        g = list(sorted(g))

        os.makedirs(f"{output_dir}\\cdb{base}", exist_ok=True)
        with open(f"{output_dir}\\cdb{base}\\{current_step}.txt", "w+") as f:
            for each in g:
                f.write(str(each) + "\n")

        print(f"Step {current_step} of base {base} saved.")

        return True
    return False


def main():
    """
    Selects opportunities to compute CDB based on the given threshold.

    At the end, prints all potential OEIS sequences
    """
    global threshold

    the_range = range(10, 11)  # Alter this (to a list even) to change what bases are examined
    trivial = [2 ** n for n in range(6)]

    while True:
        sequences = {}

        # Iterate over all bases
        for base in the_range:
            # Bases of the form 2**n are trivial, so are skipped
            if base not in trivial:
                compute_next_cdb_in_base(base)
                sequences[base] = analyze_cdb(base)
        print()

        threshold = -1
        # Displays the sequences associated with each base
        for base in the_range:
            if base not in trivial:
                print(f"{base}: Seq({sequences[base]}),")  # Easy to copy & paste for scratch work
        print()

        with open(f"{output_dir}\\sequences.txt", "w+") as f:
            for k, v in sequences.items():
                f.write(f"{k}:{str(v)}\n")
        print("sequences.txt updated.")

        lst = sorted(list(sequences.values()), key=lambda x: x[-1])
        threshold = lst[len(lst) // 2][-1]  # Set new threshold in the middle of what's available
        print(f"New threshold of {threshold} assigned.")


if __name__ == "__main__":
    main()
