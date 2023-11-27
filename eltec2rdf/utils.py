"""Miscellaneous utilies for eltec2rdf."""

from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def _or(*operands: Callable[..., T],
        args: tuple = (),
        kwargs: dict | None = None
        ) -> T | None:
    """Logical n-ary OR.

    Evaluates a series of callables (operands) with
    args and kwargs and short-circuits on first truthy result.
    """
    kwargs = {} if kwargs is None else kwargs

    for operand in operands:
        if result := operand(*args, **kwargs):
            return result
