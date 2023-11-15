"""eltec2rdf helpers."""

import functools


def f_or(*args):
    """Functional or."""
    return functools.reduce(lambda x, y: x or y, args)
