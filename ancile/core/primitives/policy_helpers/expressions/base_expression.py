from abc import ABC, abstractmethod


class BaseExpression(ABC):

    operation = None

    def __init__(self):
        pass

    def __repr__(self):
        pass

    @abstractmethod
    def d_step(self):
        pass

    @abstractmethod
    def e_step(self):
        pass

    @abstractmethod
    def simplify(self):
        pass
