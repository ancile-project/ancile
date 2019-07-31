from __future__ import annotations
from abc import ABC, abstractmethod
from ancile.core.primitives.policy_helpers.command import Command
from ancile.core.primitives.policy_helpers.expressions import *


class BaseExpression(ABC):
    """
    An abstract class for all Policy expressions.
    It only has d_step, e_step, and simplify.
    """

    operation = None

    @abstractmethod
    def d_step(self, command: Command) -> BaseExpression:
        pass

    @abstractmethod
    def e_step(self) -> Constants:
        pass

    @abstractmethod
    def simplify(self) -> BaseExpression:
        pass
