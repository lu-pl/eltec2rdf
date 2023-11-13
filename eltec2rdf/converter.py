"""Functionality for ELTeC to RDF conversion."""

import itertools

from collections.abc import Mapping, Iterator

from eltec2rdf.extractors import ELTeCBindingsExtractor

from lodkit.graph import Graph
from lodkit.types import _Triple
from lodkit.utils import plist

from rdflib import Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS

from clisn import crm, lrm, crmcls


class ELTeCConverter:
    """Converter for RDF generation based on an ELTec resource."""

    def __init__(self, eltec_url: str) -> None:
        """Initialize an ELTeCConverter instance."""
        self._eltec_url = eltec_url
        self._graph = Graph()

        self.bindings = ELTeCBindingsExtractor(self._eltec_url)

    def _get_doc_uris(self) -> Mapping[str, URIRef]:
        """Get URIRefs for the document namespace."""
        _corpus_id, _document_id = map(
            self.bindings.get,
            ("repo_id", "file_stem")
        )
        doc_ns = Namespace(
            f"https://{_corpus_id}.clscor.io/entity/doc/{_document_id}/"
        )

        uris = dict(
            tei=doc_ns["tei"],
            url=doc_ns["url"],
            doc_id=doc_ns["id"],
            f1=doc_ns["work"],
            f2=doc_ns["expression/1"],
            f3=doc_ns["originalSource"],
            f3_e42=doc_ns["originalSource/bibl"],
            f27=doc_ns["work/creation"],
            f28=doc_ns["expression/creation"],
            d1=doc_ns["tei/digitalSource"],
            d1_e41=doc_ns["tei/digitalSource/id/1"]
        )

        return uris

    def _get_actor_uris(self) -> Mapping[str, URIRef]:
        """Get URIRefs for the actor namespace."""
        _corpus_id, _author_gnd_id = map(
            self.bindings.get,
            ("repo_id", "author_gnd_id")
        )

        actor_ns = Namespace(
            f"https://{_corpus_id}.clscor.io/entity/actor/gnd{_author_gnd_id}/"
        )

        uris = dict(
            e39=actor_ns[""],
            e39_e41=actor_ns["id/1"]
        )

        return uris

    def generate_triples(self) -> Iterator[_Triple]:
        """Generate triples from an ELTeC resource.

        Bindings are optained by querying the ELTeC source
        with self._get_bindings.
        """
        doc = self._get_doc_uris()
        actor = self._get_actor_uris()

        _author, _title = map(
            self.bindings.get,
            ("source_author", "source_title")
        )
        short_ref = f"{_author}: {_title}"

        tei_triples = plist(
            doc["tei"],
            (RDF.type, crmcls["X2_Corpus_Document"]),
            (RDFS.label, Literal(f"{short_ref} [TEI Document on Github]")),
            (crm["P1_is_identified_by"], doc["url"]),
            (crm["P1_is_identified_by"], doc["doc_id"]),
            (lrm["R4_embodies"], doc["f2"])
        )

        url_triples = plist(
            doc["url"],
            (RDFS.label, Literal(f"Github URL of '{short_ref}'")),
            (crm["P190_has_symbolic_content"], Literal(self._eltec_url))
        )

        id_triples = plist(
            doc["doc_id"],
            (RDFS.label, Literal(f"ELTeC ID of '{short_ref}'")),
            (
                crm["P2_has_type"],
                Literal("https://eltec.clscor.io/entity/type/id")
            ),
            (
                crm["P190_has_symbolic_content"],
                Literal(self.bindings["file_stem"].upper())
            )
        )

        type_triples = ...

        triples = itertools.chain(
            tei_triples,
            url_triples,
            id_triples
        )

        yield from triples


# adhoc testing
eltec_url = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-deu/master/level1/DEU007.xml"
converter = ELTeCConverter(eltec_url)

x = converter.generate_triples()
g = Graph()

for i in x:
    g.add(i)

print(g.serialize())
