"""Pydantic models for RDFGenerator bindings validation."""

from collections.abc import Iterator
from typing import Literal

from rdflib.namespace import RDFS
from pydantic import BaseModel, ConfigDict

import lodkit.importer
from eltec2rdf.vocabs import identifier


# better list cast here, else the iterator will likely be exhausted somewhere
vocab_id_types: tuple[str, ...] = tuple(
    map(str, identifier.objects(None, RDFS.label))
)

source_types: tuple[str, ...] = (
    "firstEdition",
    "printSource",
    "digitalSource",
    "unspecified"
)


class IDMapping(BaseModel):
    """Simple model schema for IDMappings."""

    id_type: Literal[vocab_id_types] | None
    id_value: str | None = None


class SourceData(IDMapping):
    """Model schema for source data (tei:sourceDesc)."""

    source_type: Literal[source_types]
    # source_type: str


class BindingsBaseModel(BaseModel):
    """Bindings model schema for basic CLSCor conversion."""

    model_config = ConfigDict(extra="allow")

    resource_uri: str
    work_title: str
    author_name: str

    author_ids: list[IDMapping] | None = None
    work_ids: list[SourceData] | None = None
