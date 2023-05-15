# clq.py

`clq.py` is used to construct sociomathematical teams following the open-source framework of **colloquiality theory**. Teams are constructed by assigning team members, who have a default *role*, to a certain *function*. You can read about its primary motivation in [Terminal Anticolloquiality and Its Treatment](https://complexor.files.wordpress.com/2023/05/terminal-anticolloquiality-and-its-treatment.pdf).

## Roles and functions

It is important to distinguish, as best as can be done, between the notions of *role* and *function*. In essence, the role is what the sociomathematician *is*; and the function is what they *do*. It is difficult to define these notions without cross-reference because they are near-synonymous: the role is the *canonical function which an individual typically fills*; and the function is the *role which an individual is currently filling*.

### The colloquialist

The colloquialist is the root scientist within a sociomathematical team. Their core responsibility is to actively approach terminal anticolloquiality in order to assess moments and potential opportunities for recolloquialising actions. Ultimately the role of the colloquialist is to "grok vibes and deliver indicators to meet the moment". This means that they are responsible for establishing the nature of all forms and methods of communication *intuitively* rather than *analytically*, and reacting in a way which promotes the health of the experiment.

The efficacy of a colloquialist relies heavily on its ability to **multithread**, ie perform multiple functions in support of itself during colloquialative processes. This can be beneficial to the experiment, as the colloquialist is usually the best choice for any sociomathematical role, at the increased risk of **noncolloquial** rather than *anticolloquial* indicators. This key difference is important: noncolloquialative processes are easier to write off in social scenarios, whereas anticolloquialative ones *run directly counter to colloquialising norms and have a colloquial impact*.

Colloquialists are often considered to be the "early warning system" for a sociomathematical experiment; When they indicate that something is going wrong, then it usually has. This can, however, negatively influence the colloquiality of the team, which may not recognize symptoms of anticolloquiality until it becomes terminal.

### The analyst

The analyst is the primary scientist in support of the colloquialist. Analysts are responsible for crunching numbers and assigning quantitative value to indicators based on predetermined (and often self-determined) schemata. They may also highlight opportunities for qualitative assessment, and even offer potential frameworks for such analysis.

Due to the centrality of an analyst's importance in setting the stage for futurising activities, it is difficult to truly get them out of that function. As such they, like the interrogator, tend to be the weakest ultary team member unless supported cross-functionally. Unfortunately, since this is not always a viable composition, it's important to consider arithmetical options for transitioning analysts into place.

### The catastrophist

The catastrophist is the primary scientist in support of the analyst. Catastrophists are responsible for always asking "What could go wrong?" and surmising worst-case scenarios. Additionally, unlike what the term's connotations might suggest, the catastrophist does not simply catastrophise negatively, but expounds upon and "explodes" the frameworks which the analyst presents so they might be seen from different perspectives.

Assigning a function to a catastrophist is challenging, because on its own it is quite anticolloquial. But an ultary catastrophist provides a unique form of additional analysis to its function, always with the explicit caveat that it is dealing in hypotheticals.

### The interventionist

The interventionist is the primary scientist in support of the catastrophist. Interventionists are responsible for assessing risks and concerns to projects in terms of present indications. They are *not* solely responsible for engaging in mitigating actions, if at all. But they are in a sense the first line of defense against the unmitigated disasters provided through the catastrophist's indications.

Due to their canonical function, interventionists are highly empathetic in their analysis and decision-making processes. Consequently, they often thread as catastrophists, regardless of the function in which they are currently placed. However, an interventionist's desire to see solutions to problems come to fruition may guide their actions.

### The contrarian

The contrarian is the primary scientist in support of an interventionist. Their core responsibility is to produce counterrogatives against the indication given by the interventionist.

Contrarians typically perform well in place when supporting any of the three prior roles. However, without the full complement, it struggles to deliver useful indications to an interrogator.

### The interrogator

The interrogator is the primary scientist in support of the contrarian. Interrogators excel in the process of *active decolloquialisation*. Active decolloquialisation is the process through which anticolloquial data is stripped down to its noncolloquial essence. This is most effectively accomplished through survey of the colloquialist.

### The therapist

The therapist is the primary scientist in support of the interrogator. Therapists engage in the process of *active recolloquialisation*. Active recolloquialisation is the process through which the noncolloquial essence of anticolloquial data is reorganised and colloquialised for the team.

### The dreamer

The dreamer is the primary scientist in support of the therapist. Dreamers mediate the recontextualisation of the anticolloquial in artful ways which enable out-of-the-box thinking about what is being learned

### The interpreter

The interpreter is the primary scientist in support of the dreamer. The interpreter compares the context of the subject and the provided dreams to try and determine elements of the anticolloquial experience such as meaning, inspiration, and objectives.

### The historian

The historian is the primary scientist in support of the interpreter as well as the sociomathematical team as a whole. Historians are the other imperative member of a sociomathematical team besides the colloquialist. They are responsible for compiling and summarising the information which has been gathered by the team, and delivering an *indication* to the colloquialist that determines their future direction.

# Socioarithmetic over Sociomathematical Strings

Socioarithmetic is used to express the modification of sociomathematical teams according to a mathematical framework which can be interrogated logically. It provides a shorthand for the historian to use in studying the actions of the team and its reorganisation throughout a project.

Below is a summary of known properties of socioarithmetic. It consists of four related but *nonmutual* operations, ie these operations are compatible but not through canonical notions such as inverse, distributivity, or even bijection (not even when limiting the set to involutions!).

## Limitations

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
