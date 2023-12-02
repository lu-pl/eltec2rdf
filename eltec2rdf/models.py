"""Pydantic models for RDFGenerator bindings validation."""

from collections.abc import Iterator
from typing import Literal

from rdflib.namespace import RDFS
from pydantic import BaseModel, ConfigDict

import lodkit.importer
from eltec2rdf.vocabs import identifier


# better list cast here, else the iterator will likely be exhausted somewhere
vocab_id_types: list[str] = list(
    map(str, identifier.objects(None, RDFS.label))
)


class IDMapping(BaseModel):
    """Simple model for IDMappings."""

    # work_type: Literal[]
    id_type: Literal[*vocab_id_types] | None = None
    id_value: str | None = None


class BindingsBaseModel(BaseModel):
    """BindingsValidator for basic CLSCor bindings."""

    model_config = ConfigDict(extra="allow")

    resource_uri: str
    work_title: str
    author_name: str

    author_ids: list[IDMapping] | None = None
    work_ids: list[IDMapping] | None = None
