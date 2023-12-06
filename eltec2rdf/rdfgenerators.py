"""Functionality for ELTeC to RDF conversion."""

import itertools

from collections.abc import Iterator
from contextlib import suppress
from types import SimpleNamespace

from lodkit.types import _Triple
from eltec2rdf.utils.utils import plist

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from clisn import crm, crmcls, lrm

from eltec2rdf.rdfgenerator_abc import RDFGenerator
from eltec2rdf.utils.utils import mkuri, uri_ns, resolve_source_type
from eltec2rdf.vocabs.vocabs import vocab, VocabLookupException
from eltec2rdf.models import SourceData


class CLSCorGenerator(RDFGenerator):
    """Basic RDFGenerator for the CLSCor model."""

    def generate_triples(self) -> Iterator[_Triple]:
        """Generate triples from an ELTeC resource."""
        work_ids: dict[URIRef, SourceData] = {
            mkuri(): ids
            for ids in self.bindings.work_ids
        }

        f3_uris: list[URIRef] = [
            mkuri()
            for ids in self.bindings.work_ids
        ]

        author_ids: dict[URIRef, dict] = {
            mkuri(_id.id_value): _id
            for _id in self.bindings.author_ids
        }

        uris: SimpleNamespace = uri_ns(
            "e39", "e35",
            ("e39_e41", f"{self.bindings.author_name} [E41]"),
            "x2", "x2_e42",
            ("x1_eltec", "ELTeC"),
            "f1", "f2", "f3", "f27", "f28"
        )

        # todo: singleton (type)
        schema_level1: str = (
            "https://raw.githubusercontent.com/COST-ELTeC/"
            "Schemas/master/eltec-1.rng"
        )
        schema_uri: URIRef = mkuri(schema_level1)

        e55_eltec_title_uri: URIRef = mkuri("ELTeC Title")
        e55_eltec_id_uri: URIRef = mkuri("ELTeC ID")
        e55_eltec_author_name_uri: URIRef = mkuri("ELTeC Author Name")

        x1_uri: URIRef = mkuri(self.bindings.repo_id)
        x8_uri: URIRef = mkuri("ELTeC Level 1 Schema")

        f1_triples = plist(
            uris.f1,
            (RDF.type, lrm.F1_Work),
            (RDFS.label, Literal(f"{self.bindings.work_title} [Work]")),
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
            (lrm.R4i_is_embodied_in, (uris.x2, *f3_uris))  # and f3s (todo)
        )

        x1_triples = plist(
            x1_uri,
            (RDF.type, crmcls.X1_Corpus),
            (lrm.R71_has_part, uris.x2),
            (crmcls.Y4i_is_subcorpus_of, uris.x1_eltec)
        )

        x1_eltec_triples = plist(
            uris.x1_eltec,
            (RDF.type, crmcls.X1_Corpus),
            (crmcls.Y4_has_subcorpus, x1_uri)
        )

        x2_triples = plist(
            uris.x2,
            (RDF.type, crmcls.X2_Corpus_Document),
            (RDFS.label, Literal(f"{self.bindings.work_title} [TEI Document]")),
            (crm.P1_is_identified_by, uris.x2_e42),
            (lrm.R4_embodies, uris.f2),
            (lrm.R71i_is_part_of, x1_uri),
            (crmcls.Y2_has_format, vocab("TEI")),
            (crmcls.Y3_adheres_to_schema, x8_uri)
        )

        x2_e42_triples = plist(
            uris.x2_e42,
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{self.bindings.work_title} [ELTeC ID]")),
            (crm.P190_has_symbolic_content, Literal(f"{self.bindings.file_stem}")),
            (crm.P2_has_type, e55_eltec_id_uri)
        )

        def work_id_triples() -> Iterator[_Triple]:
            """Triple iterator for work ID E42 assertions."""
            for e42_uri, work_data in work_ids.items():
                triples = plist(
                    e42_uri,
                    (RDF.type, crm.E42_Identifier),
                    (RDFS.label, Literal(f"{self.bindings.work_title} [ID]")),
                    (crm.P190_has_symbolic_content, Literal(f"{work_data.id_value}"))
                )

                with suppress(VocabLookupException):
                    vocab_uri = vocab(work_data.id_type)
                    yield (
                        e42_uri,
                        crm.P2_has_type,
                        vocab_uri
                    )

                yield from triples

        def f3_triples() -> Iterator[_Triple]:
            """Triple iterator for F3 generation based on work_ids."""
            for f3_uri, (e42_uri, work_data) in zip(f3_uris, work_ids.items()):
                f3_triples = plist(
                    f3_uri,
                    (RDF.type, lrm.F3_Manifestation),
                    (
                        RDFS.label,
                        Literal(f"{self.bindings.work_title} [Manifestation]")
                    ),
                    (crm.P1_is_identified_by, e42_uri),
                    (lrm.R4_embodies, uris.f2),
                )

                with suppress(VocabLookupException):
                    source_type: str = resolve_source_type(
                        work_data.source_type
                    )
                    vocab_uri = vocab(source_type)
                    yield (
                        f3_uri,
                        crm.P2_has_type,
                        vocab_uri
                    )

                yield from f3_triples

        x8_triples = plist(
            x8_uri,
            (RDF.type, crmcls.X8_Schema),
            (RDFS.label, Literal("ELTeC Level 1 RNG Schema")),
            (crm.P1_is_identified_by, schema_uri),
            (crmcls.Y3i_is_schema_of, uris.x2)
        )

        f27_triples = plist(
            uris.f27,
            (RDF.type, lrm.F27_Work_Creation),
            (RDFS.label, Literal(f"{self.bindings.work_title} [Work Creation]")),
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
            (crm.P2_has_type, e55_eltec_title_uri),
            (
                RDFS.label,
                Literal(f"{self.bindings.work_title} [Title of Expression]")
            ),
            (
                crm.p190_has_symbolic_content,
                Literal(f"{self.bindings.work_title}")
            )
        )

        def e39_triples() -> Iterator[_Triple]:
            """E39 triple generator."""
            first_id, *rest_ids = (
                mkuri(self.bindings.author_name),
                *author_ids.keys()
            )

            e42_uris = (
                mkuri(f"{author_id.id_value} [E42]")
                for _, author_id in author_ids.items()
            )

            e39_triples = plist(
                first_id,
                (RDF.type, crm.E39_Actor),
                (RDFS.label, Literal(f"{self.bindings.author_name} [Actor]")),
                (crm.P14i_performed, (uris.f27, uris.f28)),
                # create e41s based on author ids(todo)
                (crm.P1_is_identified_by, (uris.e39_e41, *e42_uris))
            )

            e39_same_as = (
                (first_id, OWL.sameAs, _id)
                for _id in rest_ids
            )

            yield from e39_triples
            yield from e39_same_as

        e39_e41_triples = plist(
            uris.e39_e41,
            (RDF.type, crm.E41_Appellation),
            (RDFS.label, Literal("ELTeC Author Name [Appellation]")),
            (
                crm.P190_has_symbolic_content,
                Literal(f"{self.bindings.author_name} [ELTeC Author Name]")
            ),
            (crm.P2_has_type, e55_eltec_author_name_uri),
            (crm.P1i_identifies, uris.e39)
        )

        def e39_e42_triples() -> Iterator[_Triple]:
            for _, author_id in author_ids.items():
                e42_uri = mkuri(f"{author_id.id_value} [E42]")
                e42_triples = plist(
                    e42_uri,
                    (RDF.type, crm.E42_Identifier),
                    (RDFS.label, Literal(f"{self.bindings.author_name} [ID]")),
                    (crm.P190_has_symbolic_content, Literal(f"{author_id.id_value}"))
                )

                with suppress(VocabLookupException):
                    vocab_uri = vocab(author_id.id_type)
                    yield (
                        e42_uri,
                        crm.P2_has_type,
                        vocab_uri
                    )

                yield from e42_triples

        # todo: singleton (type)
        e55_eltec_title_triples = plist(
            e55_eltec_title_uri,
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal("ELTeC Work Title")),
            (crm.P2i_is_type_of, uris.e35)
        )

        # todo: singleton (type)
        eltec_schema_triples = plist(
            schema_uri,
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal("Link to ELTeC Level 1 RNG Schema")),
            (crm.P190_has_symbolic_content, Literal(schema_level1))
        )

        # todo: singleton (type)
        e55_eltec_id_triples = plist(
            e55_eltec_id_uri,
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal("ELTeC Corpus Document ID")),
            (crm.P2i_is_type_of, uris.x2_e42)
        )

        e55_eltec_author_name_triples = plist(
            e55_eltec_author_name_uri,
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal("ELTeC Author Name")),
            (crm.P2i_is_type_of, uris.e39_e41)
        )

        triples = itertools.chain(
            f1_triples,
            f2_triples,
            x1_triples,
            x1_eltec_triples,
            x2_triples,
            x2_e42_triples,
            x8_triples,
            f3_triples(),
            f27_triples,
            f28_triples,
            e35_triples,
            e39_triples(),
            e39_e41_triples,
            e39_e42_triples(),
            e55_eltec_title_triples,
            e55_eltec_id_triples,
            e55_eltec_author_name_triples,
            eltec_schema_triples,
            work_id_triples()
        )

        return triples
