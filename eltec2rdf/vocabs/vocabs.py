"""Functionality for vocab lookup."""

import abc
import typing

from importlib.resources import files
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDFS


_vocabs_path = files("eltec2rdf.vocabs")


@typing.runtime_checkable
class SupportsIterdir(typing.Protocol):
    """An ABC with one abstract method 'iterdir'."""

    @abc.abstractmethod
    def iterdir(self):
        """Abstractmethod for iterdir of the Traversable protocol."""
        raise NotImplementedError


def load_vocabs_graph(_path: SupportsIterdir = _vocabs_path) -> Graph:
    """Scan a dir for ttl files and load them in to a Graph."""
    _graph = Graph()

    for f in _vocabs_path.iterdir():
        if f.name.endswith(".ttl"):
            _graph.parse(f)

    return _graph


vocab_graph = load_vocabs_graph()


class VocabLookupException(Exception):
    """Exception for indicating a failed vocab term lookup."""


def vocab(term: str, _graph: Graph = vocab_graph) -> URIRef:
    """Lookup a term in a vocab graph and return the subject URI."""
    _subjects = vocab_graph.subjects(RDFS.label, Literal(term))

    try:
        vocab_uri = next(_subjects)
    except StopIteration:
        raise VocabLookupException(f"No subject URI for term '{term}'.")

    return vocab_uri
