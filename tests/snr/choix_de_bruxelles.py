from cxr.snr import Seq
from cxr.base36 import Tridozenal as Td
import cxr.base36
import os


def choix_de_bruxelles_base_10(d, length, log=False):
    """
    The Brussels Choice in base 10

    Because this computer is fluent in base 10 it's quite a bit faster
    """
    if isinstance(length, int):
        length = [length]
    if not isinstance(d, list):
        d = [d]
    output = [number for number in d]
    len_d = len(d)

    for index, number in enumerate(d):
        if log:
            if index and index % 10 == 0:
                print(f"{index}/{len_d} done")
        s_d = str(number)
        for l in length:
            if len(s_d) < l:
                continue
            for i in range(len(s_d) - l + 1):
                substring = s_d[i:i + l]
                if substring[0] != "0":
                    if int(substring) % 2 == 0:
                        quotient = int(substring) // 2
                        to_add = s_d[:i] + str(quotient) + s_d[i + l:]
                        if to_add not in output:
                            output.append(to_add)
                    to_add = s_d[:i] + str(int(substring) * 2) + s_d[i + l:]
                    if to_add not in output:
                        output.append(to_add)

    return output


def choix_de_bruxelles(d, length, log=False):
    """
    The Brussels Choice in arbitrary base
    Set cxr.base36.default_base to set the base this is executed in
    """
    if not isinstance(d, list):
        d = [d]
    output = [number for number in d]
    len_d = len(d)
    two = Td(2)
    two_inverse = two.multiplicative_inverse(place=30)

    for index, number in enumerate(d):
        if log:
            if index:
                print(f"{index}/{len_d} done")
        s_d = str(number)
        for l in range(1, length):
            if len(s_d) < l:
                break
            for i in range(len(s_d) - l + 1):
                substring = s_d[i:i + l]
                if substring[0] != "0":
                    i_ss = Td.get_from_string(substring)
                    if (i_ss.base % 2 == 1 and sum(i_ss.integer) % 2 == 0) or (i_ss.base % 2 == 0 and i_ss.integer[0] % 2 == 0):
                        quotient = i_ss * two_inverse
                        quotient.round(place=20)
                        if len(quotient.mantissa) != 0:
                            raise ValueError("Quotient mantissa is not empty")
                        to_add = s_d[:i] + str(quotient) + s_d[i+l:]
                        td = Td.get_from_string(to_add)
                        if td not in output:
                            output.append(td)
                    to_add = s_d[:i] + str(i_ss * two) + s_d[i+l:]
                    td = Td.get_from_string(to_add)
                    if td not in output:
                        output.append(td)

    return output


def analyze_cdb(base):
    """
    Collect lengths of each set for the given base,
    and compiles it into a Seq
    """

    analysis = []
    if not os.path.exists("cdb"):
        os.mkdir(f"cdb")
    if not os.path.exists(f"cdb/cdb{base}"):
        os.mkdir(f"cdb/cdb{base}")
    files = os.listdir(f"cdb/cdb{base}")
    for file in range(len(files)):
        with open(f"cdb/cdb{base}/{file}.txt", "r") as f:
            lines = f.readlines()
            analysis.append(len(lines))

    return Seq(analysis)


def compute_next_cdb_in_base(base):
    """
    Perform the next step of Choix do Bruxelles for the given base.

    Saves the results in the appropriate directory
    """

    if not os.path.exists(f"cdb"):
        os.mkdir("cdb")

    cxr.base36.default_base = base

    if not os.path.exists(f"cdb/cdb{base}"):
        os.mkdir(f"cdb/cdb{base}")

    def open_step(step):
        output = []
        with open(f"cdb/cdb{base}/{step}.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                output.append(Td.get_from_string(line.strip()))
        return output

    files = os.listdir(f"cdb/cdb{base}")
    current_step = len(files)

    # Set initial step if necessary
    if current_step == 0:
        with open(f"cdb/cdb{base}/0.txt", "w+") as f:
            f.write("1\n")
        current_step += 1

    # Get previous steps
    g = open_step(current_step - 1)
    s = open_step(current_step - 2) if current_step > 1 else []

    # Get difference, which is the set on which CDBN will be performed
    s = set(s)
    g = set(g).difference(s)
    print(len(g))
    g = list(sorted(g))

    for each in g:
        print(each, end=", ")
    print()

    # Perform CDBN
    l = max([len(k.integer) for k in g]) + 1
    g = choix_de_bruxelles(g, l, log=True)

    # Recombine with previous step to get full set
    g = set(g).union(s)
    g = list(sorted(g))

    print(f"Length of step {current_step} in base {base} is {len(g)}.")

    with open(f"cdb/cdb{base}/{current_step}.txt", "w+") as f:
        for each in g:
            f.write(str(each) + "\n")

    print(f"Step {current_step} of base {base} saved.")


def main():
    """
    Selects opportunities to compute CDBN based on the given threshold.

    At the end, prints all potential OEIS sequences
    """

    # This is the largest set size that CDBN will attempt to operate on
    threshold = 1300

    # Iterate over all bases
    for base in range(1, 37):
        # Bases of the form 2**n are trivial
        if base in [2 ** n for n in range(6)]:
            pass
        else:
            analysis = analyze_cdb(base)

            while analysis[len(analysis) - 1] - analysis[len(analysis) - 2] < threshold:
                compute_next_cdb_in_base(base)
                analysis = analyze_cdb(base)
    print()

    # Displays the sequences associated with each base
    for base in range(1, 37):
        if base in [2 ** n for n in range(6)]:
            pass
        else:
            print(f"base {base}: {analyze_cdb(base)}")
    print()


if __name__ == "__main__":
    main()
