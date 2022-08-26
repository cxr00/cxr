

class Node:

    def __init__(self, key, nodes=None, data=None, parent=None):
        if key is None:
            raise TypeError(f"Node key cannot be None")
        self.key = key
        self.nodes = []
        self.node_type = type(key)
        self.data = data if data else {}
        self.parent = []
        if nodes:
            for node in nodes:
                self.add(node)
        if parent:
            if isinstance(parent, list):
                for e in parent:
                    if isinstance(e, Node):
                        if e.node_type == self.node_type:
                            self.parent.append(e)
                        else:
                            raise ValueError(f"Incompatible parent type {e.node_type}, must be {self.node_type}")
                    else:
                        raise ValueError(f"Parent must be Node, not {type(e)}")
            elif isinstance(parent, Node):
                if parent.node_type == self.node_type:
                    self.parent = parent
                else:
                    raise ValueError(f"Incompatible parent type {parent.node_type}, must be {self.node_type}")
            else:
                raise ValueError(f"Parent must be Node, not {type(parent)}")

    def __getitem__(self, item):
        if isinstance(item, self.node_type):
            for node in self:
                if node.key == item:
                    return node
            raise KeyError(f"Node {item} not found in {self.key}")
        else:
            raise TypeError(f"Must be {self.node_type}, not {type(item)}")

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        else:
            raise AttributeError(f"{self.node_type.__name__} Node has no attribute {item}")

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        self.remove(other)
        return self

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def __str__(self):
        if not self.nodes:
            return str(self.key)
        output = f"{self.key}:("
        output += ", ".join([str(node) for node in self]) + ")"
        output += ")"
        return output

    @staticmethod
    def topological_sort(nodes):
        """
        Topological sort of the DAG, where each Node appears before its children in the list

        Access using self.sort()
        """
        output = nodes

        is_sorted = False
        while not is_sorted:
            is_sorted = True
            for i in range(len(output) - 1):
                if output[i+1].leads_to(output[i]):
                    output[i+1], output[i] = output[i], output[i+1]
                    is_sorted = False

        return output

    def add(self, node):
        if isinstance(node, Node):
            if node.key in [n.key for n in self]:
                raise KeyError(f"Node {node.key} already added to {self.key}")

            if node.node_type != self.node_type:
                raise TypeError(f"Node {node.key} must be {self.node_type.__name__}, not {node.node_type.__name__}")
            self.nodes.append(node)

            if self._check_for_cycle(self):
                self.nodes = self.nodes[:-1]
                raise ValueError(f"Adding Node {node.key} would create a cycle")

            if isinstance(node.parent, Node):
                node.parent = [node.parent, self]
            else:
                if len(node.parent) == 0:
                    node.parent = self
                else:
                    node.parent.append(self)

        elif isinstance(node, self.node_type):
            self.add(type(self)(node))
        else:
            raise KeyError(f"Must be Node or {self.node_type}, not {type(node)}")

    def remove(self, node):
        if isinstance(node, Node):
            if node not in self:
                raise ValueError(f"Node {node.key} is not sub-Node of {self.key}")
            else:
                self.nodes.pop(self.nodes.index(node))
        elif isinstance(node, self.node_type):
            keys = self.keys()
            if node not in keys:
                raise ValueError(f"Node {node} is not sub-Node of {self.key}")
            else:
                self.nodes.pop(keys.index(node))
        else:
            raise ValueError(f"Must be Node or {self.node_type}, not {type(node)}")

    def sort(self):
        # Structured in much the same way as cxr.bst.Node.balance()
        return Node.topological_sort(self.all_nodes())

    def leads_to(self, other_node):

        if isinstance(other_node, self.node_type):
            for node in self:
                if node.key == other_node:
                    return True
                elif node.leads_to(other_node):
                    return True

            return False

        elif isinstance(other_node, Node):
            for node in self:
                if node == other_node:
                    return True
                elif node.leads_to(other_node):
                    return True

            return False
        else:
            raise TypeError(f"Invalid type of {type(other_node).__name__}, must be {self.node_type.__name__}")

    def find_by(self, attr, value):
        output = []

        if attr in self.data:
            if value in self.data[attr]:
                output.append(self)

        for node in self:
            output += node.find_by(attr, value)

        return output

    def keys(self):
        return [k.key for k in self]

    def longest_path_to(self, node_key):
        return self._path_to(node_key, lambda x, y: len(x) < len(y))

    def shortest_path_to(self, node_key):
        return self._path_to(node_key, lambda x, y: len(x) > len(y))

    def path_to(self, node_key):
        path = self.shortest_path_to(node_key)
        if path[-1].key == node_key:
            return path
        else:
            raise KeyError(f"Invalid key: {node_key}")

    def transitive_reduction(self):

        is_transed = False
        while not is_transed:
            is_transed = True

            for i, node_a in enumerate(self):
                self.nodes[i] = self.nodes[i].transitive_reduction()
                for node_b in self:
                    if node_a != node_b and node_b.leads_to(node_a):
                        self.nodes.pop(i)
                        is_transed = False
                        break
                if not is_transed:
                    break

        return self

    def all_nodes(self):

        output = [self]

        for node in self:
            get = node.all_nodes()
            for each in get:
                if each not in output:
                    output.append(each)

        return output

    def all_leaves(self):
        output = []
        for each in self.all_nodes():
            if not len(each):
                output.append(each)
        return output

    def is_root(self):
        if self.parent:
            return False
        else:
            return True

    def find_node(self, key):
        for n in self.all_nodes():
            if n.key == key:
                return n
        raise KeyError(f"Invalid key: {key}")

    def find_attribute(self, attr):
        """
        Searches the Node for instances of a given attribute
        :param attr: The attribute being sought
        :return: a dictionary of Node keys and the values they has for attr
        """
        output = {}
        if attr in self.data:
            output.update({self.key: self.data[attr]})
        for o in self:
            if attr in o.data:
                output.update({o.key: o.data[attr]})
            output.update(o.find_attribute(attr))
        return output

    def _check_for_cycle(self, root):

        for node in self:
            if node == root:
                return True
            else:
                return node._check_for_cycle(root=root)

        return False

    def _path_to(self, node_key, func, current=None):
        """
        Finds either the shortest or longest path, depending on the given func

        This is my first application of anonymous functions
        that reduces code duplication. I'm quite proud
        """
        if not current:
            current = [self]

        if self.key == node_key:
            return current

        if node_key in self:
            return current + [self[node_key]]

        output = current
        for node in self:
            path = node._path_to(node_key, func, current + [node])
            if path[-1].key == node_key:
                if output[-1].key != node_key:
                    output = path
                elif func(output, path):
                    output = path

        return output
