"""
Qoid is a simple markup language which helps serialize StateManagers in pygame
"""

import os
import copy
import ast
import re


class QoidError(KeyError):
    __doc__ = "A QoidError is raised for KeyErrors and KeyError-like problems which occur specifically in qoid_test.py."


class QoidParseError(SyntaxError):
    __doc__ = "A QoidParseError is raised for any SyntaxError involving the parsing of a file using Qoid markup."


class Property:
    __doc__ = "A Property is a tag-value pair, where the tag is used to refer to the value given"

    def __init__(self, tag: str = "Property", val=None, parent=None):
        self.tag = str(tag)
        self.val = val
        self.parent = parent

    def __add__(self, other):
        if isinstance(other, Property):
            return Qoid(f"{self.tag} + {other.tag}", [self, other])
        else:
            return NotImplemented

    def __bytes__(self):
        return str.encode(format(self))

    def __deepcopy__(self, memodict=None):
        if isinstance(self.val, (int, str, float, bool, tuple)):
            return Property(self.tag, self.val)
        else:
            return Property(self.tag, copy.deepcopy(self.val))

    def __eq__(self, other):
        if isinstance(other, Property):
            return self.tag == other.tag and self.val == other.val
        return False

    def __format__(self, format_spec=None):
        if self.val is not None:
            val_str = str(self.val)
        else:
            val_str = ""
        if val_str:
            return self.tag + ": " + val_str
        else:
            return self.tag

    def __ge__(self, other):
        return self.tag >= other.tag

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(format(self))

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return 1 if self.val else 0

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Property({self.tag}, {self.val})"

    def __str__(self):
        return format(self)

    def get_parent(self):
        """
        :return: the parent Qoid
        """
        return self.parent

    def set(self, tag=None, val=None):
        """
        Set the Property's tag, value, or both

        :param tag: the new tag for the Property
        :param val: the new value for the Property
        """
        if tag:
            self.tag = tag
        if val:
            self.val = val


class Qoid:
    __doc__ = "A Qoid is a set of Properties. Each Qoid has a tag which functions as a key."

    def __init__(self, tag: str="Qoid", val=None, parent=None):
        self.tag = tag
        self.val = []
        self.parent = parent
        if val:
            if isinstance(val, (Qoid, list)):
                for e in val:
                    if isinstance(e, Property):
                        self.append(e)
                    else:
                        err = [val.index(e), type(e)]
                        raise TypeError(f"Invalid element val[{err[0]}] of type {err[1]}: must contain only Property")
            else:
                raise ValueError(f"Invalid val type {type(val)}: must submit Qoid or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += copy.deepcopy(other)
        return out

    def __bytes__(self):
        return str.encode(str(self))

    def __contains__(self, item):
        if isinstance(item, Property):
            for e in self:
                if item == e:
                    return True
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return True
        return False

    def __deepcopy__(self, memodict=None):
        out = Qoid(self.tag)
        for p in self:
            out += copy.deepcopy(p)
        return out

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        if isinstance(other, Qoid):
            if self.tag != other.tag:
                return False
            elif len(self) != len(other):
                return False

            temp = copy.deepcopy(other.val)

            for each in self:
                if each in temp:
                    temp.pop(temp.index(each))
                else:
                    return False

            if len(temp) == 0:
                return True
        return False

    def __format__(self, format_spec=None):
        out = f"#{self.tag}\n" if len(self.tag) else ""
        for e in self:
            out += format(e) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return Qoid(self.tag, [self.val[i] for i in range(start, stop, step)])
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Property):
            self.append(other)
            return self
        elif isinstance(other, Qoid):
            for e in other:
                self.append(e)
            return self
        elif isinstance(other, list):
            out = self
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible type {type(other)}, must be Property or Qoid")

    def __isub__(self, subtra):
        if isinstance(subtra, Property):
            try:
                self.pop(subtra)
            except QoidError:
                pass
            return self
        elif isinstance(subtra, Qoid):
            for e in subtra:
                if e.val is None:
                    try:
                        self.pop(e.tag)
                    except QoidError:
                        pass
                else:
                    try:
                        self.pop(e)
                    except QoidError:
                        pass
            return self
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Qoid.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        if isinstance(other, Property):
            out = Qoid(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Qoid({self.tag}, {[repr(v) for v in self.val]})"

    def __reversed__(self):
        return Qoid(self.tag, val=list(reversed(self.val)))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Property):
                self.val[key] = value
            else:
                self.val[key] = Property(self.val[key].tag, value)
        elif isinstance(key, str):
            if isinstance(value, Property):
                self.val[self.index(key)] = value
            else:
                self.val[self.index(key)] = Property(key, value)
        else:
            raise TypeError(f"Unsupported type {type(key)} for key in Qoid.__setitem__(self, key, value)")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= copy.deepcopy(other)
        return out

    def __str__(self):
        return format(self)

    def all_of(self, tag: str):
        """
        :param tag: the tag to search for
        :return: a list of all Properties with the given tag
        """
        out = []
        for e in self:
            if e.tag == tag:
                out.append(e)
        return out

    def append(self, item: Property):
        """
        Add a Property to the Qoid

        :param item: the item to add
        """
        item.parent = self
        self.val.append(item)

    def count(self, tag):
        """
        Counts the number of times the given tag appears

        :param tag: the tag to count
        :return: the number of times tag appears
        """
        c = 0
        for e in self:
            c += 1 if e.tag == tag else 0
        return c

    def extend(self, val: iter):
        """
        Add all the Properties given to the Qoid

        :param val: the Properties to add
        """
        for e in self:
            if not isinstance(e, Property):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Property is allowed")
        self.val.extend(val)

    def get(self, tag: str = None, n=-1):
        """
        Get the value of the first Property which matches the given tag,
        or the complete Property at the given index.

        :param tag: the tag to search for
        :param n: the index to select
        :return: the first Property with the given tag; at the given index; or the set of Properties
        """
        if tag:
            tag = str(tag)
            self_tags = self.tags()
            if tag in self_tags:
                return self.val[self_tags.index(tag)].val
            raise QoidError(f"'{tag}'")
        else:
            return self.val[n]

    def get_parent(self):
        """
        :return: the Bill in which this Qoid is contained
        """
        return self.parent

    def index(self, item):
        """
        Get the first index of a Property with the given tag

        :param item: the Property or tag to search for
        :return: the first index of the Property or tag
        """
        if isinstance(item, Property):
            for e in self:
                if item == e:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        else:
            raise TypeError(f"Invalid type {type(item)}, must use Property or str")

    def insert(self, index, obj):
        """
        Add a set of Properties starting from the given index

        :param index: the location in the Qoid to start
        :param obj: the object to be inserted
        """
        if isinstance(index, int):
            if isinstance(obj, Property):
                self.val = self[:index] + [obj] + self[index:]
            elif isinstance(obj, Qoid):
                self.val = self[:index] + obj.val + self[index:]
            else:
                raise TypeError(f"Unsupported type '{type(obj)}' for argument 'obj', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}' for argument 'index', must be 'int'")

    def pop(self, this=None):
        """
        Remove either the property at the given index, with the given tag,
        or which matches the property given

        :param this: the index, tag, or Property to pop
        :return: the popped Property
        """
        if not this:
            return self.val.pop()
        elif isinstance(this, int):
            if len(self) > this >= 0:
                return self.val.pop(this)
            else:
                raise IndexError("Qoid index out of range")
        elif isinstance(this, str):
            for e in self:
                if e.tag == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this}'")
        elif isinstance(this, Property):
            for e in self:
                if e == this:
                    return self.val.pop(self.val.index(e))
            raise QoidError(f"'{this}'")
        else:
            raise TypeError(f"Unsupported type {type(this)}, must be int, str, or Property")

    def reverse(self):
        """
        Reverse the order of the Properties in the Qoid
        """
        self.val = list(reversed(self.val))

    def set(self, tag=None, index=-1, val=None):
        """
        Set the first Property which matches the given tag, or at the given index.
        If no argument is specified, returns all contents.

        :param tag: the tag to be set
        :param index: the index of the Property to be set
        :param val: the value of the Property to set
        """
        if tag:
            tag = str(tag)
            for e in self:
                if e.tag == tag:
                    e.set(tag, val)
                    return
            raise QoidError(f"'{tag}'")
        else:
            if len(self) > index >= 0:
                self.val[index].set(val=val)
                return
            raise IndexError("Qoid index out of range")

    def tags(self):
        """
        Get the set of all tags in this Qoid
        :return: a list of tags
        """
        return [e.tag for e in self]

    def update_parent(self):
        """
        Ensures all Properties in this Qoid have itself as parent
        """
        for e in self:
            e.parent = self

    def vals(self):
        """
        :return: the set of all values in this Qoid
        """
        return [e.val if e.val else "" for e in self]

    @staticmethod
    def from_dict(d, key):
        output = Qoid(key)

        for k, v in d.items():
            output += Property(k, v)

        return output


class Bill:
    __doc__ = "A Bill is a Qoid whose elements are Qoids."

    def __init__(self, tag: str = "Bill", val=None, parent=None, path=None):
        self.tag = str(tag)
        self.val = []
        self.path = path
        self.parent = parent
        if val:
            if isinstance(val, (Bill, list)):
                for e in val:
                    if isinstance(e, Qoid):
                        self.append(e)
                    else:
                        raise ValueError(f"Invalid val type {type(e)}, must be Qoid")
            else:
                raise ValueError(f"Invalid val type {type(val)}, must submit Bill or list")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += copy.deepcopy(other)
        return out

    def __bytes__(self):
        return str.encode(str(self))

    def __contains__(self, item):
        if isinstance(item, Qoid):
            for e in self:
                if item == e:
                    return True
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return True
        return False

    def __deepcopy__(self, memodict=None):
        out = Bill(self.tag)
        for q in self:
            out += copy.deepcopy(q)
        return out

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        if isinstance(other, Bill):
            if self.tag != other.tag:
                return False
            elif len(self) != len(other):
                return False

            # Due to the way __contains__ works, this is necessary
            temp = copy.deepcopy(other.val)

            for each in self:
                if each in temp:
                    temp.pop(temp.index(each))
                else:
                    return False

            if len(temp) == 0:
                return True
        return False

    def __format__(self, format_spec=None):
        out = ""
        for e in self:
            out += format(e) + "\n"
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return Bill(tag=self.tag, val=[self.val[i] for i in range(start, stop, step)])
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Qoid):
            self.append(other)
            return self
        elif isinstance(other, Bill):
            for e in other:
                self.append(e)
            return self
        elif isinstance(other, list):
            out = self
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible operands Bill and {type(other)}")

    def __isub__(self, subtra):
        if isinstance(subtra, Qoid):
            self.pop(self.index(subtra))
            return self
        elif isinstance(subtra, Bill):
            for e in subtra:
                if e.val is None:
                    try:
                        self.pop(self.index(e.tag))
                    except QoidError:
                        pass
                else:
                    try:
                        self.pop(self.index(e))
                    except QoidError:
                        pass
            return self
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Bill.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        if isinstance(other, Qoid):
            out = Bill(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Bill({self.tag}, {self.val})"

    def __reversed__(self):
        return Bill(self.tag, val=list(reversed(self.val)))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Qoid):
                self.val[key] = value
            else:
                raise ValueError(f"Unsupported type {type(value)} for 'value in Qoid.__setitem__(self, key, value); must be Qoid")
        elif isinstance(key, str):
            if isinstance(value, Qoid):
                self.val[self.index(key)] = value
            else:
                raise ValueError(f"Unsupported type {type(value)} for 'value in Qoid.__setitem__(self, key, value); must be Qoid")
        else:
            raise TypeError(f"Unsupported type {type(key)} for 'key' in Qoid.__setitem__(self, key, value); must be int or str")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= copy.deepcopy(other)
        return out

    def __str__(self):
        return format(self)

    def all_of(self, tag: str):
        """
        :param tag: the tag to search for
        :return: a list of all Qoids with the given tag
        """
        out = []
        for e in self:
            if e.tag == tag:
                out.append(e)
        return out

    def append(self, item: Qoid):
        """
        Add the given Qoid to the Bill.

        :param item: the Qoid to be appended
        """
        item.parent = self
        self.val.append(item)

    def count(self, tag: str):
        """
        Count the number of occurrences of the given tag

        :param tag: the tag to be matched
        :return: the number of times the tag appears
        """
        c = 0
        for e in self:
            c += 1 if e.tag == tag else 0
        return c

    def extend(self, val: iter):
        """
        Extend the contents of the Bill with the given values

        :param val: the set to extend with
        """
        for e in val:
            if not isinstance(e, Qoid):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Register or Bill is allowed")
        self.val.extend(val)

    def get(self, tag=None, n=-1):
        """
        Get all Qoids which match the given tag.
        If no argument is specified, returns all contents.

        :param tag: the tag to match
        :param n: the index to get; -1 means return all
        """
        if tag:
            tag = str(tag)
            self_tags = self.tags()
            if tag in self_tags:
                return self.val[self_tags.index(tag)]
            else:
                raise QoidError(f"'{tag}'")
        else:
            return self.val[n]

    def get_parent(self):
        """
        :return: the parent to this Bill
        """
        return self.parent

    def index(self, item):
        """
        Get the first index of a Qoid with the given tag

        :param item: the tag to be matched
        :return: the first index of a Qoid with the given tag
        """
        if isinstance(item, Qoid):
            if item in self:
                return self.val.index(item)
            raise QoidError(f"'{item}'")
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        else:
            raise TypeError(f"Invalid type {type(item)}, must use Qoid or str")

    def insert(self, index, obj):
        """
        Place the given Qoid or Bill's contents at the given index

        :param index: the index to place the contents
        :param obj: the contents to be placed
        """
        if isinstance(index, int):
            if isinstance(obj, Qoid):
                self.val = self[:index].val + [obj] + self[index:].val
            elif isinstance(obj, Bill):
                self.val = self[:index].val + obj.val + self[index:].val
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Qoid' or 'Bill'")
        else:
            raise TypeError(f"Unsupported type '{type(index)}', must be 'int'")

    @staticmethod
    def open(source_file: str):
        """
        Read and parse a .cxr or .json file

        :param source_file: the file to be parsed
        :return: an Bill constructed out of the source file
        """
        source_file = source_file.replace("/", "\\")
        if os.path.isfile(source_file):
            with open(source_file, "r", encoding="utf-8") as f:
                if source_file.endswith(".cxr") or source_file.endswith(".meta"):
                    content = [l.replace("\n", "") for l in f.readlines()]
                    spl = source_file.split("\\")
                    tag = spl[-1]
                    tag = tag.replace(".cxr", "")
                    out = Bill.parse(content, tag=tag)
                    out.source = source_file
                    out.path = "\\".join(spl[:-1])
                    return out
                else:
                    raise TypeError(f"Invalid file type; must be .cxr or .meta")
        else:
            raise FileNotFoundError(f"Invalid source specified: {source_file}")

    def path_priority(self):
        """
        :return: the local path to which the file will save
        """
        if self.path and not self.parent:
            p = self.path + "\\"
        else:
            p = ""
        if self.tag == ".meta":
            return p + self.tag
        else:
            return p + self.tag + (".cxr" if not self.tag.endswith(".cxr") else "")

    def create_path(self):
        """
        :return: a file path for saving the given Bill
        """
        p = self.path_priority()
        if self.parent:
            out = self.parent.create_path()
            return os.path.join(out, p)
        else:
            return p

    @staticmethod
    def parse(source, tag: str = "Bill"):
        """
        Parse the contents of a file into a Bill

        :param source: the contents to be parsed
        :param tag: the tag value to give the parsed Bill
        :return: the parsed Bill
        """
        if isinstance(source, list):
            re_float = re.compile("^[+-]?\ *(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
            spool = None
            state = 0
            val = []
            for x in range(len(source)):
                if state == 0:
                    if not source[x]:
                        pass
                    elif source[x][0] == '#':
                        spool = Qoid(source[x][1:])
                        state = 1
                else:
                    if not source[x]:
                        val.append(spool)
                        spool = None
                        state = 0
                    elif source[x][0] == "/":
                        pass
                    else:
                        s = source[x].split(':', 1)
                        s = [item.strip() for item in s]

                        p_val = None
                        if len(s) > 1:
                            if s[1] == "True":
                                p_val = True
                            elif s[1] == "False":
                                p_val = False
                            elif ("{" in s[1] and "}" in s[1]) or ("[" in s[1] and "]" in s[1]) or ("(" in s[1] and ")" in s[1]):
                                p_val = ast.literal_eval(s[1])
                            elif s[1].isnumeric():
                                p_val = int(s[1])
                            elif "." in s[1]:
                                try:
                                    m = re_float.match(s[1])
                                    p_val = float(m.group(0))
                                except Exception as exc:
                                    p_val = s[1]
                            else:
                                p_val = s[1]

                        p = Property(s[0], p_val)
                        spool += p
            if spool is not None:
                val.append(spool)
            return Bill(tag=tag, val=val)
        elif isinstance(source, dict):
            qoids = []
            for key, value in source.items():
                # Step 1: ensure the tag is a string, and value is a 2-length list
                if isinstance(key, str) and isinstance(value, list) and len(value) == 2:
                    t = value[0]
                    v = value[1]
                    # Step 2: ensure both value elements are lists
                    if isinstance(t, list) and isinstance(v, list) and len(t) == len(v):
                        # Step 3: ensure all elements are strings
                        for e in t:
                            if not isinstance(e, str):
                                raise QoidParseError("Invalid JSON format: tags contain non-string")
                        for e in v:
                            if not isinstance(e, str):
                                raise QoidParseError("Invalid JSON format: vals contain non-string")
                        # Step 4: create qoid
                        properties = []
                        for k in range(len(t)):
                            properties.append(Property(tag=t[k], val=v[k]))
                        q = Qoid(key, val=properties)
                        qoids.append(q)
                    else:
                        raise QoidParseError("Invalid JSON format: value is not tag-value lists")
                else:
                    raise QoidParseError("Invalid JSON format: json item is not a tag-value pair")
            return Bill(tag=tag, val=qoids)
        else:
            raise TypeError(f"Illegal source of type {type(source)}: must be list or dict")

    def pop(self, index=-1):
        """
        Remove the Qoid at the given index

        :param index: the index to remove
        :return: the Qoid popped from the Bill
        """
        return self.val.pop(index)

    def reverse(self):
        """
        Reverse the value set of the Bill
        """
        self.val = list(reversed(self.val))

    def save(self, echo=True):
        """
        Save

        :param echo: decides whether to display debug information
        """
        with open(self.create_path(), 'w+', encoding="utf-8") as out:
            out.write(format(self))
        if echo:
            print(f"Bill {self.tag} saved to {self.create_path()}")

    def tags(self):
        """
        :return: the set of all tags in this Bill
        """
        return [e.tag for e in self]

    def update_parent(self):
        """
        Ensure that each member of the Bill is properly parented
        """
        for e in self:
            e.parent = self
            e.update_parent()

    def vals(self):
        """
        :return: the set of values in the Bill
        """
        return [e.val for e in self]


class Register:
    __doc__ = "A Register is a Qoid whose elements are all Bills or other Registers"

    def __init__(self, tag: str = "Register", val=None, parent=None, meta=None, path=None):
        self.tag = tag[:-4] if tag.endswith(".cxr") else tag
        self.val = []
        self.path = path
        if self.path and not self.path.endswith("\\"):
            self.path += "\\"
        self.parent = parent
        self.meta = meta if meta else Bill(".meta", parent=self)
        if val:
            if isinstance(val, (list, tuple)):
                for e in val:
                    if isinstance(e, (Register, Bill)):
                        self.append(e)
                    else:
                        raise ValueError(f"Invalid val type {type(e)} in {type(val)}, must be Bill or Register")
            elif isinstance(val, (Bill, Register)):
                self.append(val)
            else:
                raise ValueError(f"Invalid val type {type(val)}, must be list, tuple, Bill, or Register")

    def __add__(self, other):
        out = copy.deepcopy(self)
        out += copy.deepcopy(other)
        return out

    def __bytes__(self):
        return str.encode(format(self))

    def __contains__(self, item):
        if isinstance(item, (Register, Bill)):
            for e in self:
                if item == e:
                    return True
            if item == self.meta:
                return True
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return True
        return False

    def __deepcopy__(self, memodict=None):
        out = Register(self.tag, meta=copy.deepcopy(self.meta))
        for br in self:
            out += copy.deepcopy(br)
        return out

    def __delitem__(self, key):
        if isinstance(key, int):
            del self.val[key]
        elif isinstance(key, str):
            del self.val[self.index(key)]
        else:
            raise ValueError(f"Invalid type {type(key)}, must use int or str")

    def __eq__(self, other):
        if isinstance(other, Register):
            if self.tag != other.tag:
                return False
            elif len(self) != len(other):
                return False
            elif self.meta != other.meta:
                return False

            temp = copy.deepcopy(other.val)

            for each in self:
                if each in temp:
                    temp.pop(temp.index(each))
                else:
                    return False

            if len(temp) == 0:
                return True
        return False

    def __format__(self, format_spec=None):
        out = ""
        for e in self:
            out += f"/ {e.tag}\n\n"
            out += format(e)
        return out

    def __ge__(self, other):
        return self.tag >= other.tag

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start if item.start else 0
            stop = item.stop if item.stop else len(self)
            step = item.step if item.step else 1
            return Register(self.tag, [self.val[i] for i in range(start, stop, step)])
        elif isinstance(item, int):
            return self.get(n=item)
        elif isinstance(item, str):
            return self.get(tag=item)
        else:
            raise ValueError(f"Invalid type {type(item)}, must use slice, int, or str")

    def __gt__(self, other):
        return self.tag > other.tag

    def __hash__(self):
        return hash(str(self))

    def __iadd__(self, other):
        if isinstance(other, Bill):
            if other.tag in self:
                raise ValueError(f"Bill {other.tag} already exists within the Register {self.tag}")
            else:
                self.append(other)
                return self
        elif isinstance(other, Register):
            if other.tag in self:
                raise ValueError(f"Register {other.tag} already exists within the Register {self.tag}")
            else:
                self.append(other)
                return self
        elif isinstance(other, list):
            out = self
            for e in other:
                out += e
            return out
        else:
            raise ValueError(f"Incompatible operands {type(self)} and {type(other)}")

    """Subtraction removes the subtrahend from the minuend if it exists"""
    def __isub__(self, subtra):
        if isinstance(subtra, Bill):
            try:
                self.pop(self.index(subtra.tag))
            except QoidError:
                pass
            return self
        elif isinstance(subtra, Register):
            try:
                self.pop(self.index(subtra))
            except QoidError:
                pass
            return self
        elif isinstance(subtra, list):
            out = self
            for e in subtra:
                out -= e
            return out
        else:
            raise TypeError(f"Unsupported type {type(subtra)} for subtrahend in Register.__isub__(self, subtra)")

    def __iter__(self):
        return iter(self.val)

    def __le__(self, other):
        return self.tag <= other.tag

    def __len__(self):
        return len(self.val)

    def __lt__(self, other):
        return self.tag < other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        if isinstance(other, Bill):
            out = Register(self.tag, [other])
            out += self
            return out
        else:
            return NotImplemented

    def __repr__(self):
        return f"Register({self.tag}, {self.val})"

    def __reversed__(self):
        return Register(self.tag, val=reversed(self.val))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, (Bill, Register)):
                self.val[key] = value
            else:
                raise TypeError(f"Unsupported type {type(value)}; must be Bill or Register")
        elif isinstance(key, str):
            if isinstance(value, (Bill, Register)):
                self.val[self.index(key)] = value
            else:
                raise TypeError(f"Unsupported type {type(value)}; must be Bill or Register")
        else:
            raise TypeError(f"Unsupported type {type(key)} for 'key' in Qoid.__setitem__(self, key, value)")

    def __sub__(self, other):
        out = copy.deepcopy(self)
        out -= copy.deepcopy(other)
        return out

    def __str__(self):
        return format(self)

    def append(self, item):
        """
        Append the given Register or Bill to the Register

        :param item: the Register or Bill to be added
        """
        if isinstance(item, (Register, Bill)):
            if item.tag not in self:
                item.parent = self
                self.val.append(item)
            else:
                raise KeyError(f"Bill or Register with tag {item.tag} already exists in Register {self.tag}")
        else:
            raise ValueError(f"Can only append Register and Bill, not {type(item)}")

    def path_priority(self):
        """
        :return: the constructed path
        """
        filename = self.tag + (".cxr" if not self.tag.endswith(".cxr") else "")

        if self.path and not self.parent:
            return self.path + "\\" + filename
        else:
            return filename

    def create_path(self):
        """
        :return: the local path
        """
        p = self.path_priority()
        if self.parent:
            out = self.parent.create_path()
            return os.path.join(out, p)
        else:
            return p

    def extend(self, val: iter):
        """
        Extend the contents of the Register with the given value

        :param val: the set to extend with
        """
        for e in val:
            if not isinstance(e, (Register, Bill)):
                raise TypeError(f"Unsupported {type(e)} in iterable, only Register or Bill is allowed")
        self.val.extend(val)

    def get(self, tag: str = None, n=-1):
        """
        Get the Register or Bill with the given tag or at the given index
        If no arguments are specified, returns all contents

        :param tag: the tag to match
        :param n: the index to retrieve
        :return: the value at the given tag or index
        """
        if tag:
            tag = str(tag)
            self_tags = self.tags()
            if tag in self_tags:
                return self.val[self_tags.index(tag)]
            else:
                raise QoidError(f"'{tag}'")
        else:
            return self.val[n]

    def get_parent(self):
        """
        :return: the parent for this Register
        """
        return self.parent

    def index(self, item):
        """
        Gives the index of the first occurrence of the item

        :param item: the Bill or Register to match
        :return: the index of the first occurrence of the item
        """
        if isinstance(item, (Register, Bill)):
            for e in self:
                if item == e:
                    return self.val.index(e)
            raise QoidError(f"'{item}'")
        elif isinstance(item, str):
            for e in self:
                if item == e.tag:
                    return self.val.index(e)
            raise QoidError(f"'{format(item)}'")
        else:
            raise TypeError(f"Invalid type {type(item)}, must use Property or str")

    def insert(self, index, obj):
        """
        Insert the given Bill or Register at the given index

        :param index: the index to insert at
        :param obj: the Bill or Register to insert
        """
        if isinstance(index, int):
            if isinstance(obj, Bill):
                self.val = self[:index].val + [obj] + self[index:].val
            elif isinstance(obj, Register):
                self.val = self[:index].val + obj.val + self[index:].val
            else:
                raise TypeError(f"Unsupported type '{type(obj)}', must be 'Property' or 'Qoid'")
        else:
            raise TypeError(f"Unsupported type '{type(obj)}', must be 'int'")

    @staticmethod
    def open(source_folder: str):
        """
        Read and parse a .cxr folder

        :param source_folder:
        :return: the completed Register
        """
        source_folder = source_folder.replace("/", "\\")
        if os.path.isdir(source_folder) and source_folder.endswith(".cxr"):
            spl = source_folder.split("\\")
            out = Register(tag=spl[-1])
            out.path = "\\".join(spl[:-1])
            for e in os.listdir(source_folder):
                try:
                    if e.endswith(".cxr") or e == ".meta":
                        if os.path.isdir(os.path.join(source_folder, e)):
                            i = Register.open(os.path.join(source_folder, e))
                        else:
                            i = Bill.open(os.path.join(source_folder, e))

                    else:
                        raise QoidError("Invalid file type, must be .cxr or .meta")
                    if e == ".meta":
                        out.meta = i
                    else:
                        out += i
                except QoidError:
                    print(f"Ignoring invalid file type at {os.path.join(source_folder, e)}")
            return out
        else:
            raise NotADirectoryError(f"Invalid source specified: {source_folder}")

    def pop(self, index=-1):
        """
        :param index: the index to pop
        :return: the popped value
        """
        return self.val.pop(index)

    def reverse(self):
        """
        Reverse the order of the values in the Register
        """
        self.val = list(reversed(self.val))

    def save(self, echo=True, echo_bill=False):
        """
        Save the Register to a .cxr folder

        :param echo: determines whether the save debug message displays
        """
        p = self.create_path()
        if not os.path.isdir(p):
            os.mkdir(p)
        for e in self:
            if isinstance(e, Register):
                p = e.create_path()
                if not os.path.isdir(p):
                    os.mkdir(p)
            e.save(echo=echo if isinstance(e, Register) else echo_bill)
        # self.meta.save(echo)
        if echo:
            print(f"Register {self.tag} saved to {self.create_path()}")

    def tags(self):
        """
        :return: a list of all tags in the Register
        """
        return [e.tag for e in self]

    def update_parent(self):
        """
        Ensures the contents of the Register are properly parented
        """
        for e in self:
            e.parent = self
            e.update_parent()

    def vals(self):
        """
        :return: a list of all lists of values in the Register
        """
        return [e.val for e in self]
