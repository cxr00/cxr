from cxr.state.qoid import Property, Qoid, Bill
from cxr.state.dag import Node

import random
import os

key_chars = [chr(a) for a in (list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123)))]
key_length = 6


class StateError(KeyError):
    """
    An exception which is thrown when a KeyError prevents actions by or concerning StateManagers
    """


class StateData:
    """
    StateData distinguishes a StateManager's serializable and nonserializable parameters.
    """

    def __init__(self, parent=None):
        self._ser = {}
        self._nonser = {}
        self.parent = parent
        self._ser_first = True

    def __iter__(self):
        return iter([*self._ser.keys(), *self._nonser.keys()])

    def __getitem__(self, item):
        if item in self._ser:
            return self._ser[item]
        elif item in self._nonser:
            return self._nonser[item]
        else:
            raise StateError(f"{self.parent.name}({self.parent.key}) StateData has no element {item}")

    def __setitem__(self, key, value):
        """
        Checks whether the key exists in either _ser or _nonser, otherwise use default behavior
        """

        if key in self._nonser:
            self._nonser[key] = value
        elif key in self._ser:
            self._ser[key] = value
        else:
            if self._ser_first:
                self._ser[key] = value
            else:
                self._nonser[key] = value

    def __str__(self):
        output = {}
        for k, v in self.items():
            output[k] = v
        return str(output)

    def __repr__(self):
        return str(self)

    def has_serializables(self):
        return bool(self._ser)

    def toggle_ser_priority(self, ser_first=None):
        self._ser_first = ser_first if ser_first is not None else not self._ser_first

    def items(self):
        return [*self._ser.items(), *self._nonser.items()]

    def ser(self, attr, value):
        if attr in self._nonser:
            raise TypeError(f"Cannot set serializable attribute in {self.parent.name} ({self.parent.key}): Item with key {attr} is in nonserializable")
        self._ser[attr] = value

    def nonser(self, attr, value):
        if attr in self._ser:
            raise TypeError(f"Cannot set nonserializable attribute in {self.parent.name} ({self.parent.key}): Item with key {attr} is in serializable")
        self._nonser[attr] = value

    def qoid(self):
        q = Qoid(self.parent.key if self.parent else "StateData")

        for k, v in self._ser.items():
            q += Property(k, v)

        return q

    def update(self, d):
        for k, v in d.items():
            self[k] = v


class StateManager:
    """
    StateManager collects related states, and keeps a current state for speedy evaluation
    """

    _reference = {}

    def __init__(self, key, name):
        if key in StateManager._reference:
            raise StateError(f"Init failed: StateManager with key {key} already exists in global register")
        self.key = key
        self.name = name
        self._current = None
        self._current_key = None
        self._states = {}
        self._controller = None
        self._data = StateData(self)
        self._checks = []
        self._cxrnode = None

        StateManager._reference[self.key] = self

    def __call__(self, event):
        self._control(event)
        if self._current:
            self._current(event)
        for check in self._checks:
            check(event)

    def __deepcopy__(self, memodict={}):
        raise TypeError("Cannot deepcopy a StateManager instance")

    def __getitem__(self, item):
        return self._data[item]

    def __getattr__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def has_serializables(self):
        return self._data.has_serializables()

    def toggle_ser_priority(self, ser_first=None):
        self._data.toggle_ser_priority(ser_first)

    def set_attribute(self, attr, value):
        """
        Set an arbitrary attribute
        """
        self._data[attr] = value

    def set_flag(self, flag, initial=False):
        """
        Set a boolean flag
        """
        self._data[flag] = initial

    def set_counter(self, flag, initial=0):
        self._data[flag] = initial

    def set_target(self, flag, target, initial=0):
        """
        Set a target tracker
        """
        self._data[flag] = {"num": initial, "target": target}

    def add_state(self, key):

        def outer_wrapper(f):

            def inner_wrapper(event):
                f(event)

            if key in self._states:
                raise StateError(f"State add failed: {self.name}({self.key}) StateManager already has a state with key {key}")
            else:
                self._states[key] = inner_wrapper
                if not self._current:
                    self._current = self._states[key]
                    self._current_key = key

        return outer_wrapper

    def change_state(self, key):
        if key not in self._states:
            raise StateError(f"State change failed: StateManager {self.key} has no state {key}")
        self._current = self._states[key]
        self._current_key = key

    def get_state(self, key):
        if key not in self._states:
            raise StateError(f"Get state failed: StateManager {self.name} ({self.key}) has no state {key}")
        return self._states[key]

    def controller(self, f):
        """
        Decorator to assign a state controller function to the given StateManager

        The controller function determines the current state.
        It is executed immediately before the current state is executed.

        :param f: the function which will serve as the controller
        """
        self._controller = f

    def _control(self, event):
        """
        Execute the controller function
        """
        if not self._controller:
            raise ValueError(f"No controller is specified for {self.name} StateManager ({self.key})")
        self._controller(event)

    def check(self, f):
        """
        Decorator which adds an additional function check to the given StateManager
        """
        self._checks.append(f)

    def ser(self, key, value=None):
        """
        Add a nonserializable parameter to the StateData
        """
        self._data.ser(key, value)

    def nonser(self, key, value=None):
        """
        Add a nonserializable parameter to the StateData
        """
        self._data.nonser(key, value)

    def qoid(self):
        b = Bill(self.name)
        b += self._data.qoid()
        return b

    def load(self, *params):
        b = Bill.open(self._cxrnode.path())
        if len(params):
            for param in params:
                self[param] = b[self.key][param]
        else:
            sd = {}
            for p in b[self.key]:
                sd.update({p.tag: p.val})
            self._data.update(sd)

    def save(self, *params):
        if self.has_serializables():
            try:
                b = Bill.open(self._cxrnode.path())
                if self.key not in b.tags():
                    b += self._data.qoid()
                else:
                    q = self._data.qoid()
                    if len(params):
                        for param in params:
                            b[self.key][param] = q[param]
                    else:
                        b[self.key] = q
            except FileNotFoundError:
                b = self.qoid()
                self._cxrnode.touch()
                b.path = self._cxrnode.parent.path()
            b.save(echo=False)

    def current_state(self):
        return self._current_key

    def exists(self):
        return self.key in StateManager._reference

    @staticmethod
    def all():
        return list(StateManager._reference.values())

    @staticmethod
    def get(key):
        """
        Get the StateManager with the given key
        """
        if key not in StateManager._reference:
            raise StateError(f"Get failed: StateManager with key {key} not in global register")
        else:
            return StateManager._reference[key]

    @staticmethod
    def delete(item):
        """
        Delete a StateManager from the global register
        """
        if isinstance(item, StateManager):
            item._cxrnode.remove_reference(item)
            del StateManager._reference[item.key]
        elif isinstance(item, str):
            if item not in StateManager._reference:
                raise StateError(f"Delete failed: StateManager with key {item} not in global register")
            item = StateManager._reference[item]
            item._cxrnode.remove_reference(item)
            del StateManager._reference[item]
        else:
            raise StateError(f"Delete failed: Can only delete by string or StateManager, not {(type(item))}")

    @staticmethod
    def generate_key():
        """
        Create a unique key for a StateManager object
        """
        return "".join([random.choice(key_chars) for _ in range(key_length)])

    @staticmethod
    def generate(path, subtype=None, key=None, randomise=False, **kwargs):
        """
        The primary method for creating StateManager objects

        :param path: The StateManagerReference path where the SM will be located
        :param subtype: The subclass of StateManager which is to be generated
        :param key: The unique identifier to give the SM; a random one is generated if none is specified
        :param randomise: Whether or not to use a randomised key (such as for fully-nonserialized or intentionally-obfuscated SMs)
        :return:
        """
        name = path.split("/")[-1]
        if not key:
            if randomise:
                n = 0
                while True:
                    key = name + "_" + StateManager.generate_key()
                    if key not in StateManager._reference:
                        break
                    else:
                        n += 1
                        if n % 77377 == 0:
                            err_text = [
                                "Failed to generate unique key in 77377 iterations.",
                                "You either have too many or got REALLY unlucky.",
                                "Make sure you are deleting old unused references!"
                            ]
                            raise StateError("\n".join(err_text))
            else:
                new_key = name + "_"
                n = len(StateManagerReference.get_node(path))
                while True:
                    key = new_key + str(n)
                    if key not in StateManager._reference:
                        break
                    else:
                        n += 1
        if subtype:
            output = subtype(key, name, **kwargs)
        else:
            output = StateManager(key, name)
        cxrnode = StateManagerReference.get_node(path)
        cxrnode.add_reference(output)
        return output

    @staticmethod
    def reset():
        """
        Clear the StateManager register
        """
        StateManager._reference = {}


class StateManagerFactory:
    """
    Factory class for constructing StateManagers. Specify path, subtype, and randomise, and optional key in SMF.make()
    """
    def __init__(self, path, subtype=None, randomise=False):
        self.path = path
        self.subtype = subtype
        self.randomise = randomise

    def make(self, key=None):
        return StateManager.generate(self.path, self.subtype, key, self.randomise)


class CXRNode(Node):
    """
    CXRNode is a StateManagerReference utility for pathing and file generation

    CXRNode emulates the file structure of the StateManagerReference without
    needing to have everything loaded all at once. It uses a path function
    to produce a save location.
    """

    def __init__(self, key, nodes=None, data=None, parent=None):
        super().__init__(key, nodes, data, parent)
        self._reference = {}

    def __len__(self):
        return len(self._reference.keys())

    def __str__(self):
        """
        The string representation of a CXRNode is the path used
        to retrieve its reference from the root node
        """
        if not self.parent or self.parent.is_root():
            return self.key
        else:
            return str(self.parent) + "/" + self.key

    @staticmethod
    def initialize(root):
        """
        Create a CXRNode at the given root
        """
        if not os.path.isdir(root):
            if not os.path.isfile(root):
                os.makedirs(root)
            else:
                raise FileExistsError(f"Cannot initialize to {root}, as it already exists as a file.")

        node = CXRNode(root)
        node.build()
        return node

    def add_reference(self, *references):
        """
        Add one or more references to the node

        :param references: the StateManagers to be referenced
        """
        for reference in references:
            self._reference[reference.key] = reference
            reference._cxrnode = self

    def remove_reference(self, *references):
        """
        Remove one or more references from the node

        :param references: the StateManagers to be dereferenced
        """
        for r in references:
            if r in self._reference:
                del self._reference[r.key]
                # self._reference.pop(self._reference.index(r))
                # r._cxrnode = None

    def build(self):
        """
        Construct subnodes based on valid cxr paths
        """
        if os.path.isfile(self.path()):
            return

        for f in os.listdir(self.path()):
            if f.endswith(".cxr"):
                f = f.replace(".cxr", "")
                self.add(CXRNode(f))
                self[f].build()

    def add_path(self, path):
        """
        Add all necessary nodes to construct a node at the given path

        :param path: the directions to the node eg "path/to/node"
        """
        if isinstance(path, str):
            path = path.split("/")
        f = path[0]
        if f not in self.keys():
            self.add(f)
        if len(path) > 1:
            node = self[f]
            node.add_path(path[1:])

    def build_filepath(self):
        """
        Create all necessary directories for the CXRNode
        """
        path = self.path().split("\\")
        for i in range(len(path) - 1):
            join = "\\".join(path[:i+1])
            if os.path.isdir(join):
                continue
            elif os.path.isfile(join):
                raise FileExistsError(f"Cannot create directory {join} as it is already a file")
            else:
                os.mkdir(join)

    def has_path(self, path):
        """
        Determine if the given path is valid in the CXRNode
        """
        if isinstance(path, str):
            path = path.split("/")
        f = path[0]
        if f not in self.keys():
            return False
        elif len(path) > 1:
            return self[f].has_path(path[1:])
        else:
            return True

    def path(self):
        """
        Create a file path using the node's relative location
        """
        if self.is_root():
            return self.key
        else:
            p = self.parent
            return p.path() + "\\" + self.key + ".cxr"

    def get(self, path, add_path=True):
        """
        Retrieve a node at the given path.
        If a particular node in the path does not exist, one is created.

        :param path: the directions to the node, eg "path/to/node"
        :param add_path: memoization variable; do not set manually
        """
        if isinstance(path, str):
            path = path.split("/")
        if add_path:
            self.add_path(path)
        if len(path) == 1:
            return self[path[0]]
        else:
            return self[path[0]].get(path[1:], False)

    def touch(self):
        """
        Create a file at the given location if one does not yet exist
        """
        self.build_filepath()
        if not os.path.exists(self.path()):
            open(self.path(), "w+")


class StateManagerReference:
    """
    The StateManagerReference tracks the serialization points for each StateManager
    """

    root = ""
    frame = None

    @staticmethod
    def initialize(root=None):
        """
        Initialize the SMR frame at the given root,
        or reinitialize at the current root
        """
        if root:
            StateManagerReference.root = root
        StateManagerReference.frame = CXRNode.initialize(root)

    @staticmethod
    def get(path):
        """
        Retrieve a reference's values based on the given path
        """
        return StateManagerReference.frame.get(path)._reference.values()

    @staticmethod
    def get_dict(path):
        """
        Retrieve a reference dict based on the given path
        """
        return StateManagerReference.frame.get(path)._reference


    @staticmethod
    def get_all(path):
        """
        Get all references of the given CXRNode and its subnodes
        """
        node = StateManagerReference.frame.get(path)
        output = node._reference
        for subnode in node:
            output += StateManagerReference.get_all(str(subnode))
        return output.values()

    @staticmethod
    def get_filepath(path):
        """
        Convert a CXRNode path into a relative filepath
        """
        return StateManagerReference.frame.get(path).path()

    @staticmethod
    def has_path(path):
        """
        Determine if a path points to a valid CXRNode
        """
        return StateManagerReference.frame.has_path(path)

    @staticmethod
    def get_node(path):
        """
        Get the CXRNode located at the given path
        """
        return StateManagerReference.frame.get(path)

    @staticmethod
    def find_by_attribute(path, attr, value):
        """
        Find all StateManagers with attributes matching the given value
        """
        output = []
        for v in StateManagerReference.get(path):
            if attr in v.data:
                if value == v[attr]:
                    output.append(v)
        return output

    @staticmethod
    def find_by_function(path, attr, f):
        """
        Find attributes which return True when evaluated by the given function
        """
        output = []
        for v in StateManagerReference.get(path):
            if attr in v.data:
                if f(v[attr]):
                    output.append(v)
        return output

    @staticmethod
    def save(path, *params):
        """
        Save the reference at the given path
        """
        StateManagerReference.get_node(path).build_filepath()
        for reference in StateManagerReference.get(path):
            reference.save(*params)

    @staticmethod
    def load(path, *params):
        """
        Load all references at the given path
        """
        for reference in StateManagerReference.get(path):
            reference.load(*params)
