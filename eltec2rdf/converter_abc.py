"""ABC and base model for CLSCor RDF generator."""

import abc

from collections.abc import Iterator
from typing import Any

from pydantic import BaseModel, ConfigDict
from lodkit.types import _Triple

from rdflib import Graph as RDFLibGraph


class BindingsModel(BaseModel):
    """BindingsValidator for basic CLSCor bindings."""

    model_config = ConfigDict(extra="allow")

    x: int
    y: str
    z: str | None = None


class RDFGenerator(abc.ABC):
    """RDFGenerator ABC."""

    def __init__(self,
                 model: type[BindingsModel] = BindingsModel,
                 graph: RDFLibGraph | None = None,
                 **bindings: Any) -> None:
        """Initialize an RDFGenerator."""
        self.bindings = model(**bindings)

        self._triples = self.generate_triples()
        self._graph = RDFLibGraph() if graph is None else graph

    def to_graph(self):
        """Add triples to an rdflib.Graph instance and return."""
        for triple in self._triples:
            self._graph.add(triple)

        return self._graph()

    @property
    def graph(self):
        """Getter for the rdflib.Graph component.

        For updating (i.e. adding triples to) the Graph component,
        run the RDFGenerator.to_graph method.
        """
        return self._graph

    @abc.abstractmethod
    def generate_triples(self) -> Iterator[_Triple]:
        """Generate an iterator of triples.

        Concrete implementations of the generate_triples method
        typically use bindings from self.bindings for triple construction.
        """
        raise NotImplementedError

    def __iter__(self):
        """Return an iterator object."""
        return self._triples

    def __next__(self):
        """Return the next item from the iterator."""
        return next(self)


class CLSCorGenerator(RDFGenerator):
    """Basisc CLSCor RDF generator."""
