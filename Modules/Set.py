# This module encapsulates some basic operations on sets

class Unique_set:
    """
    Unique_set: the elements in a set are distinct.

    Attributes:
        elements (list): 
    """

    def __init__(self, elements):
        self.elements = self._simplify(elements)

    def _simplify(self, elements):
        """Simplify elements for Unique_set (remove duplicates)."""
        seen = set()
        res = []
        for item in elements:
            if item not in seen:
                seen.add(item)
                res.append(item)
        return res

    def _elements_dict(self):
        """Convert elements to dictionary representation."""
        return {item: 1 for item in self.elements}

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, item):
        return item in self.elements

    def __len__(self):
        return len(self.elements)

    def clear(self):
        self.elements = []

    def __sub__(self, other):
        """Difference: elements in self but not in other."""
        # Convert other to proper representation
        other_dict = other._elements_dict() if isinstance(other, Unique_set) else {}

        res = []
        for item in self:
            if item not in other_dict:
                res.append(item)
        return self.__class__(res)

    def __and__(self, other):
        """Intersection: elements in both self and other."""
        other_dict = other._elements_dict() if isinstance(other, Unique_set) else {}

        res = []
        for item in self:
            if item in other_dict:
                res.append(item)
        return self.__class__(res)

    def __or__(self, other):
        """Union: elements in either self or other."""
        # Start with current elements
        res_dict = {}
        for item in self:
            res_dict[item] = 1

        # Add elements from other
        for item in other:
            res_dict[item] = 1

        # Convert back to list representation
        return self.__class__(list(res_dict.keys()))

    def __xor__(self, other):
        """Symmetric difference: elements in either self or other but not both."""
        diff1 = self - other
        diff2 = other - self
        return diff1 | diff2

    # Subsets
    def is_subset(self, other):
        other_dict = other._elements_dict() if isinstance(other, Unique_set) else {}
        return len(self) <= len(other_dict) and all(item in other_dict for item in self)

    def is_superset(self, other):
        return other.is_subset(self)

    # Judge equivalence
    def __eq__(self, other):
        if not isinstance(other, Unique_set):
            return False
        return self.is_subset(other) and self.is_superset(other)

    def __ne__(self, other):
        return not self == other

    # Display
    def __str__(self):
        """String representation of the set."""
        if len(self.elements) == 0:
            return "EmptySet"
        # Try to sort if all elements are comparable
        try:
            sorted_elements = sorted(self.elements)
            return f"{{{', '.join(str(x) for x in sorted_elements)}}}"
        except TypeError:
            # If sorting fails, display as is
            return f"{{{', '.join(str(x) for x in self.elements)}}}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.elements})"


class Generalized_set(Unique_set):
    """
    Generalized set that allows repeated elements (with counts).
    
    Attributes:
        elements (dict): 
    """

    def __init__(self, elements):
        # elements can be dict or list/iterable
        if isinstance(elements, dict):
            self.elements = self._simplify(elements)
        else:
            # Convert list to dict with counts
            element_dict = {}
            for item in elements:
                element_dict[item] = element_dict.get(item, 0) + 1
            self.elements = self._simplify(element_dict)

    def _simplify(self, elements):
        """Simplify elements for Generalized_set (remove zero-count items)."""
        if isinstance(elements, dict):
            return {k: v for k, v in elements.items() if v > 0}
        else:
            # For list input, count occurrences
            element_dict = {}
            for item in elements:
                element_dict[item] = element_dict.get(item, 0) + 1
            return {k: v for k, v in element_dict.items() if v > 0}

    def _elements_dict(self):
        """Return the dictionary representation directly."""
        return self.elements.copy()

    def __iter__(self):
        """Iterate over elements with repetitions."""
        for item, count in self.elements.items():
            for _ in range(count):
                yield item

    def __contains__(self, item):
        return item in self.elements

    def __len__(self):
        """Total count of all elements (including repetitions)."""
        return sum(self.elements.values())

    def unique_len(self):
        """Number of unique elements."""
        return len(self.elements)

    def clear(self):
        self.elements = {}

    def __sub__(self, other):
        """Difference with count subtraction."""
        # Convert other to proper representation
        if isinstance(other, Generalized_set):
            other_dict = other.elements
        elif isinstance(other, Unique_set):
            other_dict = other._elements_dict()
        else:
            other_dict = {}

        res = {}
        for item, count in self.elements.items():
            other_count = other_dict.get(item, 0)
            new_count = count - other_count
            if new_count > 0:
                res[item] = new_count

        return Generalized_set(res)

    def __and__(self, other):
        """Intersection with min counts."""
        if isinstance(other, Generalized_set):
            other_dict = other.elements
        elif isinstance(other, Unique_set):
            other_dict = other._elements_dict()
        else:
            other_dict = {}

        res = {}
        for item, count in self.elements.items():
            if item in other_dict:
                res[item] = min(count, other_dict[item])

        return Generalized_set(res)

    def __or__(self, other):
        """Union with max counts."""
        if isinstance(other, Generalized_set):
            other_dict = other.elements
        elif isinstance(other, Unique_set):
            other_dict = other._elements_dict()
        else:
            other_dict = {}

        res = {}
        # Add self elements
        for item, count in self.elements.items():
            res[item] = count

        # Add other elements (taking max count)
        for item, count in other_dict.items():
            if item in res:
                res[item] = max(res[item], count)
            else:
                res[item] = count

        return Generalized_set(res)

    def __add__(self, other):
        """Addition: sum of counts."""
        if isinstance(other, Generalized_set):
            other_dict = other.elements
        elif isinstance(other, Unique_set):
            other_dict = other._elements_dict()
        else:
            other_dict = {}

        res = {}
        # Add self elements
        for item, count in self.elements.items():
            res[item] = count

        # Add other elements (sum counts)
        for item, count in other_dict.items():
            if item in res:
                res[item] += count
            else:
                res[item] = count

        return Generalized_set(res)

    def __xor__(self, other):
        diff1 = self - other
        diff2 = other - self
        return diff1 | diff2

    def is_subset(self, other):
        """Check if self is subset of other (considering counts)."""
        if isinstance(other, Generalized_set):
            other_dict = other.elements
        elif isinstance(other, Unique_set):
            other_dict = other._elements_dict()
        else:
            return False

        for item, count in self.elements.items():
            if item not in other_dict or other_dict[item] < count:
                return False
        return True

    def __str__(self):
        if len(self.elements) == 0:
            return "EmptySet"
        try:
            sorted_keys = sorted(self.elements.keys())
            items = []
            for key in sorted_keys:
                items.append(f"{key}: {self.elements[key]}")
            return f"{{{', '.join(items)}}}"
        except TypeError:
            items = [f"{k}: {v}" for k, v in self.elements.items()]
            return f"{{{', '.join(items)}}}"


# Helper functions
def inter_sets(*args):
    """Intersection of multiple sets."""
    if len(args) < 2:
        raise ValueError("There must be at least 2 sets to operate.")

    for arg in args:
        if not isinstance(arg, (Unique_set, Generalized_set)):
            raise TypeError("Argument must be a set.")

    # Start with first set
    res = args[0]
    # Intersect with all other sets
    for arg in args[1:]:
        res &= arg
    return res


def combine_sets(*args):
    """Union of multiple sets."""
    if len(args) < 2:
        raise ValueError("There must be at least 2 sets to operate.")

    for arg in args:
        if not isinstance(arg, (Unique_set, Generalized_set)):
            raise TypeError("Argument must be a set.")

    # Start with first set
    res = args[0]
    # Union with all other sets
    for arg in args[1:]:
        res |= arg
    return res


def to_generalized_set(obj):
    """Convert any compatible object to Generalized_set."""
    if isinstance(obj, Generalized_set):
        return obj
    elif isinstance(obj, Unique_set):
        element_dict = {}
        for item in obj:
            element_dict[item] = 1
        return Generalized_set(element_dict)
    elif isinstance(obj, dict):
        return Generalized_set(obj)
    elif hasattr(obj, '__iter__'):
        # Convert any iterable
        element_dict = {}
        for item in obj:
            element_dict[item] = element_dict.get(item, 0) + 1
        return Generalized_set(element_dict)
    else:
        raise TypeError(f"Cannot convert {type(obj)} to Generalized_set")


# Example usage
if __name__ == "__main__":
    # Test Unique_set
    u1 = Unique_set([1, 2, 3, 2, 1])
    print(f"Unique_set 1: {u1}")

    u2 = Unique_set([2, 3, 4])
    print(f"Unique_set 2: {u2}")

    print(f"Union: {u1 | u2}")
    print(f"Intersection: {u1 & u2}")
    print(f"Difference: {u1 - u2}")

    # Test Generalized_set
    g1 = Generalized_set([1, 1, 2, 3, 3, 3])
    print(f"\nGeneralized_set 1: {g1}")

    g2 = Generalized_set({2: 2, 3: 1, 4: 2})
    print(f"Generalized_set 2: {g2}")

    print(f"Union: {g1 | g2}")
    print(f"Intersection: {g1 & g2}")
    print(f"Difference: {g1 - g2}")
    print(f"Addition: {g1 + g2}")

    # Test inheritance
    print(f"\nIs g1 a Unique_set? {isinstance(g1, Unique_set)}")
    print(f"Is u1 a Generalized_set? {isinstance(u1, Generalized_set)}")
