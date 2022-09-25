# clq.py: Socioarithmetic over Sociomathematical Strings

Below is a summary of known properties of socioarithmetic. It consists of four related but *nonmutual* operations, ie these operations are compatible but not through canonical notions such as inverse, distributivity, or even bijection (not even when limiting the set to involutions!).

## Sociomathematical strings and normal form <a name="normal"></a>

A sociomathematical string (henceforth "string") represents an injective map from the set {0,1,2,3,4,5,6,7,8,9} to itself. All strings are **bimodal** in that they have both *permutative* and *descriptive* forms.

* The permutative form maps the element role to the index function (eg `023p` maps 0 -> 0, 2 -> 1, and 3 -> 2)
* The descriptive form maps the index role to the element function (eg `023d` maps 0 -> 0, 1 -> 2, and 2 -> 3)

Through use of `instance.compile()` you can convert a string into its **normal form**. A normal form consists of an assessment (either `__`, `L-`, `L+`, `W-`, or `W+`) followed by pairs of associations. The left element of a pair is the *role designation* (eg 0 for colloquialist, 4 for contrarian) while the right element is the *function designation* (eg which role the member is *functioning as*).

```python
from cxr import Clq  # Can optionally

a = Clq("103254d")
print(a.compile("L+"))  # L+100132235445
```

Normal forms can be decompiled back into strings using `Clq.decompile(st)`.

## Magmoids

A **magmoid** is a magma without the property of closure under the given operation. Thus it is merely a set with a binary operation. An operation performed on two elements of the set may be *undefined*; this property is called **undefinitude**. The operations we will be viewing are all magmoids.

## Inclusion <a name="inclusion"></a>

Inclusion is sociomathematical addition. It is an associative unital magmoid with identity `Z = -d = -p` and in code is described by `Clq.__arith__(a, b, True)`. It is called *inclusion* because, in the event that a particular role maps to a function not within a string, it is *included* in the output.

```python
a = Clq("02143d")
print(a + a)  # 01234d

a = Clq("-12-45d")
b = "1032d"  # Strings are automatically converted to Clq instances during inclusion
print(a + b)  # 103245d

a = Clq("102349d")
b = "0246d"
print(a + b)  # UndefinedError
```

The identity is referred to as the **sociomathematical zero**. However, for any length-n string, there are *up to n* elements which are nilpotent:

```
-  # Global identity Z

# Local identities E_n for n = 1 through 10
0
01
012
0123
012345
0123456
01234567
012345678
0123456789
```

When restricted to the set of length-n involutions, inclusion loses undefinitude but remains a magmoid.

## Rejection <a name="rejection"></a>

Rejection is sociomathematical subtraction. It is a left-unital magmoid whose identity is the sociomathematical zero. In code it is described by `Clq.__arith__(a, b, False)`. While it serves to "undo" the process of inclusion in some regards, it also eliminates members which are "in place" relative to the subtrahend.

```python
a = Clq("013254d")
b = Clq("0132p")
print(a - b)  # ----54d

a = Clq("1023d")
b = "102p"  # Rejection works like inclusion vis-a-vis string interactions
print(a - b)  # 10-3d

a = Clq("1234p")
b = "213p"
print(a - b)  # -214p
```

Over the set of length-n involutions, rejection loses undefinitude but remains a magmoid.

# Isolation <a name="isolation"></a>

Isolation is sociomathematical convolution. It is a monoid with identities E_n depending on length. In code it is described by `Clq.__metic__(a, b, True)`. The multiplicand is used in the following way:

* For each role-function pair RF in the right operand, find the role-function pair RF2 whose function is equal to the role of RF;
* Change RF2's function to the function of RF;
* For each role-function pair in the left operand, if its function is not associated with the function of a pair in the right operand, it is *removed* from the string

```python

a = Clq("0213d")
b = "-1-3d"
print(a * b)  # --13d

a = Clq("--78--2d")
b = 2  # Shorthand for --2d
print(a * b)  # ------2d
```

# Reduction <a name="reduction"></a>

Reduction is sociomathematical deconvolution. It is a left-unital magmoid whose identity is `Z`. In code it is described by `Clq.__metic__(a, b, False)`. The divisor is used in the following way:

* For each role-function pair RF in the divisor, find the role-function pair RF2 whose function is equal to the role of RF;
* Remove RF2 from the string;
* Find the string RF3 whose function matches the function of RF, and change that function to the role of RF (F -> R)

```python
a = Clq("0231d")     # __00311223
print(a / "-2d")     # 013d: __001123

a = Clq("1402d")     # __20013214
print(a / "24d")     # -1-0d: __3011

a = Clq("-1-3-56d")  # __11335566
print(a / "-5-6d")   # -----13d: __5163
```
