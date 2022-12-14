# clq.py: Socioarithmetic over Sociomathematical Strings

Below is a summary of known properties of socioarithmetic. It consists of four related but *nonmutual* operations, ie these operations are compatible but not through canonical notions such as inverse, distributivity, or even bijection (not even when limiting the set to involutions!).

# Limitations

The primary limitation of socioarithmetic is that **it cannot change the role of an input, only its function**. This means you must introduce new roles via inclusion, and then sculpt them via other operations.

While a team with all roles in place is ideal, it is not always logistically optimal. The purpose of socioarithmetic is not merely to negotiate roles into place, but to theorise working from a clear disadvantage in order to evaluate prospects.

## Sociomathematical strings and normal form <a name="normal"></a>

A sociomathematical string (henceforth "string") represents an injective map from the set {0,1,2,3,4,5,6,7,8,9} to itself. All strings are **bimodal** in that they have both *permutative* and *descriptive* forms.

* The permutative form maps the element role to the index function (eg `023p` maps 0 -> 0, 2 -> 1, and 3 -> 2)
* The descriptive form maps the index role to the element function (eg `023d` maps 0 -> 0, 1 -> 2, and 2 -> 3)

Through use of `instance.compile()` you can convert a string into its **normal form**. A normal form consists of an underscore `_` followed by pairs of associations. The left element of a pair is the *role designation* (eg 0 for colloquialist, 4 for contrarian) while the right element is the *function designation* (eg which role the member is *functioning as*).

```python
from cxr import Clq  # Can optionally

a = Clq("103254d")
print(a.compile())  # _100132235445
```

Normal forms can be decompiled back into strings using `Clq.decompile(st)`.

## Magmoids

A **magmoid** is a magma without the property of closure under the given operation. Thus it is merely a set with a binary operation. An operation performed on two elements of the set may be *undefined*; this property is called **undefinitude**. The operations we will be viewing are all magmoids.

## Inclusion <a name="inclusion"></a>

Inclusion is sociomathematical addition. It is an associative unital magmoid with identity `Z = -d = -p` and in code is described by `Clq.__arith__(a, b, True)`. It is called *inclusion* because, in the event that a particular role maps to a function not within a string, that pair is *included* in the output.

For each role-function pair RF in the left operand, find the pair R'F' in the right operand such that F = R' and set F = F'; if no such pair R'F' exists, then add R'F' to the result.

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

Rejection is sociomathematical subtraction. It is a left-unital magmoid whose identity is the sociomathematical zero `Z`. In code it is described by `Clq.__arith__(a, b, False)`. It is called rejection because in the event a subtracted role-function pair is present in the original string, that pair is *rejected* from the result.

For each role-function pair RF in the left operand, find the pair R'F' in the right operand such that F = F'. If R = R', then remove RF (*reject*) from the output; otherwise set F = R'.

```python
a = Clq("013254d")
b = Clq("0132p")
print(a - b)  # ----54d

a = Clq("1023d")
b = "102p"
print(a - b)  # ---3d

a = Clq("1234p")
b = "213p"
print(a - b)  # -214p
```

Over the set of length-n involutions, rejection loses undefinitude but remains a magmoid.

## Isolation <a name="isolation"></a>

Isolation is sociomathematical convolution. It is a monoid with identities `E_n` depending on length. In code it is described by `Clq.__metic__(a, b, True)`. It is called isolation because it removes all role-function pairs whose function is not in the right operand, *isolating* what remains.

For each role-function pair RF in the left operand, if there is a pair R'F' in the right operand such that F = R', set F = F'; otherwise remove RF.

```python

a = Clq("0213d")
b = "-1-3d"
print(a * b)  # --13d

a = Clq("--78--2d")
b = 2  # Shorthand for --2d
print(a * b)  # ------2d
```

## Reduction <a name="reduction"></a>

Reduction is sociomathematical deconvolution. It is a left-unital magmoid whose identity is `Z`. In code it is described by `Clq.__metic__(a, b, False)`. It is called reduction because it removes functions

For each role-function pair RF in the left operand, find the pair R''F' in the right operand such that F = F'; remove R'F'' if present and set F = R'.

```python
a = Clq("0231d")     # __00311223
print(a / "-2d")     # 013d: __001123

a = Clq("1402d")     # __20013214
print(a / "24d")     # -1-0d: __3011

a = Clq("-1-3-56d")  # __11335566
print(a / "-5-6d")   # -----13d: __5163
```

## Long-form explanations

* `Inclusion`: For each role-function pair RF in the left operand, find the pair RF' in the right operand such that F = R' and set F = F'; if no such pair R'F' exists, then *include* RF in the result.


* `Rejection`: For each role-function pair RF in the left operand, find the pair R'F' in the right operand such that F = F'. If R = R', then *reject* RF from the output; otherwise set F = R'.


* `Isolation`: For each role-function pair RF in the left operand, if there is a pair R'F' in the right operand such that F = R', set F = F'; otherwise remove RF.


* `Reduction`: For each role-function pair RF in the left operand, find the pair R''F' in the right operand such that F = F'; remove R'F'' if present and set F = R'.

## Mnemonics for addition & removal

Because these related operations are highly permutative, it can be difficult to grasp what a specific one is doing. Hopefully this minimized format serves to express the fundamental properties of each operation.

```
R   /   F - left operand role / function
R'  /  F' - right operand role / function
R'' / F'' - incidental role / function

_RF + _FF' = _RF'  # add _R'F' if no F = R'
_RF - _F'F = _RF'  # rem _R'F' if _RF = _R'F'
_RF * _FF' = _RF'  # rem _RF if no F = R'
_RF / _F'F = _RF'  # rem _R'F'' if F = F'
```
