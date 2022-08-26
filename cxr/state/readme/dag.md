## cxr.dag

This is an implementation of a directed acyclic graph. This is the second data structure I've built, but it would have been much easier to start with this rather than binary search trees. DAGs are definitely more intuitive data structures.

After finishing up with `cxr.bst`, I reviewed my random code folder and the other data structures I had attempted to implement. I found a class called DAGNode which, after the bugs were ironed out, was looking pretty good.

I managed to use anonymous functions to shorten the code for shortest and longest path, and that was when I decided to take the implementation more seriously.

Transitive reduction and topological sort were also immensely satisfying to implement.

### Summary of features

* Shortest and longest path
* Topological sort and transitive reduction
* Internal data
* `__iadd__` and `__isub__`

### Getting started

A DAG begins with a root Node.

```python
from cxr.state import dag

root = dag.Node("node1")

root.add(dag.Node("node2"))  # Adds Node node2 to root
root += "node3"  # Creates a node named node3 and adds it to root

root["node3"] += "node4"  # Accesses node3 and adds node4 to it
root["node3"].remove("node4")  # Searches for and removes node4
```

Nodes automatically determine a type and prevent Nodes of a different type from being added.

```python
root += 2  # Fails to create and add new node because 2 is not a string
```

There are also errors thrown for failed additions and removals

```python
root["node3"] += root  # Fails because it would create a cycle
root += "node2"  # Fails because node2 would be a duplicate
root -= "node4"  # Fails because node4 is not in root
```

A Node may be topologically sorted, which produces a list of sorted Nodes including the Node itself.

```python
top_sort = root.sort()
```

Nodes may also be reduced to their __transitive closure__.

```python
root = root.transitive_reduction()
```
