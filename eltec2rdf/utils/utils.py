"""Miscellaneous utilies for eltec2rdf."""

import contextlib
import hashlib
import re
import functools

from collections.abc import Callable, Iterator, Sequence
from itertools import repeat
from typing import TypeVar, Optional
from types import SimpleNamespace
from uuid import uuid4

from rdflib import URIRef, Graph, BNode
from lodkit.utils import genhash
from lodkit.types import _Triple, _TripleObject


T = TypeVar("T")
TDefault = TypeVar("TDefault")


def resolve_source_type(source_type: str, join_value=" ") -> str:
    """Resolve source_type data for vocabs lookup.

    Split a camelCase string and join it using join_value.
    """
    resolved = functools.reduce(
        lambda x, y: f"{x.lower()}{join_value}" + y.lower(),
        re.split('(?<=[a-z])(?=[A-Z])', source_type)
    )

    return resolved


def first(seq: Sequence[T],
          default: TDefault | None = None) -> T | TDefault | None:
    """Try to return the first item of a Sequence.

    If index lookup fails, return a default value.
    """
    with contextlib.suppress(Exception):
        return seq[0]
    return default


def trim(string: str) -> str:
    """Remove leading, trailing and generally superfluous whitespace."""
    trimmed = re.sub(r"\s{2,}", " ", string).strip()
    return trimmed


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
    return None


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


def uri_ns(*names: str | tuple[str, str]) -> SimpleNamespace:
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


def get_e39_hash_value(data: list[dict]):
    """Get a hash value for e39 assertions from author IDs.

    Select the first id_value that has an id_type,
    else return the first id_value.
    """
    for element in data:
        if element["id_type"]:
            return element["id_value"]

    return data[0]["id_value"]
