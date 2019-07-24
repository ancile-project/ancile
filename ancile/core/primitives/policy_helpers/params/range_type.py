from enum import Enum


class RangeType(Enum):
    OPEN = 1     # (a,b)
    CLOSED = 2   # [a,b]
    LOPEN = 3    # (a,b]
    ROPEN = 4    # [a,b)
