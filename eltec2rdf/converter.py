"""Functionality for ELTeC to RDF conversion."""

import itertools

from collections.abc import Mapping, Iterator

from eltec2rdf.extractors import ELTeCBindingsExtractor

from lodkit.graph import Graph
from lodkit.types import _Triple
from lodkit.utils import plist

from rdflib import Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS

from clisn import crm, crmcls, crmdig, lrm, CLSInfraNamespaceManager


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
        """Generate triples from an ELTeC resource."""
        # uri collections
        doc = self._get_doc_uris()
        actor = self._get_actor_uris()

        _author, _title, _author_id = map(
            self.bindings.get,
            ("source_author", "source_title", "author_id")
        )

        _sources = self.bindings["other_sources"]
        print_source = next(
            source
            for source in _sources
            if source["type"] == "printSource"
        )["title"]

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
            (RDF.type, crm["E42_Identifier"]),
            (RDFS.label, Literal(f"Github URL of '{short_ref}'")),
            (crm["P190_has_symbolic_content"], Literal(self._eltec_url))
        )

        id_triples = plist(
            doc["doc_id"],
            (RDF.type, crm["E42_Identifier"]),
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

        f1_triples = plist(
            doc["f1"],
            (RDF.type, lrm["F1_Work"]),
            (RDFS.label, Literal(f"{short_ref} [Work]")),
            (lrm["R3_is_realised_in"], doc["f2"])
        )

        f2_triples = plist(
            doc["f2"],
            (RDF.type, lrm["F2_Expression"]),
            (RDFS.label, Literal(f"{short_ref} [Expression]"))
        )

        f3_triples = plist(
            doc["f3"],
            # (RDFS.label, Literal("Edition ...")),
            (RDF.type, lrm["F3_Manifestation"]),
            (crm["P1_is_identified_by"], crm["f3_e42"]),
            (lrm["R4_embodies"], doc["f2"])
        )

        f27_triples = plist(
            doc["f27"],
            (RDF.type, lrm["F27_Work_Creation"]),
            (RDFS.label, Literal(f"Work creation of {short_ref}")),
            (crm["P14_carried_out_by"], actor["e39"]),
            (lrm["R16_created"], doc["f1"])
        )

        f28_triples = plist(
            doc["f28"],
            (RDF.type, lrm["F28_Expression_Creation"]),
            (RDFS.label, Literal(f"Expression creation of '{short_ref}'")),
            (crm["P14_carried_out_by"], actor["e39"]),
            (lrm["R17_created"], doc["f2"])
        )

        actor_triples = plist(
            actor["e39"],
            (RDF.type, crm["E39_Actor"]),
            (RDFS.label, Literal(f"{_author} [Actor]"))
        )

        actor_gnd_triples = plist(
            actor["e39_e41"],
            (RDF.type, crm["E41_Identifier"]),
            (
                RDFS.label,
                Literal(f"GND ID of '{_author}'")),
            (
                crm["P190_has_symbolic_content"],
                Literal(f"{_author_id}")
            ),
            (
                crm["P2_has_type"],
                URIRef("https://core.clscor.io/entity/type/id/gnd")
            )
        )

        d1_triples = plist(
            doc["d1"],
            (RDF.type, crmdig["D1_Digital_Object"]),
            (RDFS.label, Literal(f"Digital Source of '{short_ref}'")),
            (crm["P1_is_identified_by"], doc["d1_e41"])
        )

        d1_id_triples = plist(
            doc["d1_e41"],
            (RDF.type, crm["E41_Identifier"]),
            (RDFS.label, Literal(f"Textgrid Identifier of '{short_ref}'")),
            (
                crm["P190_has_symbolic_content"],
                Literal(self.bindings["source_ref"])
            ),
            (
                crm["P2_has_type"],
                URIRef("https://core.clscor.io/entity/type/id/textgrid")
            )
        )

        biblref_triples = plist(
            doc["f3_e42"],
            (RDF.type, crm["E42_Appellation"]),
            (
                RDFS.label,
                Literal(
                    "Bibliographic reference of the origial source "
                    "as extrated from TEI file"
                )
            ),
            (crm["P190_has_symbolic_content"], Literal(print_source))
        )

        triples = itertools.chain(
            tei_triples,
            url_triples,
            id_triples,
            f1_triples,
            f2_triples,
            f3_triples,
            f27_triples,
            f28_triples,
            actor_triples,
            actor_gnd_triples,
            d1_triples,
            d1_id_triples,
            biblref_triples
        )

        yield from triples


##################################################
##################################################
# adhoc testing

# eltec_url = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-deu/master/level1/DEU007.xml"
# eltec_url = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-deu/master/level1/DEU002.xml"

# eltec_url = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-fra/master/level1/FRA00401_Allais.xml"

##errors
# eltec_url = "https://github.com/COST-ELTeC/ELTeC-fra/blob/master/level1/FRA00301_Aimard.xml"
eltec_url = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-eng/master/level1/ENG18440_Disraeli.xml"

converter = ELTeCConverter(eltec_url)

import json
d = converter.bindings
print(json.dumps(dict(d), indent=4))




# triples = converter.generate_triples()
# graph = Graph()
# CLSInfraNamespaceManager(graph)

# for triple in triples:
#     graph.add(triple)

# print(graph.serialize())
