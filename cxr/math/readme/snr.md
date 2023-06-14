# cxr.snr

SNR is the Signature Near-Ring, a construction based on the INVERT transform. You can read an in-depth explanation of the signature function and SNR [here](https://complexor.files.wordpress.com/2023/06/recursive-signatures-and-the-signature-left-near-ring.pdf).

## Seq

The Seq class is the base class for mathematical manipulations of sequences.

Seq objects may be constructed easily with an arbitrary number of integer arguments, or with a list or tuple. If no argument is specified, the null sequence is created.`

```python
from cxr.math.snr import Seq

a = Seq()
a = Seq(1, 2, 1)
a = Seq(2, 3)
```

### Mathematical operations

The Seq class implements arithmetic builtins. 
Sequences may add, subtract, convolve, and deconvolve.

#### Addition

```python
a = Seq(1, 1)
b = Seq(1, 1, 1)

print(a + b)
```
```
2, 2, 1
```

#### Subtraction

```python
a = Seq(2, 4, 3)
b = Seq(1, 2, 2, 1)

print(a - b)
```
```
1, 2, 1, -1
```

#### Convolution

```python
a = Seq(1, 1)
b = Seq(1, 1, 1)

print(a * b)
```
```
1, 2, 2, 1
```

#### Deconvolution

```python
a = Seq(2, 4, 2)
b = Seq(1, 1)

print(a / b)
```
```
2, 2
```

#### The signature function

The recursive signature function (also known as the INVERT transform)
turns a sequence (or "signature") into a recursive sequence. For example, the signature
[1, 1] returns the Fibonacci numbers.

```python
a = Seq(1, 1)

print(a.f())
```

```
1, 1, 2, 3, 5, 8, 13, 21, ...
```

The default length of the signature function is 30. This length may be altered by changing
the variable `std_l` in snr.py or by calling the function with a length argument.

```python
a = Seq(2, 1)
std_l = 5

print(a.f())
print(a.f(7))
```
```
1, 2, 5, 12, 29
1, 2, 5, 12, 29, 70, 169
```

### The inverse signature function

If a sequence begins with 1, then the inverse signature function can be performed to convert
the sequence into its signature. If the sequence does not begin with 1, then a ValueError is raised.
```python
a = Seq(1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89)

print(a.i())
```
```
1, 1
```

### Polynomial representation

Seq objects may be converted to polynomial format. You can specify the variable name, whether the polynomial is actually a formal power series, and whether or not to use superscripts in the output.

```python
print(Seq(2, -1, 1, -1).polynomial("y"))  # 2y^3 - y^2 + y - 1

print(Seq(1, 1).f(l=9).polynomial("k", fps=True, use_ss=True))  # 1 + k + 2k² + 3k³ + 5k⁴ + 8k⁵ + 13k⁶ + 21k⁷ + 34k⁸
```

## Sig

The Sig class builds on the arithmetic of Seq to construct the Signature Left Near-Ring.
Sig objects may be constructed with a list, tuple, Seq, arbitrary number of integers/floats, or empty input.
```python
a = Seq(1, 1)

b = Sig()
b = Sig(3)
b = Sig(1, 2, 1)
b = Sig(a)
```

### Mathematical operations

Sig objects can perform signature addition and subtraction, and signature convolution and deconvolution.

#### Signature addition
```python
a = Sig(1, 1)
b = Sig(1, 1)

print(a + b)
```
```
2, 1, -2, -1
```

#### Signature subtraction
```python
a = Sig(2, 1, -2, -1)
b = Sig(1, 1)

print(a - b)
```
```
1, 1
```

#### Signature convolution

Signature convolution utilizes the signature function to perform a unique multiplication algorithm.
Note that signature convolution is not commutative!

```python
a = Sig(1, 1)
b = Sig(1, 1, 1)

print(a * b)
print(b * a)
```
```
1, 2, 3, 4, 3, 1
1, 2, 3, 3, 2, 1
```

Because signature convolution is not commutative, there are two division algorithms that may be performed.

#### Left deconvolution

The `__floordiv__` builtin specifies left deconvolution, which produces a left operand for
signature convolution.

```python
a = Sig(1, 2, 3, 4, 3, 1)
b = Sig(1, 1, 1)

print(a // b)
```
```
1, 1
```

#### Right deconvolution

The `__truediv__` builtin specifies right deconvolution, which produces a right operand
for signature convolution. Right deconvolution is right distributive.

```python
a = Sig(1, 2, 3, 4, 3, 1)
b = Sig(1, 1)

print(a / b)
```
```
1, 1, 1
```

#### The signature function

Sig objects may perform the signature and inverse signature function
the same way Seq objects can.

## Matrix

The Matrix class exists to perform interesting signature-related operations on
matrices.

### Special Matrices

The Matrix class comes equipped with several static methods that generate interesting matrices.

#### Blank matrix

Matrix.blank() is a square matrix which contains only zeroes.

```python
a = Matrix.blank(5)

print(a)
```
```
0, 0, 0, 0, 0
0, 0, 0, 0, 0
0, 0, 0, 0, 0
0, 0, 0, 0, 0
0, 0, 0, 0, 0
```

#### Identity matrix

`Matrix.identity()` produces the identity matrix. Length can be specified. `Matrix.identity()` is also the zero-th power of any Matrix.

```python
a = Matrix.identity(5)

print(a)
```
```
1
0, 1
0, 0, 1
0, 0, 0, 1
0, 0, 0, 0, 1
```

#### Power triangles

`Matrix.power()` takes a Seq and produces a power triangle. For example, the Seq [1, 1]
produces Pascal's Triangle.

```python
a = Matrix.power(Seq(1, 1), l=5)

print(a)
```
```
1
1, 1
1, 2, 1
1, 3, 3, 1
1, 4, 6, 4, 1
```

#### Sen

`Matrix.sen()` takes a Seq and constructs the initial matrix in section 4.5 of SNR part 1.

```python
a = Matrix.sen(Seq(1, 1), 6)
b = Matrix.sen(Seq(2, 1), 6)

print(a)
print(b)
```
```
1
0
1, 1
0, 1, 1
0, 0, 1, 1
0, 0, 0, 1, 1

1
1
1, 2
0, 1, 2
0, 0, 1, 2
0, 0, 0, 1, 2
```

#### g-matrices

`Matrix.g_matrix()` takes an initial Matrix and a set of Seq objects to produce a novel matrix as outlined by section 4.5 of SNR part 1.
```python
s = Matrix.power(Seq(1, 1))
g = [Seq(1), Seq(1)]
a = Matrix.g_matrix(s, g)

print(a[:6])
```
```
1
3, 1
6, 4, 1
10, 10, 5, 1
15, 20, 15, 6, 1
21, 35, 35, 21, 7, 1
```

### Mathematical operations

Matrix objects can be added, subtracted, and multiplied.

#### Addition
```python
a = Matrix.power(Seq(1, 1), 6)
b = Matrix.power(Seq(1, 0, 1), 6)

print(a + b)
```
```
2
2, 1, 1
2, 2, 3, 0, 1
2, 3, 6, 1, 3, 0, 1
2, 4, 10, 4, 7, 0, 4, 0, 1
2, 5, 15, 10, 15, 1, 10, 0, 5, 0, 1
```

#### Subtraction
```python
a = Matrix.power(Seq(1, 1, 1), 6)
b = Matrix.power(Seq(1, 1), 6)

print(a - b)
```
```
0
0, 0, 1
0, 0, 2, 2, 1
0, 0, 3, 6, 6, 3, 1
0, 0, 4, 12, 18, 16, 10, 4, 1
0, 0, 5, 20, 40, 50, 45, 30, 15, 5, 1
```

#### Multiplication

Multiplication of Matrix objects is slightly different from traditional matrix multiplication, allowing for multiplication of Matrices with different dimensions. This operation is not commutative.
```python
a = Matrix.power(Seq(1, 1))
b = Matrix.power(Seq(2, 1, 1))

print(a * b)
print(b * a)
```
```
1
3, 1, 1
9, 6, 7, 2, 1
27, 27, 36, 19, 12, 3
81, 108, 162, 120, 91, 40
243, 405, 675, 630, 555, 331

1
4, 3, 1
16, 24, 17, 6, 1
63, 138, 141, 79, 24, 3
237, 648, 798, 532, 189, 28
843, 2645, 3630, 2650, 1015, 161
```

A Matrix may also be multiplied by a Seq object.

```python
a = Seq(1, 1)
b = Matrix.power(Seq(1, 1))

print(b * a)
```
```
1, 1
1, 2, 1
1, 3, 3, 1
1, 4, 6, 4, 1
1, 5, 10, 10, 5, 1
```

### The signature and inverse signature function

The signature function can be performed on Matrix objects via antidiagonal summation.

```python
a = Matrix.power(Seq(1, 1))

print(a.f()[:9])
```
```
1, 1, 2, 3, 5, 8, 13, 21, 34
```

When Matrix.i() function is called, it first performs Matrix.f(), followed by
the inverse signature function.
```python
a = Matrix.power(Seq(1, 1))

print(a.i())
```
```
1, 1
```

# Prism

The Prism class generalizes the Matrix class to an arbitrary number of dimensions. While it has multiplicative arithmetical functionality, it exists predominantly to allow verification of the *signature dot product*.

There are two primary *canonical* Prism functions, `Prism.power` and `Prism.canonical`. They produce very expensive objects which take a while to compute.

```python

a = Prism.power(Seq(1, 1), dim=4, l=8)
b = Prism.canonical([Seq(1, 1), Seq(1, 2, 1), Seq(3, 1)], l=8)

c = a * b
```

Prisms also have access to the signature function and its inverse, and can submit a set of sequences to produce a signature convolutional result.

![Prismatic antidiagonal summation](./prismatic%20antidiagonal%20summation.png)

This is shortened by the `signature_dot_product(T: list, S: list)` function. It can be imported directly from `cxr` as `SDP`.

![The Signature Dot Product](./signature%20dot%20product.png)

If you only care about the resultant signature, you can avoid use of Prism entirely with SDP; however, if you find yourself curious about a specific type of self-constructed Prism for example, then the class is there for you to experiment with! You can read about higher-dimensional canonical objects in [SNR part 2](https://complexor.files.wordpress.com/2023/03/the-signature-function-and-higher-dimensional-objects-2.pdf).
