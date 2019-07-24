
class RangeCell(object):
    """
    A data object representing a parameter's requirements in a policy.
    Specifically for parameters that are limited to (or excluded from) a given
    range.
    """

    def __init__(self, name: str, lower, upper, rtype: RangeType, invert_flag):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.type = rtype
        self.invert_flag = invert_flag

    def evaluate(self, name_val) -> bool:
        if self.invert_flag:
            return not self._evaluate(name_val)
        else:
            return self._evaluate(name_val)

    def _evaluate(self, name_val) -> bool:
        if self.type == RangeType.OPEN:
            return self.lower < name_val < self.upper
        elif self.type == RangeType.CLOSED:
            return self.lower <= name_val <= self.upper
        elif self.type == RangeType.LOPEN:
            return self.lower < name_val <= self.upper
        else:
            return self.lower <= name_val < self.upper

    def __repr__(self):
        invert_str = '!' if self.invert_flag else ''
        if self.type == RangeType.OPEN:
            return f'<RangeCell: {invert_str} {self.lower} < {self.name} < {self.upper} >'
        elif self.type == RangeType.CLOSED:
            return f'<RangeCell: {invert_str} {self.lower} <= {self.name} <= {self.upper} >'
        elif self.type == RangeType.LOPEN:
            return f'<RangeCell: {invert_str} {self.lower} < {self.name} <= {self.upper} >'
        elif self.type == RangeType.ROPEN:
            return f'<RangeCell: {invert_str} {self.lower} <= {self.name} < {self.upper} >'

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, RangeCell):
            return False
        else:
            return self.name == other.name and                                \
                   self.lower == other.lower and                              \
                   self.upper == other.upper and                              \
                   self.type == other.type and                                \
                   self.invert_flag == other.invert_flag

    def __ne__(self, other):
        return not self.__eq__(other)