from enum import Enum


class Constants(Enum):
    """
    ZERO - no-operation
    ONE (ZERO*) - empty string

    We use boolean values to represent them in order to
    understand if the policy has finished, e.g. resulted to ONE.
    Therefore, we treat ONE as True and ZERO as False.

    """
    ONE = True
    ZERO = False

    def __add__(self, other):
        """
        Logical OR operation
        """

        return Constants(self.value or other.value)

    def __mul__(self, other):
        """
        Logical AND operation
        """

        return Constants(self.value and other.value)

    def __neg__(self):
        """
        Logical NOT operation
        """

        return Constants(not self.value)

    def __str__(self):
        if self.value:
            return "1"
        else:
            return "0"
