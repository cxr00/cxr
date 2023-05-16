from cxr.math.snr import Seq
from cxr.math.base64 import Tridozenal as Td
import cxr.math.base64

import os
import threading

"""
This module explores the Choix de Bruxelles algorithm in bases between
2 and 36. You can learn about this algorithm here: https://www.youtube.com/watch?v=AeqK96UX3rA

When run, this script will compute CDB and output
each result to its appropriate location. At the end of computation, the main script
will display variants of http://oeis.org/A323289 for each base.

Note that due to the nature of the operation (doubling/halving) any base which is
a power of two will trivially yield the positive integers (http://oeis.org/A000027).
Should CDB be extended to tripling/tralving, the powers of three would be trivial.
Same goes for four-timesing, etc.
"""

output_dir = "cdb"  # output files are of the form {output_dir}\\cdb{base}\\{step}.txt


def choix_de_bruxelles(d, length, log=False):
    """
    The Brussels Choice in arbitrary base
    Set cxr.base64.default_base to set the base this is executed in
    """

    def do_one_number(substring):
        if substring[0] != "0":
            i_ss = Td.get_from_string(substring)
            if i_ss % 2 == Td.zero():  # Silly that I didn't use this functionality in the first place
                quotient = i_ss * two_inverse
                quotient.round(place=0)  # Actually-correct rounding
                quotient = quotient.integer_part()
                to_add = s_d[:i] + str(quotient) + s_d[i + substring_length:]
                td = Td.get_from_string(to_add)
                if td not in output:
                    output.add(td)

            # Can always double selected substring
            to_add = s_d[:i] + str(i_ss * two) + s_d[i + substring_length:]
            td = Td.get_from_string(to_add)
            if td not in output:
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
                if len(current_threads) <= 7:
                    current_threads.append(t)
                    t.start()
                else:
                    current_threads = [t for t in current_threads if t.is_alive()]
                    current_threads.append(t)
                    t.start()
    for thread in current_threads:
        thread.join()

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

    cxr.math.base64.default_base = base

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

    # Perform CDBN
    max_length = max([len(k.integer) for k in g]) + 1
    g = choix_de_bruxelles(g, max_length, log=True)

    # Recombine with previous step to get full output set
    g = set(g).union(s)
    g = list(sorted(g))

    os.makedirs(f"{output_dir}\\cdb{base}", exist_ok=True)
    with open(f"{output_dir}\\cdb{base}\\{current_step}.txt", "w+") as f:
        for each in g:
            f.write(str(each) + "\n")

    print(f"Step {current_step} of base {base} saved.")

    return True


def main():
    """
    Selects opportunities to compute CDB based on the given threshold.

    At the end, prints all potential OEIS sequences

    You can modify the_range to tackle a particular base or set of bases.
    For example, the_range = [7] will only compute base 7,
    while the_range = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31] computes all viable prime bases
    """

    the_range = range(3, 4)
    trivial = [2 ** n for n in range(6)]

    compute = True  # False means show results, True means compute then show results
    inp = "continue"
    while inp.lower() == "continue":
        print(f"Beginning CDB analysis of {the_range}...")
        sequences = {}

        # Iterate over all bases
        for base in the_range:
            # Bases of the form 2**n are trivial, so are skipped
            if base not in trivial:
                compute_next_cdb_in_base(base)
                sequences[base] = analyze_cdb(base)
        print()

        # Displays the sequences associated with each base
        for base in the_range:
            if base not in trivial:
                print(f"{base}: Seq({sequences[base]}),")  # Easy to copy & paste for scratch work
        print()

        with open(f"{output_dir}\\sequences.txt", "w+") as f:
            for k, v in sequences.items():
                f.write(f"{k}:{str(v)}\n")
        print("sequences.txt updated.")
        inp = "continue"


if __name__ == "__main__":
    main()
