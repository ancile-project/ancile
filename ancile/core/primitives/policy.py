from __future__ import annotations
from copy import deepcopy
from ancile.core.primitives.policy_helpers.expressions.special.command import Command
from ancile.core.primitives.policy_helpers.policy_parser import PolicyParser
from ancile.core.primitives.policy_helpers.expressions import *


class Policy(object):
    _policy_expr: BaseExpression

    def __init__(self, initial_policy):
        if isinstance(initial_policy, str):
            self._policy_expr = PolicyParser.parse_it(initial_policy)
        elif isinstance(initial_policy, list):
            self._policy_expr = IntersectExpression.assemble_from_list((PolicyParser.parse_it(pol) for pol in initial_policy))
        elif isinstance(initial_policy, BaseExpression):
            self._policy_expr = deepcopy(initial_policy)
        elif isinstance(initial_policy, Policy):
            self._policy_expr = deepcopy(initial_policy._policy_expr)
        else:
            raise ValueError(f'You need to supply either a string or object of '
                             f'class BaseExpression. '
                             f'Supplied: {type(initial_policy)}')

    def __bool__(self):
        """
        Check that the policy is not 0 (noop)

        """
        self._policy_expr = self._policy_expr.simplify()
        if isinstance(self._policy_expr, ConstantExpression) \
                and self._policy_expr.command is Constants.ZERO:
            return False
        else:
            return True

    def __repr__(self):
        return f'<? POLICY : {self._policy_expr} ?>'

    def advance_policy(self, command: Command, update=True):
        """
        Takes a derivative of the current policy expression using D-step

        """
        new_policy_expr = self._policy_expr.d_step(command).simplify()
        if update:
            self._policy_expr = new_policy_expr

        return new_policy_expr

    def check_finished(self):
        """
        Takes an E-step of the resulting expression. If E-step returns One
        then the policy has succeeded, otherwise the policy check has failed.
        :return:
        """
        result = self._policy_expr.e_step()
        if result is Constants.ONE:
            return True
        else:
            return False

    def concat(self, p: Policy) -> Policy:
        policy_expr = ConcatExpression(self._policy_expr, p._policy_expr).simplify()
        return Policy(policy_expr)

    def intersect(self, p: Policy) -> Policy:
        policy_expr = IntersectExpression(self._policy_expr, p._policy_expr).simplify()
        return Policy(policy_expr)

    def union(self, p: Policy) -> Policy:
        policy_expr = UnionExpression(self._policy_expr, p._policy_expr).simplify()
        return Policy(policy_expr)
