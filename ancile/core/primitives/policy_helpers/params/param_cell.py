
class ParamCell(object):
    """
    A simple data object that stores information about a parameter's
    requirements in a policy. Primary use is the evaluate method which checks a
    given input value for the parameter.
    """
    def __init__(self, name: str, operation, value):
        self.name = name
        self.op = operation
        self.value = value

    def evaluate(self, name_val) -> bool:
        """Evaluate the given value against the cell.

        returns name_val op value
        """
        return self.op(name_val, self.value)

    def __repr__(self):
        val_str = str(self.value) if not isinstance(self.value, str) \
                                  else f'"{self.value}"'
        return f'<ParamCell: {self.name} {self.op} {val_str}>'

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, ParamCell):
            return False
        else:
            return self.name == other.name and                                \
                   self.op == other.op and                                    \
                   self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

