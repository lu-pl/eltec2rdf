"""Functionality for ELTeC to RDF conversion."""

import itertools

from collections.abc import Iterator
from contextlib import suppress
from types import SimpleNamespace

from lodkit.types import _Triple
from lodkit.utils import plist
from eltec2rdf.utils.utils import plist

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS
from clisn import crm, crmcls, crmdig, lrm

from eltec2rdf.rdfgenerator_abc import RDFGenerator
from eltec2rdf.utils.utils import mkuri, uri_ns
from eltec2rdf.vocabs.vocabs import vocab, VocabLookupException
from eltec2rdf.models import IDMapping, SourceData


class CLSCorGenerator(RDFGenerator):
    """Basic RDFGenerator for the CLSCor model."""

    def generate_triples(self) -> Iterator[_Triple]:
        """Generate triples from an ELTeC resource."""
        # add eltec repo id to work_ids
        self.bindings.work_ids.append(
            SourceData(
                id_type=None,
                id_value=self.bindings.file_stem,
                source_type="digitalSource"
            )
        )

        work_ids: dict[URIRef, SourceData] = {
            mkuri(): ids
            for ids in self.bindings.work_ids
        }

        author_ids: dict[URIRef, dict] = {
            mkuri(): ids
            for ids in self.bindings.author_ids
        }

        uris: SimpleNamespace = uri_ns(
            "x2", "x8",
            "e39", "e35",
            "f1", "f2", "f3", "f27", "f28"
        )

        schema_level1: str = (
            "https://raw.githubusercontent.com/COST-ELTeC/"
            "Schemas/master/eltec-1.rng"
        )
        schema_uri: URIRef = mkuri(schema_level1)
        e55_title_uri: URIRef = mkuri("ELTeC title")

        def work_id_triples() -> Iterator[_Triple]:
            """Triple iterator for work ID assertions."""
            for work_uri, work_data in work_ids.items():
                triples = plist(
                    work_uri,
                    (RDF.type, crm.E42_Identifier),
                    (RDFS.label, Literal(f"{self.bindings.work_title} [ID]")),
                    (crm.P190_has_symbolic_content, Literal(f"{work_data.id_value}"))
                )

                with suppress(VocabLookupException):
                    vocab_uri = vocab(work_data.id_type)
                    yield (
                        work_uri,
                        crm.P2_has_type,
                        vocab_uri
                    )

                yield from triples

        f1_triples = plist(
            uris.f1,
            (RDF.type, lrm.F1_Work),
            (RDFS.label, Literal(f"{self.bindings.work_title} [Work]")),
            # P1 [E42s from work_id] (todo)
            (lrm.R16i_was_created_by, uris.f27),
            (lrm.R3_is_realised_in, uris.f2),
            (lrm.R74i_has_expression_used_in, uris.f1)
        )

        f2_triples = plist(
            uris.f2,
            (RDF.type, lrm.F2_Expression),
            (RDFS.label, Literal(f"{self.bindings.work_title} [Expression]")),
            (crm.P102_has_title, uris.e35),
            (lrm.R3i_realises, uris.f1),
            (lrm.R17i_was_created_by, uris.f28),
            (lrm.R4i_is_embodied_in, uris.x2)  # and f3s (todo)
        )

        x2_triples = plist(
            uris.x2,
            (RDF.type, crmcls.X2_Corpus_Document),
            (RDFS.label, Literal(f"{self.bindings.work_title} [TEI Document]")),
            (crm.P1_is_identified_by, tuple(work_ids.keys())),
            (lrm.R4_embodies, uris.f2),
            (crmcls.Y2_has_format, vocab("TEI")),
            (crmcls.Y3_adheres_to_schema, uris.x8)
        )

        # f3_triples

        x8_triples = plist(
            uris.x8,
            (RDF.type, crmcls.X8_Schema),
            (RDFS.label, Literal("ELTeC Level 1 RNG Schema")),
            (crm.P1_is_identified_by, schema_uri),
            (crmcls.Y3i_is_schema_of, uris.x2)
        )

        f27_triples = plist(
            uris.f27,
            (RDF.type, lrm.F27_Work_Creation),
            (crm.P14_carried_out_by, uris.e39),
            (lrm.R16_created, uris.f1)
        )

        f28_triples = plist(
            uris.f28,
            (RDF.type, lrm.F28_Expression_Creation),
            (
                RDFS.label,
                Literal(f"{self.bindings.work_title} [Expression Creation]")
            ),
            (crm.P14_carried_out_by, uris.e39),
            (lrm.R17_created, uris.f2)
        )

        e35_triples = plist(
            uris.e35,
            (RDF.type, crm.E35_Title),
            (crm.P102i_is_title_of, uris.f2),
            (crm.P2_has_type, e55_title_uri),
            (
                RDFS.label,
                Literal(f"{self.bindings.work_title} [Title of Expression]")
            ),
            (
                crm.p190_has_symbolic_content,
                Literal(f"{self.bindings.work_title}")
            )
        )

        e55_title_triples = plist(
            e55_title_uri,
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal("ELTeC Work Title")),
            (crm.P2i_is_type_of, uris.e35)
        )

        e39_triples = plist(
            uris.e39,
            (RDF.type, crm.E39_Actor),
            (RDFS.label, Literal(f"{self.bindings.author_name} [Actor]")),
            (crm.P14i_performed, (uris.f27, uris.f28)),
            # create e41s based on author ids(todo)
            (crm.P1_is_identified_by, tuple(author_ids.keys()))
        )

        eltec_schema_uri = plist(
            schema_uri,
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal("Link to ELTeC Level 1 RNG Schema")),
            (crm.P190_has_symbolic_content, Literal(schema_level1))
        )

        triples = itertools.chain(
            f1_triples,
            f2_triples,
            x2_triples,
            x8_triples,
            f27_triples,
            f28_triples,
            e35_triples,
            e39_triples,
            e55_title_triples,
            eltec_schema_uri,
            work_id_triples()
        )

        return triples
