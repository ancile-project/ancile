from __future__ import annotations
from abc import ABC, abstractmethod
from ancile.core.primitives.policy_helpers.expressions import *


class BaseExpression(ABC):

    operation = None

    def __init__(self):
        pass

    def __repr__(self):
        pass

    @abstractmethod
    def d_step(self, command, params=None) -> BaseExpression:
        pass

    @abstractmethod
    def e_step(self) -> Constants:
        pass

    @abstractmethod
    def simplify(self) -> BaseExpression:
        pass
