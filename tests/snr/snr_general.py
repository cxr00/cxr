from cxr.snr import Seq, x, Sig, Prism


import random


def random_seq():
    return Seq([random.randint(-7, 7) for _ in range(random.randint(2, 5))])


def dimensional_signature_convolution(d, g, dim):
    output = Seq(0)
    d_pow = Seq(1)
    x_pow = Seq(1)

    d_sig = d.sig().iter_add(dim - 2).seq

    for k in range(len(g)):
        output += d_pow * x_pow * g[k] * (1 - x * d_sig)
        d_pow *= d
        x_pow *= x

    output *= d

    output += d_sig

    return output


def dimensional_signature_convolution_test():

    d = random_seq()
    g = random_seq()
    l = 8
    print(d)
    print(g)
    print()

    for dim in range(1, 6):
        if dim == 1:
            print(f"dim {dim} unknown")
        # elif dim == 2:
        #     blk = Block.power(d, l)
        #     print(blk.i(g=g))
        else:
            structure = Prism.power(d, dim=dim, l=l)
            print(structure.f(g=[g]).i())
        print(dimensional_signature_convolution(d, g, dim)[:l - 1])
        print()


def sig_iter_sub():
    s = Sig(1, 1)
    o = Sig(0)
    for i in range(10):
        o -= s
        print(o)


def main():
    # sig_iter_sub()
    dimensional_signature_convolution_test()


if __name__ == "__main__":
    main()
