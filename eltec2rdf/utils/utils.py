"""Miscellaneous utilies for eltec2rdf."""

import hashlib

from collections.abc import Callable, Iterator
from itertools import repeat
from typing import TypeVar, Optional
from types import SimpleNamespace
from uuid import uuid4

from rdflib import URIRef, Graph, BNode
from lodkit.utils import genhash
from lodkit.types import _Triple, _TripleObject


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


def mkuri(
        hash_value: str | None = None,
        length: int | None = 10,
        hash_function: Callable = hashlib.sha256
) -> URIRef:
    """Create a CLSCor entity URI.

    If a hash value is give, the path is generated using
    a hash function, else the path is generated using a uuid4.
    """
    _base_uri: str = "https://clscor.io/entity/"
    _path: str = (
        str(uuid4()) if hash_value is None
        else genhash(
                hash_value,
                length=length,
                hash_function=hash_function
        )
    )

    return URIRef(f"{_base_uri}{_path[:length]}")


# this will be available in lodkit soon!
class ttl:
    """Triple/graph constructor implementing a ttl-like interface."""

    def __init__(self,
                 uri: URIRef,
                 *predicate_object_pairs: tuple[URIRef, _TripleObject | list],
                 graph: Optional[Graph] = None):
        """Initialize a plist object."""
        self.uri = uri
        self.predicate_object_pairs = predicate_object_pairs
        self.graph = Graph() if graph is None else graph
        self._iter = iter(self)

    def __iter__(self) -> Iterator[_Triple]:
        """Generate an iterator of tuple-based triple representations."""
        for pred, obj in self.predicate_object_pairs:
            match obj:
                case list() | Iterator():
                    _b = BNode()
                    yield (self.uri, pred, _b)
                    yield from ttl(_b, *obj)
                case tuple():
                    _object_list = zip(repeat(pred), obj)
                    yield from ttl(self.uri, *_object_list)
                case _:
                    yield (self.uri, pred, obj)

    def __next__(self) -> _Triple:
        """Return the next triple from the iterator."""
        return next(self._iter)

    def to_graph(self) -> Graph:
        """Generate a graph instance."""
        for triple in self:
            self.graph.add(triple)
        return self.graph


class plist(ttl):
    """Deprecated alias to ttl.

    This is for backwards api compatibility only.
    Since ttl also implements Turtle object lists now,
    refering to the class as "plist" is inaccurate/misleading.
    """


def uri_ns(*names: str | tuple[str, str]):
    """Generate a Namespace mapping for names and computed URIs."""
    def _uris():
        for name in names:
            match name:
                case str():
                    yield name, mkuri()
                case tuple():
                    yield name[0], mkuri(name[1])
                case _:
                    raise Exception(
                        "Args must be of type str | tuple[str, str]."
                    )

    return SimpleNamespace(**dict(_uris()))
