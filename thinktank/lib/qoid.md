# cxr.qoid

Qoid is a simple markup language which uses tag-value pairs to record data in traditional files and folders with the added depth of tagged elements within each file.

All objects in qoid.py have string tags, with values which add recursive depth. Start with a Property, which is a tag-value pair. Then a Qoid tags a list of Properties, a Bill tags a list of Qoids, and a Register tags a list of Bills and Registers.
An object in qoid.py can be created very quickly, then viewed or saved in its Qoid representation.

Some examples are provided below.

```python
from thinktank.lib.qoid import Property, Qoid, Bill

a = Property("tag", "value")
b = Property("tag2", "value2")
c = Qoid("qoid tag", [a, b])
d = Qoid("other qoid tag", [b, a, b])
e = Bill("test bill", [c, d])
print(e)
```
```
#qoid tag
tag: value
tag2: value2

#other qoid tag
tag2: value2
tag: value
tag2: value2
```
## Properties

A Property is a tag-value pair. The tag and value may be changed via the set function,
or by directly accessing the class variables.

```python
from thinktank.lib.qoid import Property

p_a = Property("tag", "value")
print(p_a)
p_a.set(val="new value")
print(p_a)
p_a.tag = "new tag"
print(p_a)
```
```
tag: value
tag: new value
new tag: new value
```

## Qoids

Like Properties, Qoids are a tag-value pair. However, instead of a string, the value is a list of Properties.

Qoids are printed using a simple ini-like markup language.

```python
from thinktank.lib.qoid import Property, Qoid

p_a = Property("tag1", "value1")
p_b = Property("tag2", "value2")

q_a = Qoid("qoid1", [p_b, p_a])
print(q_a)
```
```
#qoid1
tag2: value2
tag1: value1
```

## Bills

A Bill is a Qoid whose value is a list of Qoids. Bills may be saved to and loaded from `.cxr` files.

```python
from thinktank.lib.qoid import Property, Qoid, Bill

p_a = Property("tag1", "value1")
p_b = Property("tag2", "value2")

q_a = Qoid("qoid1", [p_b, p_a])
q_b = Qoid("qoid2", [p_b])

b_a = Bill("Bill 1", [q_a, q_a, q_b])
print(b_a)
print()

b_a.save()
```
```
#qoid1
tag2: value2
tag1: value1

#qoid1
tag2: value2
tag1: value1

#qoid2
tag2: value2

Bill Bill 1 saved to Bill 1.cxr
```

## Registers

A Register is a Qoid whose value set contains Bills and Registers.
Registers may be saved to and loaded from folders which end in `.cxr`.

```python
from thinktank.lib.qoid import Property, Qoid, Bill, Register

p_a = Property("tag1", "value1")
p_b = Property("tag2", "value2")

q_a = Qoid("qoid1", [p_b, p_a])
q_b = Qoid("qoid2", [p_b])

b_a = Bill("Bill 1", [q_a, q_a, q_b])
b_b = Bill("Bill 2", [q_b, q_b])

r_a = Register("Register A", [b_a, b_b])
print(r_a)

r_a.save()
```
```
/ Bill 1

#qoid1
tag2: value2
tag1: value1

#qoid1
tag2: value2
tag1: value1

#qoid2
tag2: value2

/ Bill 2

#qoid2
tag2: value2

#qoid2
tag2: value2

Bill Bill 1 saved to Register A.cxr/Bill 1.cxr
Bill Bill 2 saved to Register A.cxr/Bill 2.cxr
Register Register A saved to Register A.cxr
```


## Built-ins

Comparator | Description
--- | ---
x ( ) y | Checks if an object is ...
x == y | equal to another in terms of tag and value
x != y | not equal to another in terms of tag and value
x > y |  greater than another in terms of tag
x >= y | greater than or equal to another in terms of tag
x < y | less than another in terms of tag
x <= y | less than or equal to another in terms of tag
x in y | contained in the value set of another
**Arithmetic** | 
x + y | combines the elements of the two objects, if applicable (also works with x += y)
x - y | removes an object from another, if applicable (also works with x -= y)
**Other Built-in** | 
len | returns the length of the object's value list
getitem/setitem/delitem | get, set, or delete the member of the value set based on slice, tag (string) or index (int)
format/str | prepares useful string representation of the object
hash | 
bytes | 
