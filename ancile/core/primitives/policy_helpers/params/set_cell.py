



class SetCell(object):
    def __init__(self, name, in_objects, invert):
        self._set = set(in_objects)
        self._name = name
        self._invert_flag = invert

    def evaluate(self, name_val) -> bool:
        """Evaluate the given value against the cell.

        returns name_val op value
        """
        if not self._invert_flag:
            return name_val in self._set
        else:
            return name_val not in self._set

    def __repr__(self):
        inv_str = ' ' if not self._invert_flag else ' not '
        return f'<? SetCell: {self._name}{inv_str}in {self._set} ?>'

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, SetCell):
            return False
        else:
            return self._name == other._name and                              \
                   self._invert_flag == other._invert_flag and                \
                   self._set == other._set

    def __ne__(self, other):
        return not self.__eq__(other)