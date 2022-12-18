## cxr.base64

This is an implementation of arbitrary-base arithmetic up to base 64. Though I originally chose to limit it to 36 because that includes all base systems which use 0-9 and A-Z, I saw it necessary to extend the digits with a-z and +/.

Typically, computations in other bases are performed by converting the numbers to decimal, performing the operation, then converting the result back to the desired base. However, Tridozenals are __fluent__, meaning they perform all operations in their given base. There are certainly disadvantages to this way of computing, but I think it is a more pure approach.

Tridozenals were originally implemented using the Seq class from `snr.py`. But this meant I could not import Tridozenals into snr. So, in order to make signature arithmetic possible in an arbitrary base, I had to copy the code for Seq into its own file, `seq36.py`, then import _that_ into `base36.py` instead of all of snr. This allowed me to import Tridozenals into snr without an import loop. Eventually the contents of `seq36.py` were trimmed and put directly into `base36.py` to keep `cxr` clean.

### Getting started

#### Creating a Tridozenal

Start by importing the Tridozenal class. I like to import it as `Td`.

```python
from cxr.math.base64 import Tridozenal as Td
```

Tridozenals are constructed with three primary arguments: the `integer`, the `mantissa`, and the `base`.

```python
td0 = Td(integer=[1, 2], mantissa=[0, 0, 1], base=12)

print(td0)  # Displays 12.001
```

For ease of use, an `int` may be passed as the `integer` parameter and it will be converted to the given base.

```python
td0 = Td(integer=100, base=12)

print(td0)  # Displays 84
```

#### From String

The `get_from_string` function takes a string representation and a base to build a Tridozenal.

```python
td0 = Td.get_from_string("1.A078315B12B", base=12)

print(td0)  # Displays 1.A078315B12B
```

Note that you must specify a base, or else it will default to base 7. In general, not specifying a base will produce a base 7 construction. You can alter this behavior by setting `cxr.base64.default_base`.

#### Arithmetic

If two Tridozenals are of the same base, then arithmetic operations may be performed.

```python
td0 = Td(integer=10, base=2)
td1 = Td(integer=3, base=2)

print(td0 + td1)  # Displays 1101
print(td0 - td1)  # Displays 111
print(td0 * td1)  # Displays 11110
print(td0 / td1)  # Displays 11.0101010101010101...
print(td0 ** 2)  # Displays 1100100
```

### Advanced operations

#### Root by Newton Iteration

You can quickly find the n-th root of a Tridozenal using `.root()`.

```python
td0 = Td(integer=5, base=4)

print(td0.root())  # Gives square root, 2.03301232330313023332211033200...
print(td0.root(power=3))  # Gives cubic root, 1.231130003323303332301031032302...
```

They are relatively fast to compute, but there is an optional `log` parameter which, when set to `True`, provides details of the current state of computation.

#### Pi and e

Your favorite mathematical constants can be computed.

```python
pi = Td.pi(base=12)
e = Td.exp(base=2, power=1)  # The exponential function. When power=1, then it gives e

print(pi)  # Displays 3.184809493B918664573A6...
print(e)  # Displays 10.101101111110000101010...
```

Both functions have optional parameters which affect the output.

* `iterations`: max number of iterations of the computation
* `place`: number of mantissa places of the result
* `log`: whether the log messages will be printed
* `perfect`: whether to iterate until the mantissa is fully computed (can be slow!)

Note that `perfect` overrides `iterations` by running until fully computed.

#### Logarithms

The logarithm of a number may be computed. You can even take the log of a Tridozenal relative to another.

```python
td0 = Td(integer=10, base=5)

print(td0.ln())  # Displays 2.12240242122332442313

td1 = Td(integer=3, base=5)

print(td0.logarithm(td1, log=True))  # Displays calculation log followed by 2.02144322102013024103
```

Logarithms can take a while depending on how many places you're computing, so it's advisable to set `log=True`.

#### Base conversion

Integers (that is, Tridozenals without a mantissa) may be converted from one base to another, though it is very un-fluent:

```python
td0 = Td([2, 3], 0, base=7)

print(Td.convert(td0, 10))  # Displays 17
```

#### Changing final base64 characters

By default, 62 and 63 in base 64 uses `+` and `/`. You can alter this by calling `set_chars64`, submitting a two-character string containing two valid characters to uses.

```python
from cxr import set_chars64
set_chars64("/;")
```
