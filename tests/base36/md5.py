"""
The purpose of this module is not to provide a usable substitution to hashlib's MD5, but to showcase
the increased cost and difficulty which comes from trying to use traditional numbers in place
of bit arrays in a "pure python" implementation. Weaknesses are noted in each step where they appear.
"""
from cxr import Td
import hashlib  # To compare the result at the end, and also so you can laugh at how fast it is
import time


def pad(num, to_64=False, to_32=False):
    """
    Pad the number to either 8, 32, or 64 bits
    """
    s = str(num)
    return "0" * ((64 if to_64 else 32 if to_32 else 8) - len(s)) + s


sine_constants = [
    Td.get_from_string("11010111011010101010010001111000", base=2), Td.get_from_string("11101000110001111011011101010110", base=2),
    Td.get_from_string("100100001000000111000011011011", base=2), Td.get_from_string("11000001101111011100111011101110", base=2),
    Td.get_from_string("11110101011111000000111110101111", base=2), Td.get_from_string("1000111100001111100011000101010", base=2),
    Td.get_from_string("10101000001100000100011000010011", base=2), Td.get_from_string("11111101010001101001010100000001", base=2),
    Td.get_from_string("1101001100000001001100011011000", base=2), Td.get_from_string("10001011010001001111011110101111", base=2),
    Td.get_from_string("11111111111111110101101110110001", base=2), Td.get_from_string("10001001010111001101011110111110", base=2),
    Td.get_from_string("1101011100100000001000100100010", base=2), Td.get_from_string("11111101100110000111000110010011", base=2),
    Td.get_from_string("10100110011110010100001110001110", base=2), Td.get_from_string("1001001101101000000100000100001", base=2),
    Td.get_from_string("11110110000111100010010101100010", base=2), Td.get_from_string("11000000010000001011001101000000", base=2),
    Td.get_from_string("100110010111100101101001010001", base=2), Td.get_from_string("11101001101101101100011110101010", base=2),
    Td.get_from_string("11010110001011110001000001011101", base=2), Td.get_from_string("10010001000001010001010011", base=2),
    Td.get_from_string("11011000101000011110011010000001", base=2), Td.get_from_string("11100111110100111111101111001000", base=2),
    Td.get_from_string("100001111000011100110111100110", base=2), Td.get_from_string("11000011001101110000011111010110", base=2),
    Td.get_from_string("11110100110101010000110110000111", base=2), Td.get_from_string("1000101010110100001010011101101", base=2),
    Td.get_from_string("10101001111000111110100100000101", base=2), Td.get_from_string("11111100111011111010001111111000", base=2),
    Td.get_from_string("1100111011011110000001011011001", base=2), Td.get_from_string("10001101001010100100110010001010", base=2),
    Td.get_from_string("11111111111110100011100101000010", base=2), Td.get_from_string("10000111011100011111011010000001", base=2),
    Td.get_from_string("1101101100111010110000100100010", base=2), Td.get_from_string("11111101111001010011100000001100", base=2),
    Td.get_from_string("10100100101111101110101001000100", base=2), Td.get_from_string("1001011110111101100111110101001", base=2),
    Td.get_from_string("11110110101110110100101101100000", base=2), Td.get_from_string("10111110101111111011110001110000", base=2),
    Td.get_from_string("101000100110110111111011000110", base=2), Td.get_from_string("11101010101000010010011111111010", base=2),
    Td.get_from_string("11010100111011110011000010000101", base=2), Td.get_from_string("100100010000001110100000101", base=2),
    Td.get_from_string("11011001110101001101000000111001", base=2), Td.get_from_string("11100110110110111001100111100101", base=2),
    Td.get_from_string("11111101000100111110011111000", base=2), Td.get_from_string("11000100101011000101011001100101", base=2),
    Td.get_from_string("11110100001010010010001001000100", base=2), Td.get_from_string("1000011001010101111111110010111", base=2),
    Td.get_from_string("10101011100101000010001110100111", base=2), Td.get_from_string("11111100100100111010000000111001", base=2),
    Td.get_from_string("1100101010110110101100111000011", base=2), Td.get_from_string("10001111000011001100110010010010", base=2),
    Td.get_from_string("11111111111011111111010001111101", base=2), Td.get_from_string("10000101100001000101110111010001", base=2),
    Td.get_from_string("1101111101010000111111001001111", base=2), Td.get_from_string("11111110001011001110011011100000", base=2),
    Td.get_from_string("10100011000000010100001100010100", base=2), Td.get_from_string("1001110000010000001000110100001", base=2),
    Td.get_from_string("11110111010100110111111010000010", base=2), Td.get_from_string("10111101001110101111001000110101", base=2),
    Td.get_from_string("101010110101111101001010111011", base=2), Td.get_from_string("11101011100001101101001110010001", base=2),
]

t32 = Td(2 ** 32, base=2)


def rot_left(num, s):
    num = num % t32
    bits = list(map(int, pad(num, to_32=True)))[::-1]
    bits = bits[-s:] + bits[:-s]
    return Td(bits[::-1], base=2)


def non_linear_process(f):
    """
    A decorator for constructing each step of the infamous non-linear process
    """
    def func(x, y, z):
        a = f(x, y, z)
        a = Td.get_from_string(pad(a, to_32=True)[::-1], base=2)
        return a
    return func


# WEAKNESS: NOT arg must be substituted by (1 - arg); it is also more verbose due to accessing the integer sequence
R1 = non_linear_process(lambda x, y, z: Td([(x[i] & y[i]) | ((1-x[i]) & z[i]) for i in range(32)], base=2))
R2 = non_linear_process(lambda x, y, z: Td([(x[i] & z[i]) | (y[i] & (1-z[i])) for i in range(32)], base=2))
R3 = non_linear_process(lambda x, y, z: Td([x[i] ^ y[i] ^ z[i] for i in range(32)], base=2))
R4 = non_linear_process(lambda x, y, z: Td([y[i] ^ (x[i] | (1-z[i])) for i in range(32)], base=2))


def buffer_process(f):
    """
    A decorator for construction of complete process for each buffer
    """
    def RRN(a, b, c, d, sb, sc, s):
        a = a + f(b, c, d) + sb + sc
        a = rot_left(a, s) + b
        return a % t32
    return RRN


RR1 = buffer_process(R1)
RR2 = buffer_process(R2)
RR3 = buffer_process(R3)
RR4 = buffer_process(R4)

mod_add = lambda a, b: (a + b) % t32


def md5sum(input_string):
    t = time.time()

    """
    STEP 1 - pre-process and pad the message
    """
    message = "".join([pad(Td(ord(i), base=2)) for i in input_string])
    original_length = Td(len(message), base=2)  # Important: Computed BEFORE any padding!
    message += "1"
    to_add = (448 - len(message) % 512) if len(message) % 512 <= 448 else (960 - len(message) % 512)
    message += "0" * to_add

    """
    STEP 2 - add final padding of message length
    WEAKNESS: length padding bytes must be reversed
    """
    original_length = pad(original_length % (t32**2), to_64=True)  # I'm jealous of you if you have the time for a 64-bit length string
    original_length = [original_length[j * 8:(j + 1) * 8] for j in range(8)]
    original_length = "".join(original_length[::-1])
    message += original_length

    """
    STEP 3 - initialise buffers
    """
    A = Td.get_from_string("1100111010001010010001100000001", base=2)
    B = Td.get_from_string("11101111110011011010101110001001", base=2)
    C = Td.get_from_string("10011000101110101101110011111110", base=2)
    D = Td.get_from_string("10000001100100101010001110110", base=2)

    """
    STEP 4
    WEAKNESS: sub-block construction requires byte reversal
    """
    num_chunks = len(message) // 512
    for current_chunk in range(num_chunks):
        AA = A
        BB = B
        CC = C
        DD = D

        subblock = []
        for i in range(16):
            grab = message[current_chunk * 512 + i * 32:current_chunk * 512 + (i + 1) * 32]
            grab = [grab[j*8:(j+1)*8] for j in range(4)]
            subblock.append(Td.get_from_string("".join(grab[::-1]), base=2))

        # Inner loop structure from https://github.com/timvandermeij/md5.py. So clean!
        for i in range(64):
            if 0 <= i <= 15:
                k = i
                s = [7, 12, 17, 22]
                f = RR1
            elif 16 <= i <= 31:
                k = ((5 * i) + 1) % 16
                s = [5, 9, 14, 20]
                f = RR2
            elif 32 <= i <= 47:
                k = ((3 * i) + 5) % 16
                s = [4, 11, 16, 23]
                f = RR3
            elif 48 <= i <= 63:
                k = (7 * i) % 16
                s = [6, 10, 15, 21]
                f = RR4

            # noinspection PyUnboundLocalVariable
            temp = f(A, B, C, D, subblock[k], sine_constants[i], s[i % 4])
            A = D
            D = C
            C = B
            B = temp

        A = mod_add(A, AA)
        B = mod_add(B, BB)
        C = mod_add(C, CC)
        D = mod_add(D, DD)

    """
    STEP 5 - output md5sum
    WEAKNESS: Bytes must be converted back to hex as well as reversed again
    """
    output = []
    for e in [A, B, C, D]:
        e = pad(str(e.convert(16)))
        e = [e[j*2:(j+1)*2] for j in range(4)]
        output.append("".join(e[::-1]))
    output = "".join(output)
    t = round(time.time() - t, 3)
    t2 = time.time()
    trad = Td.get_from_string(hashlib.md5(input_string.encode()).hexdigest().upper(), base=16)
    t2 = round(time.time() - t2, 3)
    print(f"Computed md5sum in {t} seconds. (hashlib takes {t2} seconds)")
    print("cxr impl:", output.lower())
    print("hashlib: ", str(trad).lower())


if __name__ == "__main__":
    md5sum("Hello world! lkahsdfhas dfhakjsdhfjasjdflkasdf tyvm...")
